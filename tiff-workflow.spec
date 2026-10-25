# PyInstaller spec for tiff-workflow.exe (a one-folder build). Run through
# build.py, which first puts the tiff-workflow scripts in build/app/scripts.
import os
from PyInstaller.utils.hooks import collect_all

SCRIPTS = os.path.join("build", "app", "scripts")

# The wizard is imported as a module so PyInstaller bundles everything it uses
# (rich and the standard library, its function-level imports included); it
# also ships as a plain .py file in scripts/, which is what actually runs.
hidden = ["convert_tiff"]
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
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="tiff-workflow",
          console=True, version=os.path.join("build", "version_info.txt"),
          icon=None, upx=False)
coll = COLLECT(exe, a.binaries, a.datas, name="tiff-workflow", upx=False)
