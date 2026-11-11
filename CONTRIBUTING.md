# Cómo trabajamos

## Flujo de cambios

1. Todo cambio sale de una rama `tipo/descripcion-corta` (por ejemplo `modulo/m03-estructura`, `fix/acuse-folio`, `docs/modelo-datos`).
2. Cada cambio es pequeño y trae sus pruebas.
3. Omar González revisa y fusiona a `main`. Nadie fusiona su propio cambio.
4. Solo Omar despliega a pruebas y a producción.
5. Antes de pedir revisión corren las verificaciones de `tools/`.

## Requerimientos y decisiones

- Si no está en el DRS o en un cambio validado por Adolfo Pastor, no se construye.
- Las dudas van a `06_Interfaz-Desarrollo/preguntas-abiertas.md` (Drive) con su supuesto de trabajo; Adolfo responde en 24 horas en Fase 1.
- Las decisiones técnicas que afectan al usuario o a la SABG se registran en `docs/decisiones/` y se avisan a Adolfo.
- Desarrollo no contacta a la SABG; todo pasa por Adolfo.

## Datos y seguridad

- Credenciales, contraseñas y datos reales de la SABG nunca entran a este repositorio ni pasan por Claude.
- Los datos de prueba son ficticios. Los reales solo viven en el servidor de la SABG.
- El sistema nunca captura contraseñas, usuarios ni números de acceso del formato E-R22 (RN-19).
- `.env` y archivos de configuración con secretos están en `.gitignore`; se documentan con un `.env.ejemplo`.

## Lenguaje

- Se dice «verificación de forma», «verificación formal», «recibido», «con observaciones de forma».
- Nunca «validar», «aprobar», «revisor», «certificar», «avalar», «rechazar» en textos que ve el usuario.
- Leyendas fijas del Manual 6.3.7: «Aplica sin información» y «No Aplicable» con su motivo.
- Toda salida (acuse, reporte, exportación, tablero) lleva la cláusula de salvaguarda.

## Un módulo está terminado cuando

- Cumple su ficha y sus casos de prueba pasan.
- Sus textos pasan `tools/verificar_lenguaje.py`.
- Está desplegado en el ambiente de pruebas y se mostró en la demo del viernes.
