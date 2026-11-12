"""The launcher's routing and the environment it gives the wizard and the backends.

    python -m pytest tests/test_launcher.py

Since tiff-workflow v3.1 every command line goes to tiff_workflow.cli.main, the package in
the program's scripts/ folder: the launcher only drops the path of a convert_tiff.py given as
the first word (how the wizard starts a backend) and takes a backend's name in any case.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import tiff_workflow_exe as exe   # noqa: E402


@pytest.fixture
def app(tmp_path, monkeypatch):
    root = tmp_path / "伊豆沼 [app] 100% & co"
    for sub in ("exiftool", "imagemagick"):
        (root / "tools" / sub).mkdir(parents=True)
    (root / "scripts").mkdir()
    monkeypatch.setattr(exe, "APP", root)
    monkeypatch.setattr(exe, "TOOLS", root / "tools")
    monkeypatch.setattr(exe, "SCRIPTS", root / "scripts")
    monkeypatch.setattr(exe, "_exiftool_dir", lambda: root / "tools" / "exiftool")
    for var in ("PATH", "MAGICK_HOME"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("PATH", r"C:\Windows\System32;C:\Program Files\ImageMagick")
    monkeypatch.setattr(sys, "path", list(sys.path))
    return root


ARGS = ["--mode", "8", "--input-dir", r"G:\伊豆沼 [FINAL]", "--no-safe-mode"]


@pytest.mark.parametrize("name", ["compress", "COPY-EXIF", "Thumbnails"])
def test_a_backend_name_goes_through_in_lower_case(name):
    assert exe._cli_argv([name] + ARGS) == [name.lower()] + ARGS


def test_the_wizards_own_call_drops_the_path(app):
    """The wizard starts a backend as `sys.executable <its convert_tiff.py> <subcommand> ARGS`,
    and here sys.executable is this program. Whatever folder the path names, what runs is the
    package in this program's scripts/: the path is dropped."""
    for given in (str(app / "scripts" / "convert_tiff.py"), r"D:\somewhere else\convert_tiff.py",
                  "convert_tiff.py", r"C:\X\CONVERT_TIFF.PY"):
        assert exe._cli_argv([given, "compress"] + ARGS) == ["compress"] + ARGS
        assert exe._cli_argv([given]) == []


@pytest.mark.parametrize("argv", [[], ["--run-preset", "SYNC"], ["--list-presets"], ["--help"],
                                  ["compress_tiff_zip.ps1"], ["compress_tiff_zip.py", "--mode", "9"],
                                  ["tiff_workflow_common.py"], [r"C:\x\evil.py", "--mode", "8"]])
def test_everything_else_reaches_the_entry_point_as_it_is(argv):
    """The entry point decides: the wizard's options, or an error for a word it does not know.
    A path is never run."""
    assert exe._cli_argv(argv) == argv


def _fake_toolkit(app, cli_body):
    pkg = app / "scripts" / "tiff_workflow"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "cli.py").write_text(cli_body, encoding="utf-8")


def _run_launcher(app, argv):
    """The launcher's main() in a fresh Python (an imported package stays imported)."""
    code = (
        "import sys; sys.path.insert(0, r'%s'); import tiff_workflow_exe as exe\n"
        "from pathlib import Path\n"
        "exe.APP = Path(r'%s'); exe.SCRIPTS = exe.APP / 'scripts'; exe.TOOLS = exe.APP / 'tools'\n"
        "exe._exiftool_dir = lambda: exe.TOOLS / 'exiftool'\n"
        "sys.argv = ['tiff-workflow.exe'] + %r\n"
        "exe.main()\n" % (Path(exe.__file__).parent, app, list(argv)))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=120)
    return r.returncode, r.stdout.decode("utf-8").strip(), r.stderr.decode("utf-8", "replace")


@pytest.mark.parametrize("argv, cli_gets", [
    (["--run-preset", "SYNC PHOTOS"], ["--run-preset", "SYNC PHOTOS"]),
    ([], []),
    (["COMPRESS", "--dry-run"], ["compress", "--dry-run"]),
    ([r"D:\old copy\convert_tiff.py", "thumbnails", "--size", "64"], ["thumbnails", "--size", "64"]),
])
def test_the_package_in_scripts_runs_and_its_exit_code_is_the_programs(app, argv, cli_gets):
    _fake_toolkit(app, "import sys\n"
                       "def main(argv=None):\n"
                       "    print(__file__)\n"
                       "    print(repr(list(argv)))\n"
                       "    return 3\n")
    rc, out, err = _run_launcher(app, argv)
    assert rc == 3, err
    where, got = out.splitlines()[-2:]
    assert Path(where) == app / "scripts" / "tiff_workflow" / "cli.py"
    assert got == repr(cli_gets)


def test_ctrl_c_that_reaches_the_launcher_exits_130(app):
    _fake_toolkit(app, "def main(argv=None):\n    raise KeyboardInterrupt\n")
    rc, _out, err = _run_launcher(app, ["compress", "--dry-run"])
    assert rc == 130, err


def test_the_environment(app, monkeypatch):
    monkeypatch.delenv("PSExecutionPolicyPreference", raising=False)
    exe._setup_environment()
    path = os.environ["PATH"].split(os.pathsep)
    assert path[:2] == [str(app / "tools" / "exiftool"), str(app / "tools" / "imagemagick")], \
        "the bundled tools come first, ahead of an installed ImageMagick"
    assert os.environ["MAGICK_HOME"] == str(app / "tools" / "imagemagick")
    assert sys.path[0] == str(app / "scripts")
    assert "PSExecutionPolicyPreference" not in os.environ, \
        "nothing in the package is PowerShell any more: no execution policy to set"
