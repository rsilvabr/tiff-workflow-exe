"""tiff-workflow.exe: the tiff-workflow toolkit as a Windows program, no Python needed.

The wizard and the four PowerShell backends ship unchanged in `scripts/` next
to the program; PowerShell 7, ExifTool and ImageMagick in `tools/`. This
launcher only routes:

    tiff-workflow.exe                          the interactive wizard (convert_tiff.py)
    tiff-workflow.exe --run-preset NAME ...    the wizard, with its own options
    tiff-workflow.exe compress|copy-exif|thumbnails ARGS
                                               one backend directly, under the
                                               bundled PowerShell 7

Before running anything it puts tools/ first on PATH (the wizard and the
backends find pwsh, exiftool and magick there) and sets the PowerShell
execution policy of the processes it starts to Bypass: Windows' default
policy refuses every .ps1, and one unzipped from a download carries the
"from the internet" mark that RemoteSigned refuses too.
"""

import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

BACKENDS = {
    "compress": "compress_tiff_zip.ps1",
    "copy-exif": "copy_exif_to_TIFF_ps7.ps1",
    "thumbnails": "generate_thumbnails.ps1",
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
    perl5*.dll") while pwsh and magick work. The 8.3 short name of the
    folder fixes that where the volume has short names (usually C:); on one
    without them, ExifTool is copied once to an ANSI-safe folder.
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
    tool_dirs = [TOOLS / "pwsh", _exiftool_dir(), TOOLS / "imagemagick"]
    found = [str(d) for d in tool_dirs if d.is_dir()]
    os.environ["PATH"] = os.pathsep.join(found + [os.environ.get("PATH", "")])
    # The portable ImageMagick reads its configuration from its own folder.
    if (TOOLS / "imagemagick").is_dir():
        os.environ.setdefault("MAGICK_HOME", str(TOOLS / "imagemagick"))
    # The Process scope of every PowerShell this program starts; the machine's
    # own policy is not changed. A policy set by Group Policy still wins.
    os.environ["PSExecutionPolicyPreference"] = "Bypass"
    # pwsh would otherwise send a telemetry ping at start: this program makes
    # no network connections.
    os.environ["POWERSHELL_TELEMETRY_OPTOUT"] = "1"
    os.environ["POWERSHELL_UPDATECHECK"] = "Off"
    sys.path.insert(0, str(SCRIPTS))


def _pwsh() -> str:
    bundled = TOOLS / "pwsh" / "pwsh.exe"
    return str(bundled) if bundled.is_file() else "pwsh"


def _backend_command(argv):
    """The pwsh command line for `compress|copy-exif|thumbnails ARGS`, or None
    when the command line is for the wizard."""
    if argv and argv[0].lower() in BACKENDS:
        script = SCRIPTS / BACKENDS[argv[0].lower()]
        return [_pwsh(), "-NoProfile", "-File", str(script)] + list(argv[1:])
    return None


def main() -> None:
    # A redirected stdout falls back to the ANSI code page, where a program
    # folder named in Japanese cannot be printed (the wizard does the same).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    _setup_environment()
    argv = sys.argv[1:]
    cmd = _backend_command(argv)
    if cmd is not None:
        try:
            sys.exit(subprocess.run(cmd).returncode)
        except KeyboardInterrupt:
            sys.exit(130)
    script = SCRIPTS / WIZARD
    sys.argv = [str(script)] + list(argv)
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
