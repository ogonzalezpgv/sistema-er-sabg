# Sistema de Entrega-Recepción Final · SABG Campeche

Sistema web para coordinar la Entrega-Recepción Final de la administración estatal que concluye en 2027. Permite a dependencias y entidades del Poder Ejecutivo cargar su información, y le da a la Secretaría de Anticorrupción y Buen Gobierno (SABG) un repositorio único con tablero de avance.

Prestador ante el cliente: **WSR Integral, S.A. de C.V.** El código, la documentación y los datos son propiedad de la SABG (cotización WSR-2026-SABG-001).

## Principio rector

La información es responsabilidad de cada institución y de la persona servidora pública saliente (Ley E-R, art. 16). La SABG coordina, recibe y verifica en su forma; **no valida, certifica ni avala** el contenido (art. 23). Ningún texto del sistema dice «validar», «aprobar» ni «revisor». `tools/verificar_lenguaje.py` lo comprueba antes de cada despliegue.

## Fases

| Fase | Periodo | Qué hace |
| --- | --- | --- |
| 1 · Delimitación de responsables | 1 a 18-dic-2026 | Catálogo de entes, Enlaces, estructura orgánica, padrón de sujetos obligados, asignación de los 43 anexos, padrón firmado y tablero (Corte 1) |
| 2 · Carga de información | mar a ago-2027 | Captura de los 43 formatos, documentos para firma, Acta y repositorio documental (Cortes 2 y 3) |

Fase 1 se libera en tres entregas: **R1** el 1-dic (flujo del Enlace), **R2** el 4-dic (padrón firmado y acuse) y **R3** el 14-dic (verificación formal y consolidado).

## Estructura del repositorio

```
data/catalogo/     Catálogo versionado de los 43 formatos y sus naturalezas
data/lenguaje/     Términos prohibidos por el principio rector
docs/              Arquitectura, modelo de datos y registro de decisiones técnicas
tools/             Verificaciones que se corren antes de cada despliegue
```

El código de la aplicación se agrega cuando se fije el stack con el inventario del servidor (T-01, vie 13-nov-2026). Ver `docs/arquitectura.md`.

## Verificaciones

```
python3 tools/verificar_catalogo.py   # 43 formatos, conteos por obligados, tipo y naturaleza
python3 tools/verificar_lenguaje.py   # textos visibles sin «validar», «aprobar», etc.
```

## Equipo

| Persona | Rol |
| --- | --- |
| Omar González | Coordina el desarrollo; servidor, accesos y despliegue; revisa y aprueba cada cambio |
| Claude | Código, pruebas, plantillas, textos de interfaz y documentación técnica, con datos ficticios |
| Adolfo Pastor | Líder de proyecto; valida decisiones; único canal con la SABG |

Reglas de trabajo en `CONTRIBUTING.md`. Plan completo: documento «Plan de desarrollo · Sistema de Entrega-Recepción Final SABG».
