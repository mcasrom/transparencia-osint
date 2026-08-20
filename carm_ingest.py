import sqlite3
import re
import pandas as pd
from pathlib import Path

DB = Path("/home/deploy/transparencia-osint/data/transparencia.db")
CSV = Path("/home/deploy/transparencia-osint/data/carm_menores.csv")


def parse_date(v):
    if v is None or pd.isna(v):
        return None
    m = re.match(r"(\d{2})-(\d{2})-(\d{2})", str(v))
    if m:
        mm, dd, yy = m.group(1), m.group(2), m.group(3)
        try:
            return f"20{yy}-{mm}-{dd}"
        except Exception:
            return None
    return None


def main():
    df = pd.read_csv(CSV)
    conn = sqlite3.connect(DB)
    n = 0
    for _, r in df.iterrows():
        emp = str(r.get("ADJUDICATARIODESCRIPCION", "")).strip()
        if not emp or emp.lower() == "nan":
            continue
        cif = str(r.get("ADJUDICATARIOCODIGO", "")).strip()
        imp = r.get("IMPORTECONTABPAGO")
        unidad = str(r.get("UNIDADDESCRIPCION", "")).strip()
        conn.execute(
            "INSERT INTO contratos (objeto, codigo, cif, razon_social, tipo_contrato, procedimiento, poder, fecha_adjudicacion, importe, importe_iva, cpv, fuente, ccaa) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (str(r.get("OBJETO_CONTRATO_MENOR", ""))[:300], str(r.get("CODEXPEDIENTE", "")),
             cif, emp, str(r.get("TIPOCONTRATO", "")), "Directo/Contrato Menor", unidad or "Región de Murcia",
             parse_date(r.get("FECHACONTABPAGO")), float(imp) if pd.notna(imp) else None,
             float(imp) if pd.notna(imp) else None, str(r.get("CPVCODIGO", ""))[:10],
             "datosabiertos.carm.es", "Región de Murcia"))
        n += 1
    conn.commit()
    conn.close()
    print(f"OK: {n} contratos menores CARM ingeridos (ccaa=Región de Murcia)")


if __name__ == "__main__":
    main()
