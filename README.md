# tiff-workflow-exe — tiff-workflow as a Windows program

[tiff-workflow](https://github.com/rsilvabr/tiff-workflow) packaged as
`tiff-workflow.exe`: no Python to install, and the tools it calls
(ExifTool, ImageMagick) come in the same folder. Unzip and run.

> **If you can use Python, use the Python version.**
> [tiff-workflow](https://github.com/rsilvabr/tiff-workflow) itself is what
> its author runs on their own photo archive, so it is by far the more
> tested of the two. Both pass the same real-photo test battery; the program
> here is a newer way of packaging the same scripts, meant for people who
> would rather not install Python and the tools themselves.

**Current version: v3.1.1-exe1** (2026-11-15) ·
packages tiff-workflow
[v3.1.1](https://github.com/rsilvabr/tiff-workflow/releases/tag/v3.1.1) ·
ExifTool 13.59 · ImageMagick 7.1.2-27 (Q16-HDRI) ·
[All releases](docs/version_history.md) · [How it works](docs/how_it_works.md) ·
[Bug tracking](docs/bug_tracking.md)

---

## Contents

- [What it is](#what-it-is)
- [Download and first run](#download-and-first-run) · [Verifying a download](#verifying-a-download)
- [Command line](#command-line)
- [No PowerShell since v3.0.0](#no-powershell-since-v300)
- [Where settings, presets and logs go](#where-settings-presets-and-logs-go)
- [Updating and removing](#updating-and-removing)
- [What is in the folder](#what-is-in-the-folder)
- [Good to know](#good-to-know)
- [Testing](#testing)
- [Building from source](#building-from-source)
- [License](#license) · [Acknowledgments](#acknowledgments)

---

## What it is

tiff-workflow recompresses TIFF archives losslessly to ZIP/Deflate, copies
EXIF from the camera JPEG into Fuji S3/S5 Pro TIFFs, finds 16-bit TIFFs that
are really 8-bit, and makes sRGB thumbnails, with a pixel check before any
original is replaced. Everything it does is described in its own
[README](https://github.com/rsilvabr/tiff-workflow#readme) and documentation;
this repository only packages it:

- tiff-workflow's own files are **byte-for-byte** those of the tiff-workflow
  release named above, as plain `.py` files in `scripts\`: `convert_tiff.py`,
  which starts it, and the folder `tiff_workflow\` (the wizard, the three
  commands that do the work and the module they share). No feature is added
  or removed.
- A small launcher runs them with the Python inside the program and puts the
  bundled tools first on `PATH`. Nothing else is needed on the PC
  ([no PowerShell](#no-powershell-since-v300) either).
- Each version of this package names the tiff-workflow version it carries
  (`v2.7.2-exe1` = tiff-workflow v2.7.2, first package of it).

## Download and first run

1. Download `tiff-workflow-<version>-x64.zip` from
   [Releases](https://github.com/rsilvabr/tiff-workflow-exe/releases).
2. Unzip it to a folder of your own, for example `D:\Programs\tiff-workflow`.
   Avoid `C:\Program Files` (the folder must stay writable: the logs go there
   when you double-click) and do not run it from inside the zip.
3. Double-click **`tiff-workflow.exe`**. The interactive wizard opens in a
   console window and asks, step by step, what to do and where.

The first time, Windows SmartScreen may say *"Windows protected your PC"*:
the program is not code-signed. Choose **More info → Run anyway**.

## Verifying a download

Releases are built by GitHub Actions from the tagged code
([workflow](.github/workflows/release.yml)), not on the author's PC, and
GitHub records a build attestation for the zip and `tiff-workflow.exe`. With
the [GitHub CLI](https://cli.github.com/):

```
gh attestation verify tiff-workflow-<version>-x64.zip --repo rsilvabr/tiff-workflow-exe
```

It names the commit and the workflow run the file came from, and fails for a
file that was not built there. Every bundled tool is downloaded by
`build.py` from its official release with a SHA-256 check.

## Command line

From a terminal (`cmd` or PowerShell) in the program's folder:

```
tiff-workflow.exe                                 the interactive wizard
tiff-workflow.exe --run-preset "NIGHTLY ZIP"      a preset saved in the wizard, unattended
tiff-workflow.exe --list-presets
tiff-workflow.exe compress --mode 1 --input-dir "F:\Photos"
tiff-workflow.exe copy-exif --input-dir "F:\Fuji\S5pro"
tiff-workflow.exe thumbnails --input-dir "F:\Photos" --size 256
tiff-workflow.exe compress --help                 every option of a command
```

`tiff-workflow.exe` stands for tiff-workflow's `python convert_tiff.py`: each
line takes exactly what tiff-workflow takes there, and its exit code is
tiff-workflow's (0 done, 1 something failed, 2 a line that cannot run as
written). tiff-workflow's documentation applies word for word — replace
`python convert_tiff.py` with `tiff-workflow.exe`. Always pass
`--input-dir`: without it, a command works on the folder the terminal is in.

The commands work on several files at once by default, on any PC;
`--force-sequential` (compress) or `--workers 1` (copy-exif, thumbnails)
turns that off.

**A command line written for v3.0.0 or earlier is refused.** Since
tiff-workflow v3.1 an option is written in full, in lower case, with two
dashes: `--mode 9 --input-dir "F:\Photos" --no-safe-mode`, not
`-Mode 9 -InputDir "F:\Photos" -SafeMode:$false`. A `.bat`, scheduled task or
shortcut in the old form stops with exit code 2 and touches nothing until it
is rewritten. tiff-workflow's
[command line page](https://github.com/rsilvabr/tiff-workflow/blob/master/docs/command_line.md)
lists every old option next to its new form (the `tools/legacy_args.py` the
error message names is in tiff-workflow's repository, not in this program).
A preset saved by v3.0.0 or earlier that holds the old command line is
refused the same way (`--run-preset` exits 1, nothing touched): run its
workflow once from the wizard and save the preset again.

A preset can be run from a scheduled task or a shortcut:

```
"D:\Programs\tiff-workflow\tiff-workflow.exe" --run-preset "NIGHTLY ZIP"
```

Give the task a *Start in* folder you can write to: the logs go to `Logs\`
there.

## No PowerShell since v3.0.0

Up to v2.9.1 the work was done by PowerShell scripts, and the package
carried PowerShell 7 to run them. Since v3.0.0 the scripts are Python and
run in the program itself: there is no PowerShell in the package, nothing in
it starts one, and there is no execution policy to set or think about.
A preset saved by a PowerShell version that runs the scripts holds a
PowerShell command line and is refused, like those of v3.0.0
([Command line](#command-line)): save it again from the wizard.

[v2.9.1-exe1](https://github.com/rsilvabr/tiff-workflow-exe/releases/tag/v2.9.1-exe1)
is the last package with PowerShell 7 inside and stays available.
tiff-workflow describes that edition, and what changed with v3.0.0, in
[The PowerShell edition](https://github.com/rsilvabr/tiff-workflow/blob/master/docs/powershell_edition.md).

## Where settings, presets and logs go

| What | Where |
|---|---|
| Settings and presets | `%USERPROFILE%\.convert_tiff_config.json` — the same file the Python version uses, so both see the same presets. A preset runs the copy of tiff-workflow of the program that starts it, whichever copy saved it |
| Changed defaults (the wizard's menu 6, *Script settings*) | `%USERPROFILE%\.tiff_workflow_settings.json`, kept across updates; a `.tiff_workflow_settings.json` in `scripts\` is read instead when there is one |
| Logs | `Logs\` in the folder the program was started from: the program folder when you double-click, the terminal's folder from a command line, the task's *Start in* folder from Task Scheduler (exactly like the Python version) |
| Manifests the wizard creates | `scripts\manifests\` inside the program folder (next to `convert_tiff.py`, as in the Python version). A manifest you wrote yourself can live anywhere |
| A copy of ExifTool | `%LOCALAPPDATA%\tiff-workflow\exiftool-13.59`, only when the program folder's name is outside the Windows ANSI code page (Japanese, Cyrillic, ...) on a drive without 8.3 short names: ExifTool cannot start from such a folder |
| Temporary files | `%TEMP%`, or the staging folder you choose in the wizard |

Nothing goes to the Windows registry.

## Updating and removing

- **Update:** unzip the new version over the old folder, or into a new one.
  Settings and presets are kept either way; with a new folder, copy
  `scripts\manifests\` across if you use manifests (presets point at those
  files). Over the folder of v3.0.0-exe1 or earlier, delete the old loose
  files in `scripts\` afterwards — `compress_tiff_zip.py`,
  `copy_exif_to_tiff.py`, `generate_thumbnails.py`,
  `tiff_workflow_common.py`: their code is in `scripts\tiff_workflow\` now,
  and the wizard's start screen names them until they are gone. A default
  you had edited in one of them has to be set again (see below).
- **Remove:** delete the folder. The settings file and the logs stay in the
  places above until you delete them too.

## What is in the folder

| Path | What |
|---|---|
| `tiff-workflow.exe`, `_internal\` | Python 3.12, which runs the scripts, and the library the wizard uses (rich) |
| `scripts\` | tiff-workflow, unchanged: `convert_tiff.py`, which starts it, and `tiff_workflow\` — the wizard (`wizard.py`), the three commands (`compress_tiff_zip.py`, `copy_exif_to_tiff.py`, `generate_thumbnails.py`) and the module they share (`common.py`). These plain files are what runs: a default edited at the top of one of them counts, but the next update overwrites it; the wizard's menu 6 keeps a change across updates |
| `tools\exiftool\` | ExifTool 13.59 (Windows build) |
| `tools\imagemagick\` | `magick.exe` 7.1.2-27 portable (Q16-HDRI) and its configuration |
| `licenses\` | The licenses of everything above, Python's included (gathered by `build.py` from each download, so the folder is in the package, not in this repository) |

The program always uses its own tools, even when other versions are
installed on the PC: tiff-workflow was tested with exactly these.

## Good to know

- **Antivirus:** some engines flag unsigned programs built with PyInstaller.
  This package uses the one-folder layout, the one they object to least; if
  yours quarantines a file, restore it and add the folder as an exception.
- **Size:** about 90 MB unzipped (36 MB zipped).
- **Speed:** the work runs exactly as fast as with Python and the tools
  installed (the same scripts and tools do it).
- **Paths:** folders with Japanese or other non-Latin names, brackets,
  spaces, `%` and `&` are supported and tested, for the photos and for the
  program's own folder.
- **No network:** the program converts the files and folders you point it
  at, on your PC, and sends nothing about them anywhere. The one request it
  makes is the wizard's new-release notice: the main menu asks GitHub once a
  day for the latest release of this program (anonymous, nothing else sent;
  never for `--run-preset` or the `compress`/`copy-exif`/`thumbnails`
  commands). Turn it off with `"check_for_updates": false` in
  `%USERPROFILE%\.convert_tiff_config.json` or the environment variable
  `TIFFWORKFLOW_NO_UPDATE_CHECK`.
- **Bugs:** a problem with what tiff-workflow *does* (a compression, a
  thumbnail, the EXIF copy) belongs in
  [tiff-workflow's issues](https://github.com/rsilvabr/tiff-workflow/issues);
  a problem with the program itself (it does not start, a tool is missing)
  belongs [here](https://github.com/rsilvabr/tiff-workflow-exe/issues).

## Testing

`python tests/battery_on_exe.py` runs tiff-workflow's real-photo battery
(`tools/real_photo_battery.py` from a tiff-workflow checkout next to this
one) against the built program's scripts, with only the bundled exiftool
and magick on `PATH`. The scripts are started through `tiff-workflow.exe`
itself (the battery's "python" is the program), both several files at once
and one at a time. Before it, a section of its own drives
`tiff-workflow.exe`: the help, each command, a default edited in `scripts\`
(the program must use it), a preset of the current version saved from
another folder (run twice: the second run rewrites nothing), and presets
saved by v3.0.0 and by the PowerShell edition (refused, nothing written).

The program runs from a copy in a folder named `伊豆沼 [app] 100% & co` on a
drive without 8.3 short names, and every file of that copy carries the
"downloaded from the internet" mark, as after unzipping a download in
Explorer (Python does not look at the mark; the test keeps it so that the
program is run as a download leaves it). The photos (camera exports, film scans with an IR page, Fuji S5
Pro sessions, TIFFs that lost every tag) are processed in folders with
Japanese, brackets, spaces and `%`. Each release runs it against the zip
GitHub built, before the release is published; the release notes give the
result.

## Building from source

Needs Python 3.12 on `PATH` and an internet connection:

```
python build.py
```

It creates a virtual environment in `.venv` (pinned packages and
PyInstaller), downloads the tiff-workflow tag and the tools (each SHA-256
checked), and writes `dist\tiff-workflow-<version>-x64\` plus its zip. The
tiff-workflow tag and the tool versions are settings at the top of
`build.py`. Releases run the same `build.py` on GitHub Actions when a
`v*-exe*` tag is pushed.
Details: [How it works](docs/how_it_works.md).

## License

MIT for this packaging (see [LICENSE](LICENSE)). The package also contains
tiff-workflow (MIT), ExifTool (the same terms as Perl: GPL or Artistic
License), ImageMagick (its own Apache-2.0-style license) and Python with
rich (PSF and MIT). They are listed in `licenses\` and in the
PyInstaller-collected notices under `_internal\`.

## Acknowledgments

- [ExifTool](https://exiftool.org) (Phil Harvey) and
  [ImageMagick](https://imagemagick.org), which do the real work
- [PyInstaller](https://pyinstaller.org), which makes the Python program a
  Windows one
- [Claude](https://www.anthropic.com/claude) (Anthropic), among other AI tools,
  for code assistance, reviews and technical discussion
