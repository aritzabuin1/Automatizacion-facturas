# 🧪 Guía de Testing - Agente de Facturas Pro

## 📋 Plan de Pruebas Completo

Esta guía te ayudará a verificar que todo funciona correctamente antes de usar el sistema en producción.

---

## 🚀 PASO 1: Instalación y Configuración

### 1.1 Instalar Dependencias

```bash
# Activar entorno virtual
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar todas las dependencias
pip install -r requirements.txt
```

**Verificación**: No debe haber errores de instalación.

---

### 1.2 Inicializar Seguridad

```bash
# Ejecutar script de inicialización
python init_security.py
```

**Qué hace**:
- ✅ Genera encryption key
- ✅ Genera JWT secret
- ✅ Crea usuarios admin y demo
- ✅ Actualiza .env

**Verificación**: 
- Archivo `.env` debe existir
- Debe mostrar "✅ INICIALIZACIÓN COMPLETADA"

---

## 🧪 PASO 2: Tests de Seguridad

### 2.1 Test de Encriptación

```bash
# Ejecutar módulo de encriptación
python src/encryption.py
```

**Resultado esperado**:
```
✅ Nueva encryption key generada
✅ Match: True
```

---

### 2.2 Test de Autenticación

```bash
# Ejecutar módulo de autenticación
python src/auth.py
```

**Resultado esperado**:
```
✅ Login exitoso: admin
Token: eyJ...
✅ Token válido: admin
```

---

### 2.3 Verificar Base de Datos de Usuarios

```bash
# Ver usuarios creados
python -c "import sqlite3; conn = sqlite3.connect('data/users.db'); print(conn.execute('SELECT username, role FROM users').fetchall())"
```

**Resultado esperado**:
```
[('admin', 'admin'), ('demo', 'user')]
```

---

## 📊 PASO 3: Test del Dashboard

### 3.1 Iniciar Dashboard

```bash
streamlit run dashboard.py
```

**Verificación**:
1. ✅ Se abre navegador en http://localhost:8501
2. ✅ Aparece pantalla de login con fondo degradado púrpura
3. ✅ No hay errores en consola

---

### 3.2 Test de Login

**Credenciales**:
- Username: `admin`
- Password: La que configuraste en `init_security.py`

**Verificación**:
1. ✅ Login exitoso
2. ✅ Dashboard carga con métricas
3. ✅ Se ve el mensaje "Bienvenido, Administrador"

---

### 3.3 Test de Funcionalidades del Dashboard

**Verificar**:
- [ ] **Métricas**: Se muestran 4 KPIs (Total Facturas, Importe, Auto-Aprobadas, Pendientes)
- [ ] **Tabs**: 4 pestañas (Overview, Análisis, Facturas, Editar)
- [ ] **Gráficos**: Se renderizan correctamente (pie chart, bar chart)
- [ ] **Filtros**: Sidebar con filtros de fecha, estado, proveedor
- [ ] **Upload**: Botón de subir archivos funciona
- [ ] **Logout**: Botón de salir funciona

---

## 🔄 PASO 4: Test de Procesamiento

### 4.1 Procesamiento Manual

```bash
# Copiar una factura de prueba a facturas_input/
# Luego ejecutar:
python main.py ./facturas_input
```

**Verificación**:
1. ✅ Procesa el archivo sin errores
2. ✅ Muestra datos extraídos en consola
3. ✅ Crea registro en `data/facturas.db`
4. ✅ Exporta a `output/facturas.csv`

---

### 4.2 Test de Duplicados

```bash
# Ejecutar el mismo comando dos veces
python main.py ./facturas_input
python main.py ./facturas_input
```

**Resultado esperado**:
```
Segunda ejecución:
ℹ️ Factura <nombre> ya existía en la base de datos (duplicado)
```

---

### 4.3 Test del Watcher (Procesamiento Automático)

```bash
# Terminal 1: Iniciar watcher
python watcher_service.py

# Terminal 2: Copiar factura a facturas_input/
# (mientras el watcher está corriendo)
```

**Verificación**:
1. ✅ Watcher detecta el archivo nuevo
2. ✅ Procesa automáticamente
3. ✅ Logs muestran "📥 Nuevo archivo detectado"
4. ✅ Factura aparece en dashboard

---

## 🔐 PASO 5: Tests de Seguridad

### 5.1 Test de Encriptación de Datos

```python
# Ejecutar en Python
from src.encryption import init_encryption_from_env
from dotenv import load_dotenv

load_dotenv()
encryptor = init_encryption_from_env()

# Test
test_cif = "B12345678"
encrypted = encryptor.encrypt(test_cif)
decrypted = encryptor.decrypt(encrypted)

print(f"Original: {test_cif}")
print(f"Encriptado: {encrypted}")
print(f"Desencriptado: {decrypted}")
print(f"Match: {test_cif == decrypted}")
```

**Resultado esperado**: `Match: True`

---

### 5.2 Test de Audit Trail

```python
# Ver historial de logins
from src.auth import UserManager

manager = UserManager()
history = manager.get_login_history(limit=10)

for username, success, ip, timestamp in history:
    status = "✅" if success else "❌"
    print(f"{timestamp} - {username} - {status} - {ip}")
```

**Verificación**: Debe mostrar tus intentos de login recientes.

---

### 5.3 Test de Login Fallido

**En el dashboard**:
1. Cerrar sesión
2. Intentar login con password incorrecta
3. Verificar que muestra error
4. Verificar que se registra en audit trail

---

## 🐳 PASO 6: Test de Docker

### 6.1 Build de Imagen

```bash
docker build -t agente-facturas:latest .
```

**Verificación**:
- ✅ Build completa sin errores
- ✅ Imagen creada (verificar con `docker images`)

---

### 6.2 Test de Docker Compose

```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

**Verificación**:
1. ✅ Servicios inician correctamente
2. ✅ Dashboard accesible en http://localhost:8501
3. ✅ Watcher está corriendo

---

### 6.3 Test de Volúmenes

```bash
# Crear factura en facturas_input/
# Verificar que se procesa

# Parar contenedores
docker-compose down

# Reiniciar
docker-compose up -d

# Verificar que los datos persisten
```

**Verificación**: Datos en `data/` y `output/` deben persistir.

---

## ✅ CHECKLIST FINAL

### Funcionalidad Core
- [ ] ✅ Instalación de dependencias sin errores
- [ ] ✅ Inicialización de seguridad exitosa
- [ ] ✅ Encriptación funciona correctamente
- [ ] ✅ Autenticación funciona correctamente
- [ ] ✅ Dashboard carga y muestra datos
- [ ] ✅ Login/logout funciona
- [ ] ✅ Procesamiento manual funciona
- [ ] ✅ Detección de duplicados funciona
- [ ] ✅ Watcher procesa archivos automáticamente
- [ ] ✅ Exportación a CSV funciona

### Seguridad
- [ ] ✅ Passwords hasheados (no en texto plano)
- [ ] ✅ JWT tokens funcionan
- [ ] ✅ Encriptación de datos sensibles funciona
- [ ] ✅ Audit trail registra logins
- [ ] ✅ .env no está en git
- [ ] ✅ Secrets no están hardcodeados

### Docker
- [ ] ✅ Build de imagen exitoso
- [ ] ✅ Docker Compose funciona
- [ ] ✅ Volúmenes persisten datos
- [ ] ✅ Servicios se reinician automáticamente

### Documentación
- [ ] ✅ README.md completo
- [ ] ✅ SECURITY.md presente
- [ ] ✅ .env.example actualizado
- [ ] ✅ Comentarios en código

---

## 🐛 Solución de Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'cryptography'"

```bash
pip install -r requirements.txt
```

---

### Error: "ENCRYPTION_KEY no encontrada en .env"

```bash
python init_security.py
```

---

### Error: "Database is locked"

```bash
# Parar todos los procesos
# Ctrl+C en todas las terminales

# Verificar que no hay procesos huérfanos
tasklist | findstr python  # Windows
ps aux | grep python       # Linux

# Reiniciar
```

---

### Dashboard no carga / Error de importación

```bash
# Limpiar caché de Streamlit
streamlit cache clear

# Reiniciar
streamlit run dashboard.py
```

---

## 📊 Métricas de Éxito

Si todos los tests pasan:

✅ **Sistema 100% funcional**
- Seguridad: 9/10
- Funcionalidad: 10/10
- Documentación: 10/10
- Listo para producción: ✅

---

## 🚀 Siguiente Paso: Subir a GitHub

Una vez que todos los tests pasen, puedes subir a GitHub:

```bash
# 1. Verificar que .env NO está en git
git status

# 2. Añadir cambios
git add .

# 3. Commit
git commit -m "feat: add security enhancements (bcrypt, JWT, encryption)"

# 4. Push
git push origin main
```

---

<div align="center">
  <strong>🧪 Testing completado = Confianza en producción</strong>
</div>
