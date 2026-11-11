# Arquitectura

> Estado: pendiente del inventario técnico T-01 (vie 13-nov-2026). Lo que sigue son los requisitos y el criterio de decisión; el stack se fija en `docs/decisiones/ADR-0002-stack.md` cuando T-01 termine.

## Criterio para el stack

Se reutiliza el stack, la autenticación y el design system del sistema previo que corre en el servidor de la SABG si resuelve, sin trabajo nuevo:

1. Cuentas personales con perfiles y sesiones que expiran.
2. Generación de PDF con folio, conteo de hojas y código de verificación.
3. Lectura y escritura de Excel con listas desplegables.
4. Envío de correo en segundo plano.
5. Bitácora inalterable (quién, qué, cuándo, desde dónde).

Lo que no resuelva se agrega como librería. No se cambia de stack a tres semanas de abrir.

## Inventario T-01 (lo llena Omar González)

| Concepto | Dato |
| --- | --- |
| Sistema previo alojado | |
| Servidor: CPU / RAM / disco / SO | |
| Acceso remoto (VPN, SSH) | |
| Base de datos disponible | |
| Stack del sistema previo | |
| Autenticación del sistema previo | |
| Design system: repositorio, librería, tokens | |
| Dominio o subdominio | |
| Certificado TLS | |
| Correo saliente (SMTP) | |
| Respaldos: frecuencia, destino, retención | |
| Ambientes disponibles | |

## Requisitos no funcionales de Fase 1

| ID | Requisito |
| --- | --- |
| RNF-01 | Aplicación web en navegadores vigentes, sin instalación |
| RNF-02 | En el servidor de la SABG; ambientes de pruebas y producción separados |
| RNF-03 | TLS; contraseñas con resumen criptográfico; sesiones con expiración |
| RNF-04 | Respaldo diario fuera del servidor; restauración probada antes del 1-dic |
| RNF-05 | Disponibilidad en horario hábil durante la ventana; incidencias críticas en 4 horas hábiles |
| RNF-06 | Concurrencia de todos los Enlaces (~160 cuentas) al cierre del 11-dic; prueba de carga el 7-dic |
| RNF-07 | Design system de la SABG; lenguaje según el principio rector |
| RNF-08 | Datos exportables en formatos abiertos; propiedad de la SABG |
| RNF-09 | Aviso de privacidad (correo personal) y acceso por ente |
| RNF-10 | Correo desde dominio institucional |

## Liberaciones

| Liberación | Fecha | Módulos |
| --- | --- | --- |
| R1 | mar 1-dic-2026 | M-09, M-01, M-02, M-00, M-03, M-04, M-05, M-06, M-08 básico, M-10 bienvenida |
| R2 | vie 4-dic-2026 | M-07: verificaciones previas, PDF del padrón, carga del firmado con cotejo, acuse |
| R3 | lun 14-dic-2026 | M-07: verificación formal, observaciones, reapertura; padrón consolidado; M-08 ampliado |
