# transparencia_osint — WAYAHEAD

## Objetivo
Detectar irregularidades en contratación pública española (PLACSP):
troceado de contratos, concentración por empresa, adjudicaciones récord.
Filtro por órgano de contratación = "dónde va el dinero en mi municipio".

## Estado (19/Ago)
- Esqueleto creado (crawler/data/rules/dashboard).
- Validación de fuentes:
  - PLACSP: portal OK, sesión OK, pero búsqueda es WebSphere/dojo → reverse-engineering
    del endpoint de datos (hito crítico, días de trabajo). Fuente legal única.
  - transparencia.carm.es: Radware captcha → bloqueado.
  - datos.gob.es API: bloqueado para automatización.
- Conclusión: el acceso a datos ES el núcleo duro. No es un hito de una sesión.

## Roadmap
- [ ] P0: crawler PLACSP (sesión + search POST + paginación) — validar 100 contratos reales
      de un órgano de Murcia. Decidir enfoque: reverse-engineering directo o usar
      patrón de scrapers comunitarios documentados (GitHub).
- [ ] P1: DB postgres (contratos, órganos, empresas) + ingesta diaria incremental.
- [ ] P2: reglas de anomalía: troceado (misma empresa+órgano, <15k/40k, ventana<90d,
      acumulado cruzando umbral), concentración (>X% de un órgano), velocidad (días).
- [ ] P3: dashboard visual (gasto por órgano/empresa/CPV, banderas, gráficos).
- [ ] P4: expansión (BORME propietarios para cruce de familiares — fase 2, sensible).

## Notas
- Fuente: PLACSP publica contratos de TODAS las entidades públicas (CCAA y
  ayuntamientos) por la ley de 2019.
- Alternativa real si PLACSP crawler se atasca: buscar datasets de contratos
  regionales publicados como open data (no API) en descargas directas.
