"""Browser side of brandwright: log in, capture pages, read design tokens, render HTML.

Needs Playwright for Python (`pip install playwright`). Use an installed browser with `--channel msedge`
or `--channel chrome` so nothing else has to be downloaded; otherwise run `playwright install chromium` once.
Every page is opened with GET only: nothing is clicked except what --click names, and crawling skips
sign-out, delete and file links.
"""
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urldefrag, urlparse

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900, "dsf": 1, "mobile": False},
    "laptop": {"width": 1280, "height": 800, "dsf": 1, "mobile": False},
    "tablet": {"width": 834, "height": 1194, "dsf": 1, "mobile": True},
    "mobile": {"width": 390, "height": 844, "dsf": 2, "mobile": True},
}

# Overlays hidden (never clicked) before a capture: consent banners, chat bubbles, survey pop-ups.
DEFAULT_HIDE = [
    "#onetrust-banner-sdk", "#onetrust-consent-sdk", "#CybotCookiebotDialog", ".cc-window", "#truste-consent-track",
    "[id*='cookie-banner' i]", "[class*='cookie-banner' i]", "[id*='consent' i][role='dialog']",
    "[aria-label*='cookie' i][role='dialog']", "#intercom-container", ".intercom-lightweight-app",
    "#hubspot-messages-iframe-container", "iframe[title*='chat' i]", "#launcher", ".drift-frame-controller",
    "[id*='qualtrics' i]", "#usabilla_live_button_container",
]

SKIP_LINK = re.compile(r"(log-?out|sign-?out|logoff|delete|remove|unsubscribe|cancel|mailto:|tel:|javascript:)", re.I)
# Boilerplate pages that add little to a style: crawled only with --crawl-all.
SKIP_BORING = re.compile(r"/(cookies?|privacy|terms|legal|accessibility(-statement)?|sitemap|copyright|disclaimer)(/|$|\?)", re.I)
SKIP_EXT = re.compile(r"\.(pdf|zip|docx?|xlsx?|pptx?|png|jpe?g|gif|svg|webp|mp4|mp3|csv|exe|msi|dmg)(\?|$)", re.I)

MASK_JS = r"""
(opts) => {
  const fake = (s) => s.replace(/[0-9]/g, '5');
  const email = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi;
  const digits = /(\+?\d[\d \-().]{6,}\d)/g;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n, changed = 0;
  while (opts.pii && (n = walker.nextNode())) {
    const t = n.nodeValue;
    if (!t || t.trim().length < 5) continue;
    let u = t.replace(email, 'name@example.com').replace(digits, (m) => fake(m));
    if (u !== t) { n.nodeValue = u; changed++; }
  }
  for (const el of (opts.pii ? document.querySelectorAll('input, textarea') : [])) {
    const typ = (el.getAttribute('type') || 'text').toLowerCase();
    if (['hidden', 'submit', 'button', 'checkbox', 'radio', 'range', 'color'].includes(typ)) continue;
    if (el.value) { el.value = typ === 'password' ? 'xxxxxxxx' : (typ === 'email' ? 'name@example.com' : fake(el.value)); changed++; }
  }
  for (const sel of opts.blur) for (const el of document.querySelectorAll(sel)) { el.style.filter = 'blur(8px)'; changed++; }
  for (const sel of opts.hide) for (const el of document.querySelectorAll(sel)) { el.style.setProperty('display', 'none', 'important'); }
  return changed;
}
"""

COLLECT_JS = r"""
(opts) => {
  const doc = document.documentElement;
  const W = doc.scrollWidth, H = doc.scrollHeight;
  const vis = (el, s, r) => r.width >= 1 && r.height >= 1 && s.visibility !== 'hidden' && s.display !== 'none' && parseFloat(s.opacity || '1') > 0.05;
  // computed colours come back as rgb(), oklch(), color(...) and more: read each through a 1x1 canvas into hex
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', {willReadFrequently: true}); const memo = {};
  const hex = (c) => {
    if (!c) return null; if (c in memo) return memo[c];
    cx.clearRect(0, 0, 1, 1); cx.fillStyle = 'rgba(0,0,0,0)'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    const h = d[3] < 13 ? null : '#' + [d[0], d[1], d[2]].map(v => v.toString(16).padStart(2, '0')).join('') + (d[3] < 250 ? d[3].toString(16).padStart(2, '0') : '');
    memo[c] = h; return h;
  };
  const tr = (c) => hex(c) === null;
  const box = (r) => ({x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height)});
  const txt = (el) => (el.innerText || el.value || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().slice(0, 160);
  const tally = {color: {}, background: {}, border: {}, font: {}, size: {}, weight: {}, radius: {}, shadow: {}, space: {}, lineheight: {}};
  const add = (k, v, w) => { if (v === undefined || v === null || v === '') return; tally[k][v] = (tally[k][v] || 0) + w; };
  const all = Array.from(document.body.querySelectorAll('*')).slice(0, opts.maxElements);
  for (const el of all) {
    const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (!vis(el, s, r)) continue;
    const area = Math.min(r.width * r.height, W * 2000);
    let ownText = 0;
    for (const c of el.childNodes) if (c.nodeType === 3) ownText += c.nodeValue.trim().length;
    if (ownText) {
      add('color', hex(s.color), ownText);
      add('font', s.fontFamily.split(',')[0].replace(/["']/g, '').trim(), ownText);
      add('size', s.fontSize, ownText); add('weight', s.fontWeight, ownText); add('lineheight', s.lineHeight, ownText);
    }
    if (!tr(s.backgroundColor)) add('background', hex(s.backgroundColor), area);
    const bw = parseFloat(s.borderTopWidth) + parseFloat(s.borderBottomWidth) + parseFloat(s.borderLeftWidth) + parseFloat(s.borderRightWidth);
    if (bw > 0 && s.borderTopStyle !== 'none' && !tr(s.borderTopColor)) add('border', hex(s.borderTopColor), (r.width + r.height) * 2);
    if (s.borderTopLeftRadius !== '0px' && (!tr(s.backgroundColor) || bw > 0)) add('radius', s.borderTopLeftRadius, 1);
    if (s.boxShadow && s.boxShadow !== 'none') add('shadow', s.boxShadow, 1);
    for (const p of ['paddingTop', 'paddingLeft', 'marginTop', 'marginBottom', 'rowGap', 'columnGap']) {
      const v = s[p]; if (v && v !== '0px' && v !== 'normal' && v !== 'auto') add('space', v, 1);
    }
  }
  // the site's own custom properties on :root (same-origin sheets only)
  const vars = {};
  const rs = getComputedStyle(doc);
  for (const sheet of Array.from(document.styleSheets)) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    if (!rules) continue;
    for (const rule of Array.from(rules)) {
      if (rule.selectorText && /(^|,)\s*(:root|html)\s*(,|$)/.test(rule.selectorText)) {
        for (let i = 0; i < rule.style.length; i++) {
          const p = rule.style[i];
          if (p.startsWith('--') && Object.keys(vars).length < opts.maxVars) vars[p] = rs.getPropertyValue(p).trim();
        }
      }
    }
  }
  const fonts = [];
  for (const sheet of Array.from(document.styleSheets)) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    if (!rules) continue;
    for (const rule of Array.from(rules)) {
      if (rule.type === 5 && fonts.length < 40) {   // CSSFontFaceRule
        const src = rule.style.getPropertyValue('src');
        const abs = src.replace(/url\((['"]?)([^'")]+)\1\)/g, (m, q, u) => 'url("' + new URL(u, sheet.href || location.href).href + '")');
        fonts.push({family: rule.style.getPropertyValue('font-family').replace(/["']/g, '').trim(),
                    weight: rule.style.getPropertyValue('font-weight') || '400', style: rule.style.getPropertyValue('font-style') || 'normal', src: abs});
      }
    }
  }
  // components: semantic selectors, then card-like boxes
  const comps = []; const seen = new Set(); const perKind = {};
  const RECIPE = ['color', 'backgroundColor', 'fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'textTransform',
                  'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'borderTopWidth', 'borderTopStyle', 'borderTopColor',
                  'borderTopLeftRadius', 'boxShadow', 'height', 'minHeight'];
  const recipe = (s) => { const o = {}; for (const k of RECIPE) o[k] = /color$/i.test(k) ? (hex(s[k]) || 'transparent') : s[k]; return o; };
  const take = (el, kind) => {
    if (seen.has(el)) return;
    const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (!vis(el, s, r) || r.width < opts.minW || r.height < opts.minH) return;
    if ((perKind[kind] || 0) >= opts.maxPerKind) return;
    for (const p of seen) if (p.contains(el) && kind === 'card' && p.__bwKind === 'card') return;
    seen.add(el); el.__bwKind = kind; perKind[kind] = (perKind[kind] || 0) + 1;
    comps.push({kind, box: box(r), text: txt(el), tag: el.tagName.toLowerCase(), recipe: recipe(s)});
  };
  const RULES = [
    ['header', 'header, [role=banner]'], ['navigation', 'nav, [role=navigation]'], ['footer', 'footer, [role=contentinfo]'],
    ['hero', 'main > section:first-of-type, [class*=hero i], [class*=jumbotron i], [class*=masthead i]'],
    ['form', 'form'], ['table', 'table'], ['dialog', 'dialog[open], [role=dialog]'], ['tabs', '[role=tablist]'],
    ['breadcrumb', '[aria-label*=breadcrumb i], .breadcrumb, .breadcrumbs'],
    ['alert', '[role=alert], [role=status], .alert, .notification'], ['pagination', '[aria-label*=pagination i], .pagination'],
    ['button', 'button, [role=button], input[type=submit], input[type=button], a[class*=btn i], a[class*=button i]'],
    ['text input', 'input[type=text], input[type=email], input[type=search], input[type=tel], input:not([type]), select, textarea'],
  ];
  for (const [kind, sel] of RULES) { let list; try { list = document.querySelectorAll(sel); } catch (e) { continue; } for (const el of list) take(el, kind); }
  // card-like: a box with its own background, border or shadow, a heading or image inside, and text
  for (const el of all) {
    const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (r.width < 160 || r.height < 100 || r.width > W * 0.7 || r.height > 900) continue;
    const parentBg = el.parentElement ? getComputedStyle(el.parentElement).backgroundColor : '';
    const edge = (s.boxShadow && s.boxShadow !== 'none') || parseFloat(s.borderTopWidth) > 0 || (!tr(s.backgroundColor) && s.backgroundColor !== parentBg);
    if (!edge) continue;
    if (!el.querySelector('h1,h2,h3,h4,h5,h6,img,svg,picture')) continue;
    if (txt(el).length < 12) continue;
    take(el, 'card');
  }
  let bg = hex(getComputedStyle(document.body).backgroundColor) || hex(getComputedStyle(doc).backgroundColor) || '#ffffff';
  const links = Array.from(document.querySelectorAll('a[href]')).map(a => a.href).slice(0, 400);
  return {title: document.title, url: location.href, width: W, height: H, bg, tally, vars, fonts, components: comps, links};
}
"""


def need_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return sync_playwright
    except ImportError:
        sys.exit("brandwright: Playwright is not installed. Run: python -m pip install playwright\n"
                 "then either pass --channel msedge (or chrome) to use an installed browser, "
                 "or run: python -m playwright install chromium")


def slug(text, n=48):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s or "page")[:n]


def page_slug(url):
    p = urlparse(url)
    path = (p.path.strip("/") or "home") + (("-" + p.query) if p.query else "")
    return slug(p.netloc.split(".")[0] + "-" + path)


def open_browser(pw, args, profile_dir=None, headless=True):
    """Returns (context, close_fn). --cdp attaches to the user's running browser; a profile dir from `login` is reused."""
    if getattr(args, "cdp", None):
        browser = pw.chromium.connect_over_cdp(args.cdp)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        return ctx, lambda: None  # never close the user's own browser
    kw = {"headless": headless}
    if getattr(args, "channel", None):
        kw["channel"] = args.channel
    if profile_dir and Path(profile_dir).exists():
        ctx = pw.chromium.launch_persistent_context(str(profile_dir), **kw)
        return ctx, ctx.close
    browser = pw.chromium.launch(**kw)
    return browser, browser.close


def new_page(holder, vp):
    spec = VIEWPORTS[vp]
    opts = {"viewport": {"width": spec["width"], "height": spec["height"]}, "device_scale_factor": spec["dsf"],
            "is_mobile": spec["mobile"], "has_touch": spec["mobile"]}
    if hasattr(holder, "new_context") and not hasattr(holder, "pages"):  # a Browser
        ctx = holder.new_context(**opts)
        return ctx.new_page(), ctx.close
    page = holder.new_page()  # a persistent or CDP context: viewport per page, scale fixed by the profile
    page.set_viewport_size(opts["viewport"])
    return page, page.close


def settle(page, wait_ms):
    """Scroll to the bottom and back so lazy images load, then wait."""
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    h = page.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < min(h, 20000):
        page.evaluate("y => window.scrollTo(0, y)", y)
        page.wait_for_timeout(120)
        y += 700
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(wait_ms)


def cmd_login(args, kit):
    sync_playwright = need_playwright()
    prof = kit.root / "auth" / args.site
    prof.mkdir(parents=True, exist_ok=True)
    print("A browser window opens. Sign in yourself, then close the window; the session is kept in\n  %s\n"
          "(private: it can open the site as you, so never share or commit it)." % prof)
    with sync_playwright() as pw:
        kw = {"headless": False}
        if args.channel:
            kw["channel"] = args.channel
        ctx = pw.chromium.launch_persistent_context(str(prof), **kw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(args.url)
        try:
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass
        try:
            ctx.close()
        except Exception:
            pass
    print("saved login profile for site '%s'" % args.site)
    return 0


def same_site(a, b):
    return urlparse(a).netloc.lower() == urlparse(b).netloc.lower()


def cmd_capture(args, kit):
    sync_playwright = need_playwright()
    site = kit.site(args.site)
    out = kit.root / "capture" / args.site
    (out / "pages").mkdir(parents=True, exist_ok=True)
    (out / "tokens").mkdir(parents=True, exist_ok=True)
    log = out / "capture.jsonl"
    viewports = [v.strip() for v in args.viewports.split(",") if v.strip()]
    for v in viewports:
        if v not in VIEWPORTS:
            sys.exit("unknown viewport %r (known: %s)" % (v, ", ".join(VIEWPORTS)))
    urls = list(args.urls or site.get("urls") or [])
    if not urls:
        sys.exit("no URL: pass one or more, or list them under the site in brand.json")
    hide = DEFAULT_HIDE + [s for s in (args.hide or [])]
    blur = list(args.blur or []) + list(site.get("blur", []))
    profile = kit.root / "auth" / args.site
    queue, done, count = list(urls), set(), 0
    limit = len(urls) + max(0, args.crawl)
    with sync_playwright() as pw:
        holder, close = open_browser(pw, args, profile if profile.exists() else None)
        try:
            while queue and count < limit:
                url = urldefrag(queue.pop(0))[0]
                if url in done:
                    continue
                done.add(url)
                count += 1
                for vp in viewports:
                    page, close_page = new_page(holder, vp)
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=args.timeout * 1000)
                        for sel in args.click or []:
                            try:
                                page.click(sel, timeout=3000)
                            except Exception:
                                print("  could not click %s" % sel)
                        settle(page, args.wait)
                        masked = page.evaluate(MASK_JS, {"blur": blur, "hide": hide, "pii": not args.no_mask})
                        data = page.evaluate(COLLECT_JS, {"maxElements": 6000, "maxVars": 400, "minW": 24, "minH": 16,
                                                          "maxPerKind": args.max_per_kind})
                        name = "%s__%s" % (page_slug(page.url), vp)
                        shot = out / "pages" / (name + ".png")
                        page.screenshot(path=str(shot), full_page=True, timeout=60000)
                        dsf = VIEWPORTS[vp]["dsf"]
                        rec = {"file": "pages/%s.png" % name, "site": args.site, "url": page.url, "title": data["title"],
                               "viewport": vp, "dsf": dsf, "bg": data["bg"], "masked": masked,
                               "components": data["components"], "captured": time.strftime("%Y-%m-%dT%H:%M:%S")}
                        tok = {k: data[k] for k in ("tally", "vars", "fonts", "bg", "url", "title")}
                        tok["viewport"] = vp
                        tok["recipes"] = {}
                        for c in data["components"]:
                            tok["recipes"].setdefault(c["kind"], []).append(c["recipe"])
                        (out / "tokens" / (name + ".json")).write_text(json.dumps(tok), encoding="utf-8")
                        with log.open("a", encoding="utf-8") as f:
                            f.write(json.dumps(rec) + "\n")
                        print("captured %s  %s  %d components  %d values masked" % (vp, page.url, len(data["components"]), masked))
                        if vp == viewports[0] and args.crawl > 0:
                            for link in data["links"]:
                                link = urldefrag(link)[0]
                                if (same_site(link, url) and link not in done and link not in queue
                                        and not SKIP_LINK.search(link) and not SKIP_EXT.search(link)
                                        and (args.crawl_all or not SKIP_BORING.search(link))):
                                    queue.append(link)
                    except Exception as e:  # one bad page must not lose the rest
                        print("  failed %s (%s): %s" % (url, vp, str(e).splitlines()[0][:200]))
                    finally:
                        close_page()
        finally:
            close()
    print("%d page(s) captured into %s" % (count, out))
    return 0


def cmd_render(args):
    """The code route: screenshot an HTML mock-up (made with brand.css) at a viewport."""
    sync_playwright = need_playwright()
    src = Path(args.html).resolve()
    out = Path(args.out) if args.out else src.with_suffix(".png")
    with sync_playwright() as pw:
        kw = {"headless": True}
        if args.channel:
            kw["channel"] = args.channel
        browser = pw.chromium.launch(**kw)
        ctx = browser.new_context(viewport={"width": args.width, "height": args.height}, device_scale_factor=args.scale,
                                  color_scheme="dark" if args.dark else "light")
        page = ctx.new_page()
        page.goto(src.as_uri())
        page.wait_for_load_state("networkidle")
        # A font that fails (behind a login, or served without CORS headers to a file:// page) falls back silently.
        failed = page.evaluate("Promise.all([...document.fonts].map(f => f.load().catch(() => null)))"
                               ".then(() => [...new Set([...document.fonts].filter(f => f.status === 'error')"
                               ".map(f => f.family.replace(/[\"']/g, '')))])")
        for fam in failed:
            print("warning: font %s did not load, so the render uses a fallback font. Its URL in brand.css may need a "
                  "login or refuse pages opened from disk; ask for the font files and point @font-face at local copies"
                  % fam)
        if args.selector:
            page.locator(args.selector).first.screenshot(path=str(out))
        else:
            page.screenshot(path=str(out), full_page=args.full)
        browser.close()
    print("rendered %s" % out)
    return 0
