"""tiff-workflow.exe: the tiff-workflow toolkit as a Windows program, no Python needed.

The toolkit ships unchanged, as plain `.py` files, in `scripts/` next to the program: the
entry point convert_tiff.py and the package tiff_workflow/ (tiff-workflow v3.1); ExifTool
and ImageMagick in `tools/`. This launcher is the Python that runs them, and it only routes,
to tiff_workflow.cli.main:

    tiff-workflow.exe                          the interactive wizard
    tiff-workflow.exe --run-preset NAME ...    the wizard, with its own options
    tiff-workflow.exe compress|copy-exif|thumbnails ARGS
                                               one backend directly
    tiff-workflow.exe <...>\\convert_tiff.py ARGS
                                               how the wizard starts a backend: it runs
                                               `sys.executable <its convert_tiff.py>
                                               <subcommand> ARGS`, and here sys.executable is
                                               this program

Whatever folder that path names, what runs is the package in this program's own scripts/,
found through sys.path. The package is never bundled into the program
(tiff-workflow.spec): the plain files run, so a setting edited in them counts.

Before running anything it puts tools/ first on PATH (the wizard and the
backends find exiftool and magick there).

Until v2.9.1 the backends were PowerShell scripts and the package carried
PowerShell 7; from v3.0.0 they are Python (up to v3.0.x, loose scripts in scripts/).
"""

import os
import shutil
import sys
from pathlib import Path

#: The backends, by the name tiff_workflow.cli runs them under (any case is taken here).
SUBCOMMANDS = ("compress", "copy-exif", "thumbnails")
#: The toolkit's entry point; a path to it as the first word is how the wizard starts a backend.
ENTRY = "convert_tiff.py"


def _app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent / "build" / "app"


APP = _app_dir()
SCRIPTS = APP / "scripts"
TOOLS = APP / "tools"


def _ansi_safe(path: str) -> bool:
    """True when `path` survives the ANSI code page (the "mbcs" codec)."""
    try:
        path.encode("mbcs", "strict")
        return True
    except UnicodeEncodeError:
        return False


def _short_path(path: Path):
    import ctypes
    buf = ctypes.create_unicode_buffer(32768)
    n = ctypes.windll.kernel32.GetShortPathNameW(str(path), buf, len(buf))
    return buf.value if 0 < n < len(buf) else None


def _exiftool_dir() -> Path:
    """The folder to put on PATH for exiftool.

    ExifTool's Windows launcher looks for its exiftool_files folder through
    an ANSI path: in a program folder named in Japanese, Cyrillic or any
    script outside the ANSI code page it fails ("Could not find ...???...
    perl5*.dll") while magick works. The 8.3 short name of the folder fixes
    that where the volume has short names (usually C:); on one without them,
    ExifTool is copied once to an ANSI-safe folder.
    """
    bundled = TOOLS / "exiftool"
    if not bundled.is_dir() or _ansi_safe(str(bundled)):
        return bundled
    short = _short_path(bundled)
    if short and _ansi_safe(short):
        return Path(short)
    version_file = bundled / "VERSION.txt"
    version = (version_file.read_text(encoding="utf-8").strip()
               if version_file.is_file() else "unknown")
    bases = [os.environ.get("LOCALAPPDATA"), os.environ.get("ProgramData"),
             (os.environ.get("SystemDrive") or "C:") + "\\"]
    for base in bases:
        if not base:
            continue
        target = Path(base) / "tiff-workflow" / f"exiftool-{version}"
        if not _ansi_safe(str(target)):
            continue
        if (target / "exiftool.exe").is_file():
            return target
        tmp = target.with_name(f"{target.name}.{os.getpid()}.tmp")
        try:
            shutil.copytree(bundled, tmp)
            for f in tmp.rglob("*"):   # deletable later, like the package
                os.chmod(f, 0o666 if f.is_file() else 0o777)
            os.replace(tmp, target)
            return target
        except OSError:
            shutil.rmtree(tmp, ignore_errors=True)
            if (target / "exiftool.exe").is_file():   # another start won the race
                return target
    return bundled   # nothing better: the wizard reports exiftool as missing


def _setup_environment() -> None:
    tool_dirs = [_exiftool_dir(), TOOLS / "imagemagick"]
    found = [str(d) for d in tool_dirs if d.is_dir()]
    os.environ["PATH"] = os.pathsep.join(found + [os.environ.get("PATH", "")])
    # The portable ImageMagick reads its configuration from its own folder.
    if (TOOLS / "imagemagick").is_dir():
        os.environ.setdefault("MAGICK_HOME", str(TOOLS / "imagemagick"))
    sys.path.insert(0, str(SCRIPTS))


def _cli_argv(argv):
    """The command line for tiff_workflow.cli.main. A first word that is a path to a
    convert_tiff.py is dropped (the wizard starts a backend as `sys.executable
    <...>\\convert_tiff.py <subcommand> ARGS`): only its NAME counts, the package that runs
    is always this program's own. A backend's name is taken in any case, as before."""
    argv = [str(a) for a in argv]
    if argv and Path(argv[0]).name.lower() == ENTRY:
        argv = argv[1:]
    if argv and argv[0].lower() in SUBCOMMANDS:
        argv = [argv[0].lower()] + argv[1:]
    return argv


def main() -> None:
    # A redirected stdout falls back to the ANSI code page, where a program
    # folder named in Japanese cannot be printed (the scripts do the same).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    _setup_environment()
    from tiff_workflow.cli import main as run      # scripts/, put first on sys.path above
    try:
        code = run(_cli_argv(sys.argv[1:]))
    except KeyboardInterrupt:
        code = 130
    sys.exit(code)


if __name__ == "__main__":
    main()
