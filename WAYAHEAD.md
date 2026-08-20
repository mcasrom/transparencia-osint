# transparencia_osint — WAYAHEAD

## Objetivo
"Dónde se gasta el dinero en mi ciudad": contratación pública con filtros y
detección de anomalías (concentración, troceado).

## Hecho
- Motor de ingesta + reglas validado con datos reales (Euskadi, datos.gob.es).
- Dashboard interactivo v4 en vivo: filtros neutrales, rankings top-10, donut
  de gasto por tipo, KPIs con impacto, tema claro/oscuro.
- Fuentes con descarga directa: Euskadi (registro por entidad), Baleares (CSV).
- Playwright 1.60 + Chromium instalados en el server (para el crawl PLACSP).

## P0 — Crawl PLACSP (LA puerta a toda España, incluida Murcia)
- Portal contrataciondelestado.es: sesion OK, estructura JSF localizada
  (form1 + textTexto1 + ViewState + _SUBMIT), pero el boton lo dispara dojo.
- ENFOQUE ACTUAL: navegador headless (Playwright) — cargar portal, rellenar
  campo, clicar, capturar resultados. Evita el reverse-engineering del POST.
- Hito: extraer contratos reales de un organo de Murcia (ej. Ayuntamiento de
  Murcia) -> validar contra el motor existente.
- Tras crackear: ingesta masiva de toda Espana (unica fuente completa).

## Roadmap
- [ ] P0: crawl PLACSP con Playwright -> datos de Murcia/Espana.
- [ ] P1: integracion Baleares/Valencia/CyL/Cantabria (descarga directa).
- [ ] P2: mejor troceado (usar importes + fechas cuando existan).
- [ ] P3: dedup de entidades y nombres.
- [ ] P4: BORME para cruce de propietarios/familiares (sensible, fase 2).

## Hallazgo S1 (20/Ago)
- Baleares INGERIDO (7010 empresas, formato agregado). Filtro comunidad: Euskadi + Illes Balears.
- Valencia (dadesobertes.gva.es): bloqueada desde el server (timeout, IP de datacenter bloqueada) -> descarga con navegador del usuario.
- Cataluña (dadesobertes.gencat.cat): portal reestructurado, API CKAN desaparecida -> requiere navegar el nuevo portal.
- CONCLUSION: la expansion regional por descarga directa tiene limite (portales hostiles/bloqueados).
  El crawl PLACSP (S2) es la unica via completa a Valencia/Cataluna/Madrid/Murcia.
