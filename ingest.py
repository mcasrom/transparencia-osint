#!/usr/bin/env python3
"""Ingesta de contratos Euskadi (datos.gob.es XLSX) -> sqlite normalizado."""
import re
import sqlite3
import sys
import pandas as pd
from pathlib import Path

BASE = Path("/home/deploy/transparencia-osint")
DB = BASE / "data" / "transparencia.db"


def parse_amount(v):
    if v is None or pd.isna(v):
        return None
    s = str(v).replace(".", "").replace(",", ".").replace("€", "").strip()
    try:
        return float(s)
    except Exception:
        return None


def parse_date(v):
    if v is None or pd.isna(v):
        return None
    s = str(v).strip()
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return s[:10]
    return None


def ingest(xlsx, poder):
    df = pd.read_excel(xlsx, sheet_name="Catalogo contratos", header=5)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Razón social"])
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS contratos (
        id INTEGER PRIMARY KEY,
        objeto TEXT, codigo TEXT, cif TEXT, razon_social TEXT,
        tipo_contrato TEXT, procedimiento TEXT, poder TEXT,
        fecha_adjudicacion TEXT, importe REAL, importe_iva REAL, cpv TEXT,
        fuente TEXT)""")
    n = 0
    for _, r in df.iterrows():
        rs = str(r.get("Razón social", "")).strip()
        if not rs or rs.lower() == "nan":
            continue
        conn.execute(
            "INSERT INTO contratos (objeto, codigo, cif, razon_social, tipo_contrato, procedimiento, poder, fecha_adjudicacion, importe, importe_iva, cpv, fuente) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (str(r.get("Objeto del contrato", ""))[:300], str(r.get("Código del contrato", "")),
             str(r.get("CIF/NIF", "")).strip(), rs,
             str(r.get("Tipo contrato", "")), str(r.get("Procedimiento de adjudicación", "")),
             poder, parse_date(r.get("Fecha de adjudicación")),
             parse_amount(r.get("Importe de adjudicación")), parse_amount(r.get("Importe de adjudicación con IVA")),
             str(r.get("CPV", ""))[:10], "euskadi-datos.gob.es"))
        n += 1
    conn.commit()
    conn.close()
    print(f"OK: {n} contratos de {poder} ingeridos en {DB}")


if __name__ == "__main__":
    xlsx = sys.argv[1] if len(sys.argv) > 1 else BASE / "data" / "bilbao_zerbitzuak.xlsx"
    poder = sys.argv[2] if len(sys.argv) > 2 else "Bilbao Zerbitzuak"
    ingest(str(xlsx), poder)
