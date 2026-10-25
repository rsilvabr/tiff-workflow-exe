# Bug tracking

Bugs of the **packaging** — the launcher, the bundled tools, the build —
newest first, one numbered row each. A bug in what tiff-workflow itself
does belongs to [tiff-workflow's bug history](https://github.com/rsilvabr/tiff-workflow/blob/master/docs/bugs_fixed.md),
even when it was found while testing this program: those are listed at the
end of a round for reference, and reach this package with the tiff-workflow
release that fixes them.

**Next free number: #1.**

| Round | Date | Shipped in | Bugs |
|---|---|---|---|
| [Round 0 — the first package](#round-0--the-first-package-2026-10-25) | 2026-10-25 | v2.7.2-exe1 | none in the packaging; 1 in tiff-workflow |

---

## Round 0 — the first package (2026-10-25)

The launcher carries over the fixes jxl-photo-exe's round 1 found
(ExifTool in a program folder outside the ANSI code page, read-only folders
in the package), and two problems were handled before the first build:

- Windows' default execution policy, and `RemoteSigned` for the files of a
  downloaded zip, refuse the scripts: the launcher sets the Process-scope
  policy to Bypass ([How it works](how_it_works.md#the-execution-policy)).
  The battery runs the program from a copy whose files all carry the
  "from the internet" mark, and first checks that this PC's policy refuses
  such a script without the launcher.
- PowerShell 7 sends a telemetry ping at start: turned off for the
  processes the program starts.

Found in tiff-workflow while preparing it (fixed there, round 24, shipped
in v2.7.2): a preset ran the scripts of the folder it was saved from, not
the ones next to the wizard. With the settings file shared between the
Python version and this program, and an update unzipped into a new folder,
a preset would have run another copy's scripts, or stopped with "Backend
script no longer exists".
