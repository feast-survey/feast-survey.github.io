#!/usr/bin/env python3
"""
Update the FEAST publication list from the team's public ADS library.

Writes _data/publications.json, which the /publications/ page displays.
Run by the GitHub Action .github/workflows/update-publications.yml, or by hand:

    ADS_TOKEN=your_token python scripts/update_publications.py

Only the Python standard library is used.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

LIBRARY_ID = "GRuGsIj-ScC-PeUMHiq98w"     # FEAST public ADS library
API = "https://api.adsabs.harvard.edu/v1"
OUTFILE = Path(__file__).resolve().parent.parent / "_data" / "publications.json"
FIELDS = "bibcode,title,author,pub,year,pubdate,volume,page,doi,identifier,doctype"
N_AUTHORS = 3                              # authors shown before "et al."


def request(url, token, data=None):
    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        headers["Content-Type"] = "big-query/csv"
        data = data.encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def library_bibcodes(token):
    """All bibcodes in the library (paged)."""
    bibcodes, start, rows = [], 0, 100
    while True:
        q = urllib.parse.urlencode({"start": start, "rows": rows})
        res = request(f"{API}/biblib/libraries/{LIBRARY_ID}?{q}", token)
        docs = res.get("documents", [])
        bibcodes += docs
        n_total = res.get("metadata", {}).get("num_documents", len(bibcodes))
        start += rows
        if not docs or len(bibcodes) >= n_total:
            return bibcodes


def metadata(bibcodes, token):
    q = urllib.parse.urlencode({"q": "*:*", "fl": FIELDS, "rows": len(bibcodes), "sort": "date desc"})
    res = request(f"{API}/search/bigquery?{q}", token, data="bibcode\n" + "\n".join(bibcodes))
    return res["response"]["docs"]


def short_authors(authors):
    if not authors:
        return ""
    shown = "; ".join(authors[:N_AUTHORS])
    return shown + (" et al." if len(authors) > N_AUTHORS else "")


def to_entry(d):
    arxiv = next((i.split(":", 1)[1] for i in d.get("identifier", []) if i.lower().startswith("arxiv:")), None)
    doi = (d.get("doi") or [None])[0]
    pub = d.get("pub", "")
    vol, page = d.get("volume"), (d.get("page") or [None])[0]
    ref = ", ".join(x for x in [pub, vol, page] if x)
    return {
        "bibcode": d["bibcode"],
        "title": (d.get("title") or [""])[0],
        "authors": short_authors(d.get("author", [])),
        "n_authors": len(d.get("author", [])),
        "journal": ref,
        "year": d.get("year", ""),
        "pubdate": d.get("pubdate", ""),
        "ads": f"https://ui.adsabs.harvard.edu/abs/{d['bibcode']}/abstract",
        "arxiv": f"https://arxiv.org/abs/{arxiv}" if arxiv else None,
        "doi": f"https://doi.org/{doi}" if doi else None,
    }


def main():
    token = os.environ.get("ADS_TOKEN")
    if not token:
        sys.exit("ADS_TOKEN environment variable not set")
    bibcodes = library_bibcodes(token)
    if not bibcodes:
        sys.exit("The library returned no papers; not overwriting the existing list")
    entries = [to_entry(d) for d in metadata(bibcodes, token)]
    entries.sort(key=lambda e: e["pubdate"], reverse=True)
    OUTFILE.write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {len(entries)} publications to {OUTFILE}")


if __name__ == "__main__":
    main()
