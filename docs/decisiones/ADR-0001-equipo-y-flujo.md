# ADR-0001 · Equipo de desarrollo y flujo de cambios

- Fecha: 11-nov-2026
- Estado: aceptada (instrucción de Omar González, 11-nov-2026) · por validar por Adolfo Pastor
- Sustituye: células mixtas consultor–desarrollador de `04_Gestion-Proyecto/ruta-aprendizaje.md`

## Contexto

Quedan 13 días hábiles para abrir el sistema el 1-dic-2026. La ruta de aprendizaje preveía tres células mixtas, pero sus integrantes no se asignaron.

## Decisión

- El desarrollo lo llevan Omar González y Claude.
- Claude escribe código, pruebas, plantillas, textos y documentación con datos ficticios; no entra al servidor de la SABG.
- Omar revisa y fusiona cada cambio, opera el servidor y es el único que despliega.
- Adolfo Pastor valida las decisiones de alcance, reglas, textos y fechas, y es el único canal con la SABG.

## Consecuencias

- La revisión y el despliegue dependen de una persona: cambios pequeños, revisión diaria y manual de despliegue escrito desde S0.
- Credenciales y datos reales nunca pasan por Claude.
