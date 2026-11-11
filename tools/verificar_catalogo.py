"""Verifica que el catálogo de formatos cuadre con el Manual y con la propuesta de naturalezas.

Uso: python3 tools/verificar_catalogo.py [ruta-al-catalogo.json]
Sale con código 1 si encuentra diferencias.
"""

import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / "data" / "catalogo" / "formatos-v1.json"
NATURALEZAS = RAIZ / "data" / "catalogo" / "naturalezas.json"

# Cifras esperadas según catalogo-formatos.md v1 (2-nov-2026) y CONTEXTO §6.2.
ESPERADO_OBLIGADOS = {"todos": 23, "condicional": 20}
ESPERADO_TIPO = {"tabla": 35, "documento": 7, "mixto": 1}
ESPERADO_NATURALEZA = {"N1": 7, "N2": 4, "N3": 7, "N4": 21, "N5": 4}
TIPOS = set(ESPERADO_TIPO)
OBLIGADOS = set(ESPERADO_OBLIGADOS)


def verificar(ruta_catalogo: Path) -> list[str]:
    catalogo = json.loads(ruta_catalogo.read_text(encoding="utf-8"))
    naturalezas = {n["codigo"] for n in json.loads(NATURALEZAS.read_text(encoding="utf-8"))["naturalezas"]}
    formatos = catalogo["formatos"]
    problemas: list[str] = []

    claves = [f["clave"] for f in formatos]
    esperadas = [f"E-R{n:02d}" for n in range(1, 44)]
    if claves != esperadas:
        faltan = sorted(set(esperadas) - set(claves))
        sobran = sorted(set(claves) - set(esperadas))
        repetidas = sorted(c for c, n in Counter(claves).items() if n > 1)
        problemas.append(
            f"Claves fuera de orden o incompletas. Faltan: {faltan}. Sobran: {sobran}. Repetidas: {repetidas}"
        )

    for f in formatos:
        clave = f.get("clave", "?")
        for campo in ("nombre", "tema", "subtema", "tipo", "obligados", "naturaleza"):
            if not f.get(campo):
                problemas.append(f"{clave}: falta el campo «{campo}»")
        if f.get("tema") not in catalogo["temas"]:
            problemas.append(f"{clave}: tema «{f.get('tema')}» no está en el catálogo de temas")
        if f.get("subtema") not in catalogo["subtemas"]:
            problemas.append(f"{clave}: subtema «{f.get('subtema')}» no está en el catálogo de subtemas")
        if f.get("tipo") not in TIPOS:
            problemas.append(f"{clave}: tipo «{f.get('tipo')}» no es uno de {sorted(TIPOS)}")
        if f.get("obligados") not in OBLIGADOS:
            problemas.append(f"{clave}: obligados «{f.get('obligados')}» no es uno de {sorted(OBLIGADOS)}")
        if f.get("naturaleza") not in naturalezas:
            problemas.append(f"{clave}: naturaleza «{f.get('naturaleza')}» no está definida")

    for nombre, campo, esperado in (
        ("obligados", "obligados", ESPERADO_OBLIGADOS),
        ("tipo", "tipo", ESPERADO_TIPO),
        ("naturaleza", "naturaleza", ESPERADO_NATURALEZA),
    ):
        real = dict(Counter(f.get(campo) for f in formatos))
        if real != esperado:
            problemas.append(f"Conteo por {nombre}: se esperaba {esperado} y hay {real}")

    if len(catalogo["subtemas"]) != 9 or len(catalogo["temas"]) != 4:
        problemas.append("El Manual 6.1 fija 4 temas y 9 subtemas")

    return problemas


def main() -> int:
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else CATALOGO
    problemas = verificar(ruta)
    if problemas:
        print(f"Catálogo con {len(problemas)} diferencia(s):")
        for p in problemas:
            print(f"  - {p}")
        return 1
    print("Catálogo correcto: 43 formatos, 4 temas, 9 subtemas; conteos por obligados, tipo y naturaleza cuadran.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
