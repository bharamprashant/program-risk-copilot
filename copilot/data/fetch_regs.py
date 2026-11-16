"""Download DORA, GDPR and PSD2 from the EU Publications Office and split them into article chunks.

Why article-level chunks: a citation must point to something a compliance officer can open
("DORA Art. 28"). Fixed-size chunks would cut articles in half and make citations meaningless.
Long articles are split by paragraph so each chunk stays small enough to retrieve precisely.
"""
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

REGS = {
    "DORA": ("32022R2554", "Regulation (EU) 2022/2554 (Digital Operational Resilience Act)"),
    "GDPR": ("32016R0679", "Regulation (EU) 2016/679 (General Data Protection Regulation)"),
    "PSD2": ("32015L2366", "Directive (EU) 2015/2366 (Payment Services Directive 2)"),
}
RAW = Path("data/raw/regs")
OUT = Path("data/processed/chunks.jsonl")
MAX_WORDS = 350


def download(celex: str) -> str:
    path = RAW / f"{celex}.xhtml"
    if not path.exists():
        r = requests.get(f"https://publications.europa.eu/resource/celex/{celex}",
                         headers={"Accept": "application/xhtml+xml", "Accept-Language": "eng"}, timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path.read_text(encoding="utf-8")


def split_paragraphs(text: str) -> list[str]:
    # Paragraphs in EU law start with "1.   ", "2.   " ...; keep the number with its text.
    parts = re.split(r"(?=(?:^|\s)\d{1,2}\.\s{2,})", text)
    chunks, cur = [], ""
    for p in parts:
        if cur and len((cur + p).split()) > MAX_WORDS:
            chunks.append(cur.strip())
            cur = p
        else:
            cur += p
    if cur.strip():
        chunks.append(cur.strip())
    # Some articles (e.g. definitions) number items as (1), (2) instead of "1.": fall back to word windows.
    final = []
    for c in chunks:
        words = c.split()
        if len(words) <= MAX_WORDS * 1.5:
            final.append(c)
        else:
            final += [" ".join(words[i:i + MAX_WORDS]) for i in range(0, len(words), MAX_WORDS)]
    return final


def articles(reg: str, celex: str, html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for div in soup.find_all("div", id=re.compile(r"^art_\d+$")):
        num = div["id"].split("_")[1]
        title_el = div.find(class_="eli-title")
        title = title_el.get_text(" ", strip=True) if title_el else ""
        body = div.get_text(" ", strip=True)
        body = re.sub(rf"^\W*Article\W+{num}\W*", "", body)
        if title and body.startswith(title):
            body = body[len(title):].strip()
        for i, part in enumerate(split_paragraphs(body)):
            out.append({
                "id": f"{reg}-art{num}-{i}",
                "reg": reg,
                "article": int(num),
                "title": title,
                "citation": f"{reg} Art. {num}" + (f" — {title}" if title else ""),
                "source": f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex}#art_{num}",
                "text": part,
            })
    return out


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    all_chunks = []
    for reg, (celex, name) in REGS.items():
        chunks = articles(reg, celex, download(celex))
        print(f"{reg}: {len({c['article'] for c in chunks})} articles -> {len(chunks)} chunks")
        all_chunks += chunks
    with OUT.open("w") as fh:
        for c in all_chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"wrote {len(all_chunks)} chunks to {OUT}")
