#!/usr/bin/env python3
"""brandwright: brand and sub-site LoRAs for UI mock-ups, plus the token-driven code route.

A kit is one folder per brand, kept out of every repository (it holds screenshots and login sessions):
  brand.json   names, triggers, sites, model        tokens.json / brand.css   design tokens (code route)
  capture/<site>/  pages, capture.jsonl, tokens/   dataset/<lora>/  images + .txt captions
  train/       trainer configs, logs, checkpoints  loras/  picked LoRAs      out/  generated mock-ups

Commands (run with --help for options):
  doctor   new   login   capture   import   tokens   prep   caption   review
  train    status   pick   gen   sweep   ref   render   score   sheet
Core commands need only Python 3.10+. capture/login/render need Playwright; prep/score/sheet need Pillow;
gen/sweep/ref need a ComfyUI server; train needs a trainer (ostris ai-toolkit).
"""
import argparse
import base64
import colorsys
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

VERSION = "0.1.4"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ---------------------------------------------------------------- models and presets

# Training presets for ostris ai-toolkit (field names from its example configs and UI defaults, checked 2026-10-15).
# vram: smallest card it is known to train on with these settings. residual: the trainer can merge another LoRA
# during training only (model.assistant_lora_path), so a site LoRA learns just the difference from the brand LoRA.
MODELS = {
    "klein4b": {
        "label": "FLUX.2 klein base 4B", "licence": "Apache-2.0", "vram": 12, "residual": False,
        "model": {"name_or_path": "black-forest-labs/FLUX.2-klein-base-4B", "arch": "flux2_klein_4b",
                  "quantize": True, "qtype": "qfloat8", "quantize_te": True, "qtype_te": "qfloat8", "low_vram": True,
                  "model_kwargs": {"match_target_res": False}},
        "sample": {"guidance_scale": 4.0, "sample_steps": 25}, "timestep_type": "weighted",
        "comfy": "klein4b",
    },
    "zimage": {
        "label": "Z-Image (base)", "licence": "Apache-2.0", "vram": 16, "residual": True,
        "model": {"name_or_path": "Tongyi-MAI/Z-Image", "arch": "zimage", "quantize": True, "qtype": "qfloat8",
                  "quantize_te": True, "qtype_te": "qfloat8", "low_vram": True},
        "sample": {"guidance_scale": 4.0, "sample_steps": 30}, "timestep_type": "weighted",
        "comfy": "zimage",
    },
    "zimage_turbo": {
        "label": "Z-Image Turbo (with training adapter)", "licence": "Apache-2.0", "vram": 16, "residual": False,
        "model": {"name_or_path": "Tongyi-MAI/Z-Image-Turbo", "arch": "zimage", "quantize": True, "qtype": "qfloat8",
                  "quantize_te": True, "qtype_te": "qfloat8", "low_vram": True,
                  "assistant_lora_path": "ostris/zimage_turbo_training_adapter/zimage_turbo_training_adapter_v2.safetensors"},
        "sample": {"guidance_scale": 1.0, "sample_steps": 9}, "timestep_type": "weighted",
        "comfy": "zimage_turbo",
    },
    "qwen_image": {
        "label": "Qwen-Image 2512", "licence": "Apache-2.0", "vram": 24, "residual": False,
        "model": {"name_or_path": "Qwen/Qwen-Image-2512", "arch": "qwen_image", "quantize": True,
                  "qtype": "uint3|ostris/accuracy_recovery_adapters/qwen_image_2512_torchao_uint3.safetensors",
                  "quantize_te": True, "qtype_te": "qfloat8", "low_vram": True},
        "sample": {"guidance_scale": 3.0, "sample_steps": 25}, "timestep_type": "weighted", "cache_text_embeddings": True,
        "comfy": "qwen_image",
    },
}
DEFAULT_MODEL = "zimage"
# Other trainers for `train --for`: kohya-ss/musubi-tuner v0.3.6 and Nerogar/OneTrainer b08db37, read 2026-10-18
# (ai-docs/research/2026-10-18-musubi-onetrainer.md). musubi: script prefix, network module, extra cache/train flags
# (fp8 text encoder, model version), timesteps. OneTrainer: model_type, LoRA layer filter and preset.
MUSUBI = {
    "zimage": ("zimage", "lora_zimage", "--fp8_llm", "--timestep_sampling shift --weighting_scheme none --discrete_flow_shift 2.0"),
    "zimage_turbo": ("zimage", "lora_zimage", "--fp8_llm", "--timestep_sampling shift --weighting_scheme none --discrete_flow_shift 2.0"),
    "klein4b": ("flux_2", "lora_flux_2", "--fp8_text_encoder --model_version klein-base-4b", "--timestep_sampling flux2_shift"),
    "qwen_image": ("qwen_image", "lora_qwen_image", "--fp8_vl", "--timestep_sampling shift --discrete_flow_shift 2.2"),
}
ONETRAINER = {
    "zimage": ("Z_IMAGE", "^(?=.*attention)(?!.*refiner).*,^(?=.*feed_forward)(?!.*refiner).*", "attn-mlp"),
    "zimage_turbo": ("Z_IMAGE", "^(?=.*attention)(?!.*refiner).*,^(?=.*feed_forward)(?!.*refiner).*", "attn-mlp"),
    "klein4b": ("FLUX_2", "transformer_block", "blocks"),
    "qwen_image": ("QWEN", "attn,img_mlp,txt_mlp", "attn-mlp"),
}
DETURBO = "https://huggingface.co/ostris/Z-Image-De-Turbo/blob/main/z_image_de_turbo_v1_bf16.safetensors"

# Held-out sample prompts: component kinds a capture rarely contains, so samples show what the LoRA generalises.
HELD_OUT = [
    "isolated pricing table UI component with three plans and a highlighted middle plan, on a plain background",
    "desktop web page screenshot, account settings page with a left sidebar menu and a form with a \"Save changes\" button",
    "mobile web screen, order confirmation with a summary card and a button labelled \"Track order\"",
    "isolated modal dialog UI component asking \"Delete this item?\" with a cancel button and a delete button",
    "desktop web page screenshot, empty state of a dashboard with an illustration and a \"Create your first report\" button",
    "isolated notification toast UI component reading \"Changes saved\" with a close icon",
]

VIEW_PHRASE = {"desktop": "desktop web page screenshot", "laptop": "desktop web page screenshot",
               "tablet": "tablet web page screenshot", "mobile": "mobile web screen screenshot", "import": "UI screenshot"}
KIND_CAP = {"header": 2, "footer": 2, "navigation": 2, "breadcrumb": 2, "pagination": 2, "button": 8,
            "text input": 6, "tile": 24}
KIND_CAP_DEFAULT = 12
VLM_PROMPT = ("Describe this user-interface image for an image-model training caption, in one or two sentences. "
              "Say what kind of screen or component it is, its parts and how they are arranged (top to bottom, "
              "left to right), and quote the main visible headings and button labels exactly in double quotes. "
              "Do NOT mention colours, fonts, typefaces, rounded corners, shadows, spacing, the visual style, the "
              "brand, the company or logos. No preamble.")


# ---------------------------------------------------------------- kit

class Kit:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.cfg_path = self.root / "brand.json"
        if not self.cfg_path.is_file():
            sys.exit("brandwright: %s is not a kit (no brand.json). Create one with: bw.py new %s --brand NAME"
                     % (self.root, root))
        self.cfg = json.loads(self.cfg_path.read_text(encoding="utf-8"))

    def save(self):
        self.cfg_path.write_text(json.dumps(self.cfg, indent=2) + "\n", encoding="utf-8")

    def site(self, name):
        for s in self.cfg.get("sites", []):
            if s["name"] == name:
                return s
        sys.exit("brandwright: no site %r in brand.json (sites: %s). Add one: bw.py new %s --site %s"
                 % (name, ", ".join(s["name"] for s in self.cfg.get("sites", [])) or "none", self.root, name))

    def loras(self):
        """The LoRAs this kit trains: 'brand' plus every site with its own LoRA."""
        return [("brand", self.cfg["brand"]["trigger"], None)] + [
            (s["name"], s["trigger"], s["name"]) for s in self.cfg.get("sites", []) if s.get("lora", True)]

    def triggers(self, lora):
        brand = self.cfg["brand"]["trigger"]
        return brand if lora == "brand" else "%s %s" % (brand, self.site(lora)["trigger"])

    @property
    def model(self):
        return self.cfg.get("model", DEFAULT_MODEL)


def make_trigger(name, suffix):
    base = re.sub(r"[^a-z0-9]", "", name.lower())[:10] or "brand"
    return base + suffix


def cmd_new(args):
    root = Path(args.kit).resolve()
    cfg_path = root / "brand.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    else:
        if not args.brand:
            sys.exit("a new kit needs --brand NAME")
        root.mkdir(parents=True, exist_ok=True)
        cfg = {"brandwright": 1, "brand": {"name": args.brand, "trigger": args.trigger or make_trigger(args.brand, "ui")},
               "sites": [], "model": args.model, "comfy": os.environ.get("BRANDWRIGHT_COMFY", "http://127.0.0.1:8188"),
               "weights": {}, "private": True}
        # a kit holds screenshots and login sessions: make sure git never picks it up
        (root / ".gitignore").write_text("# brandwright kit: private screenshots and sessions, never commit\n*\n", encoding="utf-8")
        (root / "README.txt").write_text(
            "brandwright kit for %s. Private: screenshots, captions, login sessions (auth/) and trained LoRAs.\n"
            "Keep it on approved storage, never in a repository or a public share.\n" % args.brand, encoding="utf-8")
    known = {s["name"] for s in cfg["sites"]}
    for spec in args.site or []:
        name, _, url = spec.partition("=")
        name = re.sub(r"[^a-z0-9-]", "-", name.lower()).strip("-")
        if name in known:
            continue
        cfg["sites"].append({"name": name, "trigger": make_trigger(cfg["brand"]["name"], name.replace("-", "")[:8] + "ui"),
                             "urls": [url] if url else [], "lora": True})
        known.add(name)
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print("kit %s  brand %s (trigger %s)  sites: %s  model: %s" % (
        root, cfg["brand"]["name"], cfg["brand"]["trigger"], ", ".join("%s (%s)" % (s["name"], s["trigger"]) for s in cfg["sites"]) or "none",
        cfg["model"]))
    return 0


# ---------------------------------------------------------------- doctor

def http_json(url, data=None, timeout=10):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None,
                                 headers={"Content-Type": "application/json"} if data is not None else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def find_toolkit(args, kit=None):
    cands = [getattr(args, "toolkit", None), os.environ.get("BRANDWRIGHT_AI_TOOLKIT"),
             kit.cfg.get("ai_toolkit") if kit else None]
    for c in cands:
        if c and (Path(c) / "run.py").is_file():
            return Path(c).resolve()
    return None


def toolkit_python(tk):
    for p in (tk / v / "Scripts" / "python.exe" if win else tk / v / "bin" / "python"
              for v in ("venv", ".venv") for win in (True, False)):
        if p.is_file():
            return str(p)
    return sys.executable


def cmd_doctor(args):
    ok = True
    print("brandwright %s  python %s  %s" % (VERSION, sys.version.split()[0], sys.platform))
    try:
        import PIL
        print("  Pillow %s: prep, score and sheet work" % PIL.__version__)
    except ImportError:
        print("  Pillow missing: python -m pip install pillow  (prep, score, sheet)")
        ok = False
    try:
        import playwright  # noqa: F401
        print("  Playwright installed: capture, login and render work (add --channel msedge or chrome to use an installed browser)")
    except ImportError:
        print("  Playwright missing: python -m pip install playwright  (capture, login, render)")
        ok = False
    smi = shutil.which("nvidia-smi")
    if smi:
        try:
            gpu = subprocess.run([smi, "--query-gpu=name,memory.total,memory.used", "--format=csv,noheader"],
                                 capture_output=True, text=True, timeout=15).stdout.strip()
            print("  GPU: %s" % gpu.replace("\n", " | "))
        except Exception as e:
            print("  nvidia-smi failed: %s" % e)
    else:
        print("  no NVIDIA GPU found: train on another machine or a hosted trainer; the code route still works here")
    tk = find_toolkit(args)
    print("  ai-toolkit: %s" % (tk or "not found (set BRANDWRIGHT_AI_TOOLKIT or pass --toolkit; see brandwright-train)"))
    for url in (args.comfy or [os.environ.get("BRANDWRIGHT_COMFY", "http://127.0.0.1:8188")]):
        try:
            st = http_json(url.rstrip("/") + "/system_stats", timeout=4)
            dev = st.get("devices", [{}])[0]
            print("  ComfyUI %s: up (%s, %.1f GB free VRAM)" % (url, dev.get("name", "?"), dev.get("vram_free", 0) / 2**30))
        except Exception as e:
            print("  ComfyUI %s: not reachable (%s)" % (url, type(e).__name__))
    ollama = os.environ.get("BRANDWRIGHT_OLLAMA", "http://127.0.0.1:11434")
    try:
        tags = http_json(ollama + "/api/tags", timeout=3)
        print("  Ollama %s: %d models (local captioning)" % (ollama, len(tags.get("models", []))))
    except Exception:
        print("  Ollama %s: not reachable (captions fall back to templates)" % ollama)
    return 0 if ok else 1


# ---------------------------------------------------------------- import

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def cmd_import(args):
    kit = Kit(args.kit)
    kit.site(args.site)
    dest = kit.root / "capture" / args.site / "imports"
    dest.mkdir(parents=True, exist_ok=True)
    log = kit.root / "capture" / args.site / "capture.jsonl"
    files = [q for p in map(Path, args.paths)
             for q in (sorted(x for x in p.rglob("*") if x.suffix.lower() in IMG_EXT) if p.is_dir() else [p])]
    n = 0
    with log.open("a", encoding="utf-8") as f:
        for src in files:
            if src.suffix.lower() not in IMG_EXT:
                continue
            name = re.sub(r"[^A-Za-z0-9._-]", "-", src.name)
            shutil.copy2(src, dest / name)
            f.write(json.dumps({"file": "imports/" + name, "site": args.site, "viewport": args.viewport, "dsf": 1,
                                "kind": args.kind, "title": "", "url": "", "bg": None, "components": [],
                                "captured": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
            n += 1
    print("imported %d image(s) into %s as %s" % (n, dest, args.kind))
    return 0


# ---------------------------------------------------------------- colour helpers

def parse_color(c):
    """'#rrggbb[aa]' or 'rgb(a)(...)' -> (r, g, b) or None for transparent or unknown."""
    if not c:
        return None
    c = c.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{6})([0-9a-f]{2})?", c)
    if m:
        if m.group(2) and int(m.group(2), 16) < 13:
            return None
        h = m.group(1)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)", c)
    if m:
        a = m.group(4)
        if a is not None:
            av = float(a[:-1]) / 100 if a.endswith("%") else float(a)
            if av < 0.05:
                return None
        return tuple(int(round(float(m.group(i)))) for i in (1, 2, 3))
    return None


def to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def rgb_to_lab(rgb):
    def lin(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116  # noqa: E731
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(a, b):
    return math.dist(rgb_to_lab(a), rgb_to_lab(b))


def chroma(rgb):
    return colorsys.rgb_to_hls(*(v / 255 for v in rgb))[2]


# ---------------------------------------------------------------- tokens (code route)

def merge_tally(files):
    tally, vars_, fonts, recipes = {}, {}, {}, {}
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for k, table in d.get("tally", {}).items():
            t = tally.setdefault(k, {})
            for v, w in table.items():
                t[v] = t.get(v, 0) + w
        for k, v in d.get("vars", {}).items():
            vars_.setdefault(k, v)
        for fo in d.get("fonts", []):
            fonts.setdefault((fo["family"], fo["weight"], fo["style"]), fo)
        for kind, lst in d.get("recipes", {}).items():
            recipes.setdefault(kind, []).extend(lst)
    return tally, vars_, list(fonts.values()), recipes


def top(table, n, key=None):
    items = sorted(table.items(), key=lambda kv: -kv[1])
    return [k for k, _ in items[:n]] if key is None else [key(k) for k, _ in items[:n]]


def palette_from(tally, n=10):
    """Merge near-identical colours (delta-E < 3) across text, background and border tallies."""
    total = {}
    for k in ("background", "color", "border"):
        t = tally.get(k, {})
        s = sum(t.values()) or 1
        for c, w in t.items():
            rgb = parse_color(c)
            if rgb:
                total[rgb] = total.get(rgb, 0) + w / s
    merged = []
    for rgb, w in sorted(total.items(), key=lambda kv: -kv[1]):
        for m in merged:
            if delta_e(rgb, m[0]) < 3:
                m[1] += w
                break
        else:
            merged.append([rgb, w])
    return merged[:n]


def common_recipe(lst):
    """The most frequent style signature among a kind's elements."""
    if not lst:
        return None
    counts = Counter(json.dumps(r, sort_keys=True) for r in lst)
    return json.loads(max(counts.items(), key=lambda kv: kv[1])[0])


def build_tokens(tally, vars_, fonts, recipes):
    pal = palette_from(tally)
    bg = parse_color(top(tally.get("background", {}), 1)[0]) if tally.get("background") else (255, 255, 255)
    text = parse_color(top(tally.get("color", {}), 1)[0]) if tally.get("color") else (17, 17, 17)
    accents = [rgb for rgb, _ in pal if chroma(rgb) > 0.35 and delta_e(rgb, bg) > 20]
    primary = accents[0] if accents else text
    MONO = re.compile(r"mono|courier|consolas|menlo", re.I)
    all_fams = top(tally.get("font", {}), 6)
    fams = [f for f in all_fams if not MONO.search(f)][:3]
    mono = [f for f in all_fams if MONO.search(f)][:1]
    sizes = sorted({int(round(float(s[:-2]))) for s in top(tally.get("size", {}), 8) if s.endswith("px")})
    radii = [r for r in top(tally.get("radius", {}), 4)]
    spaces = sorted({int(round(float(s[:-2]))) for s in top(tally.get("space", {}), 10) if s.endswith("px") and float(s[:-2]) > 0})
    return {
        "color": {"$type": "color",
                  "background": {"$value": to_hex(bg or (255, 255, 255))}, "text": {"$value": to_hex(text or (17, 17, 17))},
                  "primary": {"$value": to_hex(primary or (0, 0, 0))}},
        "palette": {"$type": "color", **{"c%02d" % i: {"$value": to_hex(rgb), "$description": "share %.3f" % w}
                                         for i, (rgb, w) in enumerate(pal, 1)}},
        "font": {"family": {"$type": "fontFamily", **{"f%d" % i: {"$value": f} for i, f in enumerate(fams, 1)},
                            **({"mono": {"$value": mono[0]}} if mono else {})},
                 "size": {"$type": "dimension", **{"s%d" % i: {"$value": "%dpx" % s} for i, s in enumerate(sizes, 1)}}},
        "radius": {"$type": "dimension", **{"r%d" % i: {"$value": r} for i, r in enumerate(radii, 1)}},
        "space": {"$type": "dimension", **{"x%d" % i: {"$value": "%dpx" % s} for i, s in enumerate(spaces, 1)}},
        "shadow": {"$type": "shadow", **{"s%d" % i: {"$value": s} for i, s in enumerate(top(tally.get("shadow", {}), 3), 1)}},
        "$extensions": {"brandwright": {
            "site_custom_properties": dict(list(vars_.items())[:200]),
            "font_faces": fonts[:20],
            "recipes": recipe_set(recipes, fams)}},
    }


def recipe_set(recipes, fams):
    """The most common style of each component kind, plus 'button primary': the most common button with a coloured
    fill (the call to action, which is rarely the most common button). A recipe font that is not one of the site's
    main families (an inherited default) is dropped."""
    out = {k: common_recipe(v) for k, v in recipes.items() if v}
    # 13.3333px is Chromium's own size for an unstyled form control: such a button is a browser default, not the brand's
    coloured = [r for r in recipes.get("button", [])
                if parse_color(r.get("backgroundColor")) and chroma(parse_color(r["backgroundColor"])) > 0.3
                and r.get("fontSize") != "13.3333px"]
    if coloured:
        out["button primary"] = common_recipe(coloured)
    for r in out.values():
        first = (r.get("fontFamily") or "").split(",")[0].strip().strip("\"'")
        if first and fams and first not in fams:
            r.pop("fontFamily", None)
    return out


CSS_PROPS = {"color": "color", "backgroundColor": "background-color", "fontFamily": "font-family", "fontSize": "font-size",
             "fontWeight": "font-weight", "lineHeight": "line-height", "letterSpacing": "letter-spacing",
             "textTransform": "text-transform", "paddingTop": "padding-top", "paddingRight": "padding-right",
             "paddingBottom": "padding-bottom", "paddingLeft": "padding-left", "borderTopLeftRadius": "border-radius",
             "boxShadow": "box-shadow", "minHeight": "min-height"}


def css_for(tok, scope=":root"):
    lines = []
    ext = tok["$extensions"]["brandwright"]
    if scope == ":root":
        lines += ["@font-face { font-family: \"%s\"; font-weight: %s; font-style: %s; src: %s; }"
                  % (fo["family"], fo["weight"], fo["style"], fo["src"]) for fo in ext["font_faces"]]
    lines.append("%s {" % scope)
    lines += ["  %s: %s;" % (name, val) for name, val in ext["site_custom_properties"].items() if val]
    lines += ["  --bw-%s: %s;" % (k, tok["color"][k]["$value"]) for k in ("background", "text", "primary")]
    lines += ["  --bw-palette-%s: %s;" % (k, v["$value"]) for k, v in tok["palette"].items() if not k.startswith("$")]
    fams = [v["$value"] for k, v in tok["font"]["family"].items() if not k.startswith("$") and k != "mono"]
    if fams:
        lines.append("  --bw-font: %s, system-ui, sans-serif;" % ", ".join('"%s"' % f for f in fams))
    if "mono" in tok["font"]["family"]:
        lines.append('  --bw-font-mono: "%s", ui-monospace, monospace;' % tok["font"]["family"]["mono"]["$value"])
    for prefix, group in (("radius", tok["radius"]), ("space", tok["space"]), ("shadow", tok["shadow"]), ("size", tok["font"]["size"])):
        lines += ["  --bw-%s-%s: %s;" % (prefix, k, v["$value"]) for k, v in group.items() if not k.startswith("$")]
    lines.append("}")
    pre = "" if scope == ":root" else scope + " "
    if scope == ":root":
        lines.append("body { margin: 0; background: var(--bw-background); color: var(--bw-text); font-family: var(--bw-font, system-ui, sans-serif); }")
    for kind, cls in (("button", "bw-button"), ("button primary", "bw-button-primary"), ("text input", "bw-input"), ("card", "bw-card"), ("header", "bw-header"),
                      ("navigation", "bw-nav"), ("footer", "bw-footer"), ("alert", "bw-alert"), ("hero", "bw-hero")):
        r = ext["recipes"].get(kind)
        if not r:
            continue
        decl = []
        for k, prop in CSS_PROPS.items():
            v = r.get(k)
            if v and v not in ("none", "normal", "auto", "0px") and not (k == "backgroundColor" and parse_color(v) is None):
                decl.append("%s: %s" % (prop, v))
        if r.get("borderTopStyle") not in (None, "none") and r.get("borderTopWidth") not in (None, "0px"):
            decl.append("border: %s %s %s" % (r["borderTopWidth"], r["borderTopStyle"], r["borderTopColor"]))
        lines.append("%s.%s { %s; }" % (pre, cls, "; ".join(decl)))
    return "\n".join(lines) + "\n"


def cmd_tokens(args):
    kit = Kit(args.kit)
    all_files, per_site = [], {}
    for s in kit.cfg.get("sites", []):
        fs = sorted((kit.root / "capture" / s["name"] / "tokens").glob("*.json"))
        per_site[s["name"]] = fs
        all_files += fs
    if not all_files:
        sys.exit("no captured tokens yet: run capture first")
    brand = build_tokens(*merge_tally(all_files))
    out = {"$description": "brandwright design tokens (DTCG 2025.10 shape) for %s; sites override brand" % kit.cfg["brand"]["name"],
           "brand": brand, "sites": {}}
    css = ["/* brandwright %s: tokens and component recipes read from the live sites. Link it from a mock-up page. */"
           % kit.cfg["brand"]["name"], css_for(brand)]
    for name, fs in per_site.items():
        if fs:
            st = build_tokens(*merge_tally(fs))
            out["sites"][name] = st
            css.append(css_for(st, scope='[data-site="%s"]' % name))
    (kit.root / "tokens.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (kit.root / "brand.css").write_text("\n".join(css), encoding="utf-8")
    md = ["# %s tokens" % kit.cfg["brand"]["name"], "", "Read from %d captured page views on %s. Use `brand.css` in mock-ups: "
          "`<link rel=stylesheet href=brand.css>` and `<body data-site=\"SITE\">` for a site's overrides." % (len(all_files), time.strftime("%Y-%m-%d")), "",
          "| token | value |", "|---|---|"]
    md += ["| color.%s | %s |" % (k, brand["color"][k]["$value"]) for k in ("background", "text", "primary")]
    md += ["| palette.%s | %s (%s) |" % (k, v["$value"], v["$description"]) for k, v in brand["palette"].items() if not k.startswith("$")]
    md += ["| font.%s | %s |" % (k, v["$value"]) for k, v in brand["font"]["family"].items() if not k.startswith("$")]
    md += ["", "Component recipes found: %s." % (", ".join(sorted(brand["$extensions"]["brandwright"]["recipes"])) or "none")]
    (kit.root / "tokens.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    try:
        from PIL import Image, ImageDraw
        pal = [v["$value"] for k, v in brand["palette"].items() if not k.startswith("$")]
        im = Image.new("RGB", (80 * max(1, len(pal)), 80), "white")
        d = ImageDraw.Draw(im)
        for i, h in enumerate(pal):
            d.rectangle([i * 80, 0, i * 80 + 79, 79], fill=h)
        im.save(kit.root / "palette.png")
    except ImportError:
        pass
    print("wrote tokens.json, brand.css, tokens.md%s for %d page view(s); primary %s, fonts %s" % (
        ", palette.png" if (kit.root / "palette.png").exists() else "", len(all_files), brand["color"]["primary"]["$value"],
        ", ".join(v["$value"] for k, v in brand["font"]["family"].items() if not k.startswith("$")) or "none"))
    if "button primary" not in brand["$extensions"]["brandwright"]["recipes"]:
        print("  no coloured call-to-action button was captured, so brand.css has no .bw-button-primary: capture a page "
              "that has one (a form, a start or sign-up page), or style it from the site's own variables")
    return 0


# ---------------------------------------------------------------- prep (dataset)

def need_pil():
    try:
        from PIL import Image  # noqa: F401
        return Image
    except ImportError:
        sys.exit("brandwright: this command needs Pillow: python -m pip install pillow")


def pixels(im):
    return list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())


def dhash(im, size=8):
    g = im.convert("L").resize((size + 1, size))
    px = pixels(g)
    bits = 0
    for y in range(size):
        for x in range(size):
            bits = (bits << 1) | (px[y * (size + 1) + x] > px[y * (size + 1) + x + 1])
    return bits


def hamming(a, b):
    return bin(a ^ b).count("1")


def flatness(im):
    """Standard deviation of a small greyscale copy: near 0 means an empty or single-colour picture."""
    g = im.convert("L").resize((32, 32))
    px = pixels(g)
    mean = sum(px) / len(px)
    return (sum((p - mean) ** 2 for p in px) / len(px)) ** 0.5


ASPECTS = [(1, 1), (4, 3), (3, 4), (16, 9), (9, 16), (3, 2), (2, 3)]


def specimen(Image, crop, bg, min_side=768, margin=0.12):
    """Place a component crop on a canvas of the page background with a margin, so small parts train at a usable
    size and read as 'an isolated component on a plain background'. Upscale at most 2x."""
    w, h = crop.size
    scale = min(2.0, max(1.0, (min_side * (1 - 2 * margin)) / max(w, h)))
    if scale > 1.0:
        crop = crop.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        w, h = crop.size
    need_w, need_h = w / (1 - 2 * margin), h / (1 - 2 * margin)
    best = None
    for aw, ah in ASPECTS:
        cw = max(need_w, need_h * aw / ah)
        ch = cw * ah / aw
        if best is None or cw * ch < best[0] * best[1]:
            best = (cw, ch)
    cw, ch = int(math.ceil(best[0] / 16) * 16), int(math.ceil(best[1] / 16) * 16)
    canvas = Image.new("RGB", (cw, ch), bg)
    canvas.paste(crop.convert("RGB"), ((cw - w) // 2, (ch - h) // 2))
    return canvas


def tile_heights(viewport, width):
    """Tile height for a page screenshot: about one viewport, within an aspect the trainers bucket well."""
    ratio = {"desktop": 0.625, "laptop": 0.625, "tablet": 1.43, "mobile": 2.16}.get(viewport, 0.75)
    return int(width * ratio)


def overlaps(box, y0, y1, dsf):
    top_, bot = box["y"] * dsf, (box["y"] + box["h"]) * dsf
    return min(bot, y1) - max(top_, y0) > 0.5 * min(bot - top_, y1 - y0)


def candidates_for_site(Image, kit, site, args):
    base = kit.root / "capture" / site
    log = base / "capture.jsonl"
    if not log.is_file():
        return []
    out = []
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        path = base / rec["file"]
        if not path.is_file():
            continue
        im = Image.open(path).convert("RGB")
        W, H = im.size
        dsf = rec.get("dsf", 1)
        bg = parse_color(rec.get("bg")) or im.getpixel((2, 2))
        vp = rec.get("viewport", "import")
        if rec.get("kind") == "component":
            out.append({"img": specimen(Image, im, bg), "kind": "component", "site": site, "viewport": vp, "text": "",
                        "parts": [], "src": rec["file"], "tile": None})
            continue
        th = tile_heights(vp, W) if rec.get("kind") != "screen" or H / W > 2.2 else H
        y, n = 0, 0
        while y < H and n < args.tiles:
            y1 = min(H, y + th)
            if y1 - y < th * 0.5 and n > 0:
                break
            parts = sorted({c["kind"] for c in rec.get("components", []) if overlaps(c["box"], y, y1, dsf)})
            out.append({"img": im.crop((0, y, W, y1)), "kind": "tile", "site": site, "viewport": vp, "text": "",
                        "parts": parts, "src": rec["file"], "tile": n})
            y, n = y1, n + 1
        for c in rec.get("components", []):
            b = c["box"]
            pad = 16
            x0, y0 = max(0, (b["x"] - pad) * dsf), max(0, (b["y"] - pad) * dsf)
            x1, y1 = min(W, (b["x"] + b["w"] + pad) * dsf), min(H, (b["y"] + b["h"] + pad) * dsf)
            if x1 - x0 < 48 or y1 - y0 < 24:
                continue
            crop = im.crop((int(x0), int(y0), int(x1), int(y1)))
            if crop.size[1] > crop.size[0] * 3:  # a tall column: keep its top part only
                crop = crop.crop((0, 0, crop.size[0], crop.size[0] * 3))
            out.append({"img": specimen(Image, crop, bg) if crop.size[0] < W * 0.9 else crop, "kind": c["kind"],
                        "site": site, "viewport": vp, "text": c.get("text", ""), "parts": [], "src": rec["file"], "tile": None})
    return out


def caption_template(kit, lora, c):
    trig = kit.triggers(lora)
    view = VIEW_PHRASE.get(c["viewport"], "UI screenshot")
    if c["kind"] == "tile":
        where = "top of the page" if c["tile"] == 0 else "section further down the page"
        parts = ", ".join(p for p in c["parts"] if p not in ("button", "text input")) or "content"
        body = "%s, %s showing %s" % (view, where, parts)
    elif c["kind"] in ("component", "screen"):
        body = view
    else:
        size = "mobile" if c["viewport"] == "mobile" else "desktop"
        body = "isolated %s UI component, %s size, on a plain background" % (c["kind"], size)
        t = c["text"].strip()
        if t and len(t) <= 60:
            body += ', text reads "%s"' % t.replace('"', "'")
    return "%s, %s" % (trig, body)


def cmd_prep(args):
    Image = need_pil()
    kit = Kit(args.kit)
    sites = [s["name"] for s in kit.cfg.get("sites", [])]
    pools = {}
    for s in sites:
        cands = candidates_for_site(Image, kit, s, args)
        kept, hashes, per_kind, texts = [], [], {}, set()
        for c in cands:
            im = c["img"]
            if min(im.size) < 64 or flatness(im) < 4:
                continue
            h = dhash(im)
            if any(hamming(h, o) <= args.dedupe for o in hashes):
                continue
            key = (c["kind"], c["viewport"] == "mobile", re.sub(r"\W+", " ", c["text"].lower()).strip())
            if c["kind"] != "tile" and key[2]:
                if key in texts:  # the same component with the same words, e.g. "Menu" on every page
                    continue
                texts.add(key)
            if per_kind.get(c["kind"], 0) >= KIND_CAP.get(c["kind"], KIND_CAP_DEFAULT):
                continue
            per_kind[c["kind"]] = per_kind.get(c["kind"], 0) + 1
            hashes.append(h)
            kept.append(c)
        pools[s] = kept[: args.max_per_site]
        print("site %-16s %4d candidates -> %3d kept  %s" % (s, len(cands), len(pools[s]),
                                                              ", ".join("%s %d" % kv for kv in sorted(per_kind.items()))))
    plan = {}
    for lora, trig, site in kit.loras():
        if site:
            plan[lora] = pools.get(site, [])
        else:
            share = max(1, args.brand_max // max(1, len([s for s in sites if pools.get(s)])))
            plan[lora] = [c for s in sites for c in pools.get(s, [])[:share]]
    for lora, items in plan.items():
        d = kit.root / "dataset" / lora
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        man = []
        for i, c in enumerate(items, 1):
            im = c["img"]
            if max(im.size) > 2048:
                k = 2048 / max(im.size)
                im = im.resize((int(im.size[0] * k), int(im.size[1] * k)), Image.LANCZOS)
            name = "%04d" % i
            im.save(d / (name + ".png"))
            cap = caption_template(kit, lora, c)
            (d / (name + ".txt")).write_text(cap + "\n", encoding="utf-8")
            man.append({"file": name + ".png", "site": c["site"], "kind": c["kind"], "viewport": c["viewport"],
                        "src": c["src"], "size": list(im.size), "caption": "template"})
        (d / "manifest.jsonl").write_text("".join(json.dumps(m) + "\n" for m in man), encoding="utf-8")
        flag = "" if len(items) >= 15 else "  (thin: aim for 20-40 for a site, 40-100 for the brand)"
        print("dataset %-12s %3d images -> %s%s" % (lora, len(items), d, flag))
    return 0


# ---------------------------------------------------------------- captions

def ollama_caption(host, model, path, timeout=180):
    img = base64.b64encode(Path(path).read_bytes()).decode()
    body = {"model": model, "stream": False, "options": {"temperature": 0.2},
            "messages": [{"role": "user", "content": VLM_PROMPT, "images": [img]}]}
    r = http_json(host.rstrip("/") + "/api/chat", body, timeout=timeout)
    text = r.get("message", {}).get("content", "").strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    return re.sub(r"\s+", " ", text)


STYLE_WORDS = re.compile(r"\b(?:colou?rs?|colou?red|blue|red|green|yellow|orange|purple|pink|teal|navy|black|white|grey|gray|"
                         r"font|typeface|serif|sans-serif|rounded|shadow|gradient|minimalist|modern|clean|sleek|brand(?:ed)?|logo)\b", re.I)


def cmd_caption(args):
    kit = Kit(args.kit)
    loras = [args.lora] if args.lora else [l for l, _, _ in kit.loras()]
    host = args.host or os.environ.get("BRANDWRIGHT_OLLAMA", "http://127.0.0.1:11434")
    cache_path = kit.root / "dataset" / ".captions.json"  # the brand set shares pictures with the site sets
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}
    for lora in loras:
        d = kit.root / "dataset" / lora
        man_path = d / "manifest.jsonl"
        if not man_path.is_file():
            print("no dataset for %s: run prep first" % lora)
            continue
        man = [json.loads(l) for l in man_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        done = 0
        for m in man:
            if m.get("caption") == "vlm" and not args.force:
                continue
            if args.vlm == "none":
                break
            import hashlib
            key = hashlib.sha1((d / m["file"]).read_bytes()).hexdigest()
            try:
                desc = cache.get(key) if not args.force else None
                if not desc:
                    desc = ollama_caption(host, args.model, d / m["file"])
                    cache[key] = desc
                    cache_path.write_text(json.dumps(cache), encoding="utf-8")
            except Exception as e:
                print("  %s: VLM failed (%s); template caption kept" % (m["file"], str(e)[:120]))
                continue
            flagged = STYLE_WORDS.findall(desc)
            view = VIEW_PHRASE.get(m["viewport"], "UI screenshot") if m["kind"] in ("tile", "component", "screen") else \
                "isolated %s UI component" % m["kind"]
            cap = "%s, %s. %s" % (kit.triggers(lora), view, desc)
            (d / m["file"].replace(".png", ".txt")).write_text(cap + "\n", encoding="utf-8")
            m["caption"] = "vlm"
            done += 1
            if flagged:
                m["style_words"] = sorted({w.lower() for w in flagged})
            print("  %s %s%s" % (m["file"], desc[:100], ("  [style words: %s]" % ", ".join(m["style_words"])) if flagged else ""))
            man_path.write_text("".join(json.dumps(x) + "\n" for x in man), encoding="utf-8")  # progress survives a crash
        man_path.write_text("".join(json.dumps(m) + "\n" for m in man), encoding="utf-8")
        print("%s: %d caption(s) written by %s" % (lora, done, args.model if args.vlm != "none" else "nothing (templates kept)"))
    return 0


def cmd_review(args):
    kit = Kit(args.kit)
    rows = []
    for lora, _, _ in kit.loras():
        d = kit.root / "dataset" / lora
        if not d.is_dir():
            continue
        rows.append("<h2>%s</h2><div class=g>" % html.escape(lora))
        for p in sorted(d.glob("*.png")):
            cap = (p.with_suffix(".txt").read_text(encoding="utf-8") if p.with_suffix(".txt").exists() else "").strip()
            rows.append('<figure><img loading=lazy src="dataset/%s/%s"><figcaption><b>%s</b> %s</figcaption></figure>'
                        % (lora, p.name, p.stem, html.escape(cap)))
        rows.append("</div>")
    page = ("<!doctype html><meta charset=utf-8><title>%s dataset</title><style>body{font:14px system-ui;margin:16px}"
            ".g{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}img{width:100%%;border:1px solid #ccc}"
            "figure{margin:0}</style><h1>%s dataset review</h1><p>Delete pictures you do not want (and their .txt), fix captions "
            "in the .txt files: describe content and layout, quote visible text, never colours or fonts.</p>%s"
            % (html.escape(kit.cfg["brand"]["name"]), html.escape(kit.cfg["brand"]["name"]), "".join(rows)))
    out = kit.root / "review.html"
    out.write_text(page, encoding="utf-8")
    print("wrote %s" % out)
    return 0


# ---------------------------------------------------------------- train

def train_config(kit, lora, args):
    model = args.model or kit.model
    if model not in MODELS:
        sys.exit("unknown model %r (known: %s)" % (model, ", ".join(MODELS)))
    spec = MODELS[model]
    d = kit.root / "dataset" / lora
    n = len(list(d.glob("*.png")))
    if n == 0:
        sys.exit("dataset/%s is empty: run prep" % lora)
    steps = args.steps or min(1500, max(400, 5 * n))  # about 5 passes; the first real run peaked at 3 (L-001)
    name = "%s-%s-%s" % (re.sub(r"[^a-z0-9]+", "", kit.cfg["brand"]["name"].lower())[:16] or "brand", lora, model)
    mdl = json.loads(json.dumps(spec["model"]))
    net = {"type": "lora", "linear": args.rank, "linear_alpha": args.rank}
    mode = "single"
    if lora != "brand":
        mode = args.mode or ("residual" if spec["residual"] else "continue")
        brand_lora = Path(args.brand_lora) if args.brand_lora else (kit.root / "loras" / ("brand-%s.safetensors" % model))
        if mode in ("residual", "continue") and not brand_lora.is_file():
            sys.exit("mode %s needs the brand LoRA first: train and `pick` it (looked for %s), or pass --brand-lora, "
                     "or use --mode stack" % (mode, brand_lora))
        if mode == "residual":
            if not spec["residual"]:
                sys.exit("%s cannot merge a LoRA during training in ai-toolkit; use --mode continue or stack" % model)
            mdl["assistant_lora_path"] = str(brand_lora)
        elif mode == "continue":
            net["pretrained_lora_path"] = str(brand_lora)
    trig = kit.triggers(lora)
    # Residual samples leave the brand LoRA out (train L-005) and cost about 2 min a picture: fewer, later, no step 0.
    residual = mode == "residual"
    n_samples = args.samples if args.samples is not None else (2 if residual else 4)
    every = args.sample_every or (200 if residual else args.save_every)
    prompts = ["%s, %s" % (trig, p) for p in HELD_OUT[: max(1, n_samples)]]
    proc = {
        "type": "sd_trainer", "training_folder": str(kit.root / "train" / "out"), "device": "cuda:0",
        "trigger_word": trig.split()[-1], "network": net,
        "save": {"dtype": "float16", "save_every": args.save_every, "max_step_saves_to_keep": 20},
        "datasets": [{"folder_path": str(d), "caption_ext": "txt", "caption_dropout_rate": 0.05, "shuffle_tokens": False,
                      "cache_latents_to_disk": True, "resolution": args.res}],
        "train": {"batch_size": 1, "steps": steps, "gradient_accumulation": 1, "train_unet": True, "train_text_encoder": False,
                  "gradient_checkpointing": True, "noise_scheduler": "flowmatch", "optimizer": "adamw8bit", "lr": args.lr,
                  "timestep_type": spec["timestep_type"], "dtype": "bf16",
                  "cache_text_embeddings": bool(spec.get("cache_text_embeddings")),
                  "skip_first_sample": residual, "disable_sampling": n_samples == 0},
        "model": mdl,
        "sample": {"sampler": "flowmatch", "sample_every": every, "width": 1024, "height": 768,
                   "prompts": prompts, "neg": "", "seed": 42, "walk_seed": False, **spec["sample"]},
    }
    cfg = {"job": "extension", "config": {"name": name, "process": [proc]},
           "meta": {"name": "[name]", "version": "1.0", "brandwright": {"lora": lora, "model": model, "mode": mode,
                                                                        "images": n, "trigger": trig}}}
    return name, cfg, steps, mode, n


def export_config(kit, name, cfg, args):
    """Write the same LoRA job for musubi-tuner (dataset TOML + train.sh) or OneTrainer (config + concepts JSON)."""
    meta, proc = cfg["meta"]["brandwright"], cfg["config"]["process"][0]
    model, mode, steps, data = meta["model"], meta["mode"], proc["train"]["steps"], Path(proc["datasets"][0]["folder_path"])
    net = proc["network"]
    brand = proc["model"].get("assistant_lora_path") or net.get("pretrained_lora_path")
    out = kit.root / "train" / ("%s-%s" % (name, args.trainer))
    out.mkdir(parents=True, exist_ok=True)
    if args.trainer == "musubi":
        pre, module, te_flags, ts = MUSUBI[model]
        toml = ['[general]', 'caption_extension = ".txt"', 'batch_size = 1', 'enable_bucket = true', '']
        for r in args.res:  # one dataset per resolution, each with its own cache folder (musubi dataset_config.md)
            toml += ['[[datasets]]', 'resolution = [%d, %d]' % (r, r), 'image_directory = "%s"' % data.as_posix(),
                     'cache_directory = "%s"' % (out / ("cache_%d" % r)).as_posix(), 'num_repeats = 1', '']
        (out / "dataset.toml").write_text("\n".join(toml), encoding="utf-8")
        ver = " --model_version klein-base-4b" if model == "klein4b" else ""
        base = (['"$TURBO_ADAPTER"'] if model == "zimage_turbo" else []) + (['"%s"' % Path(brand).as_posix()] if mode == "residual" else [])
        extra = (" --base_weights %s --base_weights_multiplier %s" % (" ".join(base), " ".join(["1.0"] * len(base)))) if base else ""
        if mode == "continue":
            extra += ' --network_weights "%s"' % Path(brand).as_posix()
        s = "src/musubi_tuner/%s_" % pre
        sh = ["#!/usr/bin/env bash", "# musubi-tuner job written by brandwright %s. Run from the musubi-tuner folder after "
              "setting the model files below (see its docs/%s.md)." % (VERSION, "flux_2" if pre == "flux_2" else pre),
              "set -euo pipefail", 'DIT="path/to/dit.safetensors"', 'VAE="path/to/vae.safetensors"',
              'TEXT_ENCODER="path/to/text_encoder.safetensors"']
        if model == "zimage_turbo":
            sh.append('TURBO_ADAPTER="path/to/zimage_turbo_training_adapter_v2.safetensors"')
        sh += ['TOML="%s"' % (out / "dataset.toml").as_posix(),
               'python %scache_latents.py --dataset_config "$TOML" --vae "$VAE"%s' % (s, ver),
               'python %scache_text_encoder_outputs.py --dataset_config "$TOML" --text_encoder "$TEXT_ENCODER" --batch_size 16 %s'
               % (s, te_flags),
               'accelerate launch --num_cpu_threads_per_process 1 --mixed_precision bf16 %strain_network.py --dit "$DIT" '
               '--vae "$VAE" --text_encoder "$TEXT_ENCODER" --dataset_config "$TOML" --sdpa --mixed_precision bf16 %s '
               '--optimizer_type adamw8bit --learning_rate %g --gradient_checkpointing --network_module networks.%s '
               '--network_dim %d --network_alpha %d --fp8_base --fp8_scaled %s --max_data_loader_n_workers 2 '
               '--persistent_data_loader_workers --max_train_steps %d --save_every_n_steps %d --seed 42 --output_dir "%s" '
               '--output_name %s%s' % (s, ts, args.lr, module, net["linear"], net["linear_alpha"], te_flags, steps,
                                       args.save_every, (out / "output").as_posix(), name, extra)]
        if model == "zimage":
            sh.append("# for ComfyUI: python src/musubi_tuner/convert_lora.py --input IN.safetensors --output OUT.safetensors --target other")
        (out / "train.sh").write_text("\n".join(sh) + "\n", encoding="utf-8")
        files = ["dataset.toml", "train.sh"]
    else:
        if mode == "residual":
            sys.exit("OneTrainer cannot merge a LoRA during training; use --mode continue or stack with --for onetrainer")
        mtype, layers, preset = ONETRAINER[model]
        concepts = [{"name": name, "path": str(data), "enabled": True, "include_subdirectories": False, "balancing": 1.0,
                     "balancing_strategy": "REPEATS", "text": {"prompt_source": "sample"}}]
        (out / "concepts.json").write_text(json.dumps(concepts, indent=2), encoding="utf-8")
        n = max(1, meta["images"])
        oc = {"__version": 11,  # without it train.py migrates the file and migration 8 empties the transformer block
              "model_type": mtype, "training_method": "LORA", "base_model_name": MODELS[model]["model"]["name_or_path"],
              "output_model_destination": str(out / "output" / (name + ".safetensors")), "output_model_format": "DIFFUSERS_LORA",
              "output_dtype": "BFLOAT_16", "train_dtype": "BFLOAT_16", "resolution": ",".join(str(r) for r in args.res),
              "aspect_ratio_bucketing": True, "epochs": -(-steps // n), "batch_size": 1, "learning_rate": args.lr,
              "optimizer": {"optimizer": "ADAMW_8BIT"}, "lora_rank": net["linear"], "lora_alpha": float(net["linear_alpha"]),
              "transformer": {"train": True, "weight_dtype": "FLOAT_8", "gradient_checkpointing": True},
              "text_encoder": {"train": False, "weight_dtype": "FLOAT_8"}, "vae": {"weight_dtype": "FLOAT_32"},
              "layer_filter": layers, "layer_filter_preset": preset, "layer_filter_regex": layers.startswith("^"),
              "timestep_distribution": "LOGIT_NORMAL", "save_every": args.save_every, "save_every_unit": "STEP",
              "concept_file_name": str(out / "concepts.json"), "workspace_dir": str(out / "workspace"),
              "cache_dir": str(out / "cache")}
        if model == "zimage_turbo":
            oc["transformer"]["model_name"] = DETURBO
        if mode == "continue":
            oc["lora_model_name"] = str(brand)
        (out / "config.json").write_text(json.dumps(oc, indent=2), encoding="utf-8")
        files = ["config.json", "concepts.json"]
    print("%s job for the %s LoRA (%s, mode %s, %d steps) in %s: %s" % (args.trainer, meta["lora"], model, mode, steps, out,
                                                                       ", ".join(files)))
    print("  run: bash train.sh (set the model paths at its top first)" if args.trainer == "musubi" else
          "  run: python scripts/train.py --config-path \"%s\"  (from the OneTrainer folder; it trains by epochs: %d)"
          % (out / "config.json", -(-steps // max(1, meta["images"]))))
    return 0


def set_aside_old_run(out):
    """ai-toolkit resumes from any checkpoint already in its run folder, so a retrain under the same name would
    continue the old run (brandwright-train L-003). Move an earlier run's folder aside; returns the new path or None."""
    if not out.is_dir() or not any(out.glob("*.safetensors")):
        return None
    stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(max(p.stat().st_mtime for p in out.glob("*.safetensors"))))
    dest = out.with_name("%s-run-%s" % (out.name, stamp))
    n = 2
    while dest.exists():
        dest = out.with_name("%s-run-%s-%d" % (out.name, stamp, n))
        n += 1
    out.rename(dest)
    return dest


def cmd_train(args):
    kit = Kit(args.kit)
    name, cfg, steps, mode, n = train_config(kit, args.lora, args)
    if args.trainer != "ai-toolkit":
        if args.run:
            sys.exit("--run starts ai-toolkit only; run the %s job with its own command" % args.trainer)
        return export_config(kit, name, cfg, args)
    tdir = kit.root / "train"
    tdir.mkdir(parents=True, exist_ok=True)
    path = tdir / ("%s.json" % name)
    path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    spec = MODELS[args.model or kit.model]
    print("config %s\n  %s LoRA on %s (%s), %d images, %d steps, rank %d, lr %g, mode %s"
          % (path, args.lora, spec["label"], spec["licence"], n, steps, args.rank, args.lr, mode))
    tr, sm = cfg["config"]["process"][0]["train"], cfg["config"]["process"][0]["sample"]
    samples = "no samples" if tr["disable_sampling"] else "%d sample prompts every %d steps%s" % (
        len(sm["prompts"]), sm["sample_every"], ", none at step 0" if tr["skip_first_sample"] else "")
    print("  needs about %d GB of GPU memory; checkpoints every %d steps, %s, under train/out/%s"
          % (spec["vram"], args.save_every, samples, name))
    if not args.run:
        print("not started: add --run to start it here, or run on the training machine:\n  python run.py \"%s\"  (from the ai-toolkit folder)" % path)
        return 0
    tk = find_toolkit(args, kit)
    if not tk:
        sys.exit("ai-toolkit not found: pass --toolkit PATH or set BRANDWRIGHT_AI_TOOLKIT")
    if not args.resume:
        old = set_aside_old_run(tdir / "out" / name)
        if old:
            print("  an earlier run's checkpoints were moved to %s (pass --resume to continue that run instead)" % old)
    log = tdir / ("%s.log" % name)
    py = toolkit_python(tk)
    kw = {"cwd": str(tk), "stdout": log.open("w", encoding="utf-8"), "stderr": subprocess.STDOUT, "stdin": subprocess.DEVNULL}
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    if args.wait:  # block until training ends (for job runners that must know when the GPU is free)
        code = subprocess.call([py, "run.py", str(path)], env=env, **kw)
        print("training ended with exit code %d; log %s" % (code, log))
        return code
    if os.name == "nt":
        kw["creationflags"] = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    p = subprocess.Popen([py, "run.py", str(path)], env=env, **kw)
    (tdir / ("%s.pid" % name)).write_text(str(p.pid), encoding="utf-8")
    print("started pid %d; log %s\n  progress: bw.py status %s" % (p.pid, log, args.kit))
    return 0


STEP_RE = re.compile(r"(\d+)/(\d+) \[")


def cmd_status(args):
    kit = Kit(args.kit)
    tdir = kit.root / "train"
    if not tdir.is_dir():
        print("nothing trained yet")
        return 0
    for cfg_path in sorted(tdir.glob("*.json")):
        name = cfg_path.stem
        log = tdir / (name + ".log")
        out = tdir / "out" / name
        step, total, last = None, None, ""
        if log.is_file():
            text = log.read_text(encoding="utf-8", errors="replace")[-20000:]
            m = STEP_RE.findall(text)
            if m:
                step, total = m[-1]
            lines = [l for l in re.split(r"[\r\n]+", text) if l.strip()]
            last = lines[-1][-160:] if lines else ""
        ckpts = sorted(out.glob("*.safetensors")) if out.is_dir() else []
        samples = sorted((out / "samples").glob("*")) if (out / "samples").is_dir() else []
        pidf = tdir / (name + ".pid")
        alive = " pid %s" % pidf.read_text().strip() if pidf.is_file() else ""
        print("%s%s\n  step %s/%s  checkpoints %d  samples %d\n  last: %s" % (name, alive, step or "?", total or "?", len(ckpts),
                                                                             len(samples), last))
        if ckpts:
            print("  newest checkpoint: %s" % ckpts[-1].name)
        if samples:
            print("  newest sample: %s" % samples[-1])
    return 0


def cmd_pick(args):
    kit = Kit(args.kit)
    model = args.model or kit.model
    name = "%s-%s-%s" % (re.sub(r"[^a-z0-9]+", "", kit.cfg["brand"]["name"].lower())[:16] or "brand", args.lora, model)
    out = kit.root / "train" / "out" / name
    if args.step:
        cands = [p for p in out.glob("*.safetensors") if p.stem.endswith("_%09d" % args.step)]
    else:
        cands = [out / (name + ".safetensors")] if (out / (name + ".safetensors")).is_file() else sorted(out.glob("*.safetensors"))[-1:]
    if not cands:
        sys.exit("no checkpoint found in %s%s" % (out, " for step %d" % args.step if args.step else ""))
    src = cands[0]
    dest_dir = kit.root / "loras"
    dest_dir.mkdir(exist_ok=True)
    dest = dest_dir / ("%s-%s.safetensors" % (args.lora, model))
    shutil.copy2(src, dest)
    print("picked %s -> %s" % (src.name, dest))
    comfy_dir = args.to or os.environ.get("BRANDWRIGHT_COMFY_LORAS")
    if comfy_dir:
        stem = "%s-%s" % (re.sub(r"[^a-z0-9]+", "", kit.cfg["brand"]["name"].lower()), args.lora)
        target = Path(comfy_dir) / (stem + ".safetensors")
        try:
            shutil.copy2(src, target)
        except OSError as e:  # Windows: a running ComfyUI keeps a loaded LoRA memory-mapped, so it cannot be overwritten
            m = re.search(r"_(\d{9})$", src.stem)
            target = Path(comfy_dir) / ("%s-%s.safetensors" % (stem, "s%d" % int(m.group(1)) if m else time.strftime("%Y%m%d%H%M%S")))
            print("could not replace %s.safetensors (%s); using %s" % (stem, e.strerror or e, target.name))
            shutil.copy2(src, target)
        print("copied for ComfyUI -> %s" % target)
        kit.cfg.setdefault("comfy_loras", {})[args.lora] = target.name
    kit.cfg.setdefault("picked", {})[args.lora] = {"file": str(dest), "from": src.name, "model": model,
                                                    "date": time.strftime("%Y-%m-%d")}
    kit.save()
    return 0


# ---------------------------------------------------------------- score and sheet

def brand_palette(kit):
    tp = kit.root / "tokens.json"
    if not tp.is_file():
        sys.exit("no tokens.json: run tokens first")
    t = json.loads(tp.read_text(encoding="utf-8"))["brand"]
    cols = [t["color"][k]["$value"] for k in ("background", "text", "primary")]
    cols += [v["$value"] for k, v in t["palette"].items() if not k.startswith("$")]
    return [parse_color(c) for c in cols if parse_color(c)]


def palette_score(Image, path, pal):
    """Pixel-weighted delta-E from each of the picture's main colours to the nearest brand colour, and the share of
    pixels more than 15 delta-E from every brand colour (off-palette). Rough: photos and illustrations score worse."""
    im = Image.open(path).convert("RGB")
    im.thumbnail((256, 256))
    q = im.quantize(colors=12, method=Image.Quantize.MEDIANCUT)
    p = q.getpalette()
    counts = sorted(q.getcolors(), reverse=True)
    total = sum(c for c, _ in counts)
    de, off = 0.0, 0.0
    for c, idx in counts:
        rgb = tuple(p[idx * 3: idx * 3 + 3])
        d = min(delta_e(rgb, b) for b in pal)
        de += d * c / total
        if d > 15:
            off += c / total
    return de, off


def cmd_score(args):
    Image = need_pil()
    kit = Kit(args.kit)
    pal = brand_palette(kit)
    rows = [(*palette_score(Image, p, pal), p) for f in args.images
            for p in (sorted(Path(f).glob("*.png")) + sorted(Path(f).glob("*.jpg")) if Path(f).is_dir() else [Path(f)])]
    for de, off, p in sorted(rows):
        print("%6.1f dE  %5.1f%% off-palette  %s" % (de, off * 100, p))
    if args.json:
        Path(args.json).write_text(json.dumps([{"file": str(p), "delta_e": round(de, 2), "off_palette": round(off, 3)}
                                               for de, off, p in rows], indent=2), encoding="utf-8")
    return 0


def contact_sheet(Image, paths, out, cols=4, cell=384, labels=None):
    from PIL import ImageDraw
    rows = math.ceil(len(paths) / cols)
    ratio = max(Image.open(p).size[1] / Image.open(p).size[0] for p in paths)  # wide pictures get short cells
    cell_h = max(64, int(cell * min(1.0, ratio)))
    sheet = Image.new("RGB", (cols * cell, rows * (cell_h + 22)), "white")
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB")
        im.thumbnail((cell, cell_h))
        x, y = (i % cols) * cell, (i // cols) * (cell_h + 22)
        sheet.paste(im, (x + (cell - im.size[0]) // 2, y))
        d.text((x + 4, y + cell_h + 4), (labels[i] if labels else Path(p).stem)[:60], fill="black")
    sheet.save(out, quality=88)
    return out


def cmd_sheet(args):
    Image = need_pil()
    paths = [q for p in map(Path, args.images)
             for q in (sorted(x for x in p.iterdir() if x.suffix.lower() in IMG_EXT) if p.is_dir() else [p])]
    if not paths:
        sys.exit("no images")
    print("wrote %s" % contact_sheet(Image, paths, args.out, cols=args.cols))
    return 0


# ---------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(prog="bw.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def kit_cmd(name, help, site=False):
        p = sub.add_parser(name, help=help)
        p.add_argument("kit", help="kit folder (made by new)")
        if site:
            p.add_argument("--site", required=True, help="site name in brand.json")
        return p

    p = sub.add_parser("doctor", help="what is installed: Pillow, Playwright, GPU, ai-toolkit, ComfyUI, Ollama")
    p.add_argument("--comfy", action="append", help="ComfyUI URL to check (repeat; default BRANDWRIGHT_COMFY or :8188)")
    p.add_argument("--toolkit", help="ostris ai-toolkit folder (or set BRANDWRIGHT_AI_TOOLKIT)")

    p = sub.add_parser("new", help="create a kit, or add sites to one")
    p.add_argument("kit", help="kit folder to create or extend (keep it outside any repository)")
    p.add_argument("--brand", help="brand name (needed for a new kit)")
    p.add_argument("--trigger", help="brand trigger word (default: brand name + 'ui')")
    p.add_argument("--site", action="append", help="NAME or NAME=URL; repeat for more sites")
    p.add_argument("--model", default=DEFAULT_MODEL, choices=sorted(MODELS), help="base model to train on (default zimage)")

    p = kit_cmd("login", "open a browser window to sign in yourself; the session is kept in the kit", site=True)
    p.add_argument("url", help="page to open for signing in")
    p.add_argument("--channel", help="msedge or chrome: use the installed browser")

    p = kit_cmd("capture", "screenshot pages (with masks), component boxes and design tokens", site=True)
    p.add_argument("urls", nargs="*", help="pages to capture (default: the site's urls in brand.json)")
    p.add_argument("--crawl", type=int, default=0, help="also visit up to N same-site links found on the pages")
    p.add_argument("--crawl-all", action="store_true", help="also crawl cookie, privacy, terms and sitemap pages")
    p.add_argument("--viewports", default="desktop,mobile")
    p.add_argument("--channel")
    p.add_argument("--cdp", help="attach to a running browser started with --remote-debugging-port (e.g. http://127.0.0.1:9222)")
    p.add_argument("--hide", action="append", help="CSS selector to hide before capture (repeat)")
    p.add_argument("--blur", action="append", help="CSS selector to blur before capture (repeat); prefer --hide")
    p.add_argument("--click", action="append", help="CSS selector to click before capture (e.g. open a menu)")
    p.add_argument("--no-mask", action="store_true", help="keep e-mail addresses and digit runs as they are (test data only)")
    p.add_argument("--wait", type=int, default=800, help="ms to wait after scrolling")
    p.add_argument("--timeout", type=int, default=45)
    p.add_argument("--max-per-kind", type=int, default=8)

    p = kit_cmd("import", "add your own screenshots (full screens or single components)", site=True)
    p.add_argument("paths", nargs="+", help="image files or folders (png, jpg, webp)")
    p.add_argument("--kind", default="screen", choices=["screen", "component"])
    p.add_argument("--viewport", default="desktop", choices=["desktop", "laptop", "tablet", "mobile", "import"])

    p = kit_cmd("tokens", "merge captured styles into tokens.json (DTCG), brand.css and tokens.md")

    p = kit_cmd("prep", "build dataset/<lora>: tiles, component specimens, dedupe, caps, template captions")
    p.add_argument("--tiles", type=int, default=3, help="viewport tiles per page, from the top")
    p.add_argument("--dedupe", type=int, default=4, help="max hash distance treated as a duplicate (0-64)")
    p.add_argument("--max-per-site", type=int, default=60)
    p.add_argument("--brand-max", type=int, default=90, help="brand dataset size, shared equally across sites")

    p = kit_cmd("caption", "rewrite captions with a local vision model through Ollama")
    p.add_argument("--lora", help="one dataset only (default: all)")
    p.add_argument("--vlm", default="ollama", choices=["ollama", "none"])
    p.add_argument("--model", default=os.environ.get("BRANDWRIGHT_VLM", "qwen3-vl:8b"))
    p.add_argument("--host", help="Ollama URL (default BRANDWRIGHT_OLLAMA or http://127.0.0.1:11434)")
    p.add_argument("--force", action="store_true", help="re-caption pictures that already have a model caption")

    p = kit_cmd("review", "write review.html: every training picture with its caption")

    p = kit_cmd("train", "write an ai-toolkit config for one LoRA (brand or a site); --run starts it")
    p.add_argument("--lora", default="brand", help="brand, or a site name")
    p.add_argument("--model", choices=sorted(MODELS), help="base model (default: the kit's)")
    p.add_argument("--mode", choices=["residual", "continue", "stack"],
                   help="site LoRAs: residual = learn only the difference from the brand LoRA (Z-Image); continue = start "
                        "from the brand LoRA, use alone; stack = independent")
    p.add_argument("--brand-lora", help="brand LoRA file for residual or continue (default: loras/brand-<model>.safetensors)")
    p.add_argument("--steps", type=int, help="default: 5 per picture, 400 to 1,500 (style LoRAs peak early)")
    p.add_argument("--rank", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--res", type=int, nargs="+", default=[768, 1024])
    p.add_argument("--save-every", type=int, default=100, help="checkpoint every N steps")
    p.add_argument("--samples", type=int,
                   help="sample prompts drawn during training; 0 turns sampling off (default: 4, or 2 for residual site LoRAs)")
    p.add_argument("--sample-every", type=int,
                   help="draw samples every N steps (default: --save-every, or 200 for residual site LoRAs, which also "
                        "skip the step-0 sample)")
    p.add_argument("--for", dest="trainer", choices=["ai-toolkit", "musubi", "onetrainer"], default="ai-toolkit",
                   help="write the same job for musubi-tuner (dataset.toml + train.sh) or OneTrainer (config + concepts)")
    p.add_argument("--toolkit", help="ostris ai-toolkit folder (or BRANDWRIGHT_AI_TOOLKIT)")
    p.add_argument("--run",action="store_true", help="start training now, detached; log in train/<name>.log")
    p.add_argument("--wait", action="store_true", help="with --run: block until training ends (for job queues)")
    p.add_argument("--resume", action="store_true",
                   help="with --run: continue the run already in train/out/<name>; without it, that folder is moved aside")

    p = kit_cmd("status", "training progress, checkpoints and samples")

    p = kit_cmd("pick", "copy a checkpoint to loras/ (and to ComfyUI's loras folder with --to)")
    p.add_argument("--lora", default="brand", help="brand, or a site name")
    p.add_argument("--step", type=int, help="checkpoint step (default: the final file)")
    p.add_argument("--model", choices=sorted(MODELS), help="base model (default: the kit's)")
    p.add_argument("--to", help="ComfyUI models/loras folder (or set BRANDWRIGHT_COMFY_LORAS)")

    import bw_comfy  # noqa: E402
    bw_comfy.add_parsers(sub, kit_cmd)

    p = sub.add_parser("render", help="screenshot an HTML mock-up built on brand.css (the code route)")
    p.add_argument("html", help="the mock-up page (link brand.css from it)")
    p.add_argument("--out", help="PNG path (default: next to the HTML)")
    p.add_argument("--width", type=int, default=1440)
    p.add_argument("--height", type=int, default=900)
    p.add_argument("--scale", type=float, default=1)
    p.add_argument("--full", action="store_true")
    p.add_argument("--selector")
    p.add_argument("--dark", action="store_true")
    p.add_argument("--channel")

    p = kit_cmd("score", "palette match of images to the brand tokens (delta-E, off-palette share)")
    p.add_argument("images", nargs="+", help="images or folders")
    p.add_argument("--json", help="also write the scores to this file")

    p = sub.add_parser("sheet", help="contact sheet of images or folders")
    p.add_argument("images", nargs="+", help="images or folders")
    p.add_argument("--out", default="sheet.jpg")
    p.add_argument("--cols", type=int, default=4)

    args = ap.parse_args(argv)
    if args.cmd in ("login", "capture", "render"):
        import bw_browser
        return bw_browser.cmd_render(args) if args.cmd == "render" else getattr(bw_browser, "cmd_" + args.cmd)(args, Kit(args.kit))
    if args.cmd in ("gen", "sweep", "ref"):
        return bw_comfy.run(args, Kit)
    return {"doctor": cmd_doctor, "new": cmd_new, "import": cmd_import, "tokens": cmd_tokens, "prep": cmd_prep,
            "caption": cmd_caption, "review": cmd_review, "train": cmd_train, "status": cmd_status, "pick": cmd_pick,
            "score": cmd_score, "sheet": cmd_sheet}[args.cmd](args)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass
    sys.exit(main())
