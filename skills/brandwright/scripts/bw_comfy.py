"""ComfyUI side of brandwright: generate mock-ups with brand and site LoRAs, sweep their weights, and the
training-free route (FLUX.2 klein with reference screenshots). Standard library only; Pillow for sweep sheets.

Model files are ComfyUI's usual names; override any of them per kit in brand.json under "comfy_models".
"""
import json
import mimetypes
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

# Graph presets: loader files and sampler settings per model family (checked on ComfyUI 2026-10).
GRAPHS = {
    "zimage_turbo": {"kind": "ksampler", "unet": "z_image_turbo_bf16.safetensors", "clip": "qwen_3_4b.safetensors",
                     "clip_type": "lumina2", "vae": "ae.safetensors", "shift": 3.0, "steps": 9, "cfg": 1.0,
                     "sampler": "res_multistep", "scheduler": "simple", "latent": "EmptySD3LatentImage"},
    "zimage": {"kind": "ksampler", "unet": "z_image_bf16.safetensors", "clip": "qwen_3_4b.safetensors",
               "clip_type": "lumina2", "vae": "ae.safetensors", "shift": 3.0, "steps": 30, "cfg": 4.0,
               "sampler": "res_multistep", "scheduler": "simple", "latent": "EmptySD3LatentImage"},
    "klein4b": {"kind": "flux2", "unet": "flux-2-klein-4b.safetensors", "clip": "qwen_3_4b.safetensors", "clip_type": "flux2",
                "vae": "flux2-vae.safetensors", "steps": 4, "cfg": 1.0},
    "klein4b_base": {"kind": "flux2", "unet": "flux-2-klein-base-4b.safetensors", "clip": "qwen_3_4b.safetensors",
                     "clip_type": "flux2", "vae": "flux2-vae.safetensors", "steps": 20, "cfg": 4.0},
    "qwen_image": {"kind": "ksampler", "unet": "qwen_image_2512_fp8_e4m3fn.safetensors",
                   "clip": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "clip_type": "qwen_image", "vae": "qwen_image_vae.safetensors",
                   "shift": 3.1, "steps": 25, "cfg": 2.5, "sampler": "euler", "scheduler": "simple",
                   "latent": "EmptySD3LatentImage"},
}
# Which graph a LoRA trained on each training model runs on by default.
TRAINED_ON = {"zimage": "zimage", "zimage_turbo": "zimage_turbo", "klein4b": "klein4b", "qwen_image": "qwen_image"}

NEGATIVE = "blurry, jpeg artifacts, garbled text, misspelled words, distorted letters, watermark, cropped, low quality"


# ---------------------------------------------------------------- client

class Comfy:
    def __init__(self, base):
        self.base = base.rstrip("/")

    def post(self, path, data):
        req = urllib.request.Request(self.base + path, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())

    def get(self, path, timeout=30):
        with urllib.request.urlopen(self.base + path, timeout=timeout) as r:
            return json.loads(r.read().decode())

    def upload(self, path):
        path = Path(path)
        name = "bw_%s%s" % (uuid.uuid4().hex[:8], path.suffix.lower())
        boundary = "----bw" + uuid.uuid4().hex
        ctype = mimetypes.guess_type(path.name)[0] or "image/png"
        body = (("--%s\r\nContent-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n"
                 % (boundary, name, ctype)).encode() + path.read_bytes() +
                ("\r\n--%s\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--%s--\r\n" % (boundary, boundary)).encode())
        req = urllib.request.Request(self.base + "/upload/image", data=body,
                                     headers={"Content-Type": "multipart/form-data; boundary=" + boundary})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())["name"]

    def run(self, graph, timeout):
        try:
            pid = self.post("/prompt", {"prompt": graph, "client_id": "brandwright"})["prompt_id"]
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:1500]
            sys.exit("ComfyUI refused the graph (%s): %s" % (e.code, detail))
        t0 = time.time()
        while time.time() - t0 < timeout:
            time.sleep(2)
            h = self.get("/history/" + pid).get(pid)
            if not h:
                continue
            st = h.get("status", {})
            if st.get("status_str") == "error":
                msgs = [m for m in st.get("messages", []) if m[0] == "execution_error"]
                sys.exit("ComfyUI error: %s" % (msgs[0][1].get("exception_message", "")[:600] if msgs else st))
            if st.get("completed") or h.get("outputs"):
                return h["outputs"]
        sys.exit("timed out after %d s waiting for ComfyUI (prompt %s is still queued or running)" % (timeout, pid))

    def fetch(self, img, dest):
        q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")})
        with urllib.request.urlopen(self.base + "/view?" + q, timeout=120) as r:
            Path(dest).write_bytes(r.read())
        return dest


# ---------------------------------------------------------------- graphs

def preset(kit, name):
    g = dict(GRAPHS[name])
    g.update(kit.cfg.get("comfy_models", {}).get(name, {}))
    return g


def loaders(g, spec, loras, prefix=""):
    """Loader nodes plus a LoRA chain; returns (model ref, clip ref, vae ref)."""
    g[prefix + "unet"] = {"class_type": "UNETLoader", "inputs": {"unet_name": spec["unet"], "weight_dtype": "default"}}
    g["clip"] = {"class_type": "CLIPLoader", "inputs": {"clip_name": spec["clip"], "type": spec["clip_type"], "device": "default"}}
    g["vae"] = {"class_type": "VAELoader", "inputs": {"vae_name": spec["vae"]}}
    model = [prefix + "unet", 0]
    for i, (fname, w) in enumerate(loras):
        if abs(w) < 1e-6:
            continue
        k = "%slora%d" % (prefix, i)
        g[k] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": model, "lora_name": fname, "strength_model": w}}
        model = [k, 0]
    return model, ["clip", 0], ["vae", 0]


def branch(g, spec, model, clip, vae, prompt, width, height, seed, n, tag, refs=()):
    """One sampling branch ending in a SaveImage node named save_<tag>."""
    g["pos_" + tag] = {"class_type": "CLIPTextEncode", "inputs": {"clip": clip, "text": prompt}}
    if spec["kind"] == "ksampler":
        g["ms_" + tag] = {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": model, "shift": spec["shift"]}}
        if spec["cfg"] > 1.0:
            g["neg_" + tag] = {"class_type": "CLIPTextEncode", "inputs": {"clip": clip, "text": NEGATIVE}}
        else:
            g["neg_" + tag] = {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["pos_" + tag, 0]}}
        g["lat_" + tag] = {"class_type": spec["latent"], "inputs": {"width": width, "height": height, "batch_size": n}}
        g["ks_" + tag] = {"class_type": "KSampler", "inputs": {
            "model": ["ms_" + tag, 0], "positive": ["pos_" + tag, 0], "negative": ["neg_" + tag, 0], "latent_image": ["lat_" + tag, 0],
            "seed": seed, "steps": spec["steps"], "cfg": spec["cfg"], "sampler_name": spec["sampler"], "scheduler": spec["scheduler"],
            "denoise": 1.0}}
        samples = ["ks_" + tag, 0]
    else:  # FLUX.2: CFGGuider + Flux2Scheduler, references as ReferenceLatent on both conditionings
        g["neg_" + tag] = {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["pos_" + tag, 0]}}
        pos, neg = ["pos_" + tag, 0], ["neg_" + tag, 0]
        for i, lat in enumerate(refs):
            g["rp%d_%s" % (i, tag)] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": pos, "latent": lat}}
            g["rn%d_%s" % (i, tag)] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": neg, "latent": lat}}
            pos, neg = ["rp%d_%s" % (i, tag), 0], ["rn%d_%s" % (i, tag), 0]
        g["guide_" + tag] = {"class_type": "CFGGuider", "inputs": {"model": model, "positive": pos, "negative": neg, "cfg": spec["cfg"]}}
        g["sig_" + tag] = {"class_type": "Flux2Scheduler", "inputs": {"steps": spec["steps"], "width": width, "height": height}}
        g["lat_" + tag] = {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": width, "height": height, "batch_size": n}}
        g["noise_" + tag] = {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}}
        g["smp"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}
        g["sca_" + tag] = {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["noise_" + tag, 0], "guider": ["guide_" + tag, 0], "sampler": ["smp", 0], "sigmas": ["sig_" + tag, 0],
            "latent_image": ["lat_" + tag, 0]}}
        samples = ["sca_" + tag, 0]
    g["dec_" + tag] = {"class_type": "VAEDecode", "inputs": {"samples": samples, "vae": vae}}
    g["save_" + tag] = {"class_type": "SaveImage", "inputs": {"images": ["dec_" + tag, 0], "filename_prefix": "brandwright/" + tag}}


# ---------------------------------------------------------------- helpers

def parse_size(s):
    m = re.fullmatch(r"(\d+)x(\d+)", s)
    if not m:
        sys.exit("size must look like 1344x768")
    w, h = int(m.group(1)) // 16 * 16, int(m.group(2)) // 16 * 16
    return w, h


def lora_specs(kit, items):
    """['brand=0.8', 'careers=0.6', 'file.safetensors=0.5'] -> [(comfy file, weight, lora name or None)]."""
    out = []
    for it in items or []:
        name, _, w = it.partition("=")
        w = float(w) if w else 1.0
        fname = kit.cfg.get("comfy_loras", {}).get(name)
        if fname:
            out.append((fname, w, name))
        elif name.endswith(".safetensors"):
            out.append((name, w, None))
        else:
            sys.exit("no ComfyUI file known for LoRA %r: run `bw.py pick %s --lora %s --to <ComfyUI>/models/loras`, "
                     "or pass the file name (name.safetensors=0.8)" % (name, kit.root, name))
    return out


def with_triggers(kit, prompt, named):
    trig = []
    if any(n == "brand" for n in named) or any(n and n != "brand" for n in named):
        trig.append(kit.cfg["brand"]["trigger"])
    for n in named:
        if n and n != "brand":
            trig.append(kit.site(n)["trigger"])
    pre = ", ".join(t for t in trig if t not in prompt)
    return ("%s, %s" % (pre, prompt)) if pre else prompt


def out_dir(kit, prompt):
    d = kit.root / "out" / ("%s-%s" % (time.strftime("%Y%m%d-%H%M%S"), re.sub(r"[^a-z0-9]+", "-", prompt.lower())[:40].strip("-")))
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_outputs(client, outputs, d, meta):
    files = []
    for node, out in sorted(outputs.items()):
        for i, img in enumerate(out.get("images", [])):
            tag = node.replace("save_", "")
            dest = d / ("%s_%02d.png" % (tag, i + 1))
            client.fetch(img, dest)
            files.append(dest)
    (d / "mockup.json").write_text(json.dumps({**meta, "files": [f.name for f in files]}, indent=2), encoding="utf-8")
    return files


def graph_name(kit, args):
    if args.graph:
        return args.graph
    trained = kit.cfg.get("model", "zimage")
    return TRAINED_ON.get(trained, "zimage_turbo")


# ---------------------------------------------------------------- commands

def cmd_gen(args, kit):
    client = Comfy(args.comfy or kit.cfg.get("comfy", "http://127.0.0.1:8188"))
    name = graph_name(kit, args)
    spec = preset(kit, name)
    if args.steps:
        spec["steps"] = args.steps
    if args.cfg is not None:
        spec["cfg"] = args.cfg
    loras = lora_specs(kit, args.lora)
    prompt = with_triggers(kit, args.prompt, [n for _, _, n in loras]) if not args.raw else args.prompt
    w, h = parse_size(args.size)
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)
    g = {}
    model, clip, vae = loaders(g, spec, [(f, wt) for f, wt, _ in loras])
    branch(g, spec, model, clip, vae, prompt, w, h, seed, args.n, "mock")
    d = out_dir(kit, args.prompt)
    t0 = time.time()
    outputs = client.run(g, args.timeout)
    files = save_outputs(client, outputs, d, {"prompt": prompt, "graph": name, "loras": [[f, wt] for f, wt, _ in loras],
                                              "size": [w, h], "seed": seed, "steps": spec["steps"], "cfg": spec["cfg"]})
    print("%d mock-up(s) in %.0f s -> %s" % (len(files), time.time() - t0, d))
    for f in files:
        print("  %s" % f)
    return 0


def frange(text):
    """'0.4,0.7,1.0' or '0.4:1.0:0.3' -> list of floats."""
    if ":" in text:
        a, b, s = (float(x) for x in text.split(":"))
        out, v = [], a
        while v <= b + 1e-9:
            out.append(round(v, 3))
            v += s
        return out
    return [float(x) for x in text.split(",")]


def cmd_sweep(args, kit):
    client = Comfy(args.comfy or kit.cfg.get("comfy", "http://127.0.0.1:8188"))
    name = graph_name(kit, args)
    spec = preset(kit, name)
    a = lora_specs(kit, [args.a])[0]
    b = lora_specs(kit, [args.b])[0] if args.b else None
    prompt = with_triggers(kit, args.prompt, [a[2]] + ([b[2]] if b else []))
    w, h = parse_size(args.size)
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)
    wa, wb = frange(args.wa), (frange(args.wb) if b else [0.0])
    d = out_dir(kit, "sweep-" + args.prompt)
    cells = []
    for i, x in enumerate(wa):
        for j, y in enumerate(wb):
            g = {}
            chain = [(a[0], x)] + ([(b[0], y)] if b else [])
            model, clip, vae = loaders(g, spec, chain)
            tag = "a%.2f_b%.2f" % (x, y)
            branch(g, spec, model, clip, vae, prompt, w, h, seed, 1, tag.replace(".", "p"))
            outputs = client.run(g, args.timeout)
            files = save_outputs(client, outputs, d, {"prompt": prompt, "graph": name, "a": [a[0], x], "b": [b[0], y] if b else None,
                                                      "seed": seed})
            cells.append((files[0], "%s %.2f%s" % (a[2] or "a", x, (" / %s %.2f" % (b[2] or "b", y)) if b else "")))
            print("  %s" % cells[-1][1])
    try:
        from PIL import Image
        import bw
        bw.contact_sheet(Image, [c[0] for c in cells], d / "sweep.jpg", cols=len(wb), labels=[c[1] for c in cells])
        print("sheet -> %s (rows: %s weight, columns: %s weight)" % (d / "sweep.jpg", a[2] or "a", (b[2] or "b") if b else "-"))
    except ImportError:
        print("Pillow missing: no contact sheet; images are in %s" % d)
    (d / "sweep.json").write_text(json.dumps({"prompt": prompt, "seed": seed, "cells": [[str(c[0].name), c[1]] for c in cells]}, indent=2),
                                  encoding="utf-8")
    return 0


def cmd_ref(args, kit):
    """Training-free: FLUX.2 klein with up to four reference screenshots of the brand."""
    client = Comfy(args.comfy or kit.cfg.get("comfy", "http://127.0.0.1:8188"))
    name = args.graph or "klein4b"
    spec = preset(kit, name)
    if spec["kind"] != "flux2":
        sys.exit("ref needs a FLUX.2 graph (klein4b or klein4b_base)")
    refs = args.refs[:4]
    if len(args.refs) > 4:
        print("klein takes up to 4 references; using the first 4")
    w, h = parse_size(args.size)
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)
    loras = lora_specs(kit, args.lora)
    g = {}
    model, clip, vae = loaders(g, spec, [(f, wt) for f, wt, _ in loras])
    lats = []
    for i, r in enumerate(refs):
        up = client.upload(r)
        g["ld%d" % i] = {"class_type": "LoadImage", "inputs": {"image": up}}
        g["sc%d" % i] = {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": ["ld%d" % i, 0], "upscale_method": "lanczos",
                                                                           "megapixels": 1.0, "resolution_steps": 16}}
        g["en%d" % i] = {"class_type": "VAEEncode", "inputs": {"pixels": ["sc%d" % i, 0], "vae": vae}}
        lats.append(["en%d" % i, 0])
    prompt = args.prompt
    if not args.raw:
        prompt = ("%s. Use the exact visual style of the reference screenshots: the same colours, typeface, corner radius, "
                  "spacing, iconography and button style. Do not copy their content or layout. Crisp, legible interface text."
                  % args.prompt)
    branch(g, spec, model, clip, vae, prompt, w, h, seed, args.n, "ref", refs=lats)
    d = out_dir(kit, "ref-" + args.prompt)
    t0 = time.time()
    outputs = client.run(g, args.timeout)
    files = save_outputs(client, outputs, d, {"prompt": prompt, "graph": name, "refs": [str(r) for r in refs], "size": [w, h],
                                              "seed": seed})
    print("%d mock-up(s) in %.0f s -> %s" % (len(files), time.time() - t0, d))
    for f in files:
        print("  %s" % f)
    return 0


def add_parsers(sub):
    def common(p):
        p.add_argument("--comfy", help="ComfyUI URL (default: brand.json comfy, or BRANDWRIGHT_COMFY)")
        p.add_argument("--graph", choices=sorted(GRAPHS), help="model graph (default: the kit's training model)")
        p.add_argument("--size", default="1344x768")
        p.add_argument("--seed", type=int)
        p.add_argument("--timeout", type=int, default=900)

    p = sub.add_parser("gen", help="mock-ups with the kit's LoRAs through ComfyUI")
    p.add_argument("kit")
    p.add_argument("prompt")
    p.add_argument("--lora", action="append", help="NAME=WEIGHT (brand=0.8, a site name, or file.safetensors=0.6); repeat")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--steps", type=int)
    p.add_argument("--cfg", type=float)
    p.add_argument("--raw", action="store_true", help="do not add trigger words")
    common(p)

    p = sub.add_parser("sweep", help="grid of LoRA weights on one prompt and seed, with a contact sheet")
    p.add_argument("kit")
    p.add_argument("prompt")
    p.add_argument("--a", required=True, help="first LoRA name (e.g. brand)")
    p.add_argument("--b", help="second LoRA name (e.g. a site)")
    p.add_argument("--wa", default="0.4,0.7,1.0")
    p.add_argument("--wb", default="0.4,0.7,1.0")
    common(p)

    p = sub.add_parser("ref", help="training-free: FLUX.2 klein with up to 4 reference screenshots")
    p.add_argument("kit")
    p.add_argument("prompt")
    p.add_argument("--refs", nargs="+", required=True)
    p.add_argument("--lora", action="append")
    p.add_argument("--n", type=int, default=2)
    p.add_argument("--raw", action="store_true", help="send the prompt as written")
    common(p)


def run(args, Kit):
    kit = Kit(args.kit)
    return {"gen": cmd_gen, "sweep": cmd_sweep, "ref": cmd_ref}[args.cmd](args, kit)
