import sqlite3

conn = sqlite3.connect("data/transparencia.db")
cols = [r[1] for r in conn.execute("PRAGMA table_info(contratos)")]
if "ccaa" not in cols:
    conn.execute("ALTER TABLE contratos ADD COLUMN ccaa TEXT")
    print("columna ccaa anadida")
else:
    print("ccaa ya existe")
conn.close()
