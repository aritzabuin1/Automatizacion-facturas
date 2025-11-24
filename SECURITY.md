# =============================================================================
# GUÍA DE SEGURIDAD - Agente de Facturas Pro
# =============================================================================

## 🔒 Características de Seguridad Implementadas

### 1. Autenticación Robusta ✅

**Tecnología**: bcrypt + JWT

**Características**:
- ✅ Passwords hasheados con bcrypt (12 rounds, salt automático)
- ✅ JWT tokens con expiración (24 horas)
- ✅ Base de datos de usuarios (SQLite, migrable a PostgreSQL)
- ✅ Roles de usuario (admin, user)
- ✅ Audit trail de todos los intentos de login
- ✅ Protección contra timing attacks

**Archivos**:
- `src/auth.py` - Sistema de autenticación
- `data/users.db` - Base de datos de usuarios

---

### 2. Encriptación de Datos ✅

**Tecnología**: Fernet (AES-128 + HMAC)

**Datos encriptados**:
- ✅ CIF/NIF de proveedores (GDPR/LOPD)
- ✅ Números de factura
- ✅ Notas de validación

**Características**:
- ✅ Encriptación simétrica autenticada
- ✅ Detecta manipulación de datos
- ✅ Key gestionada desde .env

**Archivos**:
- `src/encryption.py` - Motor de encriptación

---

### 3. Gestión de Secrets ✅

**Variables de entorno** (`.env`):
```bash
# API Keys
OPENAI_API_KEY=sk-...

# Seguridad
JWT_SECRET_KEY=<random-32-chars>
ENCRYPTION_KEY=<fernet-key>
ADMIN_PASSWORD=<strong-password>
```

**Protección**:
- ✅ `.env` en `.gitignore`
- ✅ `.env.example` sin valores reales
- ✅ Secrets nunca hardcodeados en código

---

### 4. Validación de Inputs ✅

**Implementado en**:
- ✅ Autenticación (username, password)
- ✅ Creación de usuarios
- ✅ Procesamiento de facturas (Pydantic)

**Protecciones**:
- ✅ SQL Injection (SQLAlchemy ORM)
- ✅ Validación de tipos (Pydantic)
- ✅ Sanitización de inputs

---

### 5. Logging de Seguridad ✅

**Eventos registrados**:
- ✅ Intentos de login (éxito/fallo)
- ✅ Cambios de contraseña
- ✅ Errores de encriptación
- ✅ Accesos no autorizados

**Archivos**:
- `logs/watcher.log` - Logs del servicio
- `app.log` - Logs de la aplicación
- `data/users.db` (tabla login_attempts) - Audit trail

---

## 🚀 Inicialización de Seguridad

### Primera Instalación

```bash
# 1. Ejecutar script de inicialización
python init_security.py

# Esto generará:
# - Encryption key
# - JWT secret
# - Usuarios por defecto
# - Actualización de .env
```

### Generación Manual de Keys

```bash
# Encryption Key
python src/encryption.py

# JWT Secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🔐 Mejores Prácticas

### 1. Gestión de Contraseñas

**Requisitos mínimos**:
- ✅ Mínimo 8 caracteres
- ⚠️ Recomendado: 12+ caracteres con mayúsculas, números, símbolos

**Cambio de contraseña**:
```python
from src.auth import UserManager

manager = UserManager()
manager.change_password("admin", "old_password", "new_password")
```

---

### 2. Rotación de Secrets

**JWT Secret** (cada 6 meses):
```bash
# 1. Generar nuevo secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Actualizar .env
JWT_SECRET_KEY=<nuevo-secret>

# 3. Reiniciar servicios
# NOTA: Todos los tokens activos se invalidarán
```

**Encryption Key** (NUNCA rotar sin migración):
```
⚠️ CRÍTICO: NO rotar encryption key sin plan de migración
- Datos encriptados con key antigua serán irrecuperables
- Requiere desencriptar todo con key antigua y re-encriptar con nueva
```

---

### 3. Backup de Secrets

**¿Qué hacer backup?**:
- ✅ `.env` completo
- ✅ `data/users.db`
- ✅ Encryption key (separado, seguro)

**¿Dónde guardar?**:
- ✅ Gestor de contraseñas (1Password, Bitwarden)
- ✅ Vault cifrado (HashiCorp Vault)
- ✅ USB encriptado (offline)
- ❌ NUNCA en git, email, cloud sin encriptar

---

### 4. Auditoría de Seguridad

**Revisar logs regularmente**:
```python
from src.auth import UserManager

manager = UserManager()

# Ver últimos 100 intentos de login
history = manager.get_login_history(limit=100)

for username, success, ip, timestamp in history:
    print(f"{timestamp} - {username} - {'✅' if success else '❌'} - {ip}")
```

**Alertas a configurar**:
- ⚠️ >5 intentos fallidos desde misma IP
- ⚠️ Login desde IP desconocida
- ⚠️ Cambio de contraseña
- ⚠️ Errores de desencriptación (posible manipulación)

---

### 5. Hardening Adicional

**Para producción**:

1. **HTTPS obligatorio**:
   ```nginx
   # nginx.conf
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
   }
   ```

2. **Firewall**:
   ```bash
   # Solo permitir puerto 8501 desde IPs específicas
   ufw allow from 192.168.1.0/24 to any port 8501
   ```

3. **Rate Limiting** (ya implementado en código):
   - Máximo 60 requests/minuto por IP
   - Configurable en .env

4. **2FA** (futuro):
   - Integrar TOTP (Google Authenticator)
   - Obligatorio para usuarios admin

5. **Monitorización**:
   - Integrar Sentry para alertas
   - Prometheus + Grafana para métricas

---

## 🔍 Checklist de Seguridad

### Antes de Desplegar

- [ ] `.env` configurado con secrets únicos
- [ ] Contraseña admin cambiada (no usar default)
- [ ] Encryption key generada y guardada en backup
- [ ] JWT secret generado (mínimo 32 caracteres)
- [ ] `.env` en `.gitignore`
- [ ] Logs configurados y rotando
- [ ] HTTPS configurado (producción)
- [ ] Firewall configurado
- [ ] Backup de secrets guardado de forma segura

### Mantenimiento Mensual

- [ ] Revisar logs de login fallidos
- [ ] Verificar usuarios activos
- [ ] Comprobar tamaño de logs
- [ ] Backup de `data/users.db`
- [ ] Actualizar dependencias de seguridad

### Mantenimiento Semestral

- [ ] Rotar JWT secret
- [ ] Auditoría de usuarios (eliminar inactivos)
- [ ] Revisar permisos de archivos
- [ ] Actualizar contraseñas

---

## 🚨 Respuesta a Incidentes

### Contraseña Comprometida

```bash
# 1. Cambiar contraseña inmediatamente
python -c "from src.auth import UserManager; UserManager().change_password('admin', 'old', 'new')"

# 2. Revisar logs de acceso
python -c "from src.auth import UserManager; print(UserManager().get_login_history('admin'))"

# 3. Rotar JWT secret (invalida todos los tokens)
# Editar .env y reiniciar servicios
```

### Encryption Key Perdida

```
⚠️ CRÍTICO: Sin encryption key, datos encriptados son IRRECUPERABLES

Opciones:
1. Restaurar desde backup
2. Si no hay backup: datos encriptados se pierden
3. Prevención: SIEMPRE tener backup de .env
```

### Acceso No Autorizado Detectado

```bash
# 1. Revisar logs
tail -f logs/watcher.log | grep "Login fallido"

# 2. Bloquear IP (firewall)
ufw deny from <IP_SOSPECHOSA>

# 3. Cambiar todas las contraseñas
# 4. Rotar todos los secrets
# 5. Revisar datos accedidos
```

---

## 📊 Niveles de Seguridad

### Nivel 1: Básico (Actual) ✅
- ✅ Autenticación con bcrypt
- ✅ Encriptación de datos sensibles
- ✅ Secrets en .env
- ✅ Logging de seguridad

**Adecuado para**: Instalaciones pequeñas, datos no críticos

---

### Nivel 2: Intermedio (Recomendado para Producción)
- ✅ Todo lo de Nivel 1
- ⚠️ HTTPS obligatorio
- ⚠️ Rate limiting activo
- ⚠️ Monitorización con Sentry
- ⚠️ Backups automáticos

**Adecuado para**: Producción, múltiples usuarios

---

### Nivel 3: Avanzado (Empresas)
- ✅ Todo lo de Nivel 2
- ⚠️ 2FA obligatorio
- ⚠️ SSO (SAML/OAuth)
- ⚠️ Encriptación en tránsito y reposo
- ⚠️ Auditoría completa (SOC 2)
- ⚠️ Penetration testing regular

**Adecuado para**: Grandes empresas, datos ultra-sensibles

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GDPR Compliance](https://gdpr.eu/)
- [bcrypt Best Practices](https://github.com/pyca/bcrypt/)
- [Fernet Specification](https://github.com/fernet/spec/)

---

<div align="center">
  <strong>🔒 Seguridad es un proceso continuo, no un producto</strong>
</div>
