"""Busca términos prohibidos por el principio rector de la SABG en los textos que ve el usuario.

La SABG coordina; no valida, certifica ni avala (Ley E-R arts. 16 y 23).
Se corre antes de cada despliegue (lineamientos-ux-y-lenguaje.md §1).

Uso: python3 tools/verificar_lenguaje.py [carpeta-o-archivo ...]
Sin argumentos revisa las carpetas de textos de interfaz, correos y plantillas de documentos.
Sale con código 1 si encuentra coincidencias.
"""

import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REGLAS = RAIZ / "data" / "lenguaje" / "terminos-prohibidos.json"

# Carpetas con textos visibles. Se ajustan cuando se fije el stack (T-01).
RUTAS_POR_OMISION = ["textos", "plantillas"]
EXTENSIONES = {".json", ".yml", ".yaml", ".txt", ".html", ".htm", ".md", ".po", ".properties", ".csv"}


def normalizar(texto: str) -> str:
    """Minúsculas y sin acentos, para que «Validación» y «validacion» coincidan."""
    sin_acentos = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sin_acentos if not unicodedata.combining(c)).lower()


def cargar_reglas() -> tuple[list[dict], list[str]]:
    reglas = json.loads(REGLAS.read_text(encoding="utf-8"))
    permitidas = sorted((normalizar(f) for f in reglas.get("frases_permitidas", [])), key=len, reverse=True)
    return reglas["terminos"], permitidas


def archivos(rutas: list[Path]):
    for ruta in rutas:
        if ruta.is_file():
            yield ruta
        elif ruta.is_dir():
            for f in sorted(ruta.rglob("*")):
                if f.is_file() and f.suffix.lower() in EXTENSIONES:
                    yield f


def revisar(rutas: list[Path]) -> list[str]:
    terminos, permitidas = cargar_reglas()
    hallazgos = []
    for archivo in archivos(rutas):
        for n, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), start=1):
            limpia = normalizar(linea)
            for frase in permitidas:
                limpia = limpia.replace(frase, " ")
            for t in terminos:
                if t["raiz"] in limpia:
                    hallazgos.append(
                        f"{archivo.relative_to(RAIZ) if archivo.is_relative_to(RAIZ) else archivo}:{n}: "
                        f"«{t['raiz']}» → usa «{t['usar_en_su_lugar']}» · {linea.strip()[:100]}"
                    )
    return hallazgos


def main() -> int:
    rutas = [Path(a).resolve() for a in sys.argv[1:]] or [RAIZ / r for r in RUTAS_POR_OMISION]
    existentes = [r for r in rutas if r.exists()]
    if not existentes:
        print("No hay textos que revisar todavía en: " + ", ".join(str(r) for r in rutas))
        return 0
    hallazgos = revisar(existentes)
    if hallazgos:
        print(f"{len(hallazgos)} texto(s) contradicen el principio rector:")
        for h in hallazgos:
            print(f"  - {h}")
        return 1
    print("Sin términos prohibidos en los textos revisados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
