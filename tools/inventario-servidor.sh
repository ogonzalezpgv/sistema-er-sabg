#!/usr/bin/env bash
# Inventario técnico del servidor de la SABG (T-01) · versión Linux
#
# Solo lee. No modifica nada, no lee archivos .env ni de credenciales,
# y enmascara contraseñas que aparezcan en líneas de comandos o tareas programadas.
#
# Uso (en el servidor, de preferencia con sudo para ver servicios y puertos):
#   sudo bash inventario-servidor.sh > inventario-$(hostname)-$(date +%F).md
#
# Revisa el archivo antes de compartirlo: si ves algo sensible que se escapó, bórralo.

set -u
export LC_ALL=C

tiene() { command -v "$1" >/dev/null 2>&1; }
seccion() { printf '\n## %s\n\n```\n' "$1"; }
fin() { printf '```\n'; }
enmascarar() {
  sed -E \
    -e 's/(pass(word)?|passwd|pwd|secret|token|api[_-]?key|clave)([=: ]+)[^ ;&"]+/\1\3****/Ig' \
    -e 's/(-p)[^ ]+/\1****/g' \
    -e 's#(://[^:/ ]+:)[^@ ]+@#\1****@#g'
}

printf '# Inventario del servidor · %s · %s\n' "$(hostname)" "$(date '+%Y-%m-%d %H:%M %Z')"

seccion "Sistema operativo"
cat /etc/os-release 2>/dev/null | grep -E '^(NAME|VERSION|ID)=' ; uname -srm
uptime -p 2>/dev/null || uptime
fin

seccion "CPU y memoria"
nproc 2>/dev/null | sed 's/^/Núcleos: /'
grep -m1 'model name' /proc/cpuinfo 2>/dev/null
free -h 2>/dev/null
fin

seccion "Disco"
df -hT -x tmpfs -x devtmpfs -x squashfs 2>/dev/null
fin

seccion "Puertos en escucha"
if tiene ss; then ss -tlnp 2>/dev/null; elif tiene netstat; then netstat -tlnp 2>/dev/null; fi
fin

seccion "Servicios activos"
if tiene systemctl; then systemctl list-units --type=service --state=running --no-pager --no-legend 2>/dev/null | awk '{print $1}'; fi
fin

seccion "Contenedores"
if tiene docker; then docker --version; docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null; else echo "Docker no instalado"; fi
if tiene podman; then podman --version; fi
fin

seccion "Lenguajes y herramientas"
for c in php node npm python3 java dotnet ruby go composer git; do
  if tiene "$c"; then printf '%-8s ' "$c"; "$c" --version 2>&1 | head -1; fi
done
fin

seccion "Bases de datos"
for c in mysql mariadb psql sqlcmd mongod redis-server; do
  if tiene "$c"; then printf '%-13s ' "$c"; "$c" --version 2>&1 | head -1; fi
done
if tiene systemctl; then systemctl list-units --type=service --no-pager --no-legend 2>/dev/null | grep -Ei 'mysql|maria|postgres|mongo|redis|mssql' | awk '{print $1, $3, $4}'; fi
fin

seccion "Servidor web y sitios"
tiene nginx && nginx -v 2>&1
tiene apache2 && apache2 -v 2>&1 | head -1
tiene httpd && httpd -v 2>&1 | head -1
for d in /etc/nginx/sites-enabled /etc/nginx/conf.d /etc/apache2/sites-enabled /etc/httpd/conf.d; do
  [ -d "$d" ] || continue
  echo "--- $d"
  grep -RhE '^\s*(server_name|root|proxy_pass|listen|ServerName|DocumentRoot|ProxyPass)\b' "$d" 2>/dev/null | sed 's/^\s*//' | sort -u
done
fin

seccion "Certificados TLS (vigencia)"
for cert in /etc/letsencrypt/live/*/cert.pem /etc/ssl/certs/*sabg* /etc/pki/tls/certs/*sabg*; do
  [ -f "$cert" ] || continue
  echo "--- $cert"
  openssl x509 -noout -subject -issuer -enddate -in "$cert" 2>/dev/null
done
fin

seccion "Aplicaciones desplegadas (carpetas y manifiestos)"
for base in /var/www /srv /opt /home/*/apps; do
  [ -d "$base" ] || continue
  for app in "$base"/*; do
    [ -d "$app" ] || continue
    echo "--- $app"
    for m in package.json composer.json requirements.txt pyproject.toml pom.xml build.gradle Gemfile go.mod artisan manage.py docker-compose.yml docker-compose.yaml; do
      [ -e "$app/$m" ] && echo "  $m"
    done
    if [ -f "$app/package.json" ] && tiene node; then
      node -e 'const p=require(process.argv[1]);console.log("  nombre:",p.name||"");console.log("  dependencias:",Object.keys(p.dependencies||{}).join(", "))' "$app/package.json" 2>/dev/null
    fi
    if [ -f "$app/composer.json" ]; then
      grep -E '"(name|laravel/framework|symfony/[a-z-]+|php)"' "$app/composer.json" 2>/dev/null | sed 's/^\s*/  /' | head -8
    fi
    if [ -d "$app/.git" ] && tiene git; then
      echo "  remoto: $(git -C "$app" remote get-url origin 2>/dev/null | enmascarar)"
      echo "  último commit: $(git -C "$app" log -1 --format='%h %ci %s' 2>/dev/null)"
    fi
  done
done
fin

seccion "Correo saliente"
for c in postfix sendmail exim msmtp; do tiene "$c" && echo "$c instalado"; done
[ -f /etc/postfix/main.cf ] && grep -E '^(myhostname|relayhost|smtp_tls_security_level)\b' /etc/postfix/main.cf
fin

seccion "Tareas programadas (contraseñas enmascaradas)"
for f in /etc/crontab /etc/cron.d/*; do
  [ -f "$f" ] || continue
  echo "--- $f"; grep -vE '^\s*(#|$)' "$f" | enmascarar
done
for u in $(cut -d: -f1 /etc/passwd 2>/dev/null); do
  out=$(crontab -l -u "$u" 2>/dev/null | grep -vE '^\s*(#|$)')
  [ -n "$out" ] && { echo "--- crontab de $u"; echo "$out" | enmascarar; }
done
fin

seccion "Respaldos (carpetas probables, solo tamaños)"
for d in /backup /backups /var/backups /respaldos /srv/backups; do
  [ -d "$d" ] && { echo "--- $d"; du -sh "$d" 2>/dev/null; ls -lt "$d" 2>/dev/null | head -5; }
done
fin

seccion "Acceso remoto"
tiene sshd && sshd -T 2>/dev/null | grep -E '^(port|permitrootlogin|passwordauthentication) '
tiene ufw && ufw status 2>/dev/null
tiene firewall-cmd && firewall-cmd --list-all 2>/dev/null
fin

printf '\nFin del inventario.\n'
