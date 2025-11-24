#!/usr/bin/env python
"""
SERVICIO DE VIGILANCIA DE FACTURAS
===================================

¿QUÉ HACE ESTE SCRIPT?
Este es el "punto de entrada" para ejecutar el servicio de vigilancia en segundo plano.
Cuando lo ejecutas, se queda corriendo indefinidamente, procesando automáticamente
cualquier factura nueva que aparezca en la carpeta vigilada.

¿CÓMO SE USA?
- Desarrollo: python watcher_service.py
- Producción: Registrar como servicio del sistema operativo

¿POR QUÉ UN SCRIPT SEPARADO?
1. Separación de Responsabilidades: `main.py` es para procesamiento manual (CLI).
   Este script es para procesamiento automático (daemon/service).
2. Configuración Diferente: Aquí configuramos logging para un servicio de larga duración,
   con rotación de logs para que no llenen el disco.
3. Gestión de Errores: Un servicio debe ser más robusto que un CLI. Si falla procesando
   una factura, debe continuar vigilando (no crashear).
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

# Añadir el directorio raíz al path para poder importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from src.folder_watcher import FolderWatcher
from src.ingestor import Document
from src.llm_extractor import LLMExtractor
from src.validator import validate_invoice
from src.storage import Storage

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LOGGING PARA SERVICIOS
# -----------------------------------------------------------------------------
# ¿POR QUÉ ROTATINGFILEHANDLER?
# - Un servicio puede correr meses sin reiniciarse.
# - Si escribimos todo en un solo archivo, puede crecer hasta GB.
# - RotatingFileHandler crea archivos nuevos cuando se alcanza un tamaño máximo.
# - Ejemplo: watcher.log, watcher.log.1, watcher.log.2, etc.
# -----------------------------------------------------------------------------

def setup_logging():
    """Configura logging con rotación para servicios de larga duración."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Crear handler con rotación
    handler = RotatingFileHandler(
        log_dir / "watcher.log",
        maxBytes=10*1024*1024,  # 10 MB por archivo
        backupCount=5,           # Mantener 5 archivos históricos
        encoding='utf-8'
    )
    
    # Formato detallado para debugging
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Configurar el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    
    # También mostrar en consola (útil para debugging)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

logger = logging.getLogger("watcher_service")

# -----------------------------------------------------------------------------
# FUNCIÓN DE PROCESAMIENTO
# -----------------------------------------------------------------------------

def process_invoice_file(file_path: str):
    """
    Procesa un archivo de factura completo (extracción + validación + guardado).
    
    Esta función es el "callback" que se ejecuta cuando el watcher detecta un archivo nuevo.
    
    ¿POR QUÉ UNA FUNCIÓN SEPARADA?
    - Reutilización: Esta misma lógica podría usarse desde una API, un email ingestor, etc.
    - Testing: Es más fácil testear una función pura que un servicio completo.
    - Manejo de Errores: Podemos capturar errores aquí sin que afecten al watcher.
    """
    try:
        logger.info(f"🚀 Procesando: {Path(file_path).name}")
        
        # Crear documento
        doc = Document(
            id=f"watcher_{Path(file_path).name}",
            filename=Path(file_path).name,
            filepath=file_path,
            source="folder_watcher"
        )
        
        # Extraer datos con LLM
        logger.info(f"🤖 Extrayendo datos de {doc.filename}...")
        extractor = LLMExtractor(api_key=os.getenv("OPENAI_API_KEY"))
        factura = extractor.extract(doc)
        
        # Validar
        logger.info(f"✅ Validando factura {factura.numero_factura}...")
        validation = validate_invoice(factura)
        
        status = "OK" if validation.is_valid else "REVIEW"
        notes = "\n".join(validation.errors + validation.warnings)
        
        if not validation.is_valid:
            logger.warning(f"⚠️ Factura {factura.numero_factura} requiere revisión: {notes}")
        
        # Guardar en DB
        storage = Storage()
        saved = storage.save_invoice(doc.id, factura, status, notes)
        
        if saved:
            # Exportar a CSV
            storage.export_to_csv(factura)
            logger.info(f"✅ Factura {factura.numero_factura} procesada correctamente")
            
            # PRODUCCIÓN: Aquí podrías mover el archivo a una carpeta "Procesados"
            # para mantener la carpeta de entrada limpia
            # processed_dir = Path("facturas_input/procesados")
            # processed_dir.mkdir(exist_ok=True)
            # Path(file_path).rename(processed_dir / Path(file_path).name)
        else:
            logger.info(f"ℹ️ Factura {doc.filename} ya existía en la base de datos (duplicado)")
        
    except Exception as e:
        logger.error(f"❌ Error procesando {Path(file_path).name}: {e}", exc_info=True)
        # PRODUCCIÓN: Aquí podrías mover el archivo a una carpeta "Errores"
        # para revisión manual

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main():
    """Punto de entrada del servicio."""
    
    # Configurar logging
    setup_logging()
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ OPENAI_API_KEY no encontrada en .env")
        sys.exit(1)
    
    # Carpeta a vigilar
    watch_folder = os.getenv("WATCH_FOLDER", "./facturas_input")
    
    logger.info("=" * 60)
    logger.info("🚀 SERVICIO DE VIGILANCIA DE FACTURAS")
    logger.info("=" * 60)
    logger.info(f"📁 Carpeta vigilada: {watch_folder}")
    logger.info(f"🔑 API Key configurada: {'Sí' if os.getenv('OPENAI_API_KEY') else 'No'}")
    logger.info("=" * 60)
    
    # Crear y ejecutar el watcher
    try:
        watcher = FolderWatcher(
            watch_path=watch_folder,
            process_callback=process_invoice_file
        )
        
        # Ejecutar indefinidamente
        watcher.run_forever()
        
    except ValueError as e:
        logger.error(f"❌ Error de configuración: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
