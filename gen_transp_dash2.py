#!/usr/bin/env python3
"""Dashboard INTERACTIVO de transparencia_osint: filtros, sin listados estáticos."""
import json
import sqlite3
import datetime
from pathlib import Path

DB = "/home/deploy/transparencia-osint/data/transparencia.db"
OUT = Path("/home/deploy/transparencia-osint/dashboard/index.html")
SITE = "https://transparencia.viajeinteligencia.com"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT poder, razon_social, cif, tipo_contrato, procedimiento, importe, fecha_adjudicacion, cpv "
    "FROM contratos").fetchall()
data = []
for r in rows:
    data.append({
        "poder": r["poder"], "empresa": r["razon_social"], "cif": r["cif"],
        "tipo": r["tipo_contrato"] or "?", "proc": r["procedimiento"] or "?",
        "importe": r["importe"], "fecha": r["fecha_adjudicacion"] or "", "cpv": r["cpv"] or "",
        "ccaa": "Euskadi",
    })

hoy = datetime.date.today().isoformat()

html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>transparencia_osint · Consulta de contratos públicos con filtros | Viaje Inteligencia</title>
<meta name="description" content="Consulta interactiva de contratos públicos españoles: filtra por entidad, empresa, tipo, importe y detecta concentración de contratos menores y troceado. Datos oficiales abiertos.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{SITE}/">
<meta property="og:title" content="transparencia_osint · Contratación pública con filtros">
<meta property="og:locale" content="es_ES">
<style>
body {{ font-family:-apple-system,'Inter',sans-serif;background:#0b0f17;color:#e7ebf3;max-width:1100px;margin:0 auto;padding:20px;line-height:1.5;}}
h1 {{ font-size:1.4em;margin-bottom:2px;}} .sub {{ color:#8993a8;font-size:0.9em;}}
a {{ color:#67e8f9;}}
.filtros {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;background:#0e1322;border:1px solid #232b3d;border-radius:10px;padding:14px;margin:14px 0;}}
.filtros label {{ font-size:0.7em;color:#8993a8;display:block;margin-bottom:2px;}}
.filtros input,.filtros select {{ width:100%;background:#0b0f17;border:1px solid #232b3d;color:#e7ebf3;border-radius:6px;padding:7px;font-size:0.85em;box-sizing:border-box;}}
.kpis {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:12px 0;}}
.kpi {{ background:#0e1322;border:1px solid #232b3d;border-radius:10px;padding:10px 12px;}}
.kpi .n {{ font-size:1.3em;font-weight:700;color:#ffb454;}} .kpi .l {{ font-size:0.7em;color:#8993a8;}}
table {{ width:100%;border-collapse:collapse;font-size:0.8em;margin-top:8px;}}
th,td {{ text-align:left;padding:5px 8px;border-bottom:1px solid #1a2233;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:220px;}}
th {{ color:#8993a8;position:sticky;top:0;background:#0b0f17;}}
tr.anom {{ background:#2a1215; }}
.cont {{ max-height:420px;overflow:auto;border:1px solid #1a2233;border-radius:8px;}}
.met {{ font-size:0.75em;color:#8993a8;border-top:1px solid #232b3d;margin-top:18px;padding-top:10px;}}
.badge {{ background:#f87171;color:#fff;border-radius:6px;padding:2px 8px;font-size:0.7em;}}
</style>
</head>
<body>
<h1>🔎 transparencia_osint · Contratos públicos con filtros</h1>
<p class="sub">Filtra los contratos por entidad, empresa, tipo o importe. Las filas en rojo son posibles anomalías (empresa con ≥5 contratos menores a una misma entidad). Actualizado {hoy}.</p>

<div class="filtros">
  <div><label>Buscar (empresa/entidad/objeto)</label><input id="q" placeholder="ej. Netto, Vitoria..."></div>
  <div><label>Entidad</label><select id="fEnt"></select></div>
  <div><label>Empresa</label><select id="fEmp"></select></div>
  <div><label>Tipo contrato</label><select id="fTipo"></select></div>
  <div><label>Procedimiento</label><select id="fProc"></select></div>
  <div><label>Importe mín (€)</label><input id="fMin" type="number" placeholder="0"></div>
  <div><label>Importe máx (€)</label><input id="fMax" type="number" placeholder="999999"></div>
  <div><label>Comunidad</label><select id="fCcaa"></select></div>
  <label style="align-self:end;"><input id="fMenor" type="checkbox"> Solo contratos menores</label>
  <label style="align-self:end;"><input id="fAnom" type="checkbox"> Solo anomalías</label>
  <button id="reset" style="background:#232b3d;border:1px solid #3a4660;color:#e7ebf3;border-radius:6px;padding:7px;cursor:pointer;">Limpiar filtros</button>
</div>

<div class="kpis">
  <div class="kpi"><div class="n" id="kTotal">0</div><div class="l">contratos</div></div>
  <div class="kpi"><div class="n" id="kSuma">0 €</div><div class="l">importe</div></div>
  <div class="kpi"><div class="n" id="kEmp">0</div><div class="l">empresas</div></div>
  <div class="kpi"><div class="n" id="kEnt">0</div><div class="l">entidades</div></div>
  <div class="kpi"><div class="n" id="kAnom">0</div><div class="l">anomalías</div></div>
</div>

<div class="cont">
<table><thead><tr><th>Entidad</th><th>Empresa</th><th>Importe</th><th>Fecha</th><th>Tipo</th><th>Procedimiento</th><th>CPV</th><th>CCAA</th></tr></thead>
<tbody id="tbody"></tbody></table>
</div>

<div class="met">
<b>Metodología y fuentes:</b> datos oficiales abiertos de contratación de Euskadi publicados en <a href="https://datos.gob.es" rel="noopener">datos.gob.es</a> (registro de contratos por entidad). Reglas: <b>concentración</b> = misma empresa con ≥5 contratos menores a una misma entidad; <b>troceado</b> = misma empresa + misma entidad con contratos <15.000 € cada uno que suman &gt;15.000 € en una ventana de 90 días. <b>Cobertura actual: solo Euskadi</b> (el resto de España, incluida Murcia, publica vía PLACSP, pendiente de integrar). Los datos requieren verificación antes de concluir.
<br>© <a href="https://www.viajeinteligencia.com/">Viaje Inteligencia</a> · contacto: <a href="mailto:nearme@viajeinteligencia.com">nearme@viajeinteligencia.com</a>
</div>

<script>
const DATA = {json.dumps(data, ensure_ascii=False)};

// anomalías: empresa con >=5 menores a la misma entidad
const contAnom = {{}};
DATA.forEach(c => {{
  if (c.proc && c.proc.toLowerCase().includes('menor')) {{
    const k = c.cif + '|' + c.poder;
    contAnom[k] = (contAnom[k] || 0) + 1;
  }}
}});
const anomKeys = new Set(Object.keys(contAnom).filter(k => contAnom[k] >= 5));

function esc(s) {{ return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
function fmt(v) {{ return v == null ? '—' : Number(v).toLocaleString('es-ES',{{maximumFractionDigits:0}}) + ' €'; }}

function fill(id, fn) {{
  const el = document.getElementById(id);
  const s = new Set(DATA.map(fn));
  el.innerHTML = '<option value="">Todos</option>' + [...s].sort().map(x => `<option>${{esc(x)}}</option>`).join('');
}}

function apply() {{
  const q = document.getElementById('q').value.toLowerCase();
  const fEnt = document.getElementById('fEnt').value;
  const fEmp = document.getElementById('fEmp').value;
  const fTipo = document.getElementById('fTipo').value;
  const fProc = document.getElementById('fProc').value;
  const fMin = parseFloat(document.getElementById('fMin').value) || 0;
  const fMax = parseFloat(document.getElementById('fMax').value) || 1e15;
  const fCcaa = document.getElementById('fCcaa').value;
  const fMenor = document.getElementById('fMenor').checked;
  const fAnom = document.getElementById('fAnom').checked;

  let out = DATA.filter(c => {{
    if (q && !(c.empresa+' '+c.poder+' '+(c.cpv||'')).toLowerCase().includes(q)) return false;
    if (fEnt && c.poder !== fEnt) return false;
    if (fEmp && c.empresa !== fEmp) return false;
    if (fTipo && c.tipo !== fTipo) return false;
    if (fProc && c.proc !== fProc) return false;
    if (c.importe != null && (c.importe < fMin || c.importe > fMax)) return false;
    if (fCcaa && c.ccaa !== fCcaa) return false;
    if (fMenor && !(c.proc && c.proc.toLowerCase().includes('menor'))) return false;
    if (fAnom && !anomKeys.has(c.cif + '|' + c.poder)) return false;
    return true;
  }});

  const suma = out.reduce((s,c) => s + (c.importe || 0), 0);
  document.getElementById('kTotal').textContent = out.length;
  document.getElementById('kSuma').textContent = fmt(suma);
  document.getElementById('kEmp').textContent = new Set(out.map(c=>c.cif)).size;
  document.getElementById('kEnt').textContent = new Set(out.map(c=>c.poder)).size;
  document.getElementById('kAnom').textContent = out.filter(c=>anomKeys.has(c.cif+'|'+c.poder)).length;

  const tb = document.getElementById('tbody');
  tb.innerHTML = out.slice(0, 300).map(c => {{
    const an = anomKeys.has(c.cif + '|' + c.poder);
    return `<tr class="${{an ? 'anom' : ''}}"><td>${{esc(c.poder)}}</td><td>${{esc(c.empresa)}}</td><td>${{fmt(c.importe)}}</td><td>${{esc(c.fecha)}}</td><td>${{esc(c.tipo)}}</td><td>${{esc(c.proc)}}</td><td>${{esc(c.cpv)}}</td><td>${{esc(c.ccaa)}}</td></tr>`;
  }}).join('') || '<tr><td colspan="8">Sin resultados con estos filtros.</td></tr>';
}}

fill('fEnt', c=>c.poder); fill('fEmp', c=>c.empresa); fill('fTipo', c=>c.tipo); fill('fProc', c=>c.proc); fill('fCcaa', c=>c.ccaa);
['q','fEnt','fEmp','fTipo','fProc','fMin','fMax','fCcaa','fMenor','fAnom'].forEach(id => document.getElementById(id).addEventListener(id==='q'?'input':'change', apply));
document.getElementById('reset').onclick = () => {{ ['q','fEnt','fEmp','fTipo','fProc','fMin','fMax','fCcaa'].forEach(id=>document.getElementById(id).value=''); document.getElementById('fMenor').checked=false; document.getElementById('fAnom').checked=false; apply(); }};
apply();
</script>
</body></html>"""

OUT.write_text(html, encoding="utf-8")
print(f"OK: dashboard interactivo generado · {len(data)} contratos embebidos")
