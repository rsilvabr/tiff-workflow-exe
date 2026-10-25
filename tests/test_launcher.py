"""The launcher's routing and the environment it gives the wizard and the backends.

    python -m pytest tests/test_launcher.py
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import tiff_workflow_exe as exe   # noqa: E402


@pytest.fixture
def app(tmp_path, monkeypatch):
    root = tmp_path / "伊豆沼 [app] 100% & co"
    for sub in ("pwsh", "exiftool", "imagemagick"):
        (root / "tools" / sub).mkdir(parents=True)
    (root / "tools" / "pwsh" / "pwsh.exe").write_bytes(b"MZ")
    (root / "scripts").mkdir()
    monkeypatch.setattr(exe, "APP", root)
    monkeypatch.setattr(exe, "TOOLS", root / "tools")
    monkeypatch.setattr(exe, "SCRIPTS", root / "scripts")
    monkeypatch.setattr(exe, "_exiftool_dir", lambda: root / "tools" / "exiftool")
    for var in ("PATH", "MAGICK_HOME", "PSExecutionPolicyPreference",
                "POWERSHELL_TELEMETRY_OPTOUT", "POWERSHELL_UPDATECHECK"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("PATH", r"C:\Windows\System32;C:\Program Files\PowerShell\7")
    monkeypatch.setattr(sys, "path", list(sys.path))
    return root


@pytest.mark.parametrize("name, script", [
    ("compress", "compress_tiff_zip.ps1"),
    ("COPY-EXIF", "copy_exif_to_TIFF_ps7.ps1"),
    ("thumbnails", "generate_thumbnails.ps1"),
])
def test_a_backend_runs_under_the_bundled_pwsh(app, name, script):
    cmd = exe._backend_command([name, "-Mode", "8", "-InputDir", r"G:\伊豆沼 [FINAL]",
                                "-SafeMode:$false"])
    assert cmd == [str(app / "tools" / "pwsh" / "pwsh.exe"), "-NoProfile", "-File",
                   str(app / "scripts" / script),
                   "-Mode", "8", "-InputDir", r"G:\伊豆沼 [FINAL]", "-SafeMode:$false"]


@pytest.mark.parametrize("argv", [[], ["--run-preset", "SYNC"], ["--list-presets"],
                                  ["--help"], ["compress_tiff_zip.ps1"]])
def test_everything_else_goes_to_the_wizard(app, argv):
    assert exe._backend_command(argv) is None


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


def test_a_backend_exit_code_is_the_program_exit_code(app, monkeypatch):
    seen = {}

    class Done:
        returncode = 3

    def fake_run(cmd):
        seen["cmd"] = cmd
        return Done()

    monkeypatch.setattr(exe.subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["tiff-workflow.exe", "compress", "-DryRun"])
    with pytest.raises(SystemExit) as e:
        exe.main()
    assert e.value.code == 3
    assert seen["cmd"][-1] == "-DryRun"


def test_the_environment(app):
    exe._setup_environment()
    path = os.environ["PATH"].split(os.pathsep)
    assert path[:3] == [str(app / "tools" / "pwsh"), str(app / "tools" / "exiftool"),
                        str(app / "tools" / "imagemagick")], \
        "the bundled tools come first, ahead of an installed PowerShell 7"
    assert os.environ["MAGICK_HOME"] == str(app / "tools" / "imagemagick")
    assert os.environ["PSExecutionPolicyPreference"] == "Bypass"
    assert os.environ["POWERSHELL_TELEMETRY_OPTOUT"] == "1"
    assert sys.path[0] == str(app / "scripts")


def test_bypass_replaces_a_stricter_preference(app, monkeypatch):
    monkeypatch.setenv("PSExecutionPolicyPreference", "Restricted")
    exe._setup_environment()
    assert os.environ["PSExecutionPolicyPreference"] == "Bypass"
