"""Build the wiki's Commands page from the CLI's own --help output (run against the repository checkout)."""
import re
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1])
out = Path(sys.argv[2])
cli = repo / "skills" / "brandwright" / "scripts" / "bw.py"
ORDER = [("Set up", ["doctor", "new"]), ("Capture", ["login", "capture", "import", "tokens"]),
         ("Dataset", ["prep", "caption", "review"]), ("Training", ["train", "status", "pick"]),
         ("Mock-ups", ["gen", "sweep", "ref", "render", "score", "sheet"])]


def helptext(*args):
    r = subprocess.run([sys.executable, str(cli), *args, "--help"], capture_output=True, text=True, encoding="utf-8",
                       env={"COLUMNS": "100", "PYTHONIOENCODING": "utf-8", "SYSTEMROOT": "C:\\Windows", "PATH": ""})
    return r.stdout.replace(str(cli), "bw.py").strip()


version = re.search(r'^VERSION = "([^"]+)"', cli.read_text(encoding="utf-8"), re.M).group(1)
if "## Unreleased" in (repo / "CHANGELOG.md").read_text(encoding="utf-8"):
    version += " and the unreleased changes on `main`"
lines = ["# Commands", "", "Every command of `bw.py` %s with its options, copied from `--help`. `BW` means " % version +
         "`python skills/brandwright/scripts/bw.py`. Exit code 0 is success; a problem the CLI can explain exits with its message.", ""]
for title, cmds in ORDER:
    lines.append("- %s: %s" % (title, ", ".join("[%s](#%s)" % (c, c) for c in cmds)))
lines.append("")
for title, cmds in ORDER:
    lines += ["## %s" % title, ""]
    for c in cmds:
        lines += ["### %s" % c, "", "```", helptext(c), "```", ""]
out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
print("wrote", out)
