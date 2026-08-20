import sqlite3
import pandas as pd
from pathlib import Path

DB = Path("/home/deploy/transparencia-osint/data/transparencia.db")
CSV = Path("/home/deploy/transparencia-osint/data/baleares.csv")


def parse_amt(v):
    if v is None or pd.isna(v):
        return None
    s = str(v).replace(".", "").replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return None


def main():
    df = pd.read_csv(CSV, sep=";")
    conn = sqlite3.connect(DB)
    n = 0
    for _, r in df.iterrows():
        nombre = str(r.get("NOMBRE", "")).strip()
        if not nombre or nombre.lower() == "nan":
            continue
        cif = str(r.get("CIF", "")).strip()
        imp = parse_amt(r.get("IMPORTE TOTAL"))
        nro = r.get("NÚMERO ADJUDICACIONES")
        conn.execute(
            "INSERT INTO contratos (objeto, codigo, cif, razon_social, tipo_contrato, procedimiento, poder, fecha_adjudicacion, importe, importe_iva, cpv, fuente, ccaa) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (f"Agregado Baleares: {nro} adjudicaciones" if nro else "", f"BA-{cif}", cif, nombre,
             "Agregado", "Agregado (Baleares)", "Illes Balears (Gobierno)", None,
             imp, imp, "", "caib.es", "Illes Balears"))
        n += 1
    conn.commit()
    conn.close()
    print(f"OK: {n} empresas de Baleares ingeridas")


if __name__ == "__main__":
    main()
