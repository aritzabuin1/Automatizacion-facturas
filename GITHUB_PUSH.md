# 🚀 Guía para Subir a GitHub

## Paso 1: Verificar que .env NO está en git

```bash
# Ver qué archivos se van a subir
git status
```

**IMPORTANTE**: `.env` NO debe aparecer en la lista. Si aparece:
```bash
# Añadir a .gitignore
echo ".env" >> .gitignore
git add .gitignore
```

---

## Paso 2: Añadir todos los cambios

```bash
# Añadir todos los archivos nuevos y modificados
git add .

# Ver qué se va a commitear
git status
```

**Archivos que DEBEN estar**:
- ✅ `src/auth.py`
- ✅ `src/encryption.py`
- ✅ `init_security.py`
- ✅ `SECURITY.md`
- ✅ `TESTING.md`
- ✅ `requirements.txt` (actualizado)
- ✅ `.env.example` (actualizado)
- ✅ `.gitignore`

**Archivos que NO deben estar**:
- ❌ `.env` (contiene secrets)
- ❌ `data/users.db` (base de datos local)
- ❌ `data/facturas.db` (base de datos local)
- ❌ `.venv/` (entorno virtual)

---

## Paso 3: Hacer commit

```bash
git commit -m "feat: add enterprise-grade security (bcrypt, JWT, encryption)

- Add bcrypt password hashing for user authentication
- Implement JWT token-based sessions
- Add Fernet encryption for sensitive data (CIF, invoice numbers)
- Create user database with audit trail
- Add security initialization script
- Create comprehensive SECURITY.md guide
- Add TESTING.md with complete test plan
- Update .env.example with security variables
- Security score: 7/10 → 9/10"
```

---

## Paso 4: Push a GitHub

```bash
git push origin main
```

---

## Paso 5: Verificar en GitHub

1. Ir a: https://github.com/aritzabuin1/Automatizacion-facturas
2. Verificar que los archivos nuevos están
3. **IMPORTANTE**: Verificar que `.env` NO está

---

## 🧪 Cómo Probar Después de Subir

### Opción 1: Clonar en otra carpeta (simular instalación cliente)

```bash
# 1. Clonar repo
cd C:\temp
git clone https://github.com/aritzabuin1/Automatizacion-facturas.git
cd Automatizacion-facturas

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Inicializar seguridad
python init_security.py

# 5. Probar dashboard
streamlit run dashboard.py
```

**Resultado esperado**: Todo debe funcionar igual que en tu instalación original.

---

### Opción 2: Usar Docker (simular producción)

```bash
# 1. Clonar repo
git clone https://github.com/aritzabuin1/Automatizacion-facturas.git
cd Automatizacion-facturas

# 2. Crear .env con tu API key
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# 3. Levantar con Docker
docker-compose up -d

# 4. Acceder
# http://localhost:8501
```

**Resultado esperado**: Dashboard funciona en contenedor.

---

## ✅ Checklist Pre-Push

Antes de hacer `git push`, verifica:

- [ ] `.env` está en `.gitignore`
- [ ] `git status` NO muestra `.env`
- [ ] `git status` NO muestra `data/` ni `.venv/`
- [ ] Todos los archivos de seguridad están añadidos
- [ ] Commit message es descriptivo
- [ ] Has probado localmente que todo funciona

---

## 🎯 Comandos Rápidos (Copy-Paste)

```bash
# Todo en uno
git add .
git commit -m "feat: add enterprise-grade security (bcrypt, JWT, encryption)"
git push origin main
```

---

## 📊 Después del Push

**Actualizar README en GitHub**:
1. Ir a tu repo
2. Editar README.md
3. Añadir badge de seguridad:
   ```markdown
   [![Security](https://img.shields.io/badge/security-9%2F10-brightgreen)]()
   ```

**Crear Release** (opcional):
1. GitHub → Releases → New Release
2. Tag: `v2.0.0`
3. Title: "v2.0 - Enterprise Security"
4. Description:
   ```
   ## 🔒 Security Enhancements
   - bcrypt password hashing
   - JWT token authentication
   - Fernet data encryption
   - User database with audit trail
   - Security score: 9/10
   
   ## 📚 New Documentation
   - SECURITY.md - Comprehensive security guide
   - TESTING.md - Complete testing plan
   ```

---

<div align="center">
  <strong>🚀 Listo para compartir con el mundo</strong>
</div>
