"""tiff-workflow.exe: the tiff-workflow toolkit as a Windows program, no Python needed.

The wizard, the three backends and their shared module ship unchanged, as plain
`.py` files, in `scripts/` next to the program; ExifTool and ImageMagick in
`tools/`. This launcher is the Python that runs them, and it only routes:

    tiff-workflow.exe                          the interactive wizard (convert_tiff.py)
    tiff-workflow.exe --run-preset NAME ...    the wizard, with its own options
    tiff-workflow.exe compress|copy-exif|thumbnails ARGS
                                               one backend directly
    tiff-workflow.exe <a backend script> ARGS  how the wizard starts a backend: it runs
                                               `sys.executable <script> ARGS`, and here
                                               sys.executable is this program

Before running anything it puts tools/ first on PATH (the wizard and the
backends find exiftool and magick there).

Until v2.9.1 the backends were PowerShell scripts and the package carried
PowerShell 7; since v3.0.0 they are Python and there is no PowerShell in it.
"""

import os
import runpy
import shutil
import sys
from pathlib import Path

BACKENDS = {
    "compress": "compress_tiff_zip.py",
    "copy-exif": "copy_exif_to_tiff.py",
    "thumbnails": "generate_thumbnails.py",
}
WIZARD = "convert_tiff.py"


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


def _backend_script(argv):
    """The backend script (in scripts/) and its arguments for a command line that asks for
    one, else None: `compress|copy-exif|thumbnails ARGS`, or `<...>\\<backend>.py ARGS` as
    the wizard writes it. Only the NAME of a script path counts: the copy that runs is
    always the one in this program's own scripts/ folder."""
    if not argv:
        return None
    first = argv[0]
    name = BACKENDS.get(first.lower())
    if name is None and Path(first).name in BACKENDS.values():
        name = Path(first).name
    if name is None:
        return None
    return SCRIPTS / name, list(argv[1:])


def _run_script(script: Path, args) -> None:
    """Run a script of scripts/ as the main program, with `args`. Its exit code is the
    program's (the scripts end with `sys.exit(main())`)."""
    sys.argv = [str(script)] + list(args)
    runpy.run_path(str(script), run_name="__main__")


def main() -> None:
    # A redirected stdout falls back to the ANSI code page, where a program
    # folder named in Japanese cannot be printed (the scripts do the same).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    _setup_environment()
    argv = sys.argv[1:]
    backend = _backend_script(argv)
    if backend is not None:
        try:
            _run_script(*backend)
        except KeyboardInterrupt:
            sys.exit(130)
        return
    _run_script(SCRIPTS / WIZARD, argv)


if __name__ == "__main__":
    main()
