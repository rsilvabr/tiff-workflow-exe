# Version history

A package version names the tiff-workflow release it carries: `v2.7.2-exe1`
is the first package of tiff-workflow v2.7.2. What changed in tiff-workflow
itself is in [its changelog](https://github.com/rsilvabr/tiff-workflow/blob/master/docs/CHANGELOG.md).

| Version | Date | tiff-workflow | Highlights |
|---------|------|---------------|------------|
| **[v2.7.4-exe1](#v274-exe1)** | 2026-11-07 | v2.7.4 | Modes 0/9 keep each original in place until its copy is ready; safe cross-drive staging |
| [v2.7.3-exe1](#v273-exe1) | 2026-11-07 | v2.7.3 | Compress lists originals an interrupted mode 0/9 run left in `OLD_TIFFs` |
| [v2.7.2-exe1](#v272-exe1) | 2026-10-25 | v2.7.2 | First package |

---

## v2.7.4-exe1

*2026-11-07*

- Packages tiff-workflow
  [v2.7.4](https://github.com/rsilvabr/tiff-workflow/releases/tag/v2.7.4):
  modes 0 and 9 keep each original in place until its compressed copy is
  ready; a staging folder on another drive never writes over an original;
  the wizard offers to restore originals an interrupted run left behind.
- Same bundled tools as v2.7.2-exe1.

---

## v2.7.3-exe1

*2026-11-07*

- Packages tiff-workflow
  [v2.7.3](https://github.com/rsilvabr/tiff-workflow/releases/tag/v2.7.3):
  compress lists originals that an interrupted mode 0/9 run left in
  `OLD_TIFFs` with nothing in their place, and `-RestoreStranded` puts them
  back (`tiff-workflow.exe compress ... -RestoreStranded`).
- Same bundled tools as v2.7.2-exe1.

---

## v2.7.2-exe1

*2026-10-25*

- First package: tiff-workflow
  [v2.7.2](https://github.com/rsilvabr/tiff-workflow/releases/tag/v2.7.2)
  with PowerShell 7.6.7, ExifTool 13.59 and ImageMagick 7.1.2-27 (Q16-HDRI),
  built by GitHub Actions with a build attestation.
- `tiff-workflow.exe` opens the wizard; `--run-preset` / `--list-presets`
  work as in the Python version, and `compress`, `copy-exif` and
  `thumbnails` run one script directly.
- The scripts run under the bundled PowerShell 7 with the execution policy
  of the processes it starts set to Bypass, so they run on a PC with the
  default policy and from a zip unzipped from a download.
