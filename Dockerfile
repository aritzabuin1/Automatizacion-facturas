# =============================================================================
# DOCKERFILE PARA AGENTE DE FACTURAS
# =============================================================================
# ¿QUÉ ES DOCKER Y POR QUÉ LO USAMOS?
# Docker empaqueta tu aplicación + todas sus dependencias (Python, librerías, etc.)
# en un "contenedor" que funciona igual en cualquier máquina.
#
# VENTAJAS EN PRODUCCIÓN:
# 1. "Funciona en mi máquina" = "Funciona en producción"
# 2. Instalación en el cliente: Solo necesita Docker Desktop (1 click)
# 3. Actualizaciones: docker pull mi-empresa/facturas:latest
# 4. Aislamiento: No contamina el sistema del cliente con Python/dependencias
# 5. Escalabilidad: Puedes correr múltiples instancias fácilmente
#
# MULTI-STAGE BUILD:
# Usamos 2 "stages" (etapas) para optimizar el tamaño final de la imagen:
# - Stage 1 (builder): Instala dependencias pesadas (compiladores, headers)
# - Stage 2 (runtime): Solo copia lo necesario para ejecutar
# Resultado: Imagen final más pequeña (menos MB = descargas más rápidas)
# =============================================================================

# -----------------------------------------------------------------------------
# STAGE 1: BUILDER (Construcción)
# -----------------------------------------------------------------------------
# Usamos una imagen "completa" que tiene compiladores y herramientas de build
FROM python:3.11-slim as builder

# ¿POR QUÉ python:3.11-slim?
# - python:3.11 (sin -slim) pesa ~900MB (incluye compiladores, gcc, etc.)
# - python:3.11-slim pesa ~120MB (solo lo mínimo para ejecutar Python)
# - python:3.11-alpine pesa ~50MB pero puede dar problemas con librerías C

# Instalar dependencias del sistema necesarias para compilar paquetes Python
# (algunos paquetes como pillow, numpy necesitan compilar código C)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# OPTIMIZACIÓN: Copiar solo requirements.txt primero
# ¿POR QUÉ? Docker cachea cada "layer" (capa). Si copiamos todo el código
# y luego pip install, cada cambio en el código invalida el cache de pip.
# Al copiar solo requirements.txt, pip install solo se re-ejecuta si cambian las dependencias.
COPY requirements.txt .

# Instalar dependencias Python en un directorio temporal
# --user: Instala en ~/.local (no requiere root)
# --no-warn-script-location: Silencia warnings irrelevantes
RUN pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt

# -----------------------------------------------------------------------------
# STAGE 2: RUNTIME (Ejecución)
# -----------------------------------------------------------------------------
# Imagen final limpia, solo con lo necesario para ejecutar
FROM python:3.11-slim

# Metadatos de la imagen (buenas prácticas)
LABEL maintainer="tu-email@empresa.com"
LABEL description="Agente de Facturas - Procesamiento automático con IA"
LABEL version="1.0"

# Crear usuario no-root (SEGURIDAD)
# ¿POR QUÉ? Nunca ejecutar contenedores como root en producción.
# Si alguien hackea tu app, no tendrá permisos de root en el contenedor.
RUN useradd -m -u 1000 appuser

# Directorio de trabajo
WORKDIR /app

# Copiar las dependencias Python instaladas desde el builder
COPY --from=builder /root/.local /home/appuser/.local

# Asegurar que los scripts de Python estén en el PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copiar el código de la aplicación
COPY --chown=appuser:appuser . .

# Crear directorios necesarios con permisos correctos
RUN mkdir -p data output logs facturas_input && \
    chown -R appuser:appuser data output logs facturas_input

# Cambiar al usuario no-root
USER appuser

# Variables de entorno por defecto
# Estas se pueden sobrescribir con docker run -e VARIABLE=valor
ENV PYTHONUNBUFFERED=1 \
    WATCH_FOLDER=/app/facturas_input

# HEALTHCHECK: Docker puede verificar si el contenedor está "sano"
# Útil en producción con orquestadores como Kubernetes
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#   CMD python -c "import sys; sys.exit(0)"

# Exponer puerto del dashboard (si se ejecuta)
EXPOSE 8501

# ENTRYPOINT vs CMD:
# - ENTRYPOINT: Comando que SIEMPRE se ejecuta
# - CMD: Argumentos por defecto (se pueden sobrescribir)
# Ejemplo: docker run imagen watcher_service.py
#          ejecutará: python watcher_service.py

# Punto de entrada: script de inicialización
ENTRYPOINT ["python"]

# Comando por defecto: ejecutar el watcher
CMD ["watcher_service.py"]

# =============================================================================
# CÓMO USAR ESTE DOCKERFILE
# =============================================================================
# Construir la imagen:
#   docker build -t agente-facturas:latest .
#
# Ejecutar el watcher:
#   docker run -v $(pwd)/facturas_input:/app/facturas_input \
#              -v $(pwd)/data:/app/data \
#              -e OPENAI_API_KEY=tu-key \
#              agente-facturas:latest
#
# Ejecutar el dashboard:
#   docker run -p 8501:8501 \
#              -v $(pwd)/data:/app/data \
#              agente-facturas:latest streamlit run dashboard.py
#
# Ejecutar procesamiento manual:
#   docker run -v $(pwd)/facturas_input:/app/facturas_input \
#              -v $(pwd)/data:/app/data \
#              -e OPENAI_API_KEY=tu-key \
#              agente-facturas:latest main.py ./facturas_input
# =============================================================================
