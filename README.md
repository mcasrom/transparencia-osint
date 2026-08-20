# transparencia_osint

Detectar irregularidades en la contratación pública española a partir de datos
oficiales abiertos. El usuario decide los criterios (filtros), no la herramienta.

## Qué hace
- Ingiere contratos públicos reales (datos.gob.es: Euskadi, Baleares...).
- Dashboard interactivo en https://transparencia.viajeinteligencia.com
  (filtros por entidad/empresa/tipo/importe + rankings + donut + claro/oscuro).
- Reglas de anomalía (opcional, como filtro):
  - Concentración: empresa con >=5 contratos menores a una misma entidad.
  - Troceado: misma empresa+entidad, contratos <15k que suman >15k en 90 días.

## Estado
- Motor validado con datos reales (1.847 contratos Euskadi).
- Dashboard v4 en vivo (claro/oscuro, KPIs impacto, rankings, donut).
- PENDIENTE: crawl PLACSP (la puerta a toda España, incluida Murcia).

## Uso
- Ingesta: python3 ingest.py <xlsx> "<entidad>"
- Reglas: python3 rules/transp_rules.py
- Dashboard: python3 gen_transp_dash4.py
