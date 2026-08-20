#!/usr/bin/env python3
"""Bulk: recorre datos.gob.es, descarga XLSX de contratos (Euskadi y otros) e ingiere."""
import re
import subprocess
import urllib.request
import urllib.parse
import sys
from pathlib import Path

BASE = Path("/home/deploy/transparencia-osint")
DATA = BASE / "data"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0"


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=40).read()


def get_catalog_urls(limit_pages=30):
    urls = set()
    for p in range(1, limit_pages + 1):
        try:
            s = fetch(f"https://datos.gob.es/sitemap.xml?page={p}").decode("utf-8", "ignore")
        except Exception:
            continue
        for u in re.findall(r"<loc>([^<]*catalogo/[^<]*registro-de-contratos[^<]*)</loc>", s):
            urls.add(u)
    return urls


def get_xlsx_url(catalog_url):
    try:
        s = fetch(catalog_url).decode("utf-8", "ignore")
        for u in re.findall(r'href="([^"]*\.xlsx)"', s):
            if "opendata.euskadi.eus" in u and "adjuntos" in u:
                return u
    except Exception:
        pass
    return None


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(f"Buscando catalog de contratos (sitemap {limit} paginas)...")
    cats = sorted(get_catalog_urls(limit))
    print(f"Datasets de contratos encontrados: {len(cats)}")

    descargados = 0
    for i, cat in enumerate(cats[:40]):
        x = get_xlsx_url(cat)
        if not x:
            continue
        fn = DATA / f"bulk_{i}.xlsx"
        try:
            data = fetch(x)
            if len(data) < 2000:
                continue
            fn.write_bytes(data)
            subprocess.run([sys.executable, str(BASE / "ingest.py"), str(fn), f"entity{i}"],
                           capture_output=True)
            descargados += 1
            print(f"  [{i}] descargado e ingerido: {len(data)} bytes ({cat.split('/')[-1][:50]})")
        except Exception as e:
            print(f"  [{i}] error: {e}")
    print(f"Total ingeridos: {descargados}")


if __name__ == "__main__":
    main()
