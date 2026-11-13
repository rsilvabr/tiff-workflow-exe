# How it works

## One program, a wizard and three commands

Since v3.1, tiff-workflow is `convert_tiff.py`, which only starts it, and the
package `tiff_workflow\` next to it: the wizard (`wizard.py`), the three
backends that do the work (`compress_tiff_zip.py`, `copy_exif_to_tiff.py`,
`generate_thumbnails.py`) and the module they share (`common.py`).
`python convert_tiff.py` is the wizard; `python convert_tiff.py
compress|copy-exif|thumbnails ...` runs a backend (`tiff_workflow.cli.main`
decides which). The wizard starts a backend as a separate process,
`<the Python that runs the wizard> <its convert_tiff.py> <command> ...`
(`sys.executable`), and the backends call `exiftool` and `magick`, finding
them on `PATH`.

In the program, the Python that runs the wizard is `tiff-workflow.exe`
itself, so the wizard starts a backend as
`tiff-workflow.exe <folder>\convert_tiff.py compress ...`. The launcher
(`src/tiff_workflow_exe.py`) is the Python that runs the package, and it
only routes its command line to `tiff_workflow.cli.main`:

| Command line | Runs |
|---|---|
| `tiff-workflow.exe [options]` | the wizard, exactly as `python convert_tiff.py [options]` would run it |
| `tiff-workflow.exe compress\|copy-exif\|thumbnails ...` | that backend with the rest of the line, as `python convert_tiff.py compress ...` would (the command's name is taken in any case) |
| `tiff-workflow.exe <path>\convert_tiff.py ...` | the rest of the line: this is how the wizard starts a backend. Only the file's name counts; the package that runs is always the one in the program's own `scripts\` folder |

Everything runs in the program's own process: there is no second
interpreter and no other program in between. A backend's exit code is the
program's (Ctrl+C that reaches the launcher is 130).

The launcher puts `scripts\` first on Python's module path, and the package
finds its own files there, so nothing in tiff-workflow is modified.

Up to v2.9.1 the backends were PowerShell scripts and the package carried
PowerShell 7 to run them; that is described in the
[v2.9.1-exe1](https://github.com/rsilvabr/tiff-workflow-exe/blob/v2.9.1-exe1/docs/how_it_works.md)
version of this page. Since v3.0.0-exe1 there is no PowerShell in the
package and nothing in it starts one. Up to v3.0.x the toolkit was five
loose scripts in `scripts\`, run by path. A preset saved by v3.0.0 or
earlier that holds their command line (`-Mode 1 ...`, or a PowerShell one)
is refused since v3.1, with nothing touched: it has to be saved again.

## Python and its libraries

PyInstaller builds a one-folder program: `tiff-workflow.exe` plus
`_internal\` with Python 3.12, rich and every standard-library module the
toolkit imports. To find those modules, `tiff-workflow.spec` has PyInstaller
analyse `convert_tiff.py` and every module of the package (the imports
inside functions too) and collects rich completely; then it takes the
toolkit's own modules OUT of the bundle, because a bundled copy would be
imported instead of the plain files. `convert_tiff.py` and `tiff_workflow\`
ship as plain `.py` files in `scripts\`: those are what runs, and a default
edited in them counts (the test battery checks it).

## The tools

Before running anything the launcher puts `tools\exiftool` and
`tools\imagemagick` first on `PATH`, and sets `MAGICK_HOME` to the
ImageMagick folder (the portable build reads its configuration there). The
wizard and the backends find `exiftool` and `magick` there ahead of
versions installed on the PC. A backend the wizard starts is the same
launcher again, so it sets the same `PATH` itself.

| Tool | Source | Notes |
|---|---|---|
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

## Nothing to allow, nothing sent

The scripts are Python files read by the Python inside the program. Windows
has no execution policy for them, and the "from the internet" mark (an NTFS
`Zone.Identifier` stream) that every file of a downloaded zip gets when
Explorer unzips it does not stop them: Python does not look at it. The
launcher sets no policy and unblocks no file. The test battery still marks
every file of the program as a download before it runs it.

The launcher changes two environment variables, `PATH` and `MAGICK_HOME`,
and switches its own output to UTF-8 (a redirected output would otherwise
fall back to the ANSI code page, where a program folder named in Japanese
cannot be printed). The only network request the program makes is
the wizard's new-release notice (tiff-workflow's own feature; in the program
it follows tiff-workflow-exe's releases).

## Logs

The three backends write their logs into `Logs\<script>\` under the current
folder, and the wizard writes its own there too (`Logs\convert_tiff\`). The
launcher does not change the current folder: a double-click starts in the
program folder, a terminal in its own folder, a scheduled task in its
*Start in* folder — as with the Python version.

## Files next to convert_tiff.py

The folder of `convert_tiff.py` is tiff-workflow's installation: the wizard
keeps the manifests it creates in `manifests\` there, `scripts\manifests\`
in the program folder, and a settings file
(`.tiff_workflow_settings.json`) placed there is read before the one in the
user profile, where the wizard's menu 6 writes it by default.

## The build

`build.py`:

1. creates `.venv` with the pinned packages (rich) and PyInstaller;
2. downloads the tiff-workflow tag `TIFFWORKFLOW_TAG` from GitHub, takes
   `convert_tiff.py`, every `.py` of `tiff_workflow\` (no list to keep) and
   the license, and checks that `TOOLKIT_VERSION` in
   `tiff_workflow\__init__.py` matches the tag;
3. downloads the two tools (ExifTool and ImageMagick), checks each SHA-256,
   and copies what is needed into `build\app\tools`;
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
