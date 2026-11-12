#!/usr/bin/env python3
"""FranchiseConnection.com static site builder.

Wraps every fragment in src/pages/ with the shared layout and writes the
finished HTML to the repo root (GitHub Pages serves main branch / root).

Fragment header (first lines of each page):
<!--meta
title: Page title
description: Meta description
section: explore            (optional, highlights nav)
type: article               (optional: adds Article JSON-LD)
published: 2026-11-12       (optional)
-->

Inside fragments, write links as {{root}}page.html so they work both on
username.github.io/repo/ and on the custom domain.
Run:  python3 build.py
"""
import datetime, hashlib, html, json, os, re

VER = "1"
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "pages")
DOMAIN = "https://franchiseconnection.com/"
SITE = "FranchiseConnection.com"
TODAY = datetime.date.today().isoformat()
BASE_DATE = "2026-11-12"   # content baseline; pages can override with "reviewed:" meta
FRESH = {"index.html", "news.html", "events.html"}  # pages whose content changes daily


def asset_version():
    h = hashlib.md5()
    for f in ("assets/css/site.css", "assets/js/site.js"):
        h.update(open(os.path.join(ROOT, f), "rb").read())
    return h.hexdigest()[:8]

ADSENSE = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6620975821265271" crossorigin="anonymous"></script>'

NAV = [
    ("explore", "explore.html", "Explore"),
    ("tools", "tools.html", "Tools"),
    ("guides", "guides.html", "Guides"),
    ("news", "news.html", "News"),
    ("videos", "videos.html", "Videos"),
    ("franchisors", "franchisors.html", "For franchisors"),
]
MORE = [
    ("events.html", "Expos & events"), ("resources.html", "Resources"),
    ("glossary.html", "Glossary"), ("contests.html", "Contests & prizes"),
    ("support.html", "Support us"), ("careers.html", "Careers"),
    ("advertise.html", "Advertise"), ("about.html", "About"), ("contact.html", "Contact"),
]

LOGO = '''<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><path d="M4 14h32l-3-9H7z" fill="#FFC531"/><path d="M4 14c0 3 2 5 4.5 5S13 17 13 14c0 3 2 5 4.5 5S22 17 22 14c0 3 2 5 4.5 5S31 17 31 14c0 3 2 5 2.5 5S36 17 36 14" fill="#FFC531"/><path d="M8 19v16h24V19" fill="none" stroke="currentColor" stroke-width="3"/><path d="M17 35v-9h6v9" fill="none" stroke="currentColor" stroke-width="3"/></svg>'''


def parse(path):
    raw = open(path, encoding="utf-8").read()
    meta = {}
    m = re.match(r"<!--meta\n(.*?)\n-->\n?", raw, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        raw = raw[m.end():]
    return meta, raw


BASE404 = """<script>document.write('<base href="'+(location.hostname.indexOf('github.io')>-1?'/franchiseconnection-com/':'/')+'">')</script>\n"""


def head(meta, rel, root):
    title = meta.get("title", SITE)
    desc = meta.get("description", "")
    canon = DOMAIN + ("" if rel == "index.html" else rel)
    ld = [{
        "@context": "https://schema.org", "@type": "Organization", "name": SITE,
        "url": DOMAIN, "logo": DOMAIN + "assets/img/logo.png",
    }]
    if rel == "index.html":
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": DOMAIN,
                   "potentialAction": {"@type": "SearchAction", "target": DOMAIN + "explore.html?q={query}", "query-input": "required name=query"}})
    if meta.get("type") == "article":
        ld.append({"@context": "https://schema.org", "@type": "Article", "headline": meta.get("h1", title),
                   "description": desc, "datePublished": meta.get("published", BASE_DATE), "dateModified": meta.get("reviewed", meta.get("published", BASE_DATE)),
                   "author": {"@type": "Organization", "name": SITE + " Editorial Team"},
                   "publisher": {"@type": "Organization", "name": SITE, "logo": {"@type": "ImageObject", "url": DOMAIN + "assets/img/logo.png"}},
                   "mainEntityOfPage": canon, "image": DOMAIN + "assets/img/og.png"})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": DOMAIN + "guides.html"},
            {"@type": "ListItem", "position": 3, "name": meta.get("h1", title), "item": canon}]})
    robots = '<meta name="robots" content="noindex">' if rel == "404.html" else '<meta name="robots" content="index,follow,max-image-preview:large">'
    return f'''<!doctype html>
<html lang="en" data-root="{root}">
<head>
<meta charset="utf-8">
{BASE404 if rel == "404.html" else ""}<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{robots}
<link rel="canonical" href="{canon}">
<meta name="google-adsense-account" content="ca-pub-6620975821265271">
{ADSENSE}
<meta property="og:type" content="{'article' if meta.get('type') == 'article' else 'website'}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#123A42">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/img/logo.png">
<link rel="manifest" href="{root}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..700;1,8..60,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/css/site.css?v={VER}">
<script type="application/ld+json">{json.dumps(ld if len(ld) > 1 else ld[0], separators=(',', ':'))}</script>
</head>'''


def header(section, root):
    links = "".join(
        f'<li><a href="{root}{href}"{" aria-current=\"page\"" if key == section else ""}>{label}</a></li>'
        for key, href, label in NAV)
    more = "".join(f'<li><a href="{root}{h}">{l}</a></li>' for h, l in MORE)
    return f'''<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap"><a href="https://web.works/contact" target="_blank" rel="noopener">Contact, if you are interested in this website / domain name / sponsorship / advertisement / partnership</a></div></div>
<header class="site-head">
<div class="wrap head-row">
<a class="brand" href="{root}index.html" aria-label="FranchiseConnection.com home">{LOGO}<span>Franchise<b>Connection</b></span></a>
<button class="burger" id="burger" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span><em>Menu</em></button>
<nav id="menu" class="menu" aria-label="Main">
<ul class="nav-main">{links}
<li class="more"><button type="button" aria-expanded="false" aria-haspopup="true">More</button><ul class="more-list">{more}</ul></li></ul>
<a class="btn btn-sign" href="{root}match.html">Get matched free</a>
</nav>
</div>
</header>
<main id="main">'''


def footer(root, rel):
    sticky = "" if rel in ("match.html",) else f'<a class="sticky-cta" href="{root}match.html">Get your free franchise match report</a>'
    return f'''</main>
<footer class="site-foot">
<div class="wrap foot-grid">
<div class="foot-brand">
<a class="brand" href="{root}index.html">{LOGO}<span>Franchise<b>Connection</b></span></a>
<p>Independent tools, guides and matching for people buying a franchise, and a qualified-buyer channel for franchisors.</p>
<form class="js-form news-form" data-subject="Newsletter signup" data-ok="You're on the list. The next Franchise Market Pulse lands in your inbox soon.">
<label for="nl-email">Get the monthly Franchise Market Pulse</label>
<div class="inline-field"><input id="nl-email" name="email" type="email" placeholder="you@example.com" required autocomplete="email"><button class="btn btn-sign" type="submit">Subscribe</button></div>
<input class="hp" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
<input type="hidden" name="consent" value="Newsletter opt-in from footer">
<p class="form-msg" role="status"></p>
</form>
</div>
<div><h2>Buyers</h2><ul><li><a href="{root}match.html">Get matched</a></li><li><a href="{root}explore.html">Explore categories</a></li><li><a href="{root}tools.html">Calculators</a></li><li><a href="{root}guides.html">Guides</a></li><li><a href="{root}glossary.html">Glossary</a></li><li><a href="{root}resources.html">Resources</a></li></ul></div>
<div><h2>Franchisors</h2><ul><li><a href="{root}franchisors.html">List your franchise</a></li><li><a href="{root}franchisors.html#lead-program">Buyer lead program</a></li><li><a href="{root}advertise.html">Advertise &amp; sponsor</a></li><li><a href="{root}guides/how-to-franchise-your-business.html">Franchise your business</a></li></ul></div>
<div><h2>Community</h2><ul><li><a href="{root}news.html">Franchise news</a></li><li><a href="{root}videos.html">Videos</a></li><li><a href="{root}events.html">Expos &amp; events</a></li><li><a href="{root}contests.html">Contests &amp; prizes</a></li><li><a href="{root}careers.html">Careers</a></li><li><a href="{root}support.html">Support us</a></li></ul></div>
<div><h2>Company</h2><ul><li><a href="{root}about.html">About</a></li><li><a href="{root}contact.html">Contact</a></li><li><a href="{root}editorial-policy.html">Editorial policy</a></li><li><a href="{root}privacy.html">Privacy</a></li><li><a href="{root}terms.html">Terms</a></li><li><a href="{root}disclaimer.html">Disclaimer</a></li><li><a href="{root}cookies.html">Cookies</a></li><li><a href="{root}trademark.html">Trademark &amp; copyright</a></li><li><a href="{root}sitemap.html">Sitemap</a></li></ul></div>
</div>
<div class="wrap foot-legal">
<p>Franchise categories, figures and rankings on this site are educational and brand-neutral. Investment ranges are typical bands observed in published Franchise Disclosure Documents; always verify in the current FDD with an attorney and accountant. Nothing here is an offer to sell a franchise.</p>
<p>&copy; <span class="year">2026</span> {SITE}. "FranchiseConnection.com" is used as a descriptive domain name; no trademark rights are claimed in the generic words "franchise" or "connection", and the site is not affiliated with any business using a similar name. Third-party names and marks belong to their owners. <a href="{root}trademark.html">Trademark &amp; copyright disclosure</a>.</p>
</div>
</footer>
{sticky}
<div class="cookie" id="cookie" role="dialog" aria-live="polite" aria-label="Cookie notice">
<p>We use cookies for essential features, analytics and advertising (including Google AdSense). See our <a href="{root}cookies.html">cookie policy</a>.</p>
<div><button class="btn btn-ghost" data-cookie="essential">Essential only</button><button class="btn btn-sign" data-cookie="all">Accept all</button></div>
</div>
<script src="{root}assets/js/site.js?v={VER}" defer></script>
</body>
</html>
'''


CTA = '''<div class="callout"><h3>Get a free franchise match report</h3><p>Answer seven questions about your budget, goals and the hours you want to work. We rank 75 franchise categories for you and email the financing math.</p><a class="btn btn-sign" href="{root}match.html">Get my match report</a></div>'''


def nice_date(d):
    y, m, dd = (int(x) for x in d.split("-"))
    return datetime.date(y, m, dd).strftime("%B ") + str(dd) + datetime.date(y, m, dd).strftime(", %Y")


def article(meta, body, root):
    h1 = meta.get("h1", meta.get("title", ""))
    short = meta.get("short", h1)
    body = body.replace("{{cta}}", CTA.format(root=root)).replace("{{ad}}", '<div class="ad-slot" data-slot="in-article"></div>')
    return f'''<section class="page-hero"><div class="wrap">
<p class="crumbs"><a href="{root}index.html">Home</a> / <a href="{root}guides.html">Guides</a> / {short}</p>
<h1>{h1}</h1>
<p class="lead">{meta.get("lede", "")}</p>
<p class="byline">By the FranchiseConnection.com editorial team. Last reviewed {nice_date(meta.get("reviewed", meta.get("published", BASE_DATE)))}. {meta.get("minutes", "10")} min read. <button type="button" class="btn btn-ghost" style="padding:5px 10px;font-size:.85rem;margin-left:6px" data-share>Share</button></p>
</div></section>
<section class="section-tight"><div class="wrap article-grid">
<aside class="toc"><h2>On this page</h2><ol id="tocList"></ol>
<div class="panel" style="margin-top:20px"><h3 style="font-size:1rem">Not sure where to start?</h3><p class="small">Get a ranked shortlist of franchise categories that fit your budget.</p><a class="btn btn-sign btn-block" href="{root}match.html">Get matched free</a></div></aside>
<article class="prose">
{body}
</article>
</div></section>
'''


def build():
    global VER
    VER = asset_version()
    pages = []
    for dirpath, _, files in os.walk(SRC):
        for fn in sorted(files):
            if fn.endswith(".html"):
                pages.append(os.path.relpath(os.path.join(dirpath, fn), SRC).replace(os.sep, "/"))
    sitemap_entries = []
    parsed = {rel: parse(os.path.join(SRC, rel)) for rel in sorted(pages)}
    groups = {}
    for rel, (meta, _) in parsed.items():
        if rel == "404.html":
            continue
        g = "Guides" if rel.startswith("guides/") else meta.get("group", "Site")
        groups.setdefault(g, []).append((rel, meta.get("h1") or meta.get("title", rel).split(" | ")[0].split(" — ")[0]))
    def sitemap_html(root):
        return "".join(f'<div class="panel"><h2 style="font-size:1.25rem">{g}</h2><ul>' + "".join(f'<li><a href="{root}{r}">{html.escape(t)}</a></li>' for r, t in sorted(items, key=lambda x: x[1])) + "</ul></div>" for g, items in sorted(groups.items()))
    for rel in sorted(pages):
        meta, body = parsed[rel]
        depth = rel.count("/")
        root = "../" * depth
        if meta.get("type") == "article":
            body = article(meta, body, root)
        body = body.replace("{{sitemap}}", sitemap_html(root)).replace("{{root}}", root).replace("{{today}}", TODAY)
        out = head(meta, rel, root) + "\n" + header(meta.get("section", ""), root) + "\n" + body + footer(root, rel)
        dest = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write(out)
        if rel != "404.html":
            sitemap_entries.append((rel, meta))
    # sitemap.xml
    urls = []
    for rel, meta in sitemap_entries:
        loc = DOMAIN + ("" if rel == "index.html" else rel)
        pr = "1.0" if rel == "index.html" else ("0.9" if rel in ("match.html", "explore.html", "tools.html") else ("0.8" if rel.startswith("guides") else "0.6"))
        lm = TODAY if rel in FRESH else meta.get("reviewed", meta.get("published", BASE_DATE))
        urls.append(f"<url><loc>{loc}</loc><lastmod>{lm}</lastmod><priority>{pr}</priority></url>")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n")
    print(f"built {len(pages)} pages, {len(urls)} sitemap urls")


if __name__ == "__main__":
    build()
