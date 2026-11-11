# Version history

A package version names the tiff-workflow release it carries: `v2.7.2-exe1`
is the first package of tiff-workflow v2.7.2. What changed in tiff-workflow
itself is in [its changelog](https://github.com/rsilvabr/tiff-workflow/blob/master/docs/CHANGELOG.md).

| Version | Date | tiff-workflow | Highlights |
|---------|------|---------------|------------|
| **[v2.9.1-exe1](#v291-exe1)** | 2026-11-11 | v2.9.1 | Fixes: a black-and-white photo stored as RGB stays RGB; Japanese IPTC survives; no swap leaves a photo's place empty |
| [v2.9.0-exe1](#v290-exe1) | 2026-11-11 | v2.9.0 | A settings file instead of editing the scripts; Advanced options per run |
| [v2.8.0-exe1](#v280-exe1) | 2026-11-10 | v2.8.0 | exiftool works with a temp folder outside the code page; an edit record in every compressed photo; release notice |
| [v2.7.4-exe1](#v274-exe1) | 2026-11-07 | v2.7.4 | Modes 0/9 keep each original in place until its copy is ready; safe cross-drive staging |
| [v2.7.3-exe1](#v273-exe1) | 2026-11-07 | v2.7.3 | Compress lists originals an interrupted mode 0/9 run left in `OLD_TIFFs` |
| [v2.7.2-exe1](#v272-exe1) | 2026-10-25 | v2.7.2 | First package |

---

## v2.9.1-exe1

*2026-11-11*

- Packages tiff-workflow
  [v2.9.1](https://github.com/rsilvabr/tiff-workflow/releases/tag/v2.9.1),
  fixes only: a black-and-white photo stored as RGB stays RGB when
  compressed (it used to come out with one gray channel and the RGB profile
  still in it -- if you compressed such files with an earlier version, see
  that release's notes), IPTC text outside Latin survives, and replacing a
  file is a single rename everywhere, so no swap can leave a photo's place
  empty.
- Same bundled tools as v2.7.2-exe1.

---

## v2.9.0-exe1

*2026-11-11*

- Packages tiff-workflow
  [v2.9.0](https://github.com/rsilvabr/tiff-workflow/releases/tag/v2.9.0):
  the scripts' settings (folder names, timeouts, thumbnail defaults, memory
  share) can live in `.tiff_workflow_settings.json` instead of being edited
  in the scripts -- for this program, put it next to the scripts in its
  `scripts` folder or in your user profile; main menu [6] edits it. The
  wizard also offers Advanced options per run.
- Same bundled tools as v2.7.2-exe1.

---

## v2.8.0-exe1

*2026-11-10*

- Packages tiff-workflow
  [v2.8.0](https://github.com/rsilvabr/tiff-workflow/releases/tag/v2.8.0):
  exiftool works when the Windows temp folder has characters outside the
  system's code page (a user name in another script); every TIFF compress
  rewrites records it in the photo's `xmpMM:History`; the release is in every
  log and in `tiff-workflow.exe --version`; the menu says when a newer
  release of this program is out (it follows tiff-workflow-exe's releases).
- Same bundled tools as v2.7.2-exe1.

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
