import json, re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

SOURCES = [
    ("Search Engine Journal", "https://www.searchenginejournal.com/feed/", ["SEO","AI Search","Ads"]),
    ("Google Search Central", "https://developers.google.com/search/blog/feed.xml", ["Google","SEO","Technical"]),
    ("Search Engine Roundtable", "https://www.seroundtable.com/index.xml", ["Google","SEO","Technical"]),
    ("Search Engine Land", "https://searchengineland.com/feed", ["SEO","Google","AI Search","Ads"]),
]

def clean(value):
    value = value or ""
    value = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", value, flags=re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()

def local_name(tag):
    return tag.split("}")[-1].lower()

def child_text(node, wanted):
    wanted = {x.lower() for x in wanted}
    for child in list(node):
        tag = local_name(child.tag)
        if tag in wanted:
            if tag == "link" and child.attrib.get("href"):
                return child.attrib["href"]
            return "".join(child.itertext())
    return ""

def parse_date(value):
    value = clean(value)
    if not value:
        return datetime.now(timezone.utc).isoformat()
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except Exception:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()

def fetch(source):
    name, url, tags = source
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 SEO-Updates-GitHub/2.0",
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
            },
        )
        with urllib.request.urlopen(request, timeout=25) as response:
            raw = response.read()

        root = ET.fromstring(raw)
        nodes = [n for n in root.iter() if local_name(n.tag) in {"item", "entry"}]

        items = []
        for node in nodes:
            title = clean(child_text(node, {"title"}))
            link = child_text(node, {"link"}).strip()

            if not link:
                for child in list(node):
                    if local_name(child.tag) == "link" and child.attrib.get("href"):
                        link = child.attrib["href"].strip()
                        break

            date = child_text(node, {"pubdate", "published", "updated", "date"})
            description = clean(child_text(node, {"description", "summary", "encoded", "content"}))

            if title and link:
                items.append({
                    "title": title,
                    "link": link,
                    "date": parse_date(date),
                    "description": description,
                    "source": name,
                    "tags": tags,
                })

        return items, {"name": name, "ok": True, "count": len(items)}
    except Exception as exc:
        return [], {"name": name, "ok": False, "count": 0, "error": str(exc)}

all_items = []
states = []

for source in SOURCES:
    items, state = fetch(source)
    all_items.extend(items)
    states.append(state)

unique = {}
for item in all_items:
    unique.setdefault(item["link"], item)

items = sorted(unique.values(), key=lambda x: x["date"], reverse=True)[:200]

data = {
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "items": items,
    "sources": states,
}

Path("data.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"Collected {len(items)} unique articles.")
for state in states:
    status = "OK" if state["ok"] else "FAILED"
    print(f'{state["name"]}: {status} ({state["count"]})')

if not items:
    raise SystemExit("No RSS articles were collected; refusing to overwrite the feed with an empty result.")
