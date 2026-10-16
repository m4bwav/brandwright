"""Public-repository guard. Run from the repository root: python scripts/check_public.py

Fails (exit 1) when a tracked file holds an absolute path from someone's machine, a private network address, a kit
artefact (trained weights, a login profile, a dataset caption folder) or a name listed in the optional private file
named by BRANDWRIGHT_PRIVATE_NAMES (one word or phrase per line, kept outside the repository).
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = [
    (re.compile(r"\b[A-Za-z]:\\(?:Users|m4bwa|AI|ComfyUI)\\", re.I), "absolute Windows path"),
    (re.compile(r"\b[A-Za-z]:/(?:Users|m4bwa|AI|ComfyUI)/", re.I), "absolute Windows path"),
    (re.compile(r"/(?:Users|home)/[a-z0-9_.-]+/", re.I), "home folder path"),
    (re.compile(r"\b(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"), "private network address"),
    (re.compile(r"\bm4bwa\b(?!v)", re.I), "local user folder name"),
]
SKIP_FILES = {"scripts/check_public.py"}
BAD_SUFFIX = (".safetensors", ".ckpt", ".pt")


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout.split(b"\0")
    return [o.decode() for o in out if o]


def main():
    names = []
    priv = os.environ.get("BRANDWRIGHT_PRIVATE_NAMES")
    if priv and Path(priv).is_file():
        names = [l.strip() for l in Path(priv).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    problems = []
    for rel in tracked():
        if rel in SKIP_FILES:
            continue
        if rel.endswith(BAD_SUFFIX) or "/auth/" in rel or rel.startswith("kits/"):
            problems.append("%s: kit artefact must never be committed" % rel)
            continue
        p = ROOT / rel
        if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") or not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            for pat, why in PATTERNS:
                if pat.search(line):
                    problems.append("%s:%d: %s: %s" % (rel, n, why, line.strip()[:120]))
            for name in names:
                if name.lower() in line.lower():
                    problems.append("%s:%d: private name %r" % (rel, n, name))
    for pr in problems:
        print(pr)
    print("public check: %s (%d finding%s)" % ("FAIL" if problems else "PASS", len(problems), "" if len(problems) == 1 else "s"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
