# 📚 Roadmap de Estudio - Agente de Facturas Pro

## 🎯 Objetivo
Entender completamente el proyecto desde cero, siguiendo un orden lógico de complejidad creciente.

---

## 📖 NIVEL 1: Documentación General (30 minutos)

### Leer en este orden:

#### 1. **README.md** (10 min)
**Por qué primero**: Vista general del proyecto, características, instalación.

**Conceptos clave**:
- ¿Qué problema resuelve?
- ¿Cómo se instala?
- ¿Cómo se usa?

**Enfócate en**:
- Sección "Características"
- Sección "Arquitectura" (diagrama de flujo)
- Sección "Instalación Rápida"

---

#### 2. **walkthrough.md** (10 min)
**Por qué**: Resumen ejecutivo de todo lo construido.

**Conceptos clave**:
- Fases del proyecto (MVP → Producción)
- Decisiones de diseño
- Estructura final

**Enfócate en**:
- Sección "Fases Completadas"
- Sección "Arquitectura"

---

#### 3. **ANALISIS_PROYECTO.md** (10 min)
**Por qué**: Análisis crítico objetivo del proyecto.

**Conceptos clave**:
- Fortalezas y debilidades
- Puntuación por categoría
- Recomendaciones

**Enfócate en**:
- Sección "Fortalezas"
- Sección "Debilidades"
- Sección "Viabilidad Comercial"

---

## 🏗️ NIVEL 2: Arquitectura Core (1 hora)

### Leer en este orden:

#### 4. **src/models.py** (10 min)
**Por qué primero**: Define la estructura de datos central.

**Conceptos clave**:
- Pydantic para validación
- Modelo `Factura`
- Campos obligatorios vs opcionales

**Qué aprender**:
```python
# Esto es el "contrato" de datos
class Factura(BaseModel):
    numero_factura: str  # Obligatorio
    fecha_emision: date
    total_factura: float
    # ... etc
```

**Pregúntate**:
- ¿Qué campos tiene una factura?
- ¿Por qué usar Pydantic?
- ¿Cómo valida los datos?

---

#### 5. **src/ingestor.py** (10 min)
**Por qué**: Punto de entrada de datos.

**Conceptos clave**:
- Patrón Adapter
- Clase `Document`
- `LocalFileIngestor`

**Qué aprender**:
```python
# Normaliza diferentes fuentes de datos
class Document:
    id: str
    filename: str
    filepath: str
    source: str  # "local", "email", "api"
```

**Pregúntate**:
- ¿Cómo se leen los archivos?
- ¿Por qué usar un Adapter?
- ¿Cómo añadiría email como fuente?

---

#### 6. **src/llm_extractor.py** (15 min)
**Por qué**: El "cerebro" del sistema.

**Conceptos clave**:
- OpenAI GPT-4o
- Librería `instructor`
- Visión multimodal

**Qué aprender**:
```python
# Instructor garantiza salida estructurada
response = client.chat.completions.create(
    model="gpt-4o",
    response_model=Factura,  # ← Pydantic model
    messages=[...]
)
```

**Pregúntate**:
- ¿Cómo funciona la extracción con IA?
- ¿Por qué usar `instructor`?
- ¿Qué pasa si el LLM falla?

---

#### 7. **src/validator.py** (10 min)
**Por qué**: Lógica de negocio.

**Conceptos clave**:
- Validación estructural vs lógica
- Clase `ValidationResult`
- Reglas de negocio

**Qué aprender**:
```python
# Valida coherencia matemática
if abs(calculated_total - factura.total_factura) > 0.01:
    errors.append("Total no coincide")
```

**Pregúntate**:
- ¿Qué valida Pydantic vs este módulo?
- ¿Qué reglas de negocio hay?
- ¿Cómo añadiría nuevas validaciones?

---

#### 8. **src/storage.py** (15 min)
**Por qué**: Persistencia de datos.

**Conceptos clave**:
- SQLAlchemy ORM
- SQLite
- Exportación CSV

**Qué aprender**:
```python
# ORM = mapeo objeto-relacional
class FacturaDB(Base):
    __tablename__ = 'facturas'
    id = Column(Integer, primary_key=True)
    # ...
```

**Pregúntate**:
- ¿Cómo se guardan los datos?
- ¿Por qué usar ORM?
- ¿Cómo migrar a PostgreSQL?

---

## 🔒 NIVEL 3: Seguridad (45 minutos)

### Leer en este orden:

#### 9. **SECURITY.md** (15 min)
**Por qué primero**: Contexto de seguridad.

**Conceptos clave**:
- Niveles de seguridad
- Mejores prácticas
- Checklist

**Enfócate en**:
- Sección "Características Implementadas"
- Sección "Mejores Prácticas"

---

#### 10. **src/auth.py** (15 min)
**Por qué**: Autenticación de usuarios.

**Conceptos clave**:
- bcrypt (hashing de passwords)
- JWT tokens
- Audit trail

**Qué aprender**:
```python
# Password hasheado (nunca texto plano)
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# JWT token con expiración
token = jwt.encode(payload, secret_key, algorithm='HS256')
```

**Pregúntate**:
- ¿Por qué bcrypt?
- ¿Cómo funcionan los JWT?
- ¿Qué es el audit trail?

---

#### 11. **src/encryption.py** (15 min)
**Por qué**: Encriptación de datos.

**Conceptos clave**:
- Fernet (AES-128)
- Encriptación simétrica
- GDPR compliance

**Qué aprender**:
```python
# Encriptación autenticada
cipher = Fernet(key)
encrypted = cipher.encrypt(data.encode())
decrypted = cipher.decrypt(encrypted)
```

**Pregúntate**:
- ¿Qué datos se encriptan?
- ¿Por qué Fernet?
- ¿Qué pasa si pierdo la key?

---

## 🚀 NIVEL 4: Automatización (30 minutos)

### Leer en este orden:

#### 12. **src/folder_watcher.py** (15 min)
**Por qué**: Procesamiento automático.

**Conceptos clave**:
- Librería `watchdog`
- Event-driven architecture
- Patrón Observer

**Qué aprender**:
```python
# Reacciona a eventos del sistema de archivos
class InvoiceFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Procesar archivo nuevo
```

**Pregúntate**:
- ¿Cómo detecta archivos nuevos?
- ¿Por qué event-driven vs polling?
- ¿Cómo evita duplicados?

---

#### 13. **watcher_service.py** (15 min)
**Por qué**: Servicio en segundo plano.

**Conceptos clave**:
- Daemon/Service
- Logging rotativo
- Manejo de errores robusto

**Qué aprender**:
```python
# Servicio que corre indefinidamente
watcher = FolderWatcher(watch_path, callback)
watcher.run_forever()  # Hasta Ctrl+C
```

**Pregúntate**:
- ¿Cómo corre 24/7?
- ¿Qué pasa si crashea?
- ¿Cómo se registra como servicio del OS?

---

## 🎨 NIVEL 5: Interfaz (30 minutos)

### Leer en este orden:

#### 14. **dashboard.py** (30 min)
**Por qué**: Interfaz de usuario.

**Conceptos clave**:
- Streamlit
- Plotly (gráficos)
- CSS custom (glassmorphism)

**Qué aprender**:
```python
# Streamlit = Python → Web App
st.title("Dashboard")
st.metric("Total", total_facturas)
fig = px.pie(df, names='status')
st.plotly_chart(fig)
```

**Pregúntate**:
- ¿Cómo funciona Streamlit?
- ¿Cómo se crean los gráficos?
- ¿Cómo se aplica el CSS custom?

---

## 🐳 NIVEL 6: Despliegue (30 minutos)

### Leer en este orden:

#### 15. **Dockerfile** (10 min)
**Por qué**: Containerización.

**Conceptos clave**:
- Multi-stage build
- Layer caching
- Usuario no-root

**Qué aprender**:
```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /root/.local /home/appuser/.local
```

**Pregúntate**:
- ¿Por qué multi-stage?
- ¿Cómo optimiza el tamaño?
- ¿Por qué usuario no-root?

---

#### 16. **docker-compose.yml** (10 min)
**Por qué**: Orquestación de servicios.

**Conceptos clave**:
- Servicios (watcher, dashboard)
- Volúmenes (persistencia)
- Restart policies

**Qué aprender**:
```yaml
services:
  watcher:
    build: .
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

**Pregúntate**:
- ¿Qué servicios hay?
- ¿Cómo persisten los datos?
- ¿Qué pasa si un servicio crashea?

---

#### 17. **DOCKER_README.md** (10 min)
**Por qué**: Guía de despliegue.

**Conceptos clave**:
- Comandos Docker
- Troubleshooting
- Backups

---

## 🧪 NIVEL 7: Testing (30 minutos)

### Leer en este orden:

#### 18. **TESTING.md** (20 min)
**Por qué**: Plan de pruebas.

**Conceptos clave**:
- Tests de seguridad
- Tests de funcionalidad
- Tests de Docker

**Enfócate en**:
- Checklist final
- Comandos de testing

---

#### 19. **init_security.py** (10 min)
**Por qué**: Inicialización del sistema.

**Conceptos clave**:
- Generación de keys
- Creación de usuarios
- Verificación de configuración

---

## 🎯 NIVEL 8: Orquestación (15 minutos)

### Leer en este orden:

#### 20. **main.py** (15 min)
**Por qué**: Punto de entrada CLI.

**Conceptos clave**:
- Typer (CLI framework)
- Orquestación de módulos
- Logging

**Qué aprender**:
```python
# CLI con Typer
@app.command()
def process(input_path: str):
    # 1. Ingerir
    # 2. Extraer
    # 3. Validar
    # 4. Guardar
```

**Pregúntate**:
- ¿Cómo se conectan todos los módulos?
- ¿Cuál es el flujo completo?
- ¿Cómo se manejan los errores?

---

## 📊 RESUMEN: Orden de Lectura Recomendado

### Día 1: Fundamentos (2 horas)
1. README.md
2. walkthrough.md
3. ANALISIS_PROYECTO.md
4. src/models.py
5. src/ingestor.py
6. src/llm_extractor.py
7. src/validator.py
8. src/storage.py

### Día 2: Seguridad y Automatización (2 horas)
9. SECURITY.md
10. src/auth.py
11. src/encryption.py
12. src/folder_watcher.py
13. watcher_service.py

### Día 3: UI y Despliegue (2 horas)
14. dashboard.py
15. Dockerfile
16. docker-compose.yml
17. DOCKER_README.md
18. TESTING.md
19. init_security.py
20. main.py

---

## 🔍 Conceptos Clave por Tecnología

### Python
- **Pydantic**: Validación de datos
- **SQLAlchemy**: ORM para bases de datos
- **Typer**: CLI framework
- **Streamlit**: Web apps en Python

### IA
- **OpenAI GPT-4o**: Modelo de lenguaje multimodal
- **Instructor**: Salida estructurada de LLMs
- **Vision**: Procesamiento de imágenes

### Seguridad
- **bcrypt**: Hashing de passwords
- **JWT**: Tokens de sesión
- **Fernet**: Encriptación simétrica

### Automatización
- **watchdog**: Monitorización de archivos
- **Event-driven**: Arquitectura basada en eventos

### Despliegue
- **Docker**: Containerización
- **docker-compose**: Orquestación
- **Multi-stage build**: Optimización de imágenes

---

## 💡 Consejos de Estudio

### 1. Enfoque Práctico
No solo leas, **ejecuta**:
```bash
# Prueba cada módulo
python src/models.py
python src/encryption.py
python src/auth.py
```

### 2. Debugging
Añade prints para entender el flujo:
```python
print(f"DEBUG: Procesando {filename}")
```

### 3. Experimenta
Modifica valores y ve qué pasa:
```python
# ¿Qué pasa si cambio el modelo?
model="gpt-4o-mini"  # En vez de gpt-4o
```

### 4. Dibuja Diagramas
Crea tu propio diagrama de flujo en papel.

### 5. Pregunta "¿Por qué?"
Para cada decisión de diseño, pregúntate por qué se hizo así.

---

## 🎓 Recursos Adicionales

### Documentación Oficial
- [Pydantic](https://docs.pydantic.dev/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Streamlit](https://docs.streamlit.io/)
- [OpenAI API](https://platform.openai.com/docs)
- [Docker](https://docs.docker.com/)

### Conceptos Avanzados
- **ORM**: Object-Relational Mapping
- **JWT**: JSON Web Tokens
- **Event-driven**: Arquitectura basada en eventos
- **Multi-stage build**: Optimización Docker

---

## ✅ Checklist de Comprensión

Después de estudiar, deberías poder responder:

### Arquitectura
- [ ] ¿Cuál es el flujo completo de procesamiento?
- [ ] ¿Cómo se conectan los módulos?
- [ ] ¿Por qué se eligió cada tecnología?

### Seguridad
- [ ] ¿Cómo se protegen las contraseñas?
- [ ] ¿Qué datos se encriptan y por qué?
- [ ] ¿Cómo funciona el audit trail?

### Funcionalidad
- [ ] ¿Cómo se extrae información de una factura?
- [ ] ¿Cómo se validan los datos?
- [ ] ¿Cómo se detectan duplicados?

### Despliegue
- [ ] ¿Cómo se instala en un cliente?
- [ ] ¿Cómo funciona Docker?
- [ ] ¿Qué pasa si un servicio falla?

---

<div align="center">
  <strong>📚 El conocimiento se construye paso a paso</strong><br>
  <em>Tómate tu tiempo, experimenta, y pregunta</em>
</div>
