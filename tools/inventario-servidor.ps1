# Inventario técnico del servidor de la SABG (T-01) · versión Windows
#
# Solo lee. No modifica nada, no lee archivos de credenciales,
# y enmascara contraseñas que aparezcan en líneas de comandos o tareas programadas.
#
# Uso (PowerShell como administrador):
#   powershell -ExecutionPolicy Bypass -File inventario-servidor.ps1 > inventario.md
#
# Revisa el archivo antes de compartirlo: si ves algo sensible que se escapó, bórralo.

function Seccion($t) { "`n## $t`n`n``````" }
function Fin { '```' }
function Enmascarar([string]$s) {
  $s = $s -replace '(?i)(pass(word)?|pwd|secret|token|api[_-]?key|clave)([=: ]+)[^ ;&"]+', '$1$3****'
  $s -replace '(://[^:/ ]+:)[^@ ]+@', '$1****@'
}
function Version($cmd, $arg = '--version') {
  if (Get-Command $cmd -ErrorAction SilentlyContinue) { "{0,-8} {1}" -f $cmd, ((& $cmd $arg 2>&1 | Select-Object -First 1) -join '') }
}

"# Inventario del servidor · $env:COMPUTERNAME · $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

Seccion "Sistema operativo"
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture, LastBootUpTime | Format-List | Out-String
Fin

Seccion "CPU y memoria"
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors | Format-List | Out-String
$m = Get-CimInstance Win32_ComputerSystem; "Memoria total: {0:N1} GB" -f ($m.TotalPhysicalMemory / 1GB)
Fin

Seccion "Disco"
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Select-Object DeviceID, @{n='TotalGB';e={[math]::Round($_.Size/1GB,1)}}, @{n='LibreGB';e={[math]::Round($_.FreeSpace/1GB,1)}} | Format-Table | Out-String
Fin

Seccion "Puertos en escucha"
Get-NetTCPConnection -State Listen | Sort-Object LocalPort -Unique | ForEach-Object { "{0,-6} {1}" -f $_.LocalPort, (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName }
Fin

Seccion "Servicios en ejecución"
Get-Service | Where-Object Status -eq 'Running' | Select-Object -ExpandProperty Name
Fin

Seccion "Lenguajes y herramientas"
Version php; Version node; Version python; Version java '-version'; Version dotnet; Version git; Version composer
Fin

Seccion "Bases de datos (servicios)"
Get-Service | Where-Object { $_.Name -match 'MSSQL|SQLServer|MySQL|MariaDB|postgres|Mongo|Redis' } | Select-Object Name, Status, StartType | Format-Table | Out-String
Fin

Seccion "IIS: sitios y enlaces"
if (Get-Module -ListAvailable WebAdministration) {
  Import-Module WebAdministration
  Get-Website | ForEach-Object { "--- $($_.Name) · $($_.State) · $($_.PhysicalPath)"; $_.Bindings.Collection | ForEach-Object { "  $($_.protocol) $($_.bindingInformation)" } }
} else { 'IIS no instalado' }
Fin

Seccion "Certificados TLS (equipo local)"
Get-ChildItem Cert:\LocalMachine\My | Select-Object Subject, Issuer, NotAfter | Format-Table -AutoSize | Out-String
Fin

Seccion "Aplicaciones desplegadas (carpetas y manifiestos)"
foreach ($base in 'C:\inetpub\wwwroot', 'C:\apps', 'D:\apps', 'C:\sitios', 'D:\sitios') {
  if (-not (Test-Path $base)) { continue }
  Get-ChildItem $base -Directory | ForEach-Object {
    "--- $($_.FullName)"
    foreach ($m in 'package.json','composer.json','requirements.txt','web.config','appsettings.json','*.csproj','*.sln','docker-compose.yml') {
      Get-ChildItem $_.FullName -Filter $m -ErrorAction SilentlyContinue | Select-Object -First 1 | ForEach-Object { "  $($_.Name)" }
    }
  }
}
Fin

Seccion "Tareas programadas (contraseñas enmascaradas)"
Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft\*' } | ForEach-Object {
  $a = ($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -join ' | '
  Enmascarar "$($_.TaskPath)$($_.TaskName) · $($_.State) · $a"
}
Fin

Seccion "Acceso remoto"
"RDP habilitado: " + ((Get-ItemProperty 'HKLM:\System\CurrentControlSet\Control\Terminal Server').fDenyTSConnections -eq 0)
Get-Service sshd -ErrorAction SilentlyContinue | Select-Object Name, Status | Format-Table | Out-String
Fin

"`nFin del inventario."
