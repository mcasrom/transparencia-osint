#!/usr/bin/env python3
"""Dashboard transparencia_osint v4: tema claro/oscuro + KPIs impactantes + donut + rankings."""
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
    "SELECT poder, razon_social, cif, tipo_contrato, procedimiento, importe, fecha_adjudicacion, cpv, ccaa FROM contratos").fetchall()
data = [{"poder": r["poder"], "empresa": r["razon_social"], "cif": r["cif"], "tipo": r["tipo_contrato"] or "?",
         "proc": r["procedimiento"] or "?", "importe": r["importe"], "fecha": r["fecha_adjudicacion"] or "",
         "cpv": r["cpv"] or "", "ccaa": r["ccaa"] or "?"} for r in rows]
hoy = datetime.datetime.now().strftime("%d/%m/%Y %H:%M") + " UTC"

html = f"""<!doctype html>
<html lang="es" data-theme="dark">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>transparencia_osint · Contratos públicos: filtros, rankings y análisis | Viaje Inteligencia</title>
<meta name="description" content="Consulta interactiva de contratos públicos españoles con filtros, top rankings, gasto por tipo y detección de anomalías (concentración de contratos menores). Datos oficiales abiertos.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{SITE}/">
<meta property="og:locale" content="es_ES">
<style>
:root {{
  --bg:#0b0f17; --panel:#0e1322; --panel2:#121826; --line:#232b3d; --text:#e7ebf3;
  --dim:#8993a8; --accent:#ffb454; --red:#f87171; --green:#34d399; --cyan:#67e8f9; --input:#0b0f17;
}}
[data-theme="light"] {{
  --bg:#f4f6fb; --panel:#ffffff; --panel2:#eef1f8; --line:#d6ddea; --text:#16202e;
  --dim:#5b6b84; --accent:#d9820a; --red:#dc4c4c; --green:#0e9f6e; --cyan:#0e9fae; --input:#ffffff;
}}
* {{ box-sizing:border-box; }}
body {{ font-family:-apple-system,'Inter',sans-serif;background:var(--bg);color:var(--text);max-width:1150px;margin:0 auto;padding:18px;line-height:1.5;transition:background .3s,color .3s;overflow-x:hidden;}}
h1 {{ font-size:1.35em;margin:0;}} .sub {{ color:var(--dim);font-size:0.88em;margin:4px 0 12px;}}
a {{ color:var(--cyan);}}
.top {{ display:flex;justify-content:space-between;align-items:center;gap:10px;}}
.toggle {{ background:var(--panel);border:1px solid var(--line);color:var(--text);border-radius:8px;padding:7px 14px;cursor:pointer;font-size:0.85em;}}
.filtros {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;margin:12px 0;}}
.filtros label {{ font-size:0.7em;color:var(--dim);display:block;margin-bottom:2px;}}
.filtros input,.filtros select {{ width:100%;background:var(--input);border:1px solid var(--line);color:var(--text);border-radius:6px;padding:7px;font-size:0.85em;}}
.kpis {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:14px 0;}}
.kpi {{ border-radius:14px;padding:16px;position:relative;overflow:hidden;}}
.kpi .n {{ font-size:1.9em;font-weight:800;line-height:1;}}
.kpi .l {{ font-size:0.72em;opacity:.85;margin-top:4px;}}
.kpi .ic {{ position:absolute;right:10px;top:10px;font-size:1.6em;opacity:.35;}}
.kp1 {{ background:linear-gradient(135deg,#7f1d1d,#b91c1c);color:#fff;}}
.kp2 {{ background:linear-gradient(135deg,#1e3a8a,#1d4ed8);color:#fff;}}
.kp3 {{ background:linear-gradient(135deg,#14532d,#15803d);color:#fff;}}
.kp4 {{ background:linear-gradient(135deg,#713f12,#b45309);color:#fff;}}
.kp5 {{ background:linear-gradient(135deg,#4a044e,#86198f);color:#fff;}}
.layout {{ display:grid;grid-template-columns:1.3fr 1fr;gap:14px;}}
.layout > * {{ min-width:0; }}
.filtros > div {{ min-width:0; }}
.panel {{ background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;}}
.panel h3 {{ margin:0 0 10px;font-size:0.95em;color:var(--accent);}}
.panel select {{ width:100%;background:var(--input);border:1px solid var(--line);color:var(--text);border-radius:6px;padding:7px;font-size:0.85em;margin-bottom:8px;}}
table {{ width:100%;border-collapse:collapse;font-size:0.78em;table-layout:fixed;}}
th,td {{ text-align:left;padding:5px 7px;border-bottom:1px solid var(--line);max-width:340px;word-wrap:break-word;}}
th {{ color:var(--dim);position:sticky;top:0;background:var(--panel);}}
tr.anom {{ background:rgba(220,38,38,.18); }}
.cont {{ max-height:430px;overflow:auto;border:1px solid var(--line);border-radius:8px;}}
.rank {{ font-size:0.85em;}}
.rank .row {{ display:flex;align-items:center;gap:8px;margin:5px 0;}}
.rank .lab {{ min-width:240px;font-size:0.85em;word-wrap:break-word;}}
.rank .bar {{ height:16px;border-radius:4px;background:linear-gradient(90deg,var(--red),var(--accent));}}
svg {{ max-width:100%;height:auto; }}
.met {{ font-size:0.72em;color:var(--dim);border-top:1px solid var(--line);margin-top:16px;padding-top:10px;}}
.donut-wrap {{ text-align:center; }}
</style>
</head>
<body>
<div class="top">
  <div><h1>🔎 transparencia_osint · Contratos públicos</h1><div class="sub">Filtra y analiza. El criterio lo pones tú. Actualizado {hoy}.</div></div>
  <button class="toggle" id="themeBtn" onclick="toggleTheme()">🌙 Oscuro</button>
</div>

<div class="filtros">
  <div><label>Buscar</label><input id="q" placeholder="empresa, entidad, CPV"></div>
  <div><label>Entidad</label><select id="fEnt"></select></div>
  <div><label>Empresa</label><select id="fEmp"></select></div>
  <div><label>Tipo</label><select id="fTipo"></select></div>
  <div><label>Procedimiento</label><select id="fProc"></select></div>
  <div><label>Importe mín (€)</label><input id="fMin" type="number"></div>
  <div><label>Importe máx (€)</label><input id="fMax" type="number"></div>
  <div><label>Comunidad</label><select id="fCcaa"></select></div>
  <label style="align-self:end;"><input id="fMenor" type="checkbox"> Solo menores</label>
  <label style="align-self:end;"><input id="fAnom" type="checkbox"> Solo anomalías</label>
  <button id="reset" style="background:var(--panel2);border:1px solid var(--line);color:var(--text);border-radius:6px;padding:7px;cursor:pointer;">Limpiar</button>
</div>

<div class="kpis">
  <div class="kpi kp1"><div class="ic">📑</div><div class="n" id="kTotal">0</div><div class="l">contratos</div></div>
  <div class="kpi kp2"><div class="ic">💰</div><div class="n" id="kSuma">0 €</div><div class="l">gasto total</div></div>
  <div class="kpi kp3"><div class="ic">🏭</div><div class="n" id="kEmp">0</div><div class="l">empresas</div></div>
  <div class="kpi kp4"><div class="ic">🏛️</div><div class="n" id="kEnt">0</div><div class="l">entidades</div></div>
  <div class="kpi kp5"><div class="ic">🚨</div><div class="n" id="kAnom">0</div><div class="l">posibles anomalías</div></div>
</div>

<div class="layout">
  <div class="panel">
    <h3>📊 Ranking Top 10</h3>
    <select id="rankSel">
      <option value="contratos">Top contratos por importe</option>
      <option value="gastoEmp">Top empresas por gasto total</option>
      <option value="gastoEnt">Top entidades por gasto total</option>
      <option value="nContratos">Top empresas por nº contratos</option>
      <option value="tipo">Gasto por tipo</option>
      <option value="proc">Gasto por procedimiento</option>
    </select>
    <div id="rankBox" class="rank"></div>
    <h3 style="margin-top:14px;">🥧 Gasto por tipo de contrato</h3>
    <div id="donutWrap" class="donut-wrap"></div>
  </div>
  <div class="panel">
    <h3>🏷️ Detalle (Top 20)</h3>
    <div class="cont"><table><thead><tr><th>Entidad</th><th>Empresa</th><th>Importe</th><th>Fecha</th><th>CCAA</th></tr></thead><tbody id="tbody"></tbody></table></div>
  </div>
</div>

<div class="met">
<b>Metodología y fuentes:</b> datos oficiales abiertos de contratación (datos.gob.es): Euskadi (registro por entidad) + Baleares (adjudicatarios) + Valencia (pendiente). Reglas: <b>concentración</b> = empresa con ≥5 contratos menores a una misma entidad; <b>troceado</b> = misma empresa+entidad, &lt;15.000 € c/u sumando &gt;15.000 € en 90 días. <b>Cobertura: Euskadi, Illes Balears y Región de Murcia (CARM 2023, contratos menores)</b>. Resto de CCAA pendientes (buscar dataset regional o PLACSP). Los datos requieren verificación.
<br>© <a href="https://www.viajeinteligencia.com/">Viaje Inteligencia</a> · <a href="mailto:nearme@viajeinteligencia.com">contacto</a>
</div>

<script>
const DATA = {json.dumps(data, ensure_ascii=False)};
const contAnom = {{}};
DATA.forEach(c=>{{ if(c.proc&&c.proc.toLowerCase().includes('menor')){{ const k=c.cif+'|'+c.poder; contAnom[k]=(contAnom[k]||0)+1; }} }});
const anomKeys=new Set(Object.keys(contAnom).filter(k=>contAnom[k]>=5));
const esc=s=>String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const fmt=v=>v==null?'—':Number(v).toLocaleString('es-ES',{{maximumFractionDigits:0}})+' €';
const fmtN=v=>Number(v).toLocaleString('es-ES',{{maximumFractionDigits:0}});
function fill(id,fn){{ const el=document.getElementById(id),s=new Set(DATA.map(fn)); el.innerHTML='<option value="">Todos</option>'+[...s].sort().map(x=>`<option>${{esc(x)}}</option>`).join(''); }}
function filtros(){{
  const q=document.getElementById('q').value.toLowerCase(),fEnt=document.getElementById('fEnt').value,
  fEmp=document.getElementById('fEmp').value,fTipo=document.getElementById('fTipo').value,
  fProc=document.getElementById('fProc').value,fMin=parseFloat(document.getElementById('fMin').value)||0,
  fMax=parseFloat(document.getElementById('fMax').value)||1e15,fCcaa=document.getElementById('fCcaa').value,
  fMenor=document.getElementById('fMenor').checked,fAnom=document.getElementById('fAnom').checked;
  return DATA.filter(c=>{{
    if(q&&!(c.empresa+' '+c.poder+' '+(c.cpv||'')).toLowerCase().includes(q))return false;
    if(fEnt&&c.poder!==fEnt)return false; if(fEmp&&c.empresa!==fEmp)return false;
    if(fTipo&&c.tipo!==fTipo)return false; if(fProc&&c.proc!==fProc)return false;
    if(c.importe!=null&&(c.importe<fMin||c.importe>fMax))return false;
    if(fCcaa&&c.ccaa!==fCcaa)return false;
    if(fMenor&&!(c.proc&&c.proc.toLowerCase().includes('menor')))return false;
    if(fAnom&&!anomKeys.has(c.cif+'|'+c.poder))return false;
    return true;
  }});
}}
function donut(out){{
  const m={{}}; out.forEach(c=>{{ m[c.tipo]=(m[c.tipo]||0)+(c.importe||0); }});
  const total=Object.values(m).reduce((a,b)=>a+b,0)||1;
  let acc=0,segs=''; const cols=['#f87171','#67e8f9','#ffb454','#34d399','#a78bfa','#f472b6','#60a5fa','#4ade80','#facc15','#94a3b8'];
  Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,10).forEach(([k,v],i)=>{{
    const p1=acc/total*360, p2=(acc+v)/total*360; acc+=v;
    const rad=(a)=>{{ const r=a*Math.PI/180; return [220+170*Math.sin(r),220-170*Math.cos(r)]; }};
    const [x1,y1]=rad(p1),[x2,y2]=rad(p2);
    const large=(p2-p1)>180?1:0;
    segs+=`<path d="M220 220 L${{x1.toFixed(1)}} ${{y1.toFixed(1)}} A170 170 0 ${{large}} 1 ${{x2.toFixed(1)}} ${{y2.toFixed(1)}} Z" fill="${{cols[i%cols.length]}}"><title>${{esc(k)}}: ${{fmt(v)}}</title></path>`;
  }});
  const leg=Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,6).map(([k,v])=>`<div style="font-size:0.72em;margin:2px 0;">${{esc(k)}}: <b>${{fmt(v)}}</b></div>`).join('');
  document.getElementById('donutWrap').innerHTML=`<svg width="380" height="380" viewBox="0 0 440 440" style="max-width:100%">${{segs}}<text x="220" y="215" text-anchor="middle" font-size="20" font-weight="700" fill="var(--text)">${{fmtN(total)}}</text><text x="220" y="238" text-anchor="middle" font-size="12" fill="var(--dim)">gasto total</text></svg><div>${{leg}}</div>`;
}}
function renderRanking(out){{
  const mode=document.getElementById('rankSel').value,box=document.getElementById('rankBox');
  let rows=[];
  if(mode==='contratos')rows=out.slice().sort((a,b)=>(b.importe||0)-(a.importe||0)).slice(0,10).map(c=>({{l:c.empresa+' · '+c.poder,v:c.importe||0}}));
  else if(mode==='gastoEmp'){{const m={{}};out.forEach(c=>{{m[c.cif]=m[c.cif]||{{l:c.empresa,v:0}};m[c.cif].v+=c.importe||0;}});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}}
  else if(mode==='gastoEnt'){{const m={{}};out.forEach(c=>{{m[c.poder]=m[c.poder]||{{l:c.poder,v:0}};m[c.poder].v+=c.importe||0;}});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}}
  else if(mode==='nContratos'){{const m={{}};out.forEach(c=>{{m[c.cif]=m[c.cif]||{{l:c.empresa,v:0}};m[c.cif].v++;}});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}}
  else if(mode==='tipo'){{const m={{}};out.forEach(c=>{{m[c.tipo]=m[c.tipo]||{{l:c.tipo,v:0}};m[c.tipo].v+=c.importe||0;}});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}}
  else if(mode==='proc'){{const m={{}};out.forEach(c=>{{m[c.proc]=m[c.proc]||{{l:c.proc,v:0}};m[c.proc].v+=c.importe||0;}});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}}
  const mx=Math.max(1,...rows.map(r=>r.v));
  box.innerHTML=rows.map(r=>`<div class="row"><span class="lab" title="${{esc(r.l)}}">${{esc(r.l)}}</span><div style="flex:1;background:var(--line);border-radius:4px;"><div class="bar" style="width:${{r.v/mx*100}}%"></div></div><b style="font-size:0.8em;">${{mode==='nContratos'?r.v:fmt(r.v)}}</b></div>`).join('')||'Sin resultados';
}}
function apply(){{
  const out=filtros();
  document.getElementById('kTotal').textContent=fmtN(out.length);
  document.getElementById('kSuma').textContent=fmt(out.reduce((s,c)=>s+(c.importe||0),0));
  document.getElementById('kEmp').textContent=fmtN(new Set(out.map(c=>c.cif)).size);
  document.getElementById('kEnt').textContent=fmtN(new Set(out.map(c=>c.poder)).size);
  document.getElementById('kAnom').textContent=fmtN(out.filter(c=>anomKeys.has(c.cif+'|'+c.poder)).length);
  document.getElementById('tbody').innerHTML=out.slice(0,20).map(c=>{{
    const an=anomKeys.has(c.cif+'|'+c.poder);
    return `<tr class="${{an?'anom':''}}"><td>${{esc(c.poder)}}</td><td>${{esc(c.empresa)}}</td><td>${{fmt(c.importe)}}</td><td>${{esc(c.fecha)}}</td><td>${{esc(c.ccaa)}}</td></tr>`;
  }}).join('')||'<tr><td colspan="5">Sin resultados.</td></tr>';
  renderRanking(out); donut(out);
}}
function toggleTheme(){{
  const el=document.documentElement,btn=document.getElementById('themeBtn');
  const d=el.getAttribute('data-theme')==='dark';
  el.setAttribute('data-theme',d?'light':'dark');
  btn.textContent=d?'🌙 Oscuro':'☀️ Claro';
}}
fill('fEnt',c=>c.poder);fill('fEmp',c=>c.empresa);fill('fTipo',c=>c.tipo);fill('fProc',c=>c.proc);fill('fCcaa',c=>c.ccaa);
['q','fEnt','fEmp','fTipo','fProc','fMin','fMax','fCcaa','fMenor','fAnom'].forEach(id=>document.getElementById(id).addEventListener(id==='q'?'input':'change',apply));
document.getElementById('rankSel').addEventListener('change',apply);
document.getElementById('reset').onclick=()=>{{['q','fEnt','fEmp','fTipo','fProc','fMin','fMax','fCcaa'].forEach(id=>document.getElementById(id).value='');document.getElementById('fMenor').checked=false;document.getElementById('fAnom').checked=false;apply();}};
apply();
</script>
</body></html>"""

OUT.write_text(html, encoding="utf-8")
print(f"OK: dashboard v4 (claro/oscuro + KPIs impacto + donut) · {len(data)} contratos")
