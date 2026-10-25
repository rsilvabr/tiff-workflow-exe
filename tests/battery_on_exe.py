"""Runs tiff-workflow's real-photo battery against the built program.

    python tests/battery_on_exe.py [--fixtures E:\\TESTE] [--app <folder>] [--keep] [--ascii-app]

Uses tools/real_photo_battery.py from a tiff-workflow checkout (the sibling
folder ../tiff-workflow, or TIFFWORKFLOW_REPO), unchanged, on the PACKAGE's
scripts: the backends run under the bundled PowerShell 7, and the only pwsh,
exiftool and magick on PATH are the bundled ones (the battery's own checks
use them too). Before it, a section of its own drives tiff-workflow.exe
itself: --help, each backend command, a preset saved from another folder
(run twice), and the execution policy.

The program runs from a copy in a HOSTILE folder on the fixtures' drive
(Japanese, brackets, a space, % and &), and every file of that copy carries
the "downloaded from the internet" mark (Zone.Identifier, ZoneId=3) that
Explorer gives the files of a downloaded zip: under the RemoteSigned policy
PowerShell refuses such a script unless the launcher's Bypass reaches it.
--ascii-app runs it from dist/ instead, unmarked.

The report lands in AI_tools/ of this repo.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL_EXES = ("pwsh.exe", "exiftool.exe", "magick.exe")
MOTW = "[ZoneTransfer]\r\nZoneId=3\r\n"


def _rmtree(p):
    # ExifTool's archive marks some folders read-only.
    shutil.rmtree(p, onexc=lambda f, q, e: (os.chmod(q, 0o777), f(q)))


def _mark_downloaded(folder):
    n = 0
    for f in folder.rglob("*"):
        if f.is_file():
            with open(str(f) + ":Zone.Identifier", "w", encoding="ascii") as fh:
                fh.write(MOTW)
            n += 1
    return n


def _without_bypass():
    # os.environ keys are upper-case on Windows.
    return {k: v for k, v in os.environ.items() if k.upper() != "PSEXECUTIONPOLICYPREFERENCE"}


def _policy_without_bypass(pwsh):
    """The policy this PC applies when the Process scope is not set: the first
    defined of the other scopes, in PowerShell's order. Read WITH Bypass, as the
    launcher runs it: without it, a pwsh whose own module files carry the
    download mark stops at an "untrusted publisher" prompt."""
    r = subprocess.run([pwsh, "-NoProfile", "-Command",
                        "Get-ExecutionPolicy -List | ForEach-Object "
                        "{ '{0}={1}' -f $_.Scope, $_.ExecutionPolicy }"],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=120)
    scopes = dict(ln.strip().split("=", 1) for ln in r.stdout.splitlines() if "=" in ln)
    for scope in ("MachinePolicy", "UserPolicy", "CurrentUser", "LocalMachine"):
        if scopes.get(scope, "Undefined") != "Undefined":
            return scopes[scope]
    return "Restricted" if scopes else ""   # Windows' default when nothing is set


def exe_checks(b, exe, app, fixtures, work):
    """tiff-workflow.exe itself, from the hostile (marked) program folder."""
    scripts, pwsh = app / "scripts", str(app / "tools" / "pwsh" / "pwsh.exe")
    b.section("tiff-workflow.exe")

    def run_exe(tag, args, cwd, env=None, timeout=1800):
        t = time.time()
        r = subprocess.run([str(exe)] + [str(a) for a in args], cwd=str(cwd), env=env,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        out = (r.stdout or "") + (r.stderr or "")
        (work / "_logs").mkdir(parents=True, exist_ok=True)
        (work / "_logs" / f"exe__{tag}.log").write_text(
            f"$ {exe} {' '.join(map(str, args))}\nrc={r.returncode} "
            f"({time.time() - t:.0f}s)\n\n{out}", encoding="utf-8")
        print(f"   [{tag}] rc={r.returncode} {time.time() - t:.0f}s", flush=True)
        bad = [m for m in ("ParserError", "CategoryInfo", "Traceback", "PSSecurityException",
                           "cannot be loaded") if m in out]
        b.check(f"{tag}: no PowerShell error record, no traceback", not bad,
                f"found {bad}" if bad else "")
        return r.returncode, out

    # The control: without Bypass, the marked script is refused here -- the
    # checks below then prove the launcher's Bypass reaches every pwsh it starts.
    policy = _policy_without_bypass(pwsh)
    if policy in ("RemoteSigned", "AllSigned", "Restricted"):
        try:
            r = subprocess.run([pwsh, "-NoProfile", "-NonInteractive", "-File",
                                str(scripts / "generate_thumbnails.ps1"), "-InputDir", str(work),
                                "-DryRun"], capture_output=True, text=True, encoding="utf-8",
                               errors="replace", env=_without_bypass(),
                               stdin=subprocess.DEVNULL, timeout=300)
            rc, ran = r.returncode, "No TIFF files found" in (r.stdout + r.stderr)
        except subprocess.TimeoutExpired:
            rc, ran = "timeout", False
        b.check(f"control: policy {policy}, no Bypass: the marked script does not run",
                rc != 0 and not ran, f"rc={rc}")
    else:
        b.skips.append(f"execution-policy control skipped: this PC's policy is {policy}")

    rc, out = run_exe("help", ["--help"], work)
    b.check("--help: rc 0, the wizard's own help", rc == 0 and "TIFF Workflow Manager" in out,
            f"rc={rc}")

    a1, a2 = b.pick_tiff16(fixtures)
    plain = work / "plain"
    host = work / "伊豆沼 [exe] 100% & co"
    for name, src in (("A.tif", a1), ("B.tif", a2)):
        b.small(src, plain / name)       # exiftool takes these paths on its command line
    comp = host / "compress"
    comp.mkdir(parents=True)
    for name in ("A.tif", "B.tif"):
        shutil.copy2(plain / name, comp / name)

    rc, _ = run_exe("compress", ["compress", "-Mode", "1", "-InputDir", comp, "-Workers", "2"],
                    host)
    b.check("compress -Mode 1: rc 0", rc == 0, f"rc={rc}")
    for name in ("A.tif", "B.tif"):
        out_f = comp / "ZIP" / name
        ok = out_f.is_file()
        # b.compression and b.meta give exiftool the path on its command line (ANSI
        # code page): read through an argfile, and compare metadata on plain copies.
        kind = b.exif_tag(out_f, "-IFD0:Compression") if ok else "missing"
        b.check(f"compress: ZIP/{name} written, Deflate", "Deflate" in kind, kind)
        same_meta = False
        if ok:
            cmp_dir = work / "cmp"
            src_c = b.cp(comp / name, cmp_dir / "src" / name)
            out_c = b.cp(out_f, cmp_dir / "out" / name)
            same_meta = b.meta(src_c) == b.meta(out_c)
        b.check(f"compress: ZIP/{name} pixels and metadata unchanged",
                ok and b.pixels_equal(comp / name, out_f) and same_meta)
    b.check("compress: its log went to Logs\\ of the folder it started in",
            any((host / "Logs").rglob("*.log")))

    thumbs = host / "thumbs out"
    rc, _ = run_exe("thumbnails", ["thumbnails", "-InputDir", comp, "-OutputDir", thumbs,
                                   "-Size", "256"], host)
    made = sorted(thumbs.glob("*.jpg")) if thumbs.is_dir() else []
    b.check("thumbnails: rc 0, one JPEG per TIFF", rc == 0 and len(made) == 2,
            f"rc={rc}, {[p.name for p in made]}")
    for p in made:
        r = subprocess.run(["magick", "identify", "-format", "%w %h", str(p)],
                           capture_output=True, text=True)
        w, h = (int(v) for v in r.stdout.split()[:2])
        b.check(f"thumbnails: {p.name} fits 256 px", max(w, h) == 256, f"{w}x{h}")

    tagless = fixtures / "TIFF_tagless" / "S5Pro"
    if tagless.is_dir():
        s5 = host / "S5Pro [CULL]"
        shutil.copytree(tagless, s5)
        rc, _ = run_exe("copy-exif", ["copy-exif", "-InputDir", s5, "-Workers", "2"], host)
        b.check("copy-exif: rc 0", rc == 0, f"rc={rc}")
        for tif in sorted(p for p in s5.iterdir() if p.suffix.lower() in (".tif", ".tiff")):
            pair = b.find_pair(tif)
            a = b.exif_tag(tif, "-EXIF:DateTimeOriginal")
            want = b.exif_tag(pair, "-EXIF:DateTimeOriginal") if pair else ""
            same = all(b.pixels_equal(tagless / tif.name, tif, pg) for pg in (0, 1))
            b.check(f"copy-exif: {tif.name}: EXIF from its JPEG, both pages unchanged",
                    a == want and a != "" and same, ascii((a, want, same)))
    else:
        b.skips.append("copy-exif via the exe skipped: no TIFF_tagless/S5Pro fixture")

    # A preset saved by another copy of the toolkit (the config file is shared
    # with the Python version): it must run THIS program's backend.
    import convert_tiff
    home = work / "home [ユーザー]"
    home.mkdir()
    pre = host / "preset"
    pre.mkdir()
    for name in ("A.tif", "B.tif"):
        shutil.copy2(plain / name, pre / name)
    wf = {"mode": 1, "workers": 2, "staging": "", "dry_run": False}
    cmd = convert_tiff.build_compress_command(wf, folders=[pre], ps_name="pwsh")
    cmd[cmd.index("-File") + 1] = str(work / "old version (deleted)" / "compress_tiff_zip.ps1")
    entry = {"kind": "compress", "label": f"Compress TIFFs -- mode 1 -- {pre}",
             "commands": [cmd], "time": "2026-10-25 03:00:00", "manifest_path": None,
             "manifest_workflow": None, "manifest_default_mode": None, "autofind": None}
    (home / ".convert_tiff_config.json").write_text(
        json.dumps({"presets": {"NIGHTLY ZIP": entry}}), encoding="utf-8")
    env = dict(os.environ, USERPROFILE=str(home), HOME=str(home))
    rc, out = run_exe("list-presets", ["--list-presets"], host, env=env)
    b.check("--list-presets: lists the preset", rc == 0 and "NIGHTLY ZIP" in out, f"rc={rc}")
    rc, out = run_exe("preset_run1", ["--run-preset", "NIGHTLY ZIP"], host, env=env)
    outs = sorted((pre / "ZIP").glob("*.tif"))
    b.check("--run-preset (saved from another folder): rc 0, both outputs",
            rc == 0 and len(outs) == 2, f"rc={rc}, {[p.name for p in outs]}")
    b.check("--run-preset: the wizard found the bundled PowerShell 7",
            "copy_exif_to_TIFF_ps5" not in out and "powershell.exe" not in out.lower())
    mtimes = {p.name: p.stat().st_mtime_ns for p in outs}
    rc, _ = run_exe("preset_run2", ["--run-preset", "NIGHTLY ZIP"], host, env=env)
    b.check("--run-preset again over its own output: rc 0, nothing rewritten",
            rc == 0 and {p.name: p.stat().st_mtime_ns for p in outs} == mtimes, f"rc={rc}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # hostile paths
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", default=os.environ.get("TW_FIXTURES", r"E:\TESTE"))
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--app", default=None, help="the built folder (default: newest in dist/)")
    ap.add_argument("--ascii-app", action="store_true",
                    help="run the program from the built folder, not a hostile marked copy")
    args = ap.parse_args()
    fixtures = Path(args.fixtures)

    app = Path(args.app) if args.app else max(
        (p for p in (ROOT / "dist").glob("tiff-workflow-*-x64") if p.is_dir()),
        key=lambda p: p.stat().st_mtime)
    app = app.resolve()
    if not args.ascii_app:
        hostile = (Path(fixtures.anchor) / "twexe_battery_app" / "伊豆沼 [app] 100% & co"
                   / app.name)
        if hostile.parent.exists():
            _rmtree(hostile.parent)
        shutil.copytree(app, hostile)
        print(f"marked {_mark_downloaded(hostile)} files as downloaded", flush=True)
        app = hostile
    exe, scripts, tools = app / "tiff-workflow.exe", app / "scripts", app / "tools"
    repo = Path(os.environ.get("TIFFWORKFLOW_REPO", ROOT.parent / "tiff-workflow"))

    # Only the bundled tools: drop every PATH entry holding one of them, then
    # the launcher's own environment (PATH, MAGICK_HOME, Bypass, sys.path).
    os.environ["PATH"] = os.pathsep.join(
        p for p in os.environ.get("PATH", "").split(os.pathsep)
        if p and not any((Path(p) / t).exists() for t in TOOL_EXES))
    sys.path.insert(0, str(ROOT / "src"))
    import tiff_workflow_exe as launcher
    launcher.APP, launcher.SCRIPTS, launcher.TOOLS = app, scripts, tools
    launcher._setup_environment()
    for t in TOOL_EXES:
        found = shutil.which(t)
        assert found and (Path(found).resolve().is_relative_to(app.resolve())
                          or "tiff-workflow" in found), (t, found)
        print(f"{t}: {found}", flush=True)

    import convert_tiff                        # the PACKAGE's wizard (sys.path[0])
    assert Path(convert_tiff.__file__).parent == scripts, convert_tiff.__file__
    sys.path.insert(1, str(repo / "tools"))
    import real_photo_battery as b             # its `import convert_tiff` gets the one above
    b.REPO = scripts                           # run() starts REPO / <backend>
    print(f"program: {exe}\nbattery: {repo / 'tools' / 'real_photo_battery.py'}", flush=True)

    work = Path(fixtures.anchor) / "twexe_battery_work"
    if work.exists():
        _rmtree(work)
    work.mkdir()
    try:
        exe_checks(b, exe, app, fixtures, work)
    except Exception as e:
        b.check("tiff-workflow.exe section completed without crashing", False,
                f"{type(e).__name__}: {e}")

    sys.argv = ["real_photo_battery.py", "--fixtures", str(fixtures), "--shells", "pwsh",
                "--scratch", str(Path(fixtures.anchor) / "twexe_battery")] \
        + (["--keep"] if args.keep else [])
    code = 1
    try:
        b.main()
    except SystemExit as e:
        code = e.code
    finally:
        (ROOT / "AI_tools").mkdir(exist_ok=True)
        for rep in (scripts / "AI_tools").glob("*_battery_report.md"):
            dest = ROOT / "AI_tools" / rep.name.replace("_battery_report", "_exe_battery_report")
            shutil.move(str(rep), dest)
            print(f"report: {dest}")
        shutil.rmtree(scripts / "AI_tools", ignore_errors=True)
        if code == 0 and not args.keep:
            _rmtree(work)
            if not args.ascii_app:
                _rmtree(app.parent.parent)
    sys.exit(code)


if __name__ == "__main__":
    main()
