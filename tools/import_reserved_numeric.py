#!/usr/bin/env python3
"""Match release ZIP images to a pre-registered numeric URL catalog."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from PIL import Image, ImageOps, UnidentifiedImageError

from import_release import safe_image_members


DEFAULT_BATCH_ID = "photos-1-15000"
DEFAULT_BATCH_NAME = "Product Image Collection"
DEFAULT_END = 15_000
NUMERIC_JPG = re.compile(r"^([1-9][0-9]{0,4})\.jpg$", re.IGNORECASE)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--docs-dir", default="docs", type=Path)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=DEFAULT_END)
    parser.add_argument("--batch-id", default=DEFAULT_BATCH_ID)
    parser.add_argument("--batch-name", default=DEFAULT_BATCH_NAME)
    parser.add_argument("--sequence-by-archive-order", action="store_true")
    args = parser.parse_args()

    if args.tag != args.batch_id:
        raise SystemExit("release tag and batch ID must match")
    if not 1 <= args.start <= args.end:
        raise SystemExit("start and end must define a positive numeric range")

    archives = sorted(args.input_dir.glob("*.zip"))
    if not archives:
        raise SystemExit("No ZIP files found")

    catalog_path = args.docs_dir / "data" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    assets = {item.get("id"): item for item in catalog.get("assets", []) if item.get("batchId") == args.batch_id}
    expected_count = args.end - args.start + 1
    if len(assets) != expected_count:
        raise SystemExit("The numeric reservation catalog is missing; run reserve_numeric_library.py first")

    thumb_dir = args.docs_dir / "thumbnails" / args.batch_id
    thumb_dir.mkdir(parents=True, exist_ok=True)
    seen: set[int] = set()
    imported = 0
    next_number = args.start

    for zip_path in archives:
        archive_url = (
            f"https://github.com/{args.repo}/releases/download/"
            f"{quote(args.tag, safe='')}/{quote(zip_path.name)}"
        )
        with zipfile.ZipFile(zip_path) as archive:
            for info in safe_image_members(archive):
                basename = PurePosixPath(info.filename).name
                if args.sequence_by_archive_order:
                    if next_number > args.end:
                        raise ValueError("Archives contain more images than the reserved range")
                    number = next_number
                    next_number += 1
                else:
                    match = NUMERIC_JPG.fullmatch(basename)
                    if not match:
                        print(f"Ignoring non-reserved filename: {info.filename}", file=sys.stderr)
                        continue
                    number = int(match.group(1))
                    if not args.start <= number <= args.end:
                        print(f"Ignoring out-of-range filename: {info.filename}", file=sys.stderr)
                        continue
                if number in seen:
                    raise ValueError(f"Duplicate reserved filename found: {number}.jpg")
                seen.add(number)

                asset_id = f"{args.batch_id}-{number:05d}"
                thumb_name = f"{number:05d}.webp"
                thumb_path = thumb_dir / thumb_name
                try:
                    with archive.open(info) as source, Image.open(source) as raw:
                        image = ImageOps.exif_transpose(raw)
                        width, height = image.size
                        if width < 2 or height < 2:
                            raise ValueError("image dimensions are too small")
                        if image.mode not in {"RGB", "RGBA"}:
                            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
                        image.thumbnail((720, 540), Image.Resampling.LANCZOS)
                        if image.mode == "RGBA":
                            canvas = Image.new("RGB", image.size, "#F3F0E9")
                            canvas.paste(image, mask=image.getchannel("A"))
                            image = canvas
                        else:
                            image = image.convert("RGB")
                        image.save(thumb_path, "WEBP", quality=76, method=6)
                except (UnidentifiedImageError, OSError, ValueError) as error:
                    thumb_path.unlink(missing_ok=True)
                    print(f"Skipping unreadable image {info.filename}: {error}", file=sys.stderr)
                    continue

                item = assets[asset_id]
                item.update(
                    {
                        "title": f"{number}.jpg",
                        "sourcePath": info.filename,
                        "width": width,
                        "height": height,
                        "thumbnail": f"./thumbnails/{args.batch_id}/{thumb_name}",
                        "originalName": f"{number}.jpg",
                        "originalUrl": (
                            f"https://{args.repo.split('/', 1)[0].lower()}.github.io/"
                            f"{args.repo.split('/', 1)[1]}/thumbnails/{args.batch_id}/{thumb_name}"
                        ),
                        "archiveName": zip_path.name,
                        "archiveUrl": archive_url,
                        "releaseTag": args.tag,
                        "status": "ready",
                    }
                )
                imported += 1

    ready_count = sum(item.get("status") == "ready" for item in assets.values())
    if args.sequence_by_archive_order and next_number != args.end + 1:
        raise ValueError(f"Archives contain {next_number - args.start} images; expected {expected_count}")
    for batch in catalog.get("batches", []):
        if batch.get("id") == args.batch_id:
            batch.update(
                {
                    "name": args.batch_name,
                    "count": expected_count,
                    "readyCount": ready_count,
                    "archiveName": "一个或多个 ZIP",
                    "archiveUrl": f"https://github.com/{args.repo}/releases/tag/{quote(args.tag, safe='')}",
                    "releaseTag": args.tag,
                    "status": "ready" if ready_count == expected_count else "indexing",
                }
            )

    catalog["generatedAt"] = datetime.now(timezone.utc).isoformat()
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Matched {imported} uploaded images; {ready_count}/{expected_count} are ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
