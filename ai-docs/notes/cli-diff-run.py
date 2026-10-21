"""Run one scenario against a brandwright scripts folder and print a normalised transcript, to prove a refactor
of the CLI changes no behaviour: run it on the old scripts (`git show HEAD:...` into a folder) and on the new ones,
each with its own empty WORK_DIR, replace the two WORK_DIR names with one word, and diff the transcripts.
Covers new, tokens (brand.css, tokens.md, tokens.json), import, score, sheet, status, gen, sweep and ref against a fake
ComfyUI client (every graph is printed), train --for musubi|onetrainer|ai-toolkit in every mode, and train --run --wait
with a fake ai-toolkit. Needs Pillow. Used for the 2026-10-21 budget cut (ai-docs/log.md).
usage: python cli-diff-run.py SCRIPTS_DIR WORK_DIR"""
import contextlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

scripts, work = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(scripts))
import bw  # noqa: E402
import bw_comfy  # noqa: E402
from PIL import Image  # noqa: E402

graphs = []


class Fake:
    def __init__(self, base):
        self.base = base

    def run(self, g, timeout):
        graphs.append(g)
        return {k: {"images": [{"filename": "x.png"}, {"filename": "y.png"}]} for k in g if k.startswith("save_")}

    def fetch(self, img, dest):
        Image.new("RGB", (64, 48), (200, 30, 30)).save(dest)
        return dest

    def upload(self, path):
        return "up_" + Path(path).name


bw_comfy.Comfy = Fake
out = []


def run(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            code = bw.main([str(a) for a in argv])
        except SystemExit as e:
            code = "exit %s" % e.code
    text = buf.getvalue().replace(str(work), "WORK")
    text = re.sub(r"\d{8}-\d{6}", "TS", text)
    text = re.sub(r"in \d+ s", "in N s", text)
    out.append("$ %s -> %s\n%s" % (" ".join(map(str, argv[:1])), code, text))


kit = work / "kit"
run("new", kit, "--brand", "Acme Co", "--site", "shop=https://example.com", "--site", "careers")
cfg = json.loads((kit / "brand.json").read_text())
cfg["comfy_loras"] = {"brand": "acme-brand.safetensors", "shop": "acme-shop.safetensors"}
(kit / "brand.json").write_text(json.dumps(cfg))
# tokens from a synthetic capture
tdir = kit / "capture" / "shop" / "tokens"
tdir.mkdir(parents=True)
rec = {"tally": {"background": {"#ffffff": 900, "#1d70b8": 120}, "color": {"#0b0c0c": 500, "#1d70b8": 40},
                 "border": {"#b1b4b6": 30}, "font": {"Arial": 400, "Courier New": 20, "Georgia": 30},
                 "size": {"16px": 300, "19px": 100, "24px": 30}, "radius": {"4px": 9}, "space": {"10px": 9, "20px": 5, "0px": 3},
                 "shadow": {"0 2px 0 #002d18": 4}},
       "vars": {"--brand": "#1d70b8", "--empty": ""},
       "fonts": [{"family": "Arial", "weight": "400", "style": "normal", "src": "url(a.woff2)"}],
       "recipes": {"button": [{"color": "#ffffff", "backgroundColor": "#00703c", "fontFamily": "Arial", "fontSize": "19px",
                               "paddingTop": "8px", "borderTopStyle": "solid", "borderTopWidth": "2px", "borderTopColor": "#002d18"}],
                   "card": [{"color": "#0b0c0c", "backgroundColor": "transparent", "fontFamily": "Times", "boxShadow": "none"}]}}
(tdir / "p1.json").write_text(json.dumps(rec))
(kit / "capture" / "careers" / "tokens").mkdir(parents=True)
(kit / "capture" / "careers" / "tokens" / "p2.json").write_text(json.dumps(rec))
run("tokens", kit)
for f in ("brand.css", "tokens.md", "tokens.json"):
    out.append("== %s\n%s" % (f, re.sub(r"\d{4}-\d{2}-\d{2}", "DATE", (kit / f).read_text())))
# import a folder and a file
src = work / "imgs"
(src / "sub").mkdir(parents=True)
for i, c in enumerate([(10, 20, 30), (200, 200, 200), (29, 112, 184)]):
    Image.new("RGB", (300, 200), c).save(src / ("p%d.png" % i))
Image.new("RGB", (300, 200), (0, 112, 60)).save(src / "sub" / "q.jpg")
(src / "notes.txt").write_text("x")
run("import", kit, "--site", "shop", src, src / "p1.png", "--kind", "component")
out.append("== imports %s" % sorted(p.name for p in (kit / "capture" / "shop" / "imports").iterdir()))
run("score", kit, src, src / "sub" / "q.jpg", "--json", work / "score.json")
out.append("== score.json %s" % (work / "score.json").read_text().replace(str(work), "WORK"))
run("sheet", src, src / "sub" / "q.jpg", "--out", work / "s.jpg", "--cols", 2)
out.append("== sheet size %s" % (Image.open(work / "s.jpg").size,))
# status with a fake run
tr = kit / "train"
(tr / "out" / "acmeco-brand-zimage" / "samples").mkdir(parents=True)
(tr / "acmeco-brand-zimage.json").write_text("{}")
(tr / "acmeco-brand-zimage.log").write_text("x\n 120/400 [00:10]\r 130/400 [00:11]\nlast line here\n")
(tr / "acmeco-brand-zimage.pid").write_text("4242\n")
(tr / "out" / "acmeco-brand-zimage" / "acmeco-brand-zimage_000000100.safetensors").write_text("x")
(tr / "out" / "acmeco-brand-zimage" / "samples" / "s1.jpg").write_text("x")
(tr / "other.json").write_text("{}")
run("status", kit)
# gen, sweep, ref with the fake client
run("gen", kit, "a pricing card", "--lora", "brand=0.8", "--lora", "shop=0.6", "--seed", 7, "--n", 2)
run("gen", kit, "raw prompt", "--lora", "x.safetensors=0.5", "--seed", 7, "--raw", "--graph", "qwen_image", "--steps", 5, "--cfg", 1.0)
run("gen", kit, "nolora", "--seed", 3, "--graph", "zimage")
run("ref", kit, "a login page", "--refs", src / "p0.png", src / "p1.png", "--seed", 9, "--lora", "brand=0.5")
run("ref", kit, "raw ref", "--refs", *([src / "p0.png"] * 5), "--seed", 9, "--raw")
run("ref", kit, "bad", "--refs", src / "p0.png", "--graph", "zimage")
run("sweep", kit, "a card", "--a", "brand", "--b", "shop", "--seed", 5, "--wa", "0.5,1.0", "--wb", "0:1:0.5")
for d in sorted((kit / "out").iterdir()):
    for f in sorted(d.glob("*.json")):
        out.append("== %s/%s %s" % (re.sub(r"\d{8}-\d{6}", "TS", d.name), f.name, f.read_text()))
out.append("== graphs %s" % json.dumps(graphs, sort_keys=True))
# trainer exports
(kit / "dataset" / "brand").mkdir(parents=True)
for i in range(3):
    Image.new("RGB", (64, 64)).save(kit / "dataset" / "brand" / ("%04d.png" % i))
(kit / "loras").mkdir()
(kit / "loras" / "brand-zimage_turbo.safetensors").write_text("x")
(kit / "loras" / "brand-zimage.safetensors").write_text("x")
(kit / "dataset" / "shop").mkdir(parents=True)
Image.new("RGB", (64, 64)).save(kit / "dataset" / "shop" / "0001.png")
for model in ("zimage", "zimage_turbo", "klein4b"):
    for lora, mode in (("brand", None), ("shop", "residual"), ("shop", "continue"), ("shop", "stack")):
        for trainer in ("musubi", "onetrainer", "ai-toolkit"):
            argv = ["train", kit, "--lora", lora, "--model", model, "--for", trainer] + (["--mode", mode] if mode else [])
            run(*argv)
for f in sorted(tr.rglob("*")):
    if f.is_file() and f.suffix in (".sh", ".toml", ".json") and "out" not in f.parts:
        out.append("== %s\n%s" % (f.relative_to(kit).as_posix(), f.read_text().replace(str(kit), "KIT").replace(kit.as_posix(), "KIT")))
# train --run --wait with a fake toolkit
tk = work / "tk"
tk.mkdir()
(tk / "run.py").write_text("import sys; print('training', sys.argv[1:]); sys.exit(3)\n")
run("train", kit, "--run", "--wait", "--toolkit", tk)
out.append("== log %s" % (tr / "acmeco-brand-zimage.log").read_text().replace(str(kit), "KIT"))
print("\n".join(out))
