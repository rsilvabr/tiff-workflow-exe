# How it works

## One program, a wizard and four scripts

tiff-workflow is a Python wizard (`convert_tiff.py`) and four PowerShell
scripts it starts as separate processes: `compress_tiff_zip.ps1`,
`copy_exif_to_TIFF_ps7.ps1` / `copy_exif_to_TIFF_ps5.ps1` (the same Copy
EXIF for PowerShell 7 and 5.1) and `generate_thumbnails.ps1`. The wizard
starts a script as `pwsh -NoProfile -File <script> ...`, finding `pwsh` on
`PATH`, and the scripts call `exiftool` and `magick` the same way.

The launcher (`src/tiff_workflow_exe.py`) routes its command line:

| Command line | Runs |
|---|---|
| `tiff-workflow.exe [options]` | `scripts\convert_tiff.py` (the wizard), through `runpy` as `__main__`, exactly as `python convert_tiff.py` would run it |
| `tiff-workflow.exe compress\|copy-exif\|thumbnails ...` | `tools\pwsh\pwsh.exe -NoProfile -File scripts\<script>.ps1 ...`; its exit code is the program's |

The wizard finds its scripts next to itself (`scripts\`), so nothing in
tiff-workflow is modified.

## Python and its libraries

PyInstaller builds a one-folder program: `tiff-workflow.exe` plus
`_internal\` with Python 3.12, rich and every standard-library module the
wizard imports. To find those modules the build imports the wizard as a
module (`hiddenimports` in `tiff-workflow.spec`) and collects rich
completely. The wizard also ships as a plain `.py` file in `scripts\`: that
is what runs.

## The tools

Before running anything the launcher puts `tools\pwsh`, `tools\exiftool`
and `tools\imagemagick` first on `PATH`, and sets `MAGICK_HOME` to the
ImageMagick folder (the portable build reads its configuration there). The
wizard detects PowerShell by trying `pwsh` first, so it finds the bundled
PowerShell 7 ahead of one installed on the PC, and every process it starts
inherits the same `PATH`.

| Tool | Source | Notes |
|---|---|---|
| PowerShell 7.6.7 | the official portable `PowerShell-7.6.7-win-x64.zip` | the whole folder: modules and runtime files are loaded on demand |
| ExifTool 13.59 | the official Windows build | `exiftool(-k).exe` is renamed `exiftool.exe`: the `(-k)` name waits for a key press after every call |
| ImageMagick 7.1.2-27 | official portable Q16-HDRI x64 | only `magick.exe` and its `.xml`/`.icc` configuration; the other programs in the archive are aliases of it |

ExifTool's Windows launcher finds its `exiftool_files` folder through an
ANSI path, so it cannot start from a folder whose name is outside the ANSI
code page (found in jxl-photo-exe, whose launcher this one follows). When
`tools\exiftool` is such a folder, the launcher puts the folder's 8.3 short
name on `PATH` instead; on a drive without short names it copies ExifTool
once (about 30 MB) to `%LOCALAPPDATA%\tiff-workflow\exiftool-<version>` (or
`%ProgramData%`, or the system drive: the first ANSI-safe one) and uses that
copy. `build.py` writes the version into `tools\exiftool\VERSION.txt` for
the folder name.

## The execution policy

Windows' default PowerShell execution policy (`Restricted`) runs no script
at all, and `RemoteSigned`, the usual one after a change, refuses an
unsigned script that carries the "from the internet" mark (an NTFS
`Zone.Identifier` stream) — which every file of a downloaded zip gets when
Explorer unzips it. The wizard starts its scripts without
`-ExecutionPolicy`.

The launcher sets `PSExecutionPolicyPreference=Bypass` in its own
environment. PowerShell reads that variable as the policy of its *Process*
scope, so it applies to every PowerShell this program starts, directly or
through the wizard, and to nothing else: the machine and user policies are
not changed and no file is unblocked. A policy set through Group Policy
(the *MachinePolicy* and *UserPolicy* scopes) takes precedence over it, as
designed.

It also sets `POWERSHELL_TELEMETRY_OPTOUT=1` and
`POWERSHELL_UPDATECHECK=Off`: PowerShell 7 would otherwise send a telemetry
ping when it starts.

## Logs

The four scripts write their logs into `Logs\<script>\` under the current
folder, and the wizard writes its own there too (its manifest-run summary
goes to `Logs\convert_tiff\` next to the wizard, in `scripts\`). The launcher
does not change the current folder: a double-click starts in the program
folder, a terminal in its own folder, a scheduled task in its *Start in*
folder — as with the Python version.

## Files next to the wizard

The wizard keeps the manifests it creates in a `manifests\` folder next to
itself: `scripts\manifests\` in the program folder.

## The build

`build.py`:

1. creates `.venv` with the pinned packages (rich) and PyInstaller;
2. downloads the tiff-workflow tag `TIFFWORKFLOW_TAG` from GitHub, takes the
   wizard, the four scripts and the license, and checks that the wizard's
   `TOOLKIT_VERSION` matches the tag;
3. downloads the three tools, checks each SHA-256, and copies what is needed
   into `build\app\tools`;
4. runs PyInstaller with `tiff-workflow.spec` (the Windows version
   information is written from the tag);
5. assembles `dist\tiff-workflow-<version>-x64\` and zips it.

`python build.py --scripts-from <tiff-workflow checkout>` takes the scripts
from a local folder instead of the tag, for a test build before a tag
exists; the version check still applies. Releases never use it.

Packaging a new tiff-workflow release: change `TIFFWORKFLOW_TAG`, push a
`vX.Y.Z-exe1` tag (GitHub Actions builds the zip with an attestation and
creates a draft release), run `tests/battery_on_exe.py --app` on that zip,
unzipped; publish only when every check passes.
