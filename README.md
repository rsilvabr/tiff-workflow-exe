# tiff-workflow-exe — tiff-workflow as a Windows program

[tiff-workflow](https://github.com/rsilvabr/tiff-workflow) packaged as
`tiff-workflow.exe`: no Python to install, and the tools it calls
(PowerShell 7, ExifTool, ImageMagick) come in the same folder. Unzip and run.

> **If you can use Python, use the Python version.**
> [tiff-workflow](https://github.com/rsilvabr/tiff-workflow) itself is what
> its author runs on their own photo archive, so it is by far the more
> tested of the two. Both pass the same real-photo test battery; the program
> here is a newer way of packaging the same scripts, meant for people who
> would rather not install Python and the tools themselves.

**Current version: v2.9.0-exe1** (2026-11-11) · packages tiff-workflow
[v2.9.0](https://github.com/rsilvabr/tiff-workflow/releases/tag/v2.9.0) ·
PowerShell 7.6.7 · ExifTool 13.59 · ImageMagick 7.1.2-27 (Q16-HDRI) ·
[All releases](docs/version_history.md) · [How it works](docs/how_it_works.md) ·
[Bug tracking](docs/bug_tracking.md)

---

## Contents

- [What it is](#what-it-is)
- [Download and first run](#download-and-first-run) · [Verifying a download](#verifying-a-download)
- [Command line](#command-line)
- [PowerShell and the execution policy](#powershell-and-the-execution-policy)
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

- The wizard (`convert_tiff.py`) and the four PowerShell scripts inside are
  **byte-for-byte** those of the tiff-workflow release named above. No
  feature is added or removed.
- A small launcher starts them, puts the bundled tools first on `PATH`, and
  lets PowerShell run the bundled scripts
  ([below](#powershell-and-the-execution-policy)).
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
gh attestation verify tiff-workflow-2.9.0-exe1-x64.zip --repo rsilvabr/tiff-workflow-exe
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
tiff-workflow.exe compress   -Mode 1 -InputDir "F:\Photos"     (compress_tiff_zip.ps1)
tiff-workflow.exe copy-exif  -InputDir "F:\Fuji\S5pro"         (copy_exif_to_TIFF_ps7.ps1)
tiff-workflow.exe thumbnails -InputDir "F:\Photos" -Size 256   (generate_thumbnails.ps1)
```

Each `compress`/`copy-exif`/`thumbnails` line takes exactly what the
matching PowerShell script takes, and runs it under the bundled
PowerShell 7: tiff-workflow's per-script documentation applies word for
word — replace `pwsh -NoProfile -File compress_tiff_zip.ps1` with
`tiff-workflow.exe compress`, and so on. Always pass `-InputDir`: without
it, a script works on the folder the terminal is in. `copy-exif` is the
parallel PowerShell 7 version of Copy EXIF.

A preset can be run from a scheduled task or a shortcut:

```
"D:\Programs\tiff-workflow\tiff-workflow.exe" --run-preset "NIGHTLY ZIP"
```

Give the task a *Start in* folder you can write to: the logs go to `Logs\`
there.

## PowerShell and the execution policy

The work is done by PowerShell scripts. Windows' default execution policy
refuses to run any `.ps1` file, and the files of a zip unzipped from a
download carry a "from the internet" mark that the common `RemoteSigned`
policy refuses as well. So the launcher sets the policy of the PowerShell
processes it starts to `Bypass` (the `PSExecutionPolicyPreference`
environment variable, read by PowerShell as its *Process* scope). Your PC's
own policy is not changed, nothing is unblocked on disk, and a PowerShell
you open yourself behaves as before.

A policy set by your organisation through Group Policy still wins over
that; the scripts then cannot run from this program either.

PowerShell 7 comes in the package, so Copy EXIF and the compression always
run in parallel; a PowerShell 7 installed on the PC is not used, and
Windows' own PowerShell 5.1 is not needed.

## Where settings, presets and logs go

| What | Where |
|---|---|
| Settings and presets | `%USERPROFILE%\.convert_tiff_config.json` — the same file the Python version uses, so both see the same presets. A preset runs the scripts next to the program that starts it, whichever version saved it |
| Logs | `Logs\` in the folder the program was started from: the program folder when you double-click, the terminal's folder from a command line, the task's *Start in* folder from Task Scheduler (exactly like the Python version) |
| Manifests the wizard creates | `scripts\manifests\` inside the program folder (next to the wizard, as in the Python version). A manifest you wrote yourself can live anywhere |
| A copy of ExifTool | `%LOCALAPPDATA%\tiff-workflow\exiftool-13.59`, only when the program folder's name is outside the Windows ANSI code page (Japanese, Cyrillic, ...) on a drive without 8.3 short names: ExifTool cannot start from such a folder |
| Temporary files | `%TEMP%`, or the staging folder you choose in the wizard |

Nothing goes to the Windows registry.

## Updating and removing

- **Update:** unzip the new version over the old folder, or into a new one.
  Settings and presets are kept either way; with a new folder, copy
  `scripts\manifests\` across if you use manifests (presets point at those
  files).
- **Remove:** delete the folder. The settings file and the logs stay in the
  places above until you delete them too.

## What is in the folder

| Path | What |
|---|---|
| `tiff-workflow.exe`, `_internal\` | Python 3.12 and the library the wizard uses (rich) |
| `scripts\` | The tiff-workflow wizard and its four PowerShell scripts, unchanged |
| `tools\pwsh\` | PowerShell 7.6.7, the official portable build (`PowerShell-7.6.7-win-x64.zip`) |
| `tools\exiftool\` | ExifTool 13.59 (Windows build) |
| `tools\imagemagick\` | `magick.exe` 7.1.2-27 portable (Q16-HDRI) and its configuration |
| `licenses\` | The licenses of everything above, Python's included (gathered by `build.py` from each download, so the folder is in the package, not in this repository) |

The program always uses its own tools, even when other versions are
installed on the PC: tiff-workflow was tested with exactly these.

## Good to know

- **Antivirus:** some engines flag unsigned programs built with PyInstaller.
  This package uses the one-folder layout, the one they object to least; if
  yours quarantines a file, restore it and add the folder as an exception.
- **Size:** about 350 MB unzipped (140 MB zipped), more than two thirds of
  it PowerShell 7.
- **Speed:** the work runs exactly as fast as with Python and PowerShell 7
  installed (the same scripts and tools do it).
- **Paths:** folders with Japanese or other non-Latin names, brackets,
  spaces, `%` and `&` are supported and tested, for the photos and for the
  program's own folder.
- **No network:** the program converts the files and folders you point it
  at, on your PC. PowerShell's telemetry and update check are turned off for
  the processes it starts.
- **Bugs:** a problem with what tiff-workflow *does* (a compression, a
  thumbnail, the EXIF copy) belongs in
  [tiff-workflow's issues](https://github.com/rsilvabr/tiff-workflow/issues);
  a problem with the program itself (it does not start, a tool is missing)
  belongs [here](https://github.com/rsilvabr/tiff-workflow-exe/issues).

## Testing

`python tests/battery_on_exe.py` runs tiff-workflow's real-photo battery
(`tools/real_photo_battery.py` from a tiff-workflow checkout next to this
one) against the built program's scripts, under the bundled PowerShell 7,
with only the bundled pwsh, exiftool and magick on `PATH`. Before it, a
section of its own drives `tiff-workflow.exe` itself: each command, the
help, a preset saved from another folder (run twice), and the execution
policy.

The program runs from a copy in a folder named `伊豆沼 [app] 100% & co` on a
drive without 8.3 short names, and every file of that copy carries the
"downloaded from the internet" mark, as after unzipping a download in
Explorer. The photos (camera exports, film scans with an IR page, Fuji S5
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
tiff-workflow (MIT), PowerShell (MIT, with the notices of its own
components), ExifTool (the same terms as Perl: GPL or Artistic License),
ImageMagick (its own Apache-2.0-style license) and Python with rich (PSF
and MIT). They are listed in `licenses\` and in the PyInstaller-collected
notices under `_internal\`.

## Acknowledgments

- [PowerShell](https://github.com/PowerShell/PowerShell),
  [ExifTool](https://exiftool.org) (Phil Harvey) and
  [ImageMagick](https://imagemagick.org), which do the real work
- [PyInstaller](https://pyinstaller.org), which makes the Python program a
  Windows one
- [Claude](https://www.anthropic.com/claude) (Anthropic), among other AI tools,
  for code assistance, reviews and technical discussion
