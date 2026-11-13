"""Builds dist/tiff-workflow-<version>-x64.zip: tiff-workflow.exe, the scripts
of a published tiff-workflow tag, and the tools they call.

    python build.py            (Python 3.12 on PATH; first run ~5 minutes)

Everything downloaded is pinned: the tiff-workflow scripts come from the tag
below (TOOLKIT_VERSION in tiff_workflow/__init__.py must match it), the tools from their official
releases with a SHA-256 check. A virtual environment in .venv holds the
pinned Python packages and PyInstaller, so the system Python is not touched.

    python build.py --scripts-from <folder>

takes the scripts from a local tiff-workflow checkout instead of the tag (a
test build before the tag exists; TOOLKIT_VERSION must still match it).
Releases never use it.
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

# --- settings --------------------------------------------------------------
TIFFWORKFLOW_TAG = "v3.1.0"
# Package revision for this tiff-workflow tag: v2.7.2 + 1 -> release "v2.7.2-exe1".
PACKAGE_REVISION = 1
TOOLS = {
    "exiftool": ("https://sourceforge.net/projects/exiftool/files/"
                 "exiftool-13.59_64.zip/download",
                 "44b512b25af500724ba579d0a53c8fc5851628b692dd5e5d94ae4a15c2cba9ec"),
    "imagemagick": ("https://github.com/ImageMagick/ImageMagick/releases/download/"
                    "7.1.2-27/ImageMagick-7.1.2-27-portable-Q16-HDRI-x64.7z",
                    "c7d6f13b3021db5d2e23876d85f06d6039a9a345236f0d32cdb73886ddfe70ed"),
}
REQUIREMENTS = ["rich==15.0.0", "pyinstaller==6.22.2"]
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
DEPS, BUILD, DIST = ROOT / "deps", ROOT / "build", ROOT / "dist"
VENV = ROOT / ".venv"
WINTAR = Path(r"C:\Windows\System32\tar.exe")   # bsdtar: reads .zip and .7z
# The toolkit since tiff-workflow v3.1: the entry point and the package (every .py in it; the
# wizard, the three backends, what they share). v3.0.x shipped five loose scripts; up to v2.9.1
# the backends were PowerShell scripts, and the package carried PowerShell 7.
ENTRY = "convert_tiff.py"
PACKAGE = "tiff_workflow"


def rmtree(path):
    """shutil.rmtree that also removes read-only files (ExifTool's archive
    marks some of its files read-only, and copies keep the attribute)."""
    def _clear(func, p, _exc):
        os.chmod(p, 0o666)
        func(p)
    shutil.rmtree(path, onexc=_clear)


def step(msg):
    print(f"\n== {msg}", flush=True)


def fetch(url, dest, sha256=None):
    if not dest.exists():
        print(f"   downloading {url}")
        DEPS.mkdir(exist_ok=True)
        with urllib.request.urlopen(url, timeout=300) as r:
            data = r.read()
        dest.write_bytes(data)
    if sha256:
        got = hashlib.sha256(dest.read_bytes()).hexdigest()
        if got != sha256:
            dest.unlink()
            sys.exit(f"SHA-256 mismatch for {dest.name}: {got} (deleted)")
    return dest


def extract(archive, into):
    if into.exists():
        rmtree(into)
    into.mkdir(parents=True)
    subprocess.run([str(WINTAR), "-xf", str(archive), "-C", str(into)], check=True)
    return into


def venv_python():
    py = VENV / "Scripts" / "python.exe"
    if not py.exists():
        step("Python environment (.venv)")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    subprocess.run([str(py), "-m", "pip", "install", "--quiet", "--disable-pip-version-check"]
                   + REQUIREMENTS, check=True)
    return py


def get_scripts(app, local=None):
    dest = app / "scripts"
    (dest / PACKAGE).mkdir(parents=True)
    out_license = app / "licenses" / "LICENSE.tiff-workflow"
    if local:
        step(f"tiff-workflow scripts from {local} (test build, not the tag)")
        local = Path(local)
        shutil.copy2(local / ENTRY, dest / ENTRY)
        for f in sorted((local / PACKAGE).glob("*.py")):
            shutil.copy2(f, dest / PACKAGE / f.name)
        shutil.copy2(local / "LICENSE", out_license)
    else:
        step(f"tiff-workflow {TIFFWORKFLOW_TAG} scripts")
        z = fetch(f"https://github.com/rsilvabr/tiff-workflow/archive/refs/tags/"
                  f"{TIFFWORKFLOW_TAG}.zip", DEPS / f"tiff-workflow-{TIFFWORKFLOW_TAG}.zip")
        with zipfile.ZipFile(z) as zf:
            top = zf.namelist()[0].split("/")[0]
            (dest / ENTRY).write_bytes(zf.read(f"{top}/{ENTRY}"))
            for name in zf.namelist():
                rel = name[len(top) + 1:]
                if rel.startswith(PACKAGE + "/") and rel.endswith(".py") and rel.count("/") == 1:
                    (dest / rel).write_bytes(zf.read(name))
            out_license.write_bytes(zf.read(f"{top}/LICENSE"))
    found = sorted(p.name for p in (dest / PACKAGE).glob("*.py"))
    for needed in ("__init__.py", "cli.py", "wizard.py", "common.py"):
        if needed not in found:
            sys.exit(f"{PACKAGE}/{needed} is not in the scripts ({found})")
    version = TIFFWORKFLOW_TAG.lstrip("v")
    text = (dest / PACKAGE / "__init__.py").read_text(encoding="utf-8")
    m = re.search(r'^TOOLKIT_VERSION = "([^"]+)"', text, re.M)
    if not m or m.group(1) != version:
        sys.exit(f"{PACKAGE}/__init__.py: TOOLKIT_VERSION {m and m.group(1)} != tag {TIFFWORKFLOW_TAG}")
    return version


def get_tools(app):
    step("tools (exiftool, ImageMagick)")
    tools, lic = app / "tools", app / "licenses"
    url, sha = TOOLS["exiftool"]
    x = extract(fetch(url, DEPS / "exiftool-13.59_64.zip", sha), BUILD / "x_exiftool")
    src = next(x.rglob("exiftool(-k).exe")).parent
    d = tools / "exiftool"
    shutil.copytree(src / "exiftool_files", d / "exiftool_files")
    # Renamed: exiftool(-k).exe waits for a key press after every call.
    shutil.copy2(src / "exiftool(-k).exe", d / "exiftool.exe")
    shutil.copy2(src / "README.txt", lic / "exiftool-README.txt")
    # Names the copy the launcher makes when the program folder is not
    # ANSI-safe (see _exiftool_dir in src/tiff_workflow_exe.py).
    ver = re.search(r"exiftool-([\d.]+)_", url).group(1)
    (d / "VERSION.txt").write_text(ver + "\n", encoding="utf-8")

    url, sha = TOOLS["imagemagick"]
    x = extract(fetch(url, DEPS / Path(url).name, sha), BUILD / "x_imagemagick")
    src = next(x.rglob("magick.exe")).parent
    d = tools / "imagemagick"
    d.mkdir()
    # magick.exe alone does every operation; the other programs are aliases.
    for f in src.iterdir():
        if f.suffix.lower() in (".xml", ".icc") or f.name == "magick.exe":
            shutil.copy2(f, d / f.name)
    shutil.copy2(src / "LICENSE.txt", lic / "LICENSE.imagemagick.txt")
    shutil.copy2(src / "NOTICE.txt", lic / "NOTICE.imagemagick.txt")


def version_info(version):
    nums = (version.split(".") + ["0", "0", "0"])[:3] + ["0"]
    (BUILD / "version_info.txt").write_text(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers=({','.join(nums)}), prodvers=({','.join(nums)})),
  kids=[StringFileInfo([StringTable('040904B0', [
    StringStruct('CompanyName', 'rsilvabr'),
    StringStruct('FileDescription', 'tiff-workflow - TIFF archive toolkit'),
    StringStruct('FileVersion', '{version}'),
    StringStruct('ProductName', 'tiff-workflow'),
    StringStruct('ProductVersion', '{version}'),
    StringStruct('LegalCopyright', 'MIT License')])]),
  VarFileInfo([VarStruct('Translation', [1033, 1200])])])
""", encoding="utf-8")


def main():
    local = None
    if "--scripts-from" in sys.argv[1:]:
        i = sys.argv.index("--scripts-from")
        if i + 1 >= len(sys.argv):
            sys.exit("--scripts-from needs a folder")
        local = sys.argv[i + 1]
    py = venv_python()
    if BUILD.exists():
        rmtree(BUILD)
    app = BUILD / "app"
    (app / "licenses").mkdir(parents=True)
    version = get_scripts(app, local)
    get_tools(app)
    version_info(version)

    step("PyInstaller")
    subprocess.run([str(py), "-m", "PyInstaller", "--noconfirm", "--clean",
                    "--distpath", str(BUILD / "pyi_dist"), "--workpath", str(BUILD / "pyi_work"),
                    str(ROOT / "tiff-workflow.spec")], check=True, cwd=ROOT)

    step("assemble")
    out = DIST / f"tiff-workflow-{version}-exe{PACKAGE_REVISION}-x64"
    if out.exists():
        rmtree(out)
    old = out.parent / (out.name + ".zip")    # not with_suffix: the name has dots
    if old.exists():
        old.unlink()
    shutil.copytree(BUILD / "pyi_dist" / "tiff-workflow", out)
    for sub in ("scripts", "tools", "licenses"):
        # The analysis of the package compiles it in build/app/scripts: no .pyc in the package
        # (the plain files are what runs; Python compiles them where it may).
        shutil.copytree(app / sub, out / sub, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "LICENSE", out / "licenses" / "LICENSE.tiff-workflow-exe")
    # PyInstaller bundles the Python runtime but not its license (PSF).
    shutil.copy2(Path(sys.base_prefix) / "LICENSE.txt", out / "licenses" / "LICENSE.python.txt")
    shutil.copy2(ROOT / "README.md", out / "README.md")
    # No read-only files or folders in the package (ExifTool's archive marks
    # some): an update unzips over the old folder, and a copy must be deletable.
    for f in out.rglob("*"):
        os.chmod(f, 0o666 if f.is_file() else 0o777)
    z = shutil.make_archive(str(out), "zip", out.parent, out.name)
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"\nBuilt {out} ({size / 1e6:.0f} MB) and {Path(z).name} "
          f"({Path(z).stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
