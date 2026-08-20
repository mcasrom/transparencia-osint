#!/usr/bin/env python3
"""Reglas de anomalía sobre la tabla contratos (transparencia_osint)."""
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta

DB = "/home/deploy/transparencia-osint/data/transparencia.db"

LIMITE_MENOR_SERVICIOS = 15000.0
LIMITE_MENOR_OBRAS = 40000.0


def detect_troceado(conn):
    """Misma empresa + mismo poder + contratos menores + importes cerca del
    limite + ventana corta -> posible troceado."""
    rows = conn.execute("SELECT cif, razon_social, poder, fecha_adjudicacion, importe, procedimiento FROM contratos WHERE importe IS NOT NULL AND fecha_adjudicacion IS NOT NULL").fetchall()
    grupos = defaultdict(list)
    for cif, rs, poder, fecha, imp, proc in rows:
        try:
            d = datetime.strptime(fecha, "%Y-%m-%d")
        except Exception:
            continue
        grupos[(cif, poder)].append({"fecha": d, "importe": imp, "procedimiento": proc, "razon": rs})
    flags = []
    for (cif, poder), items in grupos.items():
        items.sort(key=lambda x: x["fecha"])
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                dias = (items[j]["fecha"] - items[i]["fecha"]).days
                if dias > 90:
                    break
                a, b = items[i], items[j]
                if a["importe"] < LIMITE_MENOR_SERVICIOS and b["importe"] < LIMITE_MENOR_SERVICIOS and a["importe"] + b["importe"] > LIMITE_MENOR_SERVICIOS:
                    flags.append((cif, poder, a["razon"], a["fecha"].date(), a["importe"], b["fecha"].date(), b["importe"]))
    return flags


def detect_concentracion(conn):
    """Empresa que acapara contratos menores de un poder."""
    rows = conn.execute("SELECT cif, razon_social, poder, procedimiento, COUNT(*) FROM contratos WHERE procedimiento LIKE '%menor%' GROUP BY cif, poder").fetchall()
    out = [r for r in rows if r[4] >= 3]
    return sorted(out, key=lambda x: -x[4])


def main():
    conn = sqlite3.connect(DB)
    total = conn.execute("SELECT COUNT(*) FROM contratos").fetchone()[0]
    print(f"Contratos en DB: {total}")
    print("\n=== POSIBLE TROCEADO (misma empresa+poder, <15k c/u, suma>15k, ventana 90d) ===")
    for f in detect_troceado(conn):
        print(f"  {f[0]} {f[2]}: {f[3]} {f[4]:.0f}€ + {f[5]} {f[6]:.0f}€")
    if not detect_troceado(conn):
        print("  (ninguno en este dataset)")
    print("\n=== CONCENTRACIÓN (contratos menores por empresa+poder) ===")
    for cif, rs, poder, proc, n in detect_concentracion(conn):
        print(f"  {cif} {rs}: {n} menores a {poder}")
    conn.close()


if __name__ == "__main__":
    main()
