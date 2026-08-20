#!/usr/bin/env python3
"""Dashboard transparencia_osint v6: +export CSV, filtro año, ver más, troceado agrupado, chips comunidad."""
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

T = r"""<!doctype html>
<html lang="es" data-theme="dark">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>transparencia_osint · Contratos públicos: filtros, rankings y anomalías | Viaje Inteligencia</title>
<meta name="description" content="Consulta interactiva de contratos públicos: filtros, rankings, export CSV, detección de troceado y concentración. Datos oficiales abiertos.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="__SITE__/">
<meta property="og:locale" content="es_ES">
<style>
:root{--bg:#0b0f17;--panel:#0e1322;--panel2:#121826;--line:#232b3d;--text:#e7ebf3;--dim:#8993a8;--accent:#ffb454;--red:#f87171;--amber:#fbbf24;--input:#0b0f17;}
[data-theme="light"]{--bg:#f4f6fb;--panel:#fff;--panel2:#eef1f8;--line:#d6ddea;--text:#16202e;--dim:#5b6b84;--accent:#d9820a;--red:#dc4c4c;--amber:#b45309;--input:#fff;}
*{box-sizing:border-box;}
body{font-family:-apple-system,'Inter',sans-serif;background:var(--bg);color:var(--text);max-width:1150px;margin:0 auto;padding:18px;line-height:1.5;overflow-x:hidden;}
h1{font-size:1.35em;margin:0;}.sub{color:var(--dim);font-size:0.88em;margin:4px 0 12px;}a{color:#67e8f9;}
.top{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;}
.toggle{background:var(--panel);border:1px solid var(--line);color:var(--text);border-radius:8px;padding:7px 14px;cursor:pointer;font-size:0.85em;}
.btn{background:var(--panel2);border:1px solid var(--line);color:var(--text);border-radius:8px;padding:7px 14px;cursor:pointer;font-size:0.85em;}
.tabs{display:flex;gap:8px;margin:12px 0 4px;}
.tab{padding:8px 18px;border-radius:8px 8px 0 0;cursor:pointer;background:var(--panel2);border:1px solid var(--line);border-bottom:none;font-size:0.9em;color:var(--dim);}
.tab.on{background:var(--panel);color:var(--accent);font-weight:700;border-bottom:2px solid var(--accent);}
.pane{display:none;}.pane.on{display:block;}
.filtros{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;margin:8px 0;}
.filtros>div{min-width:0;}.filtros label{font-size:0.7em;color:var(--dim);display:block;margin-bottom:2px;}
.filtros input,.filtros select{width:100%;background:var(--input);border:1px solid var(--line);color:var(--text);border-radius:6px;padding:7px;font-size:0.85em;}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;}
.chip{padding:5px 14px;border-radius:999px;border:1px solid var(--line);background:var(--panel);color:var(--dim);cursor:pointer;font-size:0.8em;}
.chip.on{background:var(--accent);color:#000;border-color:var(--accent);font-weight:600;}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:14px 0;}
.kpi{border-radius:14px;padding:16px;position:relative;overflow:hidden;}
.kpi .n{font-size:1.9em;font-weight:800;line-height:1;}.kpi .l{font-size:0.72em;opacity:.85;margin-top:4px;}.kpi .ic{position:absolute;right:10px;top:10px;font-size:1.6em;opacity:.35;}
.kp1{background:linear-gradient(135deg,#7f1d1d,#b91c1c);color:#fff;}.kp2{background:linear-gradient(135deg,#1e3a8a,#1d4ed8);color:#fff;}
.kp3{background:linear-gradient(135deg,#14532d,#15803d);color:#fff;}.kp4{background:linear-gradient(135deg,#713f12,#b45309);color:#fff;}
.kp5{background:linear-gradient(135deg,#4a044e,#86198f);color:#fff;}.kp6{background:linear-gradient(135deg,#111827,#1f2937);color:#fff;}
.layout{display:grid;grid-template-columns:1.3fr 1fr;gap:14px;}.layout>*{min-width:0;}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;}
.panel h3{margin:0 0 10px;font-size:0.95em;color:var(--accent);}
.panel select{width:100%;background:var(--input);border:1px solid var(--line);color:var(--text);border-radius:6px;padding:7px;font-size:0.85em;margin-bottom:8px;}
table{width:100%;border-collapse:collapse;font-size:0.78em;table-layout:fixed;}
th,td{text-align:left;padding:5px 7px;border-bottom:1px solid var(--line);max-width:340px;word-wrap:break-word;}
th{color:var(--dim);position:sticky;top:0;background:var(--panel);}
tr.conc{background:rgba(220,38,38,.16);}tr.troc{background:rgba(245,158,11,.16);}
.cont{max-height:430px;overflow:auto;border:1px solid var(--line);border-radius:8px;}
.rank{font-size:0.85em;}.rank .row{display:flex;align-items:center;gap:8px;margin:5px 0;}
.rank .lab{min-width:240px;font-size:0.85em;word-wrap:break-word;}
.rank .bar{height:16px;border-radius:4px;background:linear-gradient(90deg,var(--red),var(--accent));}
svg{max-width:100%;height:auto;}
.met{font-size:0.72em;color:var(--dim);border-top:1px solid var(--line);margin-top:16px;padding-top:10px;}
.narr{font-size:0.85em;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:12px;}
.narr b{color:var(--accent);}.badge{border-radius:6px;padding:1px 7px;font-size:0.7em;color:#fff;}
.b-conc{background:#dc2626;}.b-troc{background:#d97706;}
.more{width:100%;margin-top:8px;padding:8px;border:1px dashed var(--line);border-radius:8px;background:var(--panel2);color:var(--text);cursor:pointer;}
.sec{font-size:1.05em;font-weight:700;color:var(--accent);margin:22px 0 8px;padding-bottom:4px;border-bottom:1px solid var(--line);}
</style>
</head>
<body>
<div class="top">
  <div><h1>🔎 transparencia_osint · Contratos públicos</h1><div class="sub">Filtra y analiza; el criterio lo pones tú. Actualizado __HOY__.</div></div>
  <div style="display:flex;gap:8px;"><button class="btn" onclick="exportCSV()">⬇️ Exportar CSV</button><button class="toggle" onclick="toggleTheme()" id="themeBtn">🌙 Oscuro</button></div>
</div>

<div class="tabs">
  <div class="tab on" id="tabDatos" onclick="tab('datos')">📊 Datos</div>
  <div class="tab" id="tabAnom" onclick="tab('anomalias')">🚨 Anomalías</div>
</div>

<div class="pane on" id="paneDatos">
  <div class="filtros">
    <div><label>Buscar</label><input id="q" placeholder="empresa, entidad, CIF, CPV"></div>
    <div><label>Entidad</label><select id="fEnt"></select></div>
    <div><label>Empresa</label><select id="fEmp"></select></div>
    <div><label>Tipo</label><select id="fTipo"></select></div>
    <div><label>Procedimiento</label><select id="fProc"></select></div>
    <div><label>Año</label><select id="fYear"></select></div>
    <div><label>Importe mín (€)</label><input id="fMin" type="number"></div>
    <div><label>Importe máx (€)</label><input id="fMax" type="number"></div>
    <div><label>Comunidad</label><select id="fCcaa"></select></div>
    <div><label>Anomalía</label><select id="fAnom"><option value="">Todas</option><option value="conc">Concentración</option><option value="troc">Troceado</option></select></div>
    <div><label>Mín. contratos</label><input id="fMinN" type="number" placeholder="0"></div>
    <button id="reset" style="align-self:end;background:var(--panel2);border:1px solid var(--line);color:var(--text);border-radius:6px;padding:7px;cursor:pointer;">Limpiar</button>
  </div>

  <div class="kpis">
    <div class="sec">📈 Resumen</div>
  <div class="kpis">
    <div class="kpi kp1"><div class="ic">📑</div><div class="n" id="kTotal">0</div><div class="l">contratos</div></div>
    <div class="kpi kp2"><div class="ic">💰</div><div class="n" id="kSuma">0 €</div><div class="l">gasto</div></div>
    <div class="kpi kp3"><div class="ic">🏭</div><div class="n" id="kEmp">0</div><div class="l">empresas</div></div>
    <div class="kpi kp4"><div class="ic">🏛️</div><div class="n" id="kEnt">0</div><div class="l">entidades</div></div>
    <div class="kpi kp5"><div class="ic">🚨</div><div class="n" id="kAnom">0</div><div class="l">concentración</div></div>
    <div class="kpi kp6"><div class="ic">✂️</div><div class="n" id="kTroc">0</div><div class="l">troceado</div></div>
  </div>

  <div class="sec">📊 Análisis</div>
  <div class="layout">
    <div class="panel">
      <h3>📊 Ranking Top 10</h3>
      <select id="rankSel">
        <option value="contratos">Top contratos por importe</option>
        <option value="gastoEmp">Top empresas por gasto</option>
        <option value="gastoEnt">Top entidades por gasto</option>
        <option value="nContratos">Top empresas por nº contratos</option>
        <option value="tipo">Gasto por tipo</option>
        <option value="proc">Gasto por procedimiento</option>
      </select>
      <div id="rankBox" class="rank"></div>
    </div>
    <div class="panel">
      <h3>🥧 Gasto por tipo</h3>
      <div id="donutWrap" style="text-align:center;"></div>
    </div>
  </div>

  <div class="sec">🏷️ Detalle</div>
  <div class="panel">
    <h3>Registros (filtrados)</h3>
    <div class="cont"><table><thead><tr><th>Entidad</th><th>Empresa</th><th>Importe</th><th>Fecha</th><th>CCAA</th><th>Anom</th></tr></thead><tbody id="tbody"></tbody></table></div>
      <button class="more" id="moreBtn" onclick="moreRows()">Ver más ↓</button>
    </div>
  </div>
</div>

<div class="pane" id="paneAnom">
  <div class="narr">
    <b>¿Qué es una anomalía aquí?</b> Señales estadísticas, <b>no conclusiones</b>:
    <ul>
      <li><span class="badge b-conc">Concentración</span> misma empresa con <b>≥5 contratos menores</b> a la misma entidad.</li>
      <li><span class="badge b-troc">Troceado</span> misma empresa+entidad con contratos de <b>&lt;15.000 €</b> que suman <b>&gt;15.000 € en 90 días</b>.</li>
    </ul>
    Candidatos a revisar, no acusaciones.
  </div>
  <div class="chips" id="anomChips">
    <span class="chip on" data-ccaa="" onclick="setChip(this)">Todas</span>
  </div>
  <div class="kpis">
    <div class="kpi kp5"><div class="n" id="aConc">0</div><div class="l">empresas en concentración</div></div>
    <div class="kpi kp6"><div class="n" id="aTroc">0</div><div class="l">casos de troceado</div></div>
  </div>
  <div class="panel" style="margin-top:10px;"><h3>✂️ Troceado agrupado por empresa · entidad</h3><div id="trocGroup" style="font-size:0.85em;"></div></div>
  <div class="panel" style="margin-top:10px;"><h3>🚨 Concentración (empresa · entidad · nº menores)</h3><div id="concList" style="font-size:0.85em;"></div></div>
</div>

<div class="met">
<b>Metodología y fuentes:</b> datos oficiales abiertos (datos.gob.es y portales regionales): Euskadi, Illes Balears y <b>Región de Murcia (CARM 2023)</b>. Criterios: concentración = ≥5 menores a una misma entidad; troceado = &lt;15.000 € c/u sumando &gt;15.000 € en 90 días. Cobertura parcial. Señales, no acusaciones.
<br>© <a href="https://www.viajeinteligencia.com/">Viaje Inteligencia</a> · <a href="mailto:nearme@viajeinteligencia.com">contacto</a>
</div>

<script>
const DATA = __DATA__;
const LIM=15000,WINDOW=90;
const esc=s=>String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const fmt=v=>v==null?'—':Number(v).toLocaleString('es-ES',{maximumFractionDigits:0})+' €';
const fmtN=v=>Number(v).toLocaleString('es-ES',{maximumFractionDigits:0});
const concKeys=new Set(),trocIdxs=new Set(),trocGroup={},cnt={},trocByKey={};
DATA.forEach((c,i)=>{if(c.proc&&c.proc.toLowerCase().includes('menor')){const k=c.cif+'|'+c.poder;cnt[k]=(cnt[k]||0)+1;}});
Object.entries(cnt).forEach(([k,n])=>{if(n>=5)concKeys.add(k);});
const grupos={};
DATA.forEach((c,i)=>{if(c.importe!=null&&c.fecha){const f=new Date(c.fecha);if(!isNaN(f)){const k=c.cif+'|'+c.poder;(grupos[k]=grupos[k]||[]).push({i,f,im:c.importe});}}});
for(const[k,arr]of Object.entries(grupos)){arr.sort((a,b)=>a.f-b.f);let pairs=0,sum=0;for(let i=0;i<arr.length;i++)for(let j=i+1;j<arr.length;j++){const dias=(arr[j].f-arr[i].f)/86400000;if(dias>WINDOW)break;if(arr[i].im<LIM&&arr[j].im<LIM&&arr[i].im+arr[j].im>LIM){trocIdxs.add(arr[i].i);trocIdxs.add(arr[j].i);pairs++;sum+=arr[i].im+arr[j].im;}}if(pairs>0){const c=DATA[arr[0].i];trocGroup[k]={empresa:c.empresa,cif:c.cif,poder:c.poder,ccaa:c.ccaa,pairs,sum};}}
const anomOf=i=>(concKeys.has(DATA[i].cif+'|'+DATA[i].poder)?'conc':'')+(trocIdxs.has(i)?'troc':'');
let shown=20,chipCcaa='';
function fill(id,fn){const el=document.getElementById(id),s=new Set(DATA.map(fn));el.innerHTML='<option value="">Todos</option>'+[...s].sort().map(x=>`<option>${esc(x)}</option>`).join('');}
function filtros(){const q=document.getElementById('q').value.toLowerCase(),fEnt=document.getElementById('fEnt').value,fEmp=document.getElementById('fEmp').value,fTipo=document.getElementById('fTipo').value,fProc=document.getElementById('fProc').value,fYear=document.getElementById('fYear').value,fMin=parseFloat(document.getElementById('fMin').value)||0,fMax=parseFloat(document.getElementById('fMax').value)||1e15,fCcaa=document.getElementById('fCcaa').value,fAnom=document.getElementById('fAnom').value,fMinN=parseInt(document.getElementById('fMinN').value)||0;return DATA.map((c,i)=>({c,i})).filter(x=>{const c=x.c;if(q&&!(c.empresa+' '+c.poder+' '+(c.cpv||'')+' '+(c.cif||'')).toLowerCase().includes(q))return false;if(fEnt&&c.poder!==fEnt)return false;if(fEmp&&c.empresa!==fEmp)return false;if(fTipo&&c.tipo!==fTipo)return false;if(fProc&&c.proc!==fProc)return false;if(fYear&&!c.fecha.startsWith(fYear))return false;if(c.importe!=null&&(c.importe<fMin||c.importe>fMax))return false;if(fCcaa&&c.ccaa!==fCcaa)return false;const a=anomOf(x.i);if(fAnom==='conc'&&!a.includes('conc'))return false;if(fAnom==='troc'&&!a.includes('troc'))return false;if(fMinN>0&&(cnt[c.cif+'|'+c.poder]||0)<fMinN)return false;return true;});}
function renderRanking(out){const mode=document.getElementById('rankSel').value,box=document.getElementById('rankBox');let rows=[];if(mode==='contratos')rows=out.map(x=>x.c).sort((a,b)=>(b.importe||0)-(a.importe||0)).slice(0,10).map(c=>({l:c.empresa+' · '+c.poder,v:c.importe||0}));else if(mode==='gastoEmp'){const m={};out.forEach(({c})=>{m[c.cif]=m[c.cif]||{l:c.empresa,v:0};m[c.cif].v+=c.importe||0;});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}else if(mode==='gastoEnt'){const m={};out.forEach(({c})=>{m[c.poder]=m[c.poder]||{l:c.poder,v:0};m[c.poder].v+=c.importe||0;});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}else if(mode==='nContratos'){const m={};out.forEach(({c})=>{m[c.cif]=m[c.cif]||{l:c.empresa,v:0};m[c.cif].v++;});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}else if(mode==='tipo'){const m={};out.forEach(({c})=>{m[c.tipo]=m[c.tipo]||{l:c.tipo,v:0};m[c.tipo].v+=c.importe||0;});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}else if(mode==='proc'){const m={};out.forEach(({c})=>{m[c.proc]=m[c.proc]||{l:c.proc,v:0};m[c.proc].v+=c.importe||0;});rows=Object.values(m).sort((a,b)=>b.v-a.v).slice(0,10);}const mx=Math.max(1,...rows.map(r=>r.v));box.innerHTML=rows.map(r=>`<div class="row"><span class="lab" title="${esc(r.l)}">${esc(r.l)}</span><div style="flex:1;background:var(--line);border-radius:4px;"><div class="bar" style="width:${r.v/mx*100}%"></div></div><b style="font-size:0.8em;">${mode==='nContratos'?r.v:fmt(r.v)}</b></div>`).join('')||'Sin resultados';}
function donut(out){const m={};out.forEach(({c})=>{m[c.tipo]=(m[c.tipo]||0)+(c.importe||0);});const total=Object.values(m).reduce((a,b)=>a+b,0)||1;let acc=0,segs='';const cols=['#f87171','#67e8f9','#ffb454','#34d399','#a78bfa','#f472b6','#60a5fa','#4ade80','#facc15','#94a3b8'];Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,10).forEach(([k,v],i)=>{const p1=acc/total*360,p2=(acc+v)/total*360;acc+=v;const rad=a=>{const r=a*Math.PI/180;return[220+170*Math.sin(r),220-170*Math.cos(r)];};const[x1,y1]=rad(p1),[x2,y2]=rad(p2);const large=(p2-p1)>180?1:0;segs+=`<path d="M220 220 L${x1.toFixed(1)} ${y1.toFixed(1)} A170 170 0 ${large} 1 ${x2.toFixed(1)} ${y2.toFixed(1)} Z" fill="${cols[i%cols.length]}"><title>${esc(k)}: ${fmt(v)}</title></path>`;});const leg=Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,6).map(([k,v])=>`<div style="font-size:0.72em;margin:2px 0;">${esc(k)}: <b>${fmt(v)}</b></div>`).join('');document.getElementById('donutWrap').innerHTML=`<svg width="360" height="360" viewBox="0 0 440 440" style="max-width:100%">${segs}<text x="220" y="215" text-anchor="middle" font-size="20" font-weight="700" fill="var(--text)">${fmtN(total)}</text><text x="220" y="238" text-anchor="middle" font-size="12" fill="var(--dim)">gasto</text></svg><div>${leg}</div>`;}
let lastOut=[];
function apply(){const out=filtros();lastOut=out;const nConc=out.filter(x=>anomOf(x.i).includes('conc')).length,nTroc=out.filter(x=>anomOf(x.i).includes('troc')).length;document.getElementById('kTotal').textContent=fmtN(out.length);document.getElementById('kSuma').textContent=fmt(out.reduce((s,x)=>s+(x.c.importe||0),0));document.getElementById('kEmp').textContent=fmtN(new Set(out.map(x=>x.c.cif)).size);document.getElementById('kEnt').textContent=fmtN(new Set(out.map(x=>x.c.poder)).size);document.getElementById('kAnom').textContent=fmtN(nConc);document.getElementById('kTroc').textContent=fmtN(nTroc);shown=20;renderTable();renderRanking(out);donut(out);}
function renderTable(){const out=lastOut;document.getElementById('tbody').innerHTML=out.slice(0,shown).map(x=>{const c=x.c,a=anomOf(x.i);const lbl=(a.includes('troc')?'<span class="badge b-troc">troc</span>':'')+(a.includes('conc')?'<span class="badge b-conc">conc</span>':'');return`<tr class="${a.includes('conc')?'conc':''} ${a.includes('troc')?'troc':''}"><td>${esc(c.poder)}</td><td>${esc(c.empresa)}</td><td>${fmt(c.importe)}</td><td>${esc(c.fecha)}</td><td>${esc(c.ccaa)}</td><td>${lbl}</td></tr>`;}).join('')||'<tr><td colspan="6">Sin resultados.</td></tr>';document.getElementById('moreBtn').style.display=out.length>shown?'':'none';}
function moreRows(){shown+=20;renderTable();}
function renderAnom(){document.getElementById('aConc').textContent=fmtN(concKeys.size);document.getElementById('aTroc').textContent=fmtN(Object.keys(trocGroup).length);const tg=Object.entries(trocGroup).filter(([k,g])=>!chipCcaa||g.ccaa===chipCcaa).sort((a,b)=>b[1].sum-a[1].sum).slice(0,60);document.getElementById('trocGroup').innerHTML=tg.map(([k,g])=>`<div style="margin:5px 0;padding:6px 8px;background:rgba(245,158,11,.08);border-left:3px solid var(--amber);border-radius:6px;">✂️ <b>${esc(g.empresa)}</b> · ${esc(g.poder)} — <b>${g.pairs}</b> pares · suma <b>${fmt(g.sum)}</b> <span style="color:var(--dim);font-size:0.75em;">(${esc(g.ccaa)})</span></div>`).join('')||'Sin casos.';const cl=[...concKeys].map(k=>{const c=DATA.find(x=>x.cif+'|'+x.poder===k);return{c,n:cnt[k]};}).filter(x=>!chipCcaa||x.c.ccaa===chipCcaa).sort((a,b)=>b.n-a.n).slice(0,60);document.getElementById('concList').innerHTML=cl.map(x=>`<div style="margin:4px 0;">🚨 <b>${esc(x.c.empresa)}</b> → ${esc(x.c.poder)} · <b>${x.n}</b> menores <span style="color:var(--dim);font-size:0.75em;">(${esc(x.c.ccaa)})</span></div>`).join('')||'Sin casos.';}
function setChip(el){chipCcaa=el.dataset.ccaa;document.querySelectorAll('#anomChips .chip').forEach(c=>c.className='chip'+(c===el?' on':''));renderAnom();}
function tab(name){document.getElementById('tabDatos').className='tab'+(name==='datos'?' on':'');document.getElementById('tabAnom').className='tab'+(name==='anomalias'?' on':'');document.getElementById('paneDatos').className='pane'+(name==='datos'?' on':'');document.getElementById('paneAnom').className='pane'+(name==='anomalias'?' on':'');if(name==='anomalias')renderAnom();}
function exportCSV(){if(!lastOut.length)return;const head=['Entidad','Empresa','CIF','Importe','Fecha','Tipo','Procedimiento','CPV','CCAA','Anomalia'];const rows=lastOut.map(x=>{const c=x.c,a=anomOf(x.i);return[c.poder,c.empresa,c.cif,c.importe??'',c.fecha,c.tipo,c.proc,c.cpv,c.ccaa,a||''];});const csv='\ufeff'+[head,...rows].map(r=>r.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(';')).join('\n');const blob=new Blob([csv],{type:'text/csv;charset=utf-8;'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='transparencia_osint.csv';a.click();}
function toggleTheme(){const el=document.documentElement,btn=document.getElementById('themeBtn');const d=el.getAttribute('data-theme')==='dark';el.setAttribute('data-theme',d?'light':'dark');btn.textContent=d?'🌙 Oscuro':'☀️ Claro';}
fill('fEnt',c=>c.poder);fill('fEmp',c=>c.empresa);fill('fTipo',c=>c.tipo);fill('fProc',c=>c.proc);fill('fCcaa',c=>c.ccaa);
const years=[...new Set(DATA.map(c=>c.fecha?c.fecha.slice(0,4):''))].filter(Boolean).sort();
document.getElementById('fYear').innerHTML='<option value="">Todos</option>'+years.map(y=>`<option>${y}</option>`).join('');
[...new Set(DATA.map(c=>c.ccaa))].filter(Boolean).forEach(c=>{const s=document.createElement('span');s.className='chip';s.textContent=c;s.dataset.ccaa=c;s.onclick=()=>setChip(s);document.getElementById('anomChips').appendChild(s);});
['q','fEnt','fEmp','fTipo','fProc','fYear','fMin','fMax','fCcaa','fAnom','fMinN'].forEach(id=>document.getElementById(id).addEventListener(id==='q'?'input':'change',apply));
document.getElementById('rankSel').addEventListener('change',apply);
document.getElementById('reset').onclick=()=>{['q','fEnt','fEmp','fTipo','fProc','fYear','fMin','fMax','fCcaa','fAnom','fMinN'].forEach(id=>document.getElementById(id).value='');apply();};
apply();
</script>
</body></html>"""

out = T.replace("__SITE__", SITE).replace("__HOY__", hoy).replace("__DATA__", json.dumps(data, ensure_ascii=False))
OUT.write_text(out, encoding="utf-8")
print(f"OK: dashboard v6 · {len(data)} registros")
