#!/usr/bin/env python3
"""Reingesta con nombres reales de entidad + dashboard."""
import re
import subprocess
import sqlite3
import urllib.request
import sys
from pathlib import Path

BASE = Path("/home/deploy/transparencia-osint")
DATA = BASE / "data"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40).read()


def real_name(slug):
    m = re.search(r"registro-de-contratos-de-(.+)-\d{4}", slug)
    name = m.group(1) if m else slug
    return name.replace("-", " ").title()


def main():
    # vaciar DB de contratos (fuente bulk vieja)
    conn = sqlite3.connect(DATA / "transparencia.db")
    conn.execute("DELETE FROM contratos")
    conn.commit()
    conn.close()

    cats = []
    for p in range(1, 16):
        try:
            s = fetch(f"https://datos.gob.es/sitemap.xml?page={p}").decode("utf-8", "ignore")
        except Exception:
            continue
        cats += re.findall(r"<loc>([^<]*catalogo/[^<]*registro-de-contratos[^<]*)</loc>", s)
    print(f"datasets: {len(cats)}")

    ing = 0
    for i, cat in enumerate(sorted(set(cats))[:40]):
        try:
            s = fetch(cat).decode("utf-8", "ignore")
        except Exception:
            continue
        x = None
        for u in re.findall(r'href="([^"]*\.xlsx)"', s):
            if "opendata.euskadi.eus" in u and "adjuntos" in u:
                x = u
                break
        if not x:
            continue
        try:
            data = fetch(x)
            if len(data) < 2000:
                continue
            fn = DATA / f"d_{i}.xlsx"
            fn.write_bytes(data)
            name = real_name(cat.split("/")[-1])
            subprocess.run([sys.executable, str(BASE / "ingest.py"), str(fn), name], capture_output=True)
            ing += 1
            print(f"  {name[:45]} ({len(data)}b)")
        except Exception as e:
            print(f"  err {i}: {e}")
    print(f"ingeridos: {ing}")


if __name__ == "__main__":
    main()
