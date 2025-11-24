# =============================================================================
# README: GUÍA DE DESPLIEGUE CON DOCKER
# =============================================================================

# INSTALACIÓN RÁPIDA PARA CLIENTES
# =================================

## Requisitos Previos
1. Instalar Docker Desktop: https://www.docker.com/products/docker-desktop
2. Tener la API key de OpenAI

## Instalación (3 pasos)

### 1. Configurar la API Key
Crear un archivo `.env` en esta carpeta con:
```
OPENAI_API_KEY=sk-tu-key-aqui
```

### 2. Levantar los servicios
```bash
docker-compose up -d
```

### 3. Acceder al Dashboard
Abrir en el navegador: http://localhost:8501

¡Listo! El sistema ya está vigilando la carpeta `facturas_input` automáticamente.

---

## Uso Diario

### Procesar facturas
Simplemente guarda archivos PDF/JPG/PNG en la carpeta `facturas_input`.
El sistema los procesará automáticamente en segundos.

### Ver el dashboard
http://localhost:8501

### Ver logs en tiempo real
```bash
docker-compose logs -f watcher
```

### Parar el sistema
```bash
docker-compose down
```

### Reiniciar el sistema
```bash
docker-compose restart
```

---

## Comandos Útiles

### Procesar una carpeta manualmente (sin watcher)
```bash
docker-compose run --rm watcher python main.py ./facturas_input
```

### Acceder a la consola del contenedor
```bash
docker-compose exec watcher bash
```

### Ver estado de los servicios
```bash
docker-compose ps
```

### Actualizar a nueva versión
```bash
git pull  # o descargar nuevo código
docker-compose up -d --build
```

---

## Estructura de Carpetas

```
facturas_automaticas/
├── facturas_input/     ← Aquí se dejan las facturas
├── data/              ← Base de datos SQLite
├── output/            ← Archivos CSV exportados
├── logs/              ← Logs del sistema
└── .env               ← API key (NO subir a git)
```

---

## Solución de Problemas

### El watcher no procesa archivos
1. Verificar que el contenedor está corriendo: `docker-compose ps`
2. Ver logs: `docker-compose logs watcher`
3. Verificar que la API key es correcta en `.env`

### Error "No module named 'src'"
Reconstruir la imagen: `docker-compose up -d --build`

### La base de datos está corrupta
1. Parar servicios: `docker-compose down`
2. Hacer backup: `cp -r data data.backup`
3. Borrar DB: `rm data/facturas.db`
4. Reiniciar: `docker-compose up -d`

### Quiero cambiar el puerto del dashboard
Editar `docker-compose.yml`, línea `ports: - "8501:8501"`
Cambiar el primer número (ej: `"9000:8501"`)

---

## Producción: Despliegue en Servidor

### Opción 1: Servidor Linux (Ubuntu/Debian)
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt-get install docker-compose-plugin

# Clonar/copiar el proyecto
cd /opt/facturas-automaticas

# Configurar .env
nano .env

# Levantar servicios
docker-compose up -d

# Configurar inicio automático (systemd)
sudo systemctl enable docker
```

### Opción 2: Servidor Windows
1. Instalar Docker Desktop
2. Configurar Docker para iniciar con Windows
3. Copiar proyecto a C:\facturas-automaticas
4. Ejecutar `docker-compose up -d` desde PowerShell

### Opción 3: Cloud (AWS/Azure/GCP)
- Usar servicios gestionados: ECS (AWS), Container Instances (Azure), Cloud Run (GCP)
- Subir imagen a registry: Docker Hub, ECR, ACR, GCR
- Configurar auto-scaling y load balancing

---

## Backups

### Backup manual
```bash
# Parar servicios
docker-compose down

# Copiar datos
tar -czf backup-$(date +%Y%m%d).tar.gz data/ output/

# Reiniciar
docker-compose up -d
```

### Backup automático (cron)
```bash
# Editar crontab
crontab -e

# Añadir línea (backup diario a las 2 AM)
0 2 * * * cd /opt/facturas-automaticas && tar -czf /backups/facturas-$(date +\%Y\%m\%d).tar.gz data/
```

---

## Seguridad

### IMPORTANTE: Proteger la API Key
- Nunca subir `.env` a git
- Usar secretos de Docker en producción
- Rotar la API key periódicamente

### HTTPS para el Dashboard
Si expones el dashboard a internet, usa un reverse proxy con SSL:
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name facturas.tu-empresa.com;
    
    ssl_certificate /etc/letsencrypt/live/tu-empresa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-empresa.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Soporte

Para problemas o dudas:
- Email: soporte@tu-empresa.com
- Documentación: https://docs.tu-empresa.com
- Logs: `docker-compose logs -f`
