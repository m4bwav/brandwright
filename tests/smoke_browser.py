"""Browser smoke test: capture the fixture page, check masks, tokens and a render. Skips without Playwright or a browser.

python tests/smoke_browser.py [--channel msedge]
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "brandwright" / "scripts"))
import bw  # noqa: E402


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = bw.main(list(argv))
    return code, out.getvalue()


def main():
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("SKIP: Playwright not installed")
        return 0
    channel = sys.argv[sys.argv.index("--channel") + 1] if "--channel" in sys.argv else None
    extra = ["--channel", channel] if channel else []
    tmp = Path(tempfile.mkdtemp(prefix="bwsmoke"))
    try:
        kit = tmp / "kit"
        run("new", str(kit), "--brand", "Northwind", "--site", "shop")
        url = (ROOT / "tests" / "fixtures" / "site" / "index.html").as_uri()
        try:
            code, out = run("capture", str(kit), "--site", "shop", url, "--viewports", "desktop,mobile", *extra)
        except Exception as e:  # no browser installed for Playwright
            if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
                print("SKIP: no browser for Playwright (%s)" % str(e).splitlines()[0][:120])
                return 0
            raise
        print(out)
        recs = [json.loads(l) for l in (kit / "capture" / "shop" / "capture.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(recs) == 2, recs
        text = json.dumps(recs)
        assert "jamie.doe@example.org" not in text and "help.desk@northwind.example" not in text, "e-mail not masked"
        assert "867 5309" not in text and "123 4567" not in text, "phone not masked"
        assert recs[0]["masked"] >= 3, recs[0]["masked"]
        kinds = {c["kind"] for c in recs[0]["components"]}
        assert {"header", "card", "button", "form", "footer"} <= kinds, kinds
        assert not any("Accept all" in c["text"] for r in recs for c in r["components"]), "cookie banner captured"
        code, out = run("tokens", str(kit))
        css = (kit / "brand.css").read_text(encoding="utf-8")
        assert "--nw-brand: #0b6e4f" in css, css[:400]
        assert ".bw-button-primary" in css and "#f2a541" in css
        t = json.loads((kit / "tokens.json").read_text(encoding="utf-8"))
        assert t["brand"]["font"]["family"]["f1"]["$value"] == "Georgia", t["brand"]["font"]
        html = kit / "out" / "m.html"
        html.parent.mkdir(parents=True)
        html.write_text('<!doctype html><link rel=stylesheet href="../brand.css"><button class="bw-button-primary">Go</button>', encoding="utf-8")
        code, out = run("render", str(html), "--width", "400", "--height", "200", *extra)
        assert (kit / "out" / "m.png").stat().st_size > 500
        try:
            from PIL import Image  # noqa: F401
            code, out = run("prep", str(kit))
            assert (kit / "dataset" / "shop" / "0001.png").is_file()
        except ImportError:
            pass
        print("PASS: capture, masks, cookie banner hidden, tokens, brand.css, render%s" % (", prep" if "Image" in dir() else ""))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
