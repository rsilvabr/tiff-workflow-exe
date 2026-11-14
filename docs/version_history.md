# Version history

A package version names the tiff-workflow release it carries: `v2.7.2-exe1`
is the first package of tiff-workflow v2.7.2. What changed in tiff-workflow
itself is in [its changelog](https://github.com/rsilvabr/tiff-workflow/blob/master/docs/CHANGELOG.md).

| Version | Date | tiff-workflow | Highlights |
|---------|------|---------------|------------|
| **[v3.1.1-exe1](#v311-exe1)** | 2026-11-14 | v3.1.1 | Faster and lighter on the disk, the same files; thumbnails about twice as fast; Diagnose works in memory and recognizes padded black-and-white scans with IR |
| [v3.1.1-rc1-exe1](#v311-rc1-exe1) | 2026-11-14 | v3.1.1-rc1 | Test release (pre-release): rare edge cases closed by the final review of v3.1 |
| [v3.1.0-exe1](#v310-exe1) | 2026-11-13 | v3.1.0 | The usual Python command line (`--mode 1 --input-dir`); old command lines and presets of v3.0.0 are refused; fixes that stop a photo from being lost |
| [v3.0.0-exe1](#v300-exe1) | 2026-11-11 | v3.0.0 | The scripts are Python now: no PowerShell in the package, which is much smaller; same command line and results |
| [v2.9.1-exe1](#v291-exe1) | 2026-11-11 | v2.9.1 | Fixes: a black-and-white photo stored as RGB stays RGB; Japanese IPTC survives; no swap leaves a photo's place empty |
| [v2.9.0-exe1](#v290-exe1) | 2026-11-11 | v2.9.0 | A settings file instead of editing the scripts; Advanced options per run |
| [v2.8.0-exe1](#v280-exe1) | 2026-11-10 | v2.8.0 | exiftool works with a temp folder outside the code page; an edit record in every compressed photo; release notice |
| [v2.7.4-exe1](#v274-exe1) | 2026-11-07 | v2.7.4 | Modes 0/9 keep each original in place until its copy is ready; safe cross-drive staging |
| [v2.7.3-exe1](#v273-exe1) | 2026-11-07 | v2.7.3 | Compress lists originals an interrupted mode 0/9 run left in `OLD_TIFFs` |
| [v2.7.2-exe1](#v272-exe1) | 2026-10-25 | v2.7.2 | First package |

---

## v3.1.1-exe1

*2026-11-14*

- Packages tiff-workflow
  [v3.1.1](https://github.com/rsilvabr/tiff-workflow/releases/tag/v3.1.1): the fixes of the test
  release v3.1.1-rc1, and faster, lighter runs with the same files. Compression writes each
  file's metadata in a single pass (half the disk writes); `--generate-thumbnail` is about twice
  as fast; Diagnose works in memory, with no temporary files.
- Diagnose now recognizes padded black-and-white scans whose IR channel is a 4th sample (it
  reported them as real 16-bit). It asks one question less (how to compress temporary files:
  there are none); presets saved with the old answer keep working.
- Nothing else changes for whoever runs v3.1.0-exe1 or v3.1.1-rc1-exe1: the same command line,
  presets and settings.

---

## v3.1.1-rc1-exe1

*2026-11-14 -- a test release (GitHub pre-release), superseded by v3.1.1-exe1*

- Packages tiff-workflow
  [v3.1.1-rc1](https://github.com/rsilvabr/tiff-workflow/releases/tag/v3.1.1-rc1), the first
  test release of v3.1.1. Test releases are named `-rcN` (as jxl-photo's): that name is what a
  file rewritten with one records in its history, and the release check of the wizard reads it.
- Rare edge cases closed by the final review of v3.1: compress mode 8 with `--delete-source`
  keeps a `.tiff` whose compressed copy could not land; copy-exif `--compress-zip` checks the
  pixels of the file as it will land; Restore OLD_TIFFs moves an `x.tif` aside only when it is
  the restored photo's own compressed copy.
- Nothing changes for whoever runs v3.1.0-exe1: the same command line, presets and settings.
- The build gives the Windows version information the numbers only (`3.1.1.0`); the name with
  `-rc1` stays in its text fields.

---

## v3.1.0-exe1

*2026-11-13*

- Packages tiff-workflow
  [v3.1.0](https://github.com/rsilvabr/tiff-workflow/releases/tag/v3.1.0).
  **What breaks:** the commands take the usual Python options,
  `tiff-workflow.exe compress --mode 1 --input-dir "F:\Photos"` instead of
  `-Mode 1 -InputDir "F:\Photos"`. A `.bat` or scheduled task in the old form
  stops with exit code 2 and touches nothing until it is rewritten
  ([the table](https://github.com/rsilvabr/tiff-workflow/blob/master/docs/command_line.md)
  has every old option next to its new form). A preset saved by v3.0.0-exe1
  or earlier that holds the old command line is refused (`--run-preset`
  exits 1): run the workflow once from the wizard and save it again.
- The fixes of tiff-workflow v3.1.0, among them: compress modes 2, 4 and 5
  could replace one photo with another; on the plain screen a typed "no"
  could run what it declined; Delete OLD_TIFFs checks each pair again right
  before deleting. The list is in tiff-workflow's
  [changelog](https://github.com/rsilvabr/tiff-workflow/blob/master/docs/CHANGELOG.md#v310).
- `scripts\` holds tiff-workflow's new layout: `convert_tiff.py` and the
  folder `tiff_workflow\`. The launcher hands every command line to it; the
  package is left out of the program's bundle, so the plain files in
  `scripts\` are what runs and a default edited there counts. Updating over
  v3.0.0-exe1: delete the four old loose files in `scripts\`
  (`compress_tiff_zip.py`, `copy_exif_to_tiff.py`, `generate_thumbnails.py`,
  `tiff_workflow_common.py`); the wizard's start screen names them.
- ExifTool 13.59 and ImageMagick 7.1.2-27 (Q16-HDRI), the same versions as
  before.
- Battery: 425 checks pass -- the 394 of tiff-workflow's real-photo battery,
  run through the program, and 31 on the program itself (each command, a
  default edited in `scripts\`, a preset of v3.1 run twice, and presets of
  v3.0.0 and of the PowerShell edition refused with nothing written).

---

## v3.0.0-exe1

*2026-11-11*

- Packages tiff-workflow
  [v3.0.0](https://github.com/rsilvabr/tiff-workflow/releases/tag/v3.0.0):
  the scripts that do the work were rewritten from PowerShell to Python
  (`compress_tiff_zip.py`, `generate_thumbnails.py`, one
  `copy_exif_to_tiff.py` in place of the two Copy EXIF scripts, and the
  module they share, `tiff_workflow_common.py`). The command line and the
  results are the same: `tiff-workflow.exe compress|copy-exif|thumbnails`
  take the parameters they took before.
- PowerShell 7 is no longer in the package, and nothing in the program
  needs or starts PowerShell: no execution policy to set, no `tools\pwsh\`.
  The package is about 90 MB unzipped (36 MB zipped);
  v2.9.1-exe1 was about 350 MB (140 MB zipped), more than two thirds of it
  PowerShell 7.
- The launcher runs the scripts itself: `tiff-workflow.exe` is the Python
  the wizard starts its scripts with, and `compress`, `copy-exif` and
  `thumbnails` run in the program's own process.
- Several files at once is the scripts' default on any PC; it no longer
  depends on PowerShell 7.
- Presets saved by earlier versions keep working: the wizard reads their
  PowerShell command lines and runs the Python script with the same
  arguments.
- ExifTool 13.59 and ImageMagick 7.1.2-27 (Q16-HDRI), the same versions as
  before.
- Battery: 423 checks pass -- the 394 of tiff-workflow's real-photo battery, run
  through the program, and 29 on the program itself (each command, a preset
  saved from another folder and one saved by the PowerShell edition).
- [v2.9.1-exe1](https://github.com/rsilvabr/tiff-workflow-exe/releases/tag/v2.9.1-exe1)
  is the last package with PowerShell 7 inside and stays available;
  tiff-workflow describes that edition in
  [The PowerShell edition](https://github.com/rsilvabr/tiff-workflow/blob/master/docs/powershell_edition.md).

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
