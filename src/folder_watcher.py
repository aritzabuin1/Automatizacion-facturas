import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from typing import Callable

# -----------------------------------------------------------------------------
# 6. VIGILANTE DE CARPETAS (Event-Driven Architecture)
# -----------------------------------------------------------------------------
# ¿QUÉ ES ESTO?
# Es un "guardia" que vigila una carpeta 24/7. Cuando detecta un archivo nuevo,
# automáticamente lo procesa sin intervención humana.
#
# ¿POR QUÉ ASÍ EN PRODUCCIÓN?
# 1. **Automatización Real**: El cliente no tiene que "subir" nada. Solo guarda
#    la factura en una carpeta (ej: Dropbox, OneDrive, carpeta de red) y el sistema
#    la procesa automáticamente.
# 2. **Arquitectura Event-Driven**: En lugar de hacer polling (preguntar cada X segundos
#    "¿hay algo nuevo?"), usamos eventos del sistema operativo. Es más eficiente.
# 3. **Escalabilidad**: Este patrón es la base de sistemas como AWS Lambda, Azure Functions.
#    Un evento (archivo nuevo) dispara una acción (procesar factura).
# 4. **Resiliencia**: Si el servicio se cae, al reiniciarse puede procesar los archivos
#    que se quedaron pendientes (usando la DB para saber cuáles ya procesó).
#
# LIBRERÍA: `watchdog`
# - Es la librería estándar de facto para monitorizar sistemas de archivos en Python.
# - Funciona en Windows, Linux, macOS.
# - Usa APIs nativas del OS (inotify en Linux, FSEvents en macOS, ReadDirectoryChangesW en Windows).
# -----------------------------------------------------------------------------

logger = logging.getLogger("folder_watcher")

class InvoiceFileHandler(FileSystemEventHandler):
    """
    Handler personalizado que reacciona a eventos de archivos.
    
    ¿POR QUÉ UNA CLASE?
    - `watchdog` usa el patrón Observer. Nosotros heredamos de `FileSystemEventHandler`
      y sobrescribimos los métodos que nos interesan (ej: `on_created`).
    """
    
    def __init__(self, process_callback: Callable[[str], None], extensions: list[str] = None):
        """
        Args:
            process_callback: Función que se llamará cuando llegue un archivo nuevo.
                              Debe aceptar un parámetro: la ruta del archivo.
            extensions: Lista de extensiones permitidas (ej: ['.pdf', '.jpg', '.png'])
        """
        super().__init__()
        self.process_callback = process_callback
        self.extensions = extensions or ['.pdf', '.jpg', '.jpeg', '.png']
        
        # PRODUCCIÓN: Evitar procesar el mismo archivo múltiples veces si hay eventos duplicados
        # (algunos sistemas de archivos disparan múltiples eventos para una sola creación)
        self._processing = set()  # Set de archivos que están siendo procesados
    
    def on_created(self, event: FileCreatedEvent):
        """
        Se ejecuta cuando se CREA un archivo en la carpeta vigilada.
        
        ¿POR QUÉ SOLO `on_created` Y NO `on_modified`?
        - `on_modified` se dispara muchas veces mientras el archivo se está escribiendo.
        - `on_created` se dispara una vez cuando el archivo aparece.
        - En producción, si el archivo es muy grande, podríamos esperar a que termine
          de escribirse (comprobando que el tamaño no cambia durante X segundos).
        """
        if event.is_directory:
            return  # Ignoramos carpetas
        
        file_path = Path(event.src_path)
        
        # Filtrar por extensión
        if file_path.suffix.lower() not in self.extensions:
            logger.debug(f"Ignorando archivo {file_path.name} (extensión no permitida)")
            return
        
        # Evitar procesar archivos temporales (ej: ~$factura.xlsx de Excel)
        if file_path.name.startswith('~') or file_path.name.startswith('.'):
            logger.debug(f"Ignorando archivo temporal: {file_path.name}")
            return
        
        # Evitar duplicados (race condition)
        if str(file_path) in self._processing:
            logger.warning(f"El archivo {file_path.name} ya está siendo procesado, ignorando evento duplicado")
            return
        
        self._processing.add(str(file_path))
        
        try:
            logger.info(f"📥 Nuevo archivo detectado: {file_path.name}")
            
            # PRODUCCIÓN: Esperar un momento para asegurar que el archivo terminó de escribirse
            # (especialmente importante si el archivo viene de una copia de red lenta)
            time.sleep(2)
            
            # Verificar que el archivo aún existe (podría haberse borrado/movido)
            if not file_path.exists():
                logger.warning(f"El archivo {file_path.name} desapareció antes de procesarse")
                return
            
            # Llamar al callback de procesamiento
            self.process_callback(str(file_path))
            
        except Exception as e:
            logger.error(f"Error procesando {file_path.name}: {e}", exc_info=True)
        finally:
            # Limpiar el set de procesamiento
            self._processing.discard(str(file_path))


class FolderWatcher:
    """
    Servicio que vigila una carpeta y procesa archivos automáticamente.
    
    PATRÓN: Service/Daemon
    - Este objeto se puede ejecutar en segundo plano indefinidamente.
    - En producción, lo ejecutarías como un servicio de Windows (usando `nssm` o `pywin32`)
      o como un servicio systemd en Linux.
    """
    
    def __init__(self, watch_path: str, process_callback: Callable[[str], None]):
        """
        Args:
            watch_path: Ruta de la carpeta a vigilar
            process_callback: Función que procesa cada archivo nuevo
        """
        self.watch_path = Path(watch_path)
        self.process_callback = process_callback
        self.observer = None
        
        # Validar que la carpeta existe
        if not self.watch_path.exists():
            raise ValueError(f"La carpeta {watch_path} no existe")
        
        if not self.watch_path.is_dir():
            raise ValueError(f"{watch_path} no es una carpeta")
    
    def start(self):
        """
        Inicia el servicio de vigilancia.
        
        ¿CÓMO FUNCIONA?
        1. Crea un Observer (hilo en segundo plano que monitoriza el sistema de archivos)
        2. Le asigna un Handler (nuestra clase InvoiceFileHandler)
        3. El Observer notifica al Handler cuando hay eventos
        """
        logger.info(f"🔍 Iniciando vigilancia de carpeta: {self.watch_path}")
        
        # Crear el handler
        event_handler = InvoiceFileHandler(self.process_callback)
        
        # Crear el observer
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_path), recursive=False)
        
        # Iniciar el observer (corre en un hilo separado)
        self.observer.start()
        
        logger.info("✅ Servicio de vigilancia activo. Esperando archivos...")
    
    def stop(self):
        """Detiene el servicio de vigilancia."""
        if self.observer:
            logger.info("🛑 Deteniendo servicio de vigilancia...")
            self.observer.stop()
            self.observer.join()  # Esperar a que el hilo termine
            logger.info("✅ Servicio detenido")
    
    def run_forever(self):
        """
        Ejecuta el servicio indefinidamente (hasta Ctrl+C).
        
        USO EN PRODUCCIÓN:
        - En desarrollo: python watcher_service.py
        - En producción: Registrar como servicio del sistema operativo
        """
        try:
            self.start()
            # Mantener el programa vivo
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupción recibida (Ctrl+C)")
        finally:
            self.stop()
