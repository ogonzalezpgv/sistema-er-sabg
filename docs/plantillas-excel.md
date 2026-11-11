# Plantillas Excel de Fase 1 · especificación columna por columna

> Generado por `tools/generar_plantillas.py` (plantillas v1.0, catálogo 2026-01). No se edita a mano: se cambia el generador y se vuelve a correr.
> Insumo del DRS de Fase 1 (Producto 2.1: «plantillas de carga masiva definidas columna por columna»).

## Reglas generales

1. El sistema genera cada plantilla para un ente y un corte; la hoja oculta «Control» guarda ente, corte y versión de plantilla. Al subirla, el sistema no importa el archivo si no corresponde al ente o si la versión no es la vigente, y explica por qué.
2. Nada se importa a medias: o el archivo pasa completo la verificación de forma, o se devuelve un reporte por renglón con lo que falta (lineamientos de UX §4.4).
3. La columna «Verificación de forma» ayuda al Enlace a corregir antes de subir; la verificación que cuenta es la del sistema al importar.
4. Encabezados, columnas del sistema y fórmulas están protegidos (sin contraseña) para evitar cambios accidentales; las celdas de captura no.
5. Los textos de las plantillas pasan tools/verificar_lenguaje.py (términos prohibidos en data/lenguaje/terminos-prohibidos.json).
6. Las muestras usan un ente ficticio. Las plantillas reales solo se generan dentro del servidor de la SABG.

## Estructura orgánica (M-03)

Confirmar o corregir la estructura orgánica precargada del ente, hasta jefatura de departamento o equivalente.

**Cada fila es:** Una fila por unidad administrativa.

| Columna | Quién la llena | Obligatoria | Formato | Verificación de forma | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| Clave de la unidad | Precargada · el Enlace la asigna en altas | Sí | Texto, hasta 30 caracteres, única en el ente | No vacía y sin repetirse en la hoja | SFE-02 |
| Nombre de la unidad administrativa | Precargada · Enlace | Sí | Texto, hasta 200 caracteres | No vacío | Dirección General de Administración |
| Nivel | Precargada · Enlace | Sí | Lista cerrada | Valor de la lista | Dirección general o equivalente |
| Clave de la unidad superior | Precargada · Enlace | No | Texto: una clave de la columna A | Obligatoria salvo para el titular del ente; debe existir en la columna A | SFE-01 |
| Fuente documental | Precargada · Enlace | Sí | Lista cerrada | Valor de la lista | Reglamento interior |
| Referencia de la fuente | Precargada · Enlace | No | Texto: artículo y fecha de publicación | — | Art. 5, fr. II · POE 12-jun-2026 |
| Movimiento | Enlace | Sí | Lista cerrada; precargada como «Sin cambio» | Valor de la lista | Sin cambio |
| Motivo del movimiento | Enlace | No | Texto, hasta 500 caracteres | Obligatorio si el movimiento no es «Sin cambio» | — |
| Verificación de forma | Sistema (fórmula) | No | Calculada; no se edita | Dice qué falta en la fila o «Completa» | Completa |

**Listas cerradas:**

- fuentes: «Reglamento interior» · «Estatuto orgánico» · «Manual de organización» · «Estructura autorizada (SAFIN)» · «Acuerdo o decreto de creación» · «Otra»
- movimientos: «Sin cambio» · «Alta» · «Modificación» · «Baja»
- niveles: «Titular del ente» · «Subsecretaría o equivalente» · «Dirección general o equivalente» · «Dirección de área o equivalente» · «Subdirección o equivalente» · «Jefatura de departamento o equivalente»

## Padrón de sujetos obligados (M-04)

Registrar a la persona que ocupa el puesto titular de cada unidad, o marcarlo como vacante.

**Cada fila es:** Una fila por unidad de la estructura confirmada; el sistema las precarga.

| Columna | Quién la llena | Obligatoria | Formato | Verificación de forma | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| Clave de la unidad | Sistema (de la estructura confirmada) | Sí | No se edita | Debe existir en la estructura confirmada | SFE-02 |
| Unidad administrativa | Sistema | Sí | No se edita | — | Dirección General de Administración |
| Nivel | Sistema | Sí | No se edita | — | Dirección general o equivalente |
| Denominación del puesto | Precargada · Enlace | Sí | Texto, hasta 200 caracteres | No vacía | Director General de Administración |
| Carácter | Enlace | Sí | Lista cerrada | Valor de la lista; si es «Vacante», los datos de la persona quedan vacíos | Titular |
| RFC con homoclave | Enlace | Sí | 13 caracteres (identificador por confirmar con la SABG) | 13 caracteres; un RFC repetido avisa (una persona puede ocupar dos puestos, VI-10) | LOCM800101AB1 |
| Nombre(s) | Enlace | Sí | Texto | No vacío | María Fernanda |
| Primer apellido | Enlace | Sí | Texto | No vacío | López |
| Segundo apellido | Enlace | No | Texto | — | Cruz |
| Correo electrónico personal | Enlace | Sí | Correo personal, no institucional (Ley E-R art. 19 fr. V; L-01) | Contiene «@» y un punto | mf.lopez@correo-ejemplo.mx |
| Fecha de nombramiento o encargo | Enlace | Sí | Fecha dd/mm/aaaa | Fecha correcta, no posterior a hoy | 15/09/2021 |
| Verificación de forma | Sistema (fórmula) | No | Calculada; no se edita | Dice qué falta en la fila o «Completa» | Completa |

**Listas cerradas:**

- caracter: «Titular» · «Encargado del despacho» · «Vacante»

## Asignación de anexos (M-05)

Marcar qué anexos trabaja cada sujeto obligado. Todo sujeto obligado presenta sus 43 anexos; esta asignación distribuye el trabajo dentro del ente y no impide que alguien reporte más (L-01, D-20). El estado de cada anexo lo decide el sujeto obligado en Fase 2 (D-19).

**Cada fila es:** Una fila por sujeto obligado del padrón; una columna por anexo E-R01 a E-R43.

| Columna | Quién la llena | Obligatoria | Formato | Verificación de forma | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| Clave de la unidad | Sistema | Sí | No se edita | — | SFE-02 |
| Unidad administrativa | Sistema | Sí | No se edita | — | Dirección General de Administración |
| Puesto | Sistema | Sí | No se edita | — | Director General de Administración |
| Persona | Sistema | Sí | No se edita; «Vacante» si aplica | — | María Fernanda López Cruz |
| E-R01 a E-R43 (43 columnas) | Sugerencia del sistema · Enlace | No | «Sí» o vacío | Solo «Sí» o vacío | Sí |
| Anexos asignados | Sistema (fórmula) | No | Calculada; no se edita | Cuenta los «Sí» de la fila | 18 |

**Listas cerradas:**

- si: «Sí»

## Sugerencia de asignación por naturaleza `[PROPUESTA · para L-02]`

| Naturaleza | Sugerencia que precarga el sistema |
| --- | --- |
| N1 · Individual | «Sí» para todos los sujetos obligados: cada quien reporta lo propio. |
| N2 · Común del ente | «Sí» solo para el titular del ente: se carga una vez y aparece por referencia en los demás. |
| N3 · Concentrado y desglose | «Sí» para el titular del ente y para el área administrativa que presenta el total; cada unidad agrega su parte en Fase 2. [POR DEFINIR en L-02: cómo identifica el sistema al área administrativa] |
| N4 · Por atribución | Vacío: el Enlace marca a quien tiene la competencia por reglamento interior. |
| N5 · Integración ascendente | Vacío: el Enlace marca a quien atiende el asunto. |

## Pendientes que cambian estas plantillas

- VI-09: si el identificador de la persona es el RFC, otro dato o ninguno (la columna dice «por confirmar con la SABG»).
- VI-10: si una persona puede ocupar dos puestos (hoy solo se avisa).
- VI-15: si hay sub-enlaces, la plantilla se genera por rama.
- L-02: naturaleza final de cada anexo y cómo se identifica el área administrativa (N3).
- Evaluar agregar «ubicación física» del puesto (referencia SERC, `docs/referencias/serc-federal.md`).
