transparencia_osint
========================
Detectar irregularidades en contratacion publica (PLACSP):
- Troceado: misma empresa + mismo organo + importes bajo 15k/40k + ventana corta
- Concentracion: una empresa domina a un organo
- Velocidad: adjudicacion en dias record

Estructura:
  crawler/   -> extraccion PLACSP
  data/      -> DB (postgres) + dump
  rules/     -> reglas de anomalia
  dashboard/ -> visualizacion
