"""The launcher's routing and the environment it gives the wizard and the backends.

    python -m pytest tests/test_launcher.py
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


ARGS = ["-Mode", "8", "-InputDir", r"G:\伊豆沼 [FINAL]", "-SafeMode:$false"]


@pytest.mark.parametrize("name, script", [
    ("compress", "compress_tiff_zip.py"),
    ("COPY-EXIF", "copy_exif_to_tiff.py"),
    ("thumbnails", "generate_thumbnails.py"),
])
def test_a_backend_command_names_its_script(app, name, script):
    assert exe._backend_script([name] + ARGS) == (app / "scripts" / script, ARGS)


@pytest.mark.parametrize("script", ["compress_tiff_zip.py", "copy_exif_to_tiff.py",
                                    "generate_thumbnails.py"])
def test_the_wizards_own_call_runs_the_copy_in_scripts(app, script):
    """The wizard starts a backend as `sys.executable <script> ARGS`, and here
    sys.executable is this program. Whatever folder the path names, the script that
    runs is the one in this program's scripts/."""
    for given in (str(app / "scripts" / script), r"D:\somewhere else\\" + script, script):
        assert exe._backend_script([given] + ARGS) == (app / "scripts" / script, ARGS)


@pytest.mark.parametrize("argv", [[], ["--run-preset", "SYNC"], ["--list-presets"],
                                  ["--help"], ["compress_tiff_zip.ps1"], ["convert_tiff.py"],
                                  ["tiff_workflow_common.py"], [r"C:\x\evil.py", "-Mode", "8"]])
def test_everything_else_goes_to_the_wizard(app, argv):
    assert exe._backend_script(argv) is None


def test_the_wizard_runs_with_its_arguments(app, monkeypatch):
    seen = {}
    monkeypatch.setattr(exe.runpy, "run_path",
                        lambda path, run_name: seen.update(path=path, argv=list(sys.argv),
                                                           run_name=run_name))
    monkeypatch.setattr(sys, "argv", ["tiff-workflow.exe", "--run-preset", "SYNC PHOTOS"])
    exe.main()
    wizard = str(app / "scripts" / "convert_tiff.py")
    assert seen == {"path": wizard, "argv": [wizard, "--run-preset", "SYNC PHOTOS"],
                    "run_name": "__main__"}


def test_a_backend_runs_in_this_process_with_its_arguments(app, monkeypatch):
    seen = {}
    monkeypatch.setattr(exe.runpy, "run_path",
                        lambda path, run_name: seen.update(path=path, argv=list(sys.argv),
                                                           run_name=run_name))
    monkeypatch.setattr(sys, "argv", ["tiff-workflow.exe", "compress", "-DryRun"])
    exe.main()
    script = str(app / "scripts" / "compress_tiff_zip.py")
    assert seen == {"path": script, "argv": [script, "-DryRun"], "run_name": "__main__"}


def test_a_backend_exit_code_is_the_program_exit_code(app, monkeypatch):
    """The backends end with `sys.exit(main())`: the launcher must let it through."""
    (app / "scripts" / "generate_thumbnails.py").write_text(
        "import sys\nif __name__ == '__main__':\n    sys.exit(3 if sys.argv[1:] == ['-DryRun'] else 9)\n",
        encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["tiff-workflow.exe", "thumbnails", "-DryRun"])
    with pytest.raises(SystemExit) as e:
        exe.main()
    assert e.value.code == 3


def test_a_backend_finds_the_shared_module_next_to_it(app, monkeypatch):
    """scripts/ is put on sys.path: `import tiff_workflow_common` in a backend is the
    plain file that ships next to it."""
    (app / "scripts" / "tiff_workflow_common.py").write_text("WHERE = __file__\n", encoding="utf-8")
    (app / "scripts" / "compress_tiff_zip.py").write_text(
        "import sys, tiff_workflow_common as tw\n"
        "if __name__ == '__main__':\n"
        "    print(tw.WHERE)\n    sys.exit(0)\n", encoding="utf-8")
    code = (
        "import sys; sys.path.insert(0, r'%s'); import tiff_workflow_exe as exe\n"
        "from pathlib import Path\n"
        "exe.APP = Path(r'%s'); exe.SCRIPTS = exe.APP / 'scripts'; exe.TOOLS = exe.APP / 'tools'\n"
        "exe._exiftool_dir = lambda: exe.TOOLS / 'exiftool'\n"
        "sys.argv = ['tiff-workflow.exe', 'compress']\n"
        "exe.main()\n" % (Path(exe.__file__).parent, app))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=120)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    assert r.stdout.decode("utf-8").strip() == str(app / "scripts" / "tiff_workflow_common.py")


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
