"""Genera las plantillas Excel de Fase 1 y su especificación columna por columna.

Una sola fuente de verdad: las columnas se definen en PLANTILLAS; de ahí salen
los .xlsx (que en producción generará el sistema por ente) y docs/plantillas-excel.md.

Uso:
  python3 tools/generar_plantillas.py <carpeta-de-salida>   # muestras .xlsx con un ente ficticio
  python3 tools/generar_plantillas.py --solo-especificacion # solo docs/plantillas-excel.md

Datos de muestra: ficticios («Secretaría Ficticia de Ejemplo»). Nunca usar datos reales aquí.
"""

import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = json.loads((RAIZ / "data" / "catalogo" / "formatos-v1.json").read_text(encoding="utf-8"))
VERSION_PLANTILLAS = "1.0"
FILAS = 400  # filas de captura disponibles por hoja

# ---------------------------------------------------------------- listas cerradas
LISTAS = {
    "niveles": [
        "Titular del ente",
        "Subsecretaría o equivalente",
        "Dirección general o equivalente",
        "Dirección de área o equivalente",
        "Subdirección o equivalente",
        "Jefatura de departamento o equivalente",
    ],
    "fuentes": [
        "Reglamento interior",
        "Estatuto orgánico",
        "Manual de organización",
        "Estructura autorizada (SAFIN)",
        "Acuerdo o decreto de creación",
        "Otra",
    ],
    "movimientos": ["Sin cambio", "Alta", "Modificación", "Baja"],
    "caracter": ["Titular", "Encargado del despacho", "Vacante"],
    "si": ["Sí"],
}

# ---------------------------------------------------------------- definición de columnas
# Cada columna: encabezado, quién la llena (precargada / Enlace / sistema), si es obligatoria,
# formato, regla de verificación de forma y un ejemplo ficticio.
PLANTILLAS = {
    "estructura": {
        "archivo": "Plantilla_Estructura",
        "titulo": "Estructura orgánica",
        "modulo": "M-03",
        "proposito": "Confirmar o corregir la estructura orgánica precargada del ente, hasta jefatura de departamento o equivalente.",
        "fila": "Una fila por unidad administrativa.",
        "columnas": [
            dict(enc="Clave de la unidad", llena="Precargada · el Enlace la asigna en altas", oblig=True, ancho=18,
                 formato="Texto, hasta 30 caracteres, única en el ente", regla="No vacía y sin repetirse en la hoja",
                 ejemplo="SFE-02"),
            dict(enc="Nombre de la unidad administrativa", llena="Precargada · Enlace", oblig=True, ancho=46,
                 formato="Texto, hasta 200 caracteres", regla="No vacío", ejemplo="Dirección General de Administración"),
            dict(enc="Nivel", llena="Precargada · Enlace", oblig=True, ancho=34, lista="niveles",
                 formato="Lista cerrada", regla="Valor de la lista", ejemplo="Dirección general o equivalente"),
            dict(enc="Clave de la unidad superior", llena="Precargada · Enlace", oblig=False, ancho=18,
                 formato="Texto: una clave de la columna A",
                 regla="Obligatoria salvo para el titular del ente; debe existir en la columna A", ejemplo="SFE-01"),
            dict(enc="Fuente documental", llena="Precargada · Enlace", oblig=True, ancho=30, lista="fuentes",
                 formato="Lista cerrada", regla="Valor de la lista", ejemplo="Reglamento interior"),
            dict(enc="Referencia de la fuente", llena="Precargada · Enlace", oblig=False, ancho=34,
                 formato="Texto: artículo y fecha de publicación", regla="—", ejemplo="Art. 5, fr. II · POE 12-jun-2026"),
            dict(enc="Movimiento", llena="Enlace", oblig=True, ancho=16, lista="movimientos",
                 formato="Lista cerrada; precargada como «Sin cambio»", regla="Valor de la lista", ejemplo="Sin cambio"),
            dict(enc="Motivo del movimiento", llena="Enlace", oblig=False, ancho=40,
                 formato="Texto, hasta 500 caracteres", regla="Obligatorio si el movimiento no es «Sin cambio»",
                 ejemplo=""),
            dict(enc="Verificación de forma", llena="Sistema (fórmula)", oblig=False, ancho=34,
                 formato="Calculada; no se edita", regla="Dice qué falta en la fila o «Completa»", ejemplo="Completa"),
        ],
    },
    "padron": {
        "archivo": "Plantilla_Padron",
        "titulo": "Padrón de sujetos obligados",
        "modulo": "M-04",
        "proposito": "Registrar a la persona que ocupa el puesto titular de cada unidad, o marcarlo como vacante.",
        "fila": "Una fila por unidad de la estructura confirmada; el sistema las precarga.",
        "columnas": [
            dict(enc="Clave de la unidad", llena="Sistema (de la estructura confirmada)", oblig=True, ancho=16,
                 formato="No se edita", regla="Debe existir en la estructura confirmada", ejemplo="SFE-02"),
            dict(enc="Unidad administrativa", llena="Sistema", oblig=True, ancho=40, formato="No se edita",
                 regla="—", ejemplo="Dirección General de Administración"),
            dict(enc="Nivel", llena="Sistema", oblig=True, ancho=30, formato="No se edita", regla="—",
                 ejemplo="Dirección general o equivalente"),
            dict(enc="Denominación del puesto", llena="Precargada · Enlace", oblig=True, ancho=34,
                 formato="Texto, hasta 200 caracteres", regla="No vacía", ejemplo="Director General de Administración"),
            dict(enc="Carácter", llena="Enlace", oblig=True, ancho=22, lista="caracter",
                 formato="Lista cerrada", regla="Valor de la lista; si es «Vacante», los datos de la persona quedan vacíos",
                 ejemplo="Titular"),
            dict(enc="RFC con homoclave", llena="Enlace", oblig=True, ancho=17,
                 formato="13 caracteres (identificador por confirmar con la SABG)",
                 regla="13 caracteres; un RFC repetido avisa (una persona puede ocupar dos puestos, VI-10)",
                 ejemplo="LOCM800101AB1"),
            dict(enc="Nombre(s)", llena="Enlace", oblig=True, ancho=20, formato="Texto", regla="No vacío",
                 ejemplo="María Fernanda"),
            dict(enc="Primer apellido", llena="Enlace", oblig=True, ancho=18, formato="Texto", regla="No vacío",
                 ejemplo="López"),
            dict(enc="Segundo apellido", llena="Enlace", oblig=False, ancho=18, formato="Texto", regla="—",
                 ejemplo="Cruz"),
            dict(enc="Correo electrónico personal", llena="Enlace", oblig=True, ancho=32,
                 formato="Correo personal, no institucional (Ley E-R art. 19 fr. V; L-01)",
                 regla="Contiene «@» y un punto", ejemplo="mf.lopez@correo-ejemplo.mx"),
            dict(enc="Fecha de nombramiento o encargo", llena="Enlace", oblig=True, ancho=16,
                 formato="Fecha dd/mm/aaaa", regla="Fecha correcta, no posterior a hoy", ejemplo="15/09/2021"),
            dict(enc="Verificación de forma", llena="Sistema (fórmula)", oblig=False, ancho=40,
                 formato="Calculada; no se edita", regla="Dice qué falta en la fila o «Completa»", ejemplo="Completa"),
        ],
    },
    "asignacion": {
        "archivo": "Plantilla_Asignacion",
        "titulo": "Asignación de anexos",
        "modulo": "M-05",
        "proposito": "Marcar qué anexos trabaja cada sujeto obligado. Todo sujeto obligado presenta sus 43 anexos; esta asignación distribuye el trabajo dentro del ente y no impide que alguien reporte más (L-01, D-20). El estado de cada anexo lo decide el sujeto obligado en Fase 2 (D-19).",
        "fila": "Una fila por sujeto obligado del padrón; una columna por anexo E-R01 a E-R43.",
        "columnas": [
            dict(enc="Clave de la unidad", llena="Sistema", oblig=True, ancho=14, formato="No se edita", regla="—",
                 ejemplo="SFE-02"),
            dict(enc="Unidad administrativa", llena="Sistema", oblig=True, ancho=34, formato="No se edita",
                 regla="—", ejemplo="Dirección General de Administración"),
            dict(enc="Puesto", llena="Sistema", oblig=True, ancho=30, formato="No se edita", regla="—",
                 ejemplo="Director General de Administración"),
            dict(enc="Persona", llena="Sistema", oblig=True, ancho=26, formato="No se edita; «Vacante» si aplica",
                 regla="—", ejemplo="María Fernanda López Cruz"),
            dict(enc="E-R01 a E-R43 (43 columnas)", llena="Sugerencia del sistema · Enlace", oblig=False, ancho=7,
                 lista="si", formato="«Sí» o vacío", regla="Solo «Sí» o vacío",
                 ejemplo="Sí"),
            dict(enc="Anexos asignados", llena="Sistema (fórmula)", oblig=False, ancho=12,
                 formato="Calculada; no se edita", regla="Cuenta los «Sí» de la fila", ejemplo="18"),
        ],
    },
}

REGLAS_GENERALES = [
    "El sistema genera cada plantilla para un ente y un corte; la hoja oculta «Control» guarda ente, corte y versión de plantilla. Al subirla, el sistema no importa el archivo si no corresponde al ente o si la versión no es la vigente, y explica por qué.",
    "Nada se importa a medias: o el archivo pasa completo la verificación de forma, o se devuelve un reporte por renglón con lo que falta (lineamientos de UX §4.4).",
    "La columna «Verificación de forma» ayuda al Enlace a corregir antes de subir; la verificación que cuenta es la del sistema al importar.",
    "Encabezados, columnas del sistema y fórmulas están protegidos (sin contraseña) para evitar cambios accidentales; las celdas de captura no.",
    "Los textos de las plantillas pasan tools/verificar_lenguaje.py (términos prohibidos en data/lenguaje/terminos-prohibidos.json).",
    "Las muestras usan un ente ficticio. Las plantillas reales solo se generan dentro del servidor de la SABG.",
]

SUGERENCIA_ASIGNACION = [
    ("N1 · Individual", "«Sí» para todos los sujetos obligados: cada quien reporta lo propio."),
    ("N2 · Común del ente", "«Sí» solo para el titular del ente: se carga una vez y aparece por referencia en los demás."),
    ("N3 · Concentrado y desglose", "«Sí» para el titular del ente y para el área administrativa que presenta el total; cada unidad agrega su parte en Fase 2. [POR DEFINIR en L-02: cómo identifica el sistema al área administrativa]"),
    ("N4 · Por atribución", "Vacío: el Enlace marca a quien tiene la competencia por reglamento interior."),
    ("N5 · Integración ascendente", "Vacío: el Enlace marca a quien atiende el asunto."),
]

# ---------------------------------------------------------------- ente ficticio de muestra
ENTE = {"clave": "SFE", "nombre": "Secretaría Ficticia de Ejemplo", "corte": "Corte 1 · Autoanálisis"}
UNIDADES = [
    # clave, nombre, nivel, superior, fuente, referencia, puesto
    ("SFE-01", "Oficina de la persona titular de la Secretaría", 0, "", 0, "Art. 1 · POE 12-jun-2026", "Secretaria"),
    ("SFE-02", "Dirección General de Administración", 2, "SFE-01", 0, "Art. 5, fr. II · POE 12-jun-2026", "Director General de Administración"),
    ("SFE-03", "Dirección de Recursos Humanos", 3, "SFE-02", 0, "Art. 5, fr. II, inc. a", "Directora de Recursos Humanos"),
    ("SFE-04", "Departamento de Nóminas", 5, "SFE-03", 2, "Manual de organización 2025, p. 14", "Jefe del Departamento de Nóminas"),
    ("SFE-05", "Dirección de Recursos Materiales", 3, "SFE-02", 0, "Art. 5, fr. II, inc. b", "Director de Recursos Materiales"),
    ("SFE-06", "Departamento de Almacén e Inventarios", 5, "SFE-05", 2, "Manual de organización 2025, p. 18", "Jefa del Departamento de Almacén e Inventarios"),
    ("SFE-07", "Subsecretaría de Planeación", 1, "SFE-01", 0, "Art. 5, fr. I", "Subsecretario de Planeación"),
    ("SFE-08", "Unidad de Asuntos Jurídicos", 3, "SFE-01", 0, "Art. 5, fr. III", "Titular de la Unidad de Asuntos Jurídicos"),
]
AREA_ADMINISTRATIVA = "SFE-02"  # supuesto de la muestra para la sugerencia N3

# ---------------------------------------------------------------- estilo
ARIAL = "Arial"
F_ENC = Font(name=ARIAL, bold=True, color="FFFFFF", size=10)
F_TXT = Font(name=ARIAL, size=10)
F_SIS = Font(name=ARIAL, size=10, color="595959")
F_TIT = Font(name=ARIAL, bold=True, size=14)
F_SUB = Font(name=ARIAL, bold=True, size=11)
R_ENC = PatternFill("solid", fgColor="1F3A5F")
R_SIS = PatternFill("solid", fgColor="EDEDED")
R_CAP = PatternFill("solid", fgColor="FFF8DC")
R_OK = PatternFill("solid", fgColor="E2EFDA")
R_AVISO = PatternFill("solid", fgColor="FCE4D6")
LINEA = Side(style="thin", color="BFBFBF")
BORDE = Border(left=LINEA, right=LINEA, top=LINEA, bottom=LINEA)
ENVOLVER = Alignment(wrap_text=True, vertical="top")
CENTRO = Alignment(horizontal="center", vertical="center", wrap_text=True)
LIBRE = Protection(locked=False)


def hoja_listas(wb):
    ws = wb.create_sheet("Listas")
    rangos = {}
    for i, (nombre, valores) in enumerate(LISTAS.items(), start=1):
        col = get_column_letter(i)
        ws[f"{col}1"] = nombre
        for j, v in enumerate(valores, start=2):
            ws[f"{col}{j}"] = v
        rangos[nombre] = f"=Listas!${col}$2:${col}${len(valores) + 1}"
    ws.sheet_state = "hidden"
    return rangos


def hoja_control(wb, plantilla):
    ws = wb.create_sheet("Control")
    datos = [
        ("plantilla", plantilla),
        ("version_plantilla", VERSION_PLANTILLAS),
        ("version_catalogo", CATALOGO["version_catalogo"]),
        ("ente_clave", ENTE["clave"]),
        ("ente_nombre", ENTE["nombre"]),
        ("corte", ENTE["corte"]),
        ("generada", date.today().isoformat()),
        ("aviso", "Hoja de control del sistema. No la modifiques."),
    ]
    for i, (k, v) in enumerate(datos, start=1):
        ws.cell(i, 1, k)
        ws.cell(i, 2, v)
    ws.sheet_state = "hidden"


def alto(texto, ancho_chars):
    """Alto de fila para que un texto envuelto quepa (Arial 10 ≈ 1 carácter por unidad de ancho)."""
    lineas = max(1, -(-len(str(texto or "")) // max(1, int(ancho_chars * 0.95))))
    return max(15, lineas * 13.5)


def texto_largo(ws, fila, col_ini, texto, fuente):
    """Escribe un texto envuelto en las columnas col_ini..E de Instrucciones y ajusta el alto de la fila."""
    c = ws.cell(fila, col_ini, texto)
    c.font, c.alignment = fuente, ENVOLVER
    ws.merge_cells(start_row=fila, start_column=col_ini, end_row=fila, end_column=5)
    ancho = 30 * (6 - col_ini)
    ws.row_dimensions[fila].height = max(ws.row_dimensions[fila].height or 15, alto(texto, ancho))


def hoja_instrucciones(wb, clave):
    p = PLANTILLAS[clave]
    ws = wb.active
    ws.title = "Instrucciones"
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 30
    for c in "BCDE":
        ws.column_dimensions[c].width = 30
    ws["A1"] = f"{p['titulo']} · {ENTE['nombre']}"
    ws["A1"].font = F_TIT
    ws["A2"] = f"{ENTE['corte']} · Plantilla {VERSION_PLANTILLAS} · Generada por el sistema el {date.today():%d/%m/%Y}"
    ws["A2"].font = F_SIS
    fila = 4
    for etiqueta, texto in (("Para qué sirve", p["proposito"]), ("Cada fila es", p["fila"])):
        ws.cell(fila, 1, etiqueta).font = F_SUB
        ws.cell(fila, 1).alignment = ENVOLVER
        texto_largo(ws, fila, 2, texto, F_TXT)
        fila += 1

    fila += 1
    ws.cell(fila, 1, "Cómo llenarla").font = F_SUB
    pasos = [
        "1. Captura solo en las celdas amarillas de la hoja «Captura». Las grises las llena el sistema.",
        "2. Usa las listas desplegables donde existan; no escribas otros valores.",
        "3. Revisa la columna «Verificación de forma» hasta que todas las filas digan «Completa».",
        "4. No cambies el nombre de las hojas ni el orden de las columnas, y no borres la hoja oculta «Control».",
        "5. Sube el archivo en el sistema. Si algo falta, el sistema te devuelve un reporte por renglón y no importa nada hasta que el archivo esté completo.",
    ]
    for paso in pasos:
        fila += 1
        texto_largo(ws, fila, 1, paso, F_TXT)
    fila += 2
    ws.cell(fila, 1, "Leyenda").font = F_SUB
    for texto, relleno in (("Celda de captura", R_CAP), ("La llena el sistema", R_SIS), ("Fila completa", R_OK),
                           ("Fila con algo pendiente", R_AVISO)):
        fila += 1
        ws.cell(fila, 1).fill = relleno
        ws.cell(fila, 1).border = BORDE
        ws.cell(fila, 2, texto).font = F_TXT

    if clave == "asignacion":
        fila += 2
        ws.cell(fila, 1, "Sugerencia del sistema").font = F_SUB
        fila += 1
        texto_largo(ws, fila, 1, "La plantilla llega con «Sí» sugeridos según la naturaleza de cada anexo. Puedes cambiarlos.", F_TXT)
        for nat, regla in SUGERENCIA_ASIGNACION:
            fila += 1
            ws.cell(fila, 1, nat).font = F_TXT
            ws.cell(fila, 1).alignment = ENVOLVER
            texto_largo(ws, fila, 2, regla, F_TXT)

    fila += 2
    ws.cell(fila, 1, "Columnas y ejemplo de llenado").font = F_SUB
    fila += 1
    for j, t in enumerate(("Columna", "Quién la llena", "Formato", "Regla", "Ejemplo"), start=1):
        c = ws.cell(fila, j, t)
        c.font, c.fill, c.border, c.alignment = F_ENC, R_ENC, BORDE, CENTRO
    for col in p["columnas"]:
        fila += 1
        valores = (col["enc"] + (" *" if col["oblig"] else ""), col["llena"], col["formato"], col["regla"], col["ejemplo"])
        for j, v in enumerate(valores, start=1):
            c = ws.cell(fila, j, v)
            c.font, c.border, c.alignment = F_TXT, BORDE, ENVOLVER
        ws.row_dimensions[fila].height = max(alto(v, 30) for v in valores)
    fila += 1
    ws.cell(fila, 1, "* Obligatoria").font = F_SIS
    fila += 2
    texto_largo(ws, fila, 1, "La información es responsabilidad del ente y de cada persona servidora pública saliente (Ley E-R, art. 16). La SABG la recibe y verifica en su forma.", F_SIS)


def encabezados(ws, columnas, fila=1):
    for j, col in enumerate(columnas, start=1):
        c = ws.cell(fila, j, col["enc"])
        c.font, c.fill, c.border, c.alignment = F_ENC, R_ENC, BORDE, CENTRO
        ws.column_dimensions[get_column_letter(j)].width = col["ancho"]
    ws.row_dimensions[fila].height = 32


def formato_verificacion(ws, rango, celda_ref):
    ws.conditional_formatting.add(rango, FormulaRule(formula=[f'{celda_ref}="Completa"'], fill=R_OK))
    ws.conditional_formatting.add(rango, FormulaRule(formula=[f'AND({celda_ref}<>"",{celda_ref}<>"Completa")'], fill=R_AVISO))


def proteger(ws):
    ws.protection.sheet = True
    ws.protection.formatColumns = False
    ws.protection.formatRows = False
    ws.protection.autoFilter = False
    ws.protection.sort = False


def validacion_lista(ws, rangos, nombre, rango_celdas, mensaje):
    dv = DataValidation(type="list", formula1=rangos[nombre], allow_blank=True, showErrorMessage=True,
                        errorTitle="Valor fuera de la lista", error=mensaje)
    dv.add(rango_celdas)
    ws.add_data_validation(dv)


def plantilla_estructura(carpeta: Path) -> Path:
    wb = Workbook()
    hoja_instrucciones(wb, "estructura")
    ws = wb.create_sheet("Captura", 1)
    rangos = hoja_listas(wb)
    hoja_control(wb, "estructura")
    cols = PLANTILLAS["estructura"]["columnas"]
    encabezados(ws, cols)
    ultima = FILAS + 1
    for i in range(2, ultima + 1):
        for j in range(1, 9):
            c = ws.cell(i, j)
            c.fill, c.border, c.font, c.protection = R_CAP, BORDE, F_TXT, LIBRE
        ws.cell(i, 9).value = (
            f'=IF(COUNTA(A{i}:H{i})=0,"",'
            f'IF(A{i}="","Falta la clave",'
            f'IF(COUNTIF($A$2:$A${ultima},A{i})>1,"Clave repetida",'
            f'IF(B{i}="","Falta el nombre",'
            f'IF(C{i}="","Falta el nivel",'
            f'IF(AND(C{i}<>"Titular del ente",D{i}=""),"Falta la unidad superior",'
            f'IF(AND(D{i}<>"",COUNTIF($A$2:$A${ultima},D{i})=0),"La unidad superior no está en la hoja",'
            f'IF(E{i}="","Falta la fuente documental",'
            f'IF(G{i}="","Falta el movimiento",'
            f'IF(AND(G{i}<>"Sin cambio",H{i}=""),"Falta el motivo del movimiento","Completa"))))))))))'
        )
        c = ws.cell(i, 9)
        c.fill, c.border, c.font = R_SIS, BORDE, F_SIS
    for i, (clave, nombre, nivel, sup, fuente, ref, _puesto) in enumerate(UNIDADES, start=2):
        for j, v in enumerate((clave, nombre, LISTAS["niveles"][nivel], sup, LISTAS["fuentes"][fuente], ref, "Sin cambio"), start=1):
            ws.cell(i, j, v)
    validacion_lista(ws, rangos, "niveles", f"C2:C{ultima}", "Elige un nivel de la lista.")
    validacion_lista(ws, rangos, "fuentes", f"E2:E{ultima}", "Elige una fuente de la lista.")
    validacion_lista(ws, rangos, "movimientos", f"G2:G{ultima}", "Elige un movimiento de la lista.")
    formato_verificacion(ws, f"I2:I{ultima}", "$I2")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:I{ultima}"
    proteger(ws)
    ruta = carpeta / f"{PLANTILLAS['estructura']['archivo']}_{ENTE['clave']}.xlsx"
    wb.save(ruta)
    return ruta


def plantilla_padron(carpeta: Path) -> Path:
    wb = Workbook()
    hoja_instrucciones(wb, "padron")
    ws = wb.create_sheet("Captura", 1)
    rangos = hoja_listas(wb)
    hoja_control(wb, "padron")
    cols = PLANTILLAS["padron"]["columnas"]
    encabezados(ws, cols)
    ultima = len(UNIDADES) + 1
    for i, (clave, nombre, nivel, _s, _f, _r, puesto) in enumerate(UNIDADES, start=2):
        for j, v in enumerate((clave, nombre, LISTAS["niveles"][nivel]), start=1):
            c = ws.cell(i, j, v)
            c.fill, c.border, c.font = R_SIS, BORDE, F_SIS
        ws.cell(i, 4, puesto)
        for j in range(4, 12):
            c = ws.cell(i, j)
            c.fill, c.border, c.font, c.protection = R_CAP, BORDE, F_TXT, LIBRE
        ws.cell(i, 11).number_format = "dd/mm/yyyy"
        ws.cell(i, 12).value = (
            f'=IF(A{i}="","",'
            f'IF(D{i}="","Falta la denominación del puesto",'
            f'IF(E{i}="","Falta el carácter",'
            f'IF(E{i}="Vacante",IF(COUNTA(F{i}:K{i})>0,"Vacante: deja vacíos los datos de la persona","Completa"),'
            f'IF(LEN(F{i})<>13,"El RFC debe tener 13 caracteres",'
            f'IF(COUNTIF($F$2:$F${ultima},F{i})>1,"RFC repetido: confirma si ocupa dos puestos",'
            f'IF(OR(G{i}="",H{i}=""),"Falta el nombre o el primer apellido",'
            f'IF(OR(ISERROR(SEARCH("@",J{i})),ISERROR(SEARCH(".",J{i}))),"Falta el correo personal o está incompleto",'
            f'IF(K{i}="","Falta la fecha de nombramiento",'
            f'IF(K{i}>TODAY(),"La fecha de nombramiento es futura","Completa"))))))))))'
        )
        c = ws.cell(i, 12)
        c.fill, c.border, c.font = R_SIS, BORDE, F_SIS
    validacion_lista(ws, rangos, "caracter", f"E2:E{ultima}", "Elige Titular, Encargado del despacho o Vacante.")
    dv_rfc = DataValidation(type="textLength", operator="equal", formula1="13", allow_blank=True, showErrorMessage=True,
                            errorTitle="RFC incompleto", error="El RFC con homoclave tiene 13 caracteres.")
    dv_rfc.add(f"F2:F{ultima}")
    ws.add_data_validation(dv_rfc)
    dv_fecha = DataValidation(type="date", operator="between", formula1="DATE(1990,1,1)", formula2="TODAY()",
                              allow_blank=True, showErrorMessage=True, errorTitle="Fecha no válida",
                              error="Escribe una fecha en formato dd/mm/aaaa, no posterior a hoy.")
    dv_fecha.add(f"K2:K{ultima}")
    ws.add_data_validation(dv_fecha)
    formato_verificacion(ws, f"L2:L{ultima}", "$L2")
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:L{ultima}"
    proteger(ws)
    ruta = carpeta / f"{PLANTILLAS['padron']['archivo']}_{ENTE['clave']}.xlsx"
    wb.save(ruta)
    return ruta


def plantilla_asignacion(carpeta: Path) -> Path:
    wb = Workbook()
    hoja_instrucciones(wb, "asignacion")
    ws = wb.create_sheet("Captura", 1)
    rangos = hoja_listas(wb)
    hoja_control(wb, "asignacion")
    formatos = CATALOGO["formatos"]
    fijas = PLANTILLAS["asignacion"]["columnas"][:4]
    # Filas 1 a 4: clave del anexo, nombre, naturaleza y total asignado en el ente.
    for j, col in enumerate(fijas, start=1):
        ws.cell(1, j, col["enc"])
        ws.merge_cells(start_row=1, start_column=j, end_row=3, end_column=j)
        ws.column_dimensions[get_column_letter(j)].width = col["ancho"]
    ws.cell(4, 1, "Sujetos con el anexo asignado")
    ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=4)
    primera_dato, ultima = 5, 4 + len(UNIDADES)
    for k, f in enumerate(formatos):
        j = 5 + k
        letra = get_column_letter(j)
        ws.cell(1, j, f["clave"])
        ws.cell(2, j, f["nombre"])
        ws.cell(3, j, f["naturaleza"])
        ws.cell(4, j, f'=COUNTIF({letra}{primera_dato}:{letra}{ultima},"Sí")')
        ws.column_dimensions[letra].width = 7
    col_total = 5 + len(formatos)
    ws.cell(1, col_total, "Anexos asignados")
    ws.merge_cells(start_row=1, start_column=col_total, end_row=3, end_column=col_total)
    ws.column_dimensions[get_column_letter(col_total)].width = 12
    for i in range(1, 4):
        for j in range(1, col_total + 1):
            c = ws.cell(i, j)
            c.font, c.fill, c.border = F_ENC, R_ENC, BORDE
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True,
                                    text_rotation=90 if (i == 2 and 5 <= j < col_total) else 0)
    ws.row_dimensions[2].height = 190
    for j in range(1, col_total + 1):
        c = ws.cell(4, j)
        c.font, c.fill, c.border, c.alignment = F_SIS, R_SIS, BORDE, CENTRO

    titular = UNIDADES[0][0]
    for i, (clave, nombre, _n, _s, _f, _r, puesto) in enumerate(UNIDADES, start=primera_dato):
        persona = "Vacante" if clave == "SFE-06" else "(del padrón)"
        for j, v in enumerate((clave, nombre, puesto, persona), start=1):
            c = ws.cell(i, j, v)
            c.fill, c.border, c.font = R_SIS, BORDE, F_SIS
        for k, f in enumerate(formatos):
            c = ws.cell(i, 5 + k)
            c.fill, c.border, c.font, c.alignment, c.protection = R_CAP, BORDE, F_TXT, CENTRO, LIBRE
            nat = f["naturaleza"]
            if nat == "N1" or (nat == "N2" and clave == titular) or (nat == "N3" and clave in (titular, AREA_ADMINISTRATIVA)):
                c.value = "Sí"
        ini, fin = get_column_letter(5), get_column_letter(col_total - 1)
        c = ws.cell(i, col_total, f'=COUNTIF({ini}{i}:{fin}{i},"Sí")')
        c.fill, c.border, c.font, c.alignment = R_SIS, BORDE, F_SIS, CENTRO
    rango_anexos = f"E{primera_dato}:{get_column_letter(col_total - 1)}{ultima}"
    validacion_lista(ws, rangos, "si", rango_anexos, "Escribe «Sí» o deja la celda vacía.")
    # Aviso: anexos comunes (N2) o concentrados (N3) que nadie tiene asignados.
    ws.conditional_formatting.add(
        f"E4:{get_column_letter(col_total - 1)}4",
        FormulaRule(formula=['AND(E$4=0,OR(E$3="N2",E$3="N3"))'], fill=R_AVISO))
    ws.freeze_panes = f"E{primera_dato}"
    proteger(ws)
    ruta = carpeta / f"{PLANTILLAS['asignacion']['archivo']}_{ENTE['clave']}.xlsx"
    wb.save(ruta)
    return ruta


def especificacion() -> str:
    out = [
        "# Plantillas Excel de Fase 1 · especificación columna por columna",
        "",
        f"> Generado por `tools/generar_plantillas.py` (plantillas v{VERSION_PLANTILLAS}, catálogo {CATALOGO['version_catalogo']}). No se edita a mano: se cambia el generador y se vuelve a correr.",
        "> Insumo del DRS de Fase 1 (Producto 2.1: «plantillas de carga masiva definidas columna por columna»).",
        "",
        "## Reglas generales",
        "",
    ]
    out += [f"{i}. {r}" for i, r in enumerate(REGLAS_GENERALES, start=1)]
    for p in PLANTILLAS.values():
        out += ["", f"## {p['titulo']} ({p['modulo']})", "", p["proposito"], "", f"**Cada fila es:** {p['fila']}", "",
                "| Columna | Quién la llena | Obligatoria | Formato | Verificación de forma | Ejemplo |",
                "| --- | --- | --- | --- | --- | --- |"]
        for c in p["columnas"]:
            out.append(f"| {c['enc']} | {c['llena']} | {'Sí' if c['oblig'] else 'No'} | {c['formato']} | {c['regla']} | {c['ejemplo'] or '—'} |")
        if "lista" in str(p["columnas"]):
            usadas = sorted({c["lista"] for c in p["columnas"] if c.get("lista")})
            out += ["", "**Listas cerradas:**", ""]
            out += [f"- {u}: " + " · ".join(f"«{v}»" for v in LISTAS[u]) for u in usadas]
    out += ["", "## Sugerencia de asignación por naturaleza `[PROPUESTA · para L-02]`", "",
            "| Naturaleza | Sugerencia que precarga el sistema |", "| --- | --- |"]
    out += [f"| {n} | {r} |" for n, r in SUGERENCIA_ASIGNACION]
    out += ["", "## Pendientes que cambian estas plantillas", "",
            "- VI-09: si el identificador de la persona es el RFC, otro dato o ninguno (la columna dice «por confirmar con la SABG»).",
            "- VI-10: si una persona puede ocupar dos puestos (hoy solo se avisa).",
            "- VI-15: si hay sub-enlaces, la plantilla se genera por rama.",
            "- L-02: naturaleza final de cada anexo y cómo se identifica el área administrativa (N3).",
            "- Evaluar agregar «ubicación física» del puesto (referencia SERC, `docs/referencias/serc-federal.md`).",
            ""]
    return "\n".join(out)


def main() -> int:
    (RAIZ / "docs" / "plantillas-excel.md").write_text(especificacion(), encoding="utf-8")
    if "--solo-especificacion" in sys.argv:
        print("Especificación escrita en docs/plantillas-excel.md")
        return 0
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    carpeta = Path(sys.argv[1])
    carpeta.mkdir(parents=True, exist_ok=True)
    for ruta in (plantilla_estructura(carpeta), plantilla_padron(carpeta), plantilla_asignacion(carpeta)):
        print(ruta)
    print("Especificación escrita en docs/plantillas-excel.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
