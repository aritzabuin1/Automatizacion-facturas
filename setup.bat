@echo off
echo ===================================================
echo 🚀 INSTALADOR AGENTE DE FACTURAS (MVP v1.0)
echo ===================================================
echo.

echo 1. Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Por favor instala Python 3.10+ y añadelo al PATH.
    pause
    exit /b
)

echo.
echo 2. Creando entorno virtual (.venv)...
if not exist .venv (
    python -m venv .venv
    echo ✅ Entorno creado.
) else (
    echo ℹ️ El entorno ya existe.
)

echo.
echo 3. Instalando dependencias...
call .venv\Scripts\activate
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias.
    pause
    exit /b
)

echo.
echo 4. Creando carpetas necesarias...
if not exist data mkdir data
if not exist output mkdir output
if not exist facturas_input mkdir facturas_input

echo.
echo ===================================================
echo ✅ INSTALACION COMPLETADA
echo ===================================================
echo.
echo Para procesar facturas:
echo   python main.py process-folder ./facturas_input
echo.
echo Para ver el panel:
echo   streamlit run dashboard.py
echo.
pause
