"""Offline tests for brandwright's CLI. Run from the repository root: python tests/test_bw.py

No network, no GPU, no browser: kits, captures and token files are synthetic. Pillow is needed for the dataset
tests (they skip without it). The browser smoke test is tests/smoke_browser.py.
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "brandwright" / "scripts"))
import bw  # noqa: E402
import bw_comfy  # noqa: E402

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = bw.main(list(argv))
    return code, out.getvalue()


class KitCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="bwtest"))
        self.kit = self.tmp / "kit"
        run("new", str(self.kit), "--brand", "Northwind", "--site", "shop=https://shop.example/", "--site", "careers")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def cfg(self):
        return json.loads((self.kit / "brand.json").read_text(encoding="utf-8"))


class TestKit(KitCase):
    def test_new_writes_private_kit(self):
        cfg = self.cfg()
        self.assertEqual(cfg["brand"]["trigger"], "northwindui")
        self.assertEqual([s["name"] for s in cfg["sites"]], ["shop", "careers"])
        self.assertEqual(cfg["sites"][0]["urls"], ["https://shop.example/"])
        self.assertEqual((self.kit / ".gitignore").read_text(encoding="utf-8").splitlines()[-1], "*")
        self.assertEqual(cfg["model"], "zimage")

    def test_new_adds_sites_without_duplicates(self):
        run("new", str(self.kit), "--site", "shop", "--site", "help")
        self.assertEqual([s["name"] for s in self.cfg()["sites"]], ["shop", "careers", "help"])

    def test_site_triggers_carry_brand_trigger(self):
        k = bw.Kit(self.kit)
        self.assertEqual(k.triggers("brand"), "northwindui")
        self.assertTrue(k.triggers("shop").startswith("northwindui "))
        self.assertEqual([l for l, _, _ in k.loras()], ["brand", "shop", "careers"])

    def test_unknown_site_exits(self):
        with self.assertRaises(SystemExit):
            bw.Kit(self.kit).site("nope")


class TestColour(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(bw.parse_color("#1d70b8"), (29, 112, 184))
        self.assertEqual(bw.parse_color("rgb(1, 2, 3)"), (1, 2, 3))
        self.assertEqual(bw.parse_color("rgba(1, 2, 3, 0.5)"), (1, 2, 3))
        self.assertIsNone(bw.parse_color("rgba(0, 0, 0, 0)"))
        self.assertIsNone(bw.parse_color("#00000000"))
        self.assertIsNone(bw.parse_color("oklch(0.5 0.1 200)"))

    def test_delta_e(self):
        self.assertLess(bw.delta_e((255, 255, 255), (254, 254, 254)), 1)
        self.assertGreater(bw.delta_e((255, 0, 0), (0, 0, 255)), 100)


def token_file(path, primary="#0b6e4f", font="Georgia"):
    tok = {"tally": {"color": {"#1d2a30": 900, "#ffffff": 200}, "background": {"#fbf8f2": 90000, primary: 30000, "#ffffff": 20000},
                     "border": {"#d8d2c4": 400}, "font": {font: 800, "ui-monospace": 300, "Verdana": 200},
                     "size": {"16px": 500, "44px": 20}, "weight": {"400": 600}, "lineheight": {"normal": 600},
                     "radius": {"10px": 12}, "shadow": {"rgba(0, 0, 0, 0.12) 0px 2px 8px 0px": 3}, "space": {"24px": 30, "48px": 10}},
           "vars": {"--nw-brand": primary}, "fonts": [],
           "recipes": {"button": [{"color": "#1d2a30", "backgroundColor": "transparent", "fontFamily": "Verdana"}] * 3
                                 + [{"color": "#1d2a30", "backgroundColor": "#f2a541", "fontFamily": "Verdana"}] * 2,
                       "footer": [{"color": "#cfd8dc", "backgroundColor": "#1d2a30", "fontFamily": "Times New Roman"}]}}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tok), encoding="utf-8")


class TestTokens(KitCase):
    def test_tokens_css_and_overrides(self):
        token_file(self.kit / "capture" / "shop" / "tokens" / "home__desktop.json")
        token_file(self.kit / "capture" / "careers" / "tokens" / "home__desktop.json", primary="#7a1f5c")
        code, out = run("tokens", str(self.kit))
        self.assertEqual(code, 0)
        t = json.loads((self.kit / "tokens.json").read_text(encoding="utf-8"))
        self.assertIn("shop", t["sites"])
        self.assertEqual(t["sites"]["careers"]["color"]["primary"]["$value"], "#7a1f5c")
        fams = t["brand"]["font"]["family"]
        self.assertEqual(fams["f1"]["$value"], "Georgia")
        self.assertEqual(fams["mono"]["$value"], "ui-monospace")
        css = (self.kit / "brand.css").read_text(encoding="utf-8")
        self.assertIn("--nw-brand", css)
        self.assertIn(".bw-button-primary {", css)
        self.assertIn("#f2a541", css.split(".bw-button-primary {")[1].split("}")[0])
        self.assertIn('[data-site="careers"]', css)
        self.assertNotIn("Times New Roman", css)  # a recipe font that is not a main family is dropped

    def test_browser_default_button_is_not_the_primary(self):
        plain = {"backgroundColor": "rgba(0, 0, 0, 0)", "color": "#0b0c0c", "fontSize": "16px"}
        unstyled = {"backgroundColor": "#d2e2f1", "color": "#1d70b8", "fontFamily": "Arial", "fontSize": "13.3333px"}
        self.assertNotIn("button primary", bw.recipe_set({"button": [plain, plain, unstyled]}, ["Georgia"]))
        cta = {"backgroundColor": "#00703c", "color": "#ffffff", "fontSize": "19px"}
        self.assertEqual(bw.recipe_set({"button": [plain, unstyled, cta]}, ["Georgia"])["button primary"]["backgroundColor"],
                         "#00703c")

    def test_tokens_without_captures_exits(self):
        with self.assertRaises(SystemExit):
            run("tokens", str(self.kit))


@unittest.skipIf(Image is None, "Pillow not installed")
class TestPrep(KitCase):
    def capture(self, site, pages=2):
        base = self.kit / "capture" / site
        (base / "pages").mkdir(parents=True, exist_ok=True)
        with (base / "capture.jsonl").open("w", encoding="utf-8") as f:
            for p in range(pages):
                im = Image.new("RGB", (1440, 2400), "#fbf8f2")
                d = ImageDraw.Draw(im)
                d.rectangle([0, 0, 1440, 80], fill="#0b6e4f")
                for i in range(30):
                    x0 = 60 + (i * 37 + p * 101) % 900
                    d.rectangle([x0, 120 + i * 70, x0 + 120 + (i * 53) % 400, 160 + i * 70], fill=(i * 8 % 255, 90, 160))
                d.rectangle([100, 1000, 400, 1260], fill="#ffffff", outline="#d8d2c4")
                d.rectangle([140, 1200, 300, 1240], fill="#f2a541")
                name = "page%d__desktop.png" % p
                im.save(base / "pages" / name)
                comps = [{"kind": "header", "box": {"x": 0, "y": 0, "w": 1440, "h": 80}, "text": "Northwind Shop Trips Help"},
                         {"kind": "card", "box": {"x": 100, "y": 1000, "w": 300, "h": 260}, "text": "Ridge 45 pack Add to basket"},
                         {"kind": "button", "box": {"x": 140, "y": 1200, "w": 160, "h": 40}, "text": "Add to basket"}]
                f.write(json.dumps({"file": "pages/" + name, "site": site, "viewport": "desktop", "dsf": 1, "bg": "#fbf8f2",
                                    "components": comps, "title": "t", "url": "u"}) + "\n")

    def test_prep_builds_datasets_and_captions(self):
        self.capture("shop")
        self.capture("careers")
        code, out = run("prep", str(self.kit))
        self.assertEqual(code, 0)
        for lora in ("brand", "shop", "careers"):
            d = self.kit / "dataset" / lora
            pngs = sorted(d.glob("*.png"))
            self.assertTrue(pngs, lora)
            for p in pngs:
                self.assertTrue(p.with_suffix(".txt").is_file())
        man = [json.loads(l) for l in (self.kit / "dataset" / "shop" / "manifest.jsonl").read_text(encoding="utf-8").splitlines()]
        kinds = [m["kind"] for m in man]
        self.assertEqual(kinds.count("button"), 1, "the same button text on two pages is one picture")
        self.assertIn("tile", kinds)
        caps = [(self.kit / "dataset" / "shop" / m["file"].replace(".png", ".txt")).read_text(encoding="utf-8") for m in man]
        self.assertTrue(all(c.startswith("northwindui northwindshopui, ") for c in caps))
        self.assertTrue(any('text reads "Add to basket"' in c for c in caps))
        self.assertFalse(any(bw.STYLE_WORDS.search(c) for c in caps), "template captions never name colours or fonts")

    def test_specimen_pads_small_components(self):
        crop = Image.new("RGB", (160, 40), "#f2a541")
        s = bw.specimen(Image, crop, (251, 248, 242))
        self.assertGreaterEqual(min(s.size), 64)
        self.assertEqual(s.size[0] % 16, 0)
        self.assertEqual(s.getpixel((1, 1)), (251, 248, 242))

    def test_review_page(self):
        self.capture("shop", pages=1)
        run("prep", str(self.kit))
        run("review", str(self.kit))
        self.assertIn("dataset/shop/0001.png", (self.kit / "review.html").read_text(encoding="utf-8"))


class TestStyleWords(unittest.TestCase):
    def test_findall_returns_words(self):
        found = bw.STYLE_WORDS.findall("A branded blue header with rounded buttons and a logo")
        self.assertEqual([w.lower() for w in found], ["branded", "blue", "rounded", "logo"])


class TestTrain(KitCase):
    def dataset(self, lora, n=5):
        d = self.kit / "dataset" / lora
        d.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            (d / ("%04d.png" % i)).write_bytes(b"x")

    def args(self, **kw):
        base = dict(model=None, mode=None, brand_lora=None, steps=None, rank=32, lr=1e-4, res=[768, 1024], save_every=100, samples=None,
                    sample_every=None)
        base.update(kw)
        return type("A", (), base)()

    def test_brand_config(self):
        self.dataset("brand")
        name, cfg, steps, mode, n = bw.train_config(bw.Kit(self.kit), "brand", self.args())
        p = cfg["config"]["process"][0]
        self.assertEqual(p["model"]["arch"], "zimage")
        self.assertEqual(p["network"]["linear"], p["network"]["linear_alpha"])
        self.assertEqual(steps, 400)
        self.assertEqual(mode, "single")
        self.assertTrue(all(pr.startswith("northwindui, ") for pr in p["sample"]["prompts"]))

    def test_site_residual_needs_brand_lora(self):
        self.dataset("shop")
        with self.assertRaises(SystemExit):
            bw.train_config(bw.Kit(self.kit), "shop", self.args())

    def test_site_residual_and_continue(self):
        self.dataset("shop")
        (self.kit / "loras").mkdir()
        (self.kit / "loras" / "brand-zimage.safetensors").write_bytes(b"x")
        (self.kit / "loras" / "brand-klein4b.safetensors").write_bytes(b"x")
        _, cfg, _, mode, _ = bw.train_config(bw.Kit(self.kit), "shop", self.args())
        self.assertEqual(mode, "residual")
        self.assertTrue(cfg["config"]["process"][0]["model"]["assistant_lora_path"].endswith("brand-zimage.safetensors"))
        _, cfg, _, mode, _ = bw.train_config(bw.Kit(self.kit), "shop", self.args(model="klein4b"))
        self.assertEqual(mode, "continue")
        self.assertIn("pretrained_lora_path", cfg["config"]["process"][0]["network"])
        with self.assertRaises(SystemExit):
            bw.train_config(bw.Kit(self.kit), "shop", self.args(model="klein4b", mode="residual"))

    def test_sampling_defaults(self):
        # Brand LoRAs are picked from their samples: 4 prompts at every checkpoint, step 0 included.
        self.dataset("brand")
        p = bw.train_config(bw.Kit(self.kit), "brand", self.args())[1]["config"]["process"][0]
        self.assertEqual((len(p["sample"]["prompts"]), p["sample"]["sample_every"]), (4, 100))
        self.assertFalse(p["train"]["skip_first_sample"] or p["train"]["disable_sampling"])
        # Residual samples leave the brand LoRA out (train L-005): 2 prompts every 200 steps, no step 0.
        self.dataset("shop")
        (self.kit / "loras").mkdir()
        (self.kit / "loras" / "brand-zimage.safetensors").write_bytes(b"x")
        p = bw.train_config(bw.Kit(self.kit), "shop", self.args())[1]["config"]["process"][0]
        self.assertEqual((len(p["sample"]["prompts"]), p["sample"]["sample_every"]), (2, 200))
        self.assertTrue(p["train"]["skip_first_sample"])
        p = bw.train_config(bw.Kit(self.kit), "shop", self.args(samples=3, sample_every=100))[1]["config"]["process"][0]
        self.assertEqual((len(p["sample"]["prompts"]), p["sample"]["sample_every"]), (3, 100))
        p = bw.train_config(bw.Kit(self.kit), "shop", self.args(samples=0))[1]["config"]["process"][0]
        self.assertTrue(p["train"]["disable_sampling"])

    def test_train_writes_config_without_running(self):
        self.dataset("brand", 60)
        code, out = run("train", str(self.kit), "--lora", "brand")
        self.assertEqual(code, 0)
        self.assertIn("not started", out)
        cfgs = list((self.kit / "train").glob("*.json"))
        self.assertEqual(len(cfgs), 1)
        self.assertEqual(json.loads(cfgs[0].read_text(encoding="utf-8"))["config"]["process"][0]["train"]["steps"], 400)

    def test_train_for_musubi_writes_toml_and_script(self):
        self.dataset("brand", 60)
        self.dataset("shop", 20)
        (self.kit / "loras").mkdir()
        (self.kit / "loras" / "brand-zimage.safetensors").write_bytes(b"0")
        code, out = run("train", str(self.kit), "--lora", "shop", "--for", "musubi")
        self.assertEqual(code, 0)
        job = self.kit / "train" / "northwind-shop-zimage-musubi"
        toml = (job / "dataset.toml").read_text(encoding="utf-8")
        self.assertEqual(toml.count("[[datasets]]"), 2)  # one per resolution, own caches
        self.assertIn("cache_768", toml)
        sh = (job / "train.sh").read_text(encoding="utf-8")
        for flag in ("zimage_train_network.py", "networks.lora_zimage", "--network_dim 32", "--network_alpha 32",
                     "--max_train_steps 400", "--base_weights", "brand-zimage.safetensors", "--fp8_llm", "venv"):
            self.assertIn(flag, sh)
        self.assertNotIn(chr(92), sh)  # posix paths only
        self.assertFalse(list((self.kit / "train").glob("*.json")))  # no ai-toolkit config

    def test_train_for_onetrainer(self):
        self.dataset("brand", 60)
        code, out = run("train", str(self.kit), "--lora", "brand", "--for", "onetrainer", "--model", "zimage_turbo")
        self.assertEqual(code, 0)
        job = self.kit / "train" / "northwind-brand-zimage_turbo-onetrainer"
        cfg = json.loads((job / "config.json").read_text(encoding="utf-8"))
        self.assertEqual((cfg["__version"], cfg["model_type"], cfg["lora_rank"], cfg["epochs"]), (11, "Z_IMAGE", 32, 7))
        self.assertEqual(cfg["transformer"]["model_name"], bw.DETURBO)
        self.assertEqual(cfg["resolution"], "768,1024")
        concepts = json.loads((job / "concepts.json").read_text(encoding="utf-8"))
        self.assertEqual(concepts[0]["text"]["prompt_source"], "sample")
        with self.assertRaises(SystemExit):
            run("train", str(self.kit), "--lora", "brand", "--for", "onetrainer", "--run")

    def test_pick_falls_back_when_comfy_holds_the_file(self):
        out = self.kit / "train" / "out" / "northwind-brand-zimage"
        out.mkdir(parents=True)
        (out / "northwind-brand-zimage_000000250.safetensors").write_bytes(b"0")
        comfy = self.tmp / "loras"
        comfy.mkdir()
        real = shutil.copy2

        def copy2(src, dst):
            if Path(dst).name == "northwind-brand.safetensors":
                raise OSError(22, "user-mapped section open")
            return real(src, dst)

        with unittest.mock.patch.object(bw.shutil, "copy2", copy2):
            code, outp = run("pick", str(self.kit), "--lora", "brand", "--step", "250", "--to", str(comfy))
        self.assertEqual(code, 0)
        self.assertTrue((comfy / "northwind-brand-s250.safetensors").is_file())
        self.assertEqual(self.cfg()["comfy_loras"]["brand"], "northwind-brand-s250.safetensors")

    def test_retrain_sets_old_run_aside(self):
        out = self.kit / "train" / "out" / "x-brand-zimage"
        self.assertIsNone(bw.set_aside_old_run(out))
        out.mkdir(parents=True)
        (out / "samples").mkdir()
        self.assertIsNone(bw.set_aside_old_run(out))  # samples only: nothing to resume from
        (out / "x-brand-zimage_000000250.safetensors").write_bytes(b"0")
        moved = bw.set_aside_old_run(out)
        self.assertFalse(out.exists())
        self.assertTrue((moved / "x-brand-zimage_000000250.safetensors").is_file())
        self.assertTrue(moved.name.startswith("x-brand-zimage-run-"))


class TestComfyGraphs(KitCase):
    def test_ksampler_graph_with_loras(self):
        g = {}
        spec = bw_comfy.preset(bw.Kit(self.kit), "zimage_turbo")
        model, clip, vae = bw_comfy.loaders(g, spec, [("a.safetensors", 1.0), ("b.safetensors", 0.0), ("c.safetensors", 0.7)])
        bw_comfy.branch(g, spec, model, clip, vae, "p", 1344, 768, 1, 2, "t")
        loras = [n for n in g.values() if n["class_type"] == "LoraLoaderModelOnly"]
        self.assertEqual([l["inputs"]["lora_name"] for l in loras], ["a.safetensors", "c.safetensors"])
        self.assertEqual(g["clip"]["inputs"]["type"], "lumina2")
        self.assertEqual(g["ks_t"]["inputs"]["steps"], 9)
        self.assertEqual(g["neg_t"]["class_type"], "ConditioningZeroOut")

    def test_flux2_graph_with_refs(self):
        g = {}
        spec = bw_comfy.preset(bw.Kit(self.kit), "klein4b")
        model, clip, vae = bw_comfy.loaders(g, spec, [])
        bw_comfy.branch(g, spec, model, clip, vae, "p", 1024, 1024, 1, 1, "r", refs=[["e0", 0], ["e1", 0]])
        refs = [k for k, n in g.items() if n["class_type"] == "ReferenceLatent"]
        self.assertEqual(len(refs), 4)
        self.assertEqual(g["guide_r"]["class_type"], "CFGGuider")

    def test_kit_overrides_model_files(self):
        cfg = self.cfg()
        cfg["comfy_models"] = {"zimage": {"unet": "mine.safetensors"}}
        (self.kit / "brand.json").write_text(json.dumps(cfg), encoding="utf-8")
        self.assertEqual(bw_comfy.preset(bw.Kit(self.kit), "zimage")["unet"], "mine.safetensors")

    def test_triggers_added_once(self):
        k = bw.Kit(self.kit)
        p = bw_comfy.with_triggers(k, "a pricing card", ["brand", "shop"])
        self.assertTrue(p.startswith("northwindui, northwindshopui, "))
        self.assertEqual(bw_comfy.with_triggers(k, p, ["brand"]), p)

    def test_unknown_lora_name_exits(self):
        with self.assertRaises(SystemExit):
            bw_comfy.lora_specs(bw.Kit(self.kit), ["brand=0.8"])
        self.assertEqual(bw_comfy.lora_specs(bw.Kit(self.kit), ["x.safetensors=0.5"]), [("x.safetensors", 0.5, None)])

    def test_frange(self):
        self.assertEqual(bw_comfy.frange("0.4:1.0:0.3"), [0.4, 0.7, 1.0])
        self.assertEqual(bw_comfy.frange("0.5,1"), [0.5, 1.0])


@unittest.skipIf(Image is None, "Pillow not installed")
class TestScore(KitCase):
    def test_on_palette_scores_low(self):
        token_file(self.kit / "capture" / "shop" / "tokens" / "p.json")
        run("tokens", str(self.kit))
        on = self.tmp / "on.png"
        off = self.tmp / "off.png"
        Image.new("RGB", (64, 64), "#fbf8f2").save(on)
        Image.new("RGB", (64, 64), "#ff00ff").save(off)
        pal = bw.brand_palette(bw.Kit(self.kit))
        self.assertLess(bw.palette_score(Image, on, pal)[0], 3)
        self.assertGreater(bw.palette_score(Image, off, pal)[1], 0.9)


if __name__ == "__main__":
    unittest.main(verbosity=1)
