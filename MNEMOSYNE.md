# MNEMOSYNE.md

Project memory anchor for context compression, handoff, and continuity.

## Current Snapshot

- Date: 2026-08-31
- Active goal: URL reservation complete; matching photo archives are pending.
- Releases: `photos-1-15000` and `photos-15001-28441`, 33 ZIP assets total, all uploaded.
- Gallery: 28,441 ready assets and 2,940 reserved assets; catalog total 31,381.
- Reserved range: `28442-31381`, batch and future Release tag `photos-28442-31381`.
- Public site: https://arthurescc.github.io/product-image/
- Verification: 31,381 unique IDs; new range continuous and all reserved; URL mapping errors 0; public gallery still renders 28,441 ready assets.

## Stable Decisions

- Gallery card clicks open an image preview dialog. They must not download or navigate to a ZIP.
- `originalUrl` is the per-image GitHub Pages WebP URL; `archiveUrl` is the containing Release ZIP URL.
- Public copy must not expose ingestion, upload, pre-registration, or internal operating instructions.
- Decision: this repository is independent. It has no shared thumbnails, catalogs, releases, or upload portal with any other repository.
- Numeric release tags use `photos-<start>-<end>` and stable Pages URLs under `thumbnails/<tag>/<number>.webp`.
- Non-numeric source filenames can be assigned consecutive public numbers in archive filename order and ZIP member order.
- The numeric reservation workflow accepts tag, start, and end inputs; reserved rows remain hidden until matching images are imported.

## Known Constraints

- Browsers cannot address an individual JPG inside a ZIP. Public per-image URLs therefore point to independently published WebP previews.
- Original JPG files remain in GitHub Release ZIP archives. The first release uses 500-image archives; `photos-15001-28441` uses 5,000, 5,000, and 3,441-image archives.
- Release-triggered workflows must check out `main`; the release event otherwise leaves Actions in detached HEAD and `git push` fails.
- Pushes made with `GITHUB_TOKEN` do not trigger the Pages workflow, so run `pages.yml` manually after a workflow pushes generated docs.
- URLs for `28442-31381` are reserved now, but their WebP endpoints intentionally return no image until the future Release is imported.

## Verification Commands

- Publish new image ZIP archives to `Arthurescc/product-image` Releases; the local import workflow generates this library's previews and URL indexes.
- Check `docs/data/catalog.json` for 31,381 unique assets: 28,441 ready and 2,940 reserved.
- Check batch `photos-28442-31381` for continuous titles and URLs from `28442.jpg` through `31381.jpg`.
- Request public `data/catalog.json`, CSV, and Excel after Pages deployment.

## Work Log

### 2026-08-31

- Confirmed the repository's existing maximum public photo number is 28,441.
- Parameterized `.github/workflows/reserve-numeric-library.yml` for future numeric ranges.
- Pre-registered 2,940 stable URLs for photos 28,442 through 31,381 under `photos-28442-31381`.
- Regenerated catalog, Excel, and CSV; deployed Pages with run `33374425721`.
- Verified 31,381 total/unique records, 2,940 reserved records, zero URL mapping errors, and 28,441 publicly visible ready photos.
- Next step: publish matching photo archives under Release tag `photos-28442-31381`, then run the numeric import workflow for range `28442-31381`.

### 2026-08-23

- Pre-registered stable URLs for photos 15001-28441 and generalized numeric range imports.
- Added sequential archive-order mapping for ZIPs whose source JPG names are not numeric.
- Uploaded and published Release `photos-15001-28441` with `15001-20000.zip`, `20001-25000.zip`, and `25001-28441.zip`.
- Fixed release imports to check out `main`, then reran import workflow `32610519663` successfully.
- Generated 13,441 WebP previews, final dimensions, catalog rows, Excel, and CSV; deployed Pages with run `32611183733`.
- Verified six boundary image URLs, public catalog totals, downloadable Excel/CSV, and browser-rendered gallery totals.

### 2026-08-13

- Uploaded and verified all 30 ZIP archives for images 1-15000.
- Imported all images into the public gallery and generated 15,000 WebP previews.
- Removed internal upload panels and internal terminology from the visitor-facing site.
- Changed card interaction from ZIP download to an accessible image preview dialog.
- Corrected all 15,000 `originalUrl` fields to independent public image URLs.
