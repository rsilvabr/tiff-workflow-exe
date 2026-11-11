# PyInstaller spec for tiff-workflow.exe (a one-folder build). Run through
# build.py, which first puts the tiff-workflow scripts in build/app/scripts.
import os
from PyInstaller.utils.hooks import collect_all

SCRIPTS = os.path.join("build", "app", "scripts")

# The wizard is imported as a module so PyInstaller bundles everything it uses
# (rich and the standard library, its function-level imports included); it
# also ships as a plain .py file in scripts/, which is what actually runs.
#
# The three backends and tiff_workflow_common.py are NOT imported here: a module
# in the bundle would win over the plain file in scripts/, and the files that
# run must be the ones of the tiff-workflow release. What they need from the
# standard library is named instead (the wizard does not import all of it).
hidden = ["convert_tiff", "ctypes", "datetime", "json", "math", "re", "shutil",
          "subprocess", "tempfile", "threading", "uuid", "concurrent.futures",
          "concurrent.futures.thread"]
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
    excludes=["tkinter", "matplotlib", "IPython", "pytest", "numpy",
              "compress_tiff_zip", "copy_exif_to_tiff", "generate_thumbnails",
              "tiff_workflow_common"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="tiff-workflow",
          console=True, version=os.path.join("build", "version_info.txt"),
          icon=None, upx=False)
coll = COLLECT(exe, a.binaries, a.datas, name="tiff-workflow", upx=False)
