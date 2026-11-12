# PyInstaller spec for tiff-workflow.exe (a one-folder build). Run through
# build.py, which first puts the tiff-workflow scripts in build/app/scripts.
import os
from PyInstaller.utils.hooks import collect_all

SCRIPTS = os.path.join("build", "app", "scripts")
PACKAGE = "tiff_workflow"

# The toolkit -- convert_tiff.py and the package tiff_workflow/ (tiff-workflow v3.1) -- ships
# as plain .py files in scripts/, and those are what run: the launcher puts scripts/ first on
# sys.path, and a setting edited in them counts. Its modules are analysed here, so PyInstaller
# bundles everything they use (rich and the standard library, their function-level imports
# included), and then taken OUT of the bundle below: a bundled copy would be imported instead
# of the plain files.
toolkit = ["convert_tiff", PACKAGE] + sorted(
    f"{PACKAGE}.{name[:-3]}" for name in os.listdir(os.path.join(SCRIPTS, PACKAGE))
    if name.endswith(".py") and name not in ("__init__.py", "__main__.py"))


def is_toolkit(module):
    return module == "convert_tiff" or module == PACKAGE or module.startswith(PACKAGE + ".")


hidden = list(toolkit)
datas, binaries = [], []
d, b, h = collect_all("rich")
datas += d
binaries += b
hidden += h

a = Analysis(
    [os.path.join("src", "tiff_workflow_exe.py")],
    pathex=[SCRIPTS],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden,
    excludes=["tkinter", "matplotlib", "IPython", "pytest", "numpy"],
)
bundled = [entry[0] for entry in a.pure if is_toolkit(entry[0])]
assert set(toolkit) <= set(bundled), f"the toolkit was not analysed: {sorted(set(toolkit) - set(bundled))}"
a.pure = [entry for entry in a.pure if not is_toolkit(entry[0])]
print(f"tiff-workflow.spec: {len(bundled)} module(s) of the toolkit analysed and left out of the bundle")
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="tiff-workflow",
          console=True, version=os.path.join("build", "version_info.txt"),
          icon=None, upx=False)
coll = COLLECT(exe, a.binaries, a.datas, name="tiff-workflow", upx=False)
