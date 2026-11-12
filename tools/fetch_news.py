#!/usr/bin/env python3
"""Refreshes data/news.json from public news RSS feeds (run daily by GitHub Actions).

Standard library only. Keeps the newest 60 unique headlines, tagged by topic.
Existing items are kept and merged, so a failed feed never empties the page.
"""
import datetime, email.utils, json, os, re, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "news.json")
KEEP = 60
UA = {"User-Agent": "Mozilla/5.0 (compatible; FranchiseConnectionBot/1.0; +https://franchiseconnection.com/)"}

QUERIES = [
    ("Expansions", "franchise expansion new locations"),
    ("Deals", "franchise development agreement multi-unit"),
    ("Deals", "franchisor acquisition franchise brand acquired"),
    ("Lending", "SBA franchise loan financing"),
    ("Industry data", "franchise industry trends report"),
    ("Events", "franchise expo OR franchise conference"),
    ("New models", "launches franchise opportunity"),
    ("Canada", "franchise Canada expansion"),
]


def google_news(q):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q + " when:14d", "hl": "en-US", "gl": "US", "ceid": "US:en"})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def parse(xml, topic):
    items = []
    root = ET.fromstring(xml)
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        src_el = it.find("source")
        source = (src_el.text or "").strip() if src_el is not None else ""
        if source and title.endswith(" - " + source):
            title = title[: -len(" - " + source)]
        try:
            dt = email.utils.parsedate_to_datetime(it.findtext("pubDate") or "")
            date = dt.astimezone(datetime.timezone.utc).isoformat()
        except Exception:
            date = ""
        if title and link and re.search(r"franchis", title, re.I):
            items.append({"title": title, "link": link, "source": source, "date": date, "topic": topic})
    return items


def key(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())[:70]


def main():
    try:
        old = json.load(open(OUT)).get("items", [])
    except Exception:
        old = []
    fresh = []
    for topic, q in QUERIES:
        try:
            fresh += parse(google_news(q), topic)
        except Exception as e:  # keep going if one feed fails
            print("feed failed:", q, e)
    seen, merged = set(), []
    for it in sorted(fresh + old, key=lambda x: x.get("date", ""), reverse=True):
        k = key(it["title"])
        if k in seen:
            continue
        seen.add(k)
        merged.append(it)
    merged = merged[:KEEP]
    data = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "count": len(merged), "items": merged}
    json.dump(data, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"{len(fresh)} fetched, {len(merged)} kept")


if __name__ == "__main__":
    main()
