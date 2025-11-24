import os
from dataclasses import dataclass
from typing import List, Optional

# -----------------------------------------------------------------------------
# 2. INGESTA DE DOCUMENTOS (Patrón Adapter)
# -----------------------------------------------------------------------------
# ¿QUÉ ES ESTO?
# Es el módulo encargado de "traer" los documentos al sistema. Normaliza cualquier
# entrada (PDF, JPG, Email, S3) a un objeto común `Document`.
#
# ¿POR QUÉ ASÍ EN PRODUCCIÓN?
# 1. Escalabilidad: Hoy lees de una carpeta local. Mañana querrás leer de un Email (IMAP)
#    o de un Bucket S3. Con este patrón, solo creas una clase nueva (ej: `EmailIngestor`)
#    y el resto del sistema NO cambia.
# 2. Abstracción: Al resto del programa no le importa si el archivo vino de un USB o de la nube.
#    Solo le importa que tiene un `content` y un `filename`.
# -----------------------------------------------------------------------------

@dataclass
class Document:
    """Representación unificada de un documento a procesar."""
    id: str                 # ID único para traza
    filename: str           # Nombre original del archivo
    filepath: str           # Ruta local donde está el archivo (para abrirlo)
    source: str             # Origen: 'local', 'email', 'upload'
    content_bytes: Optional[bytes] = None # Contenido binario (opcional si tenemos filepath)

class LocalFileIngestor:
    """Ingestor simple que busca archivos en una carpeta local."""
    
    def __init__(self, directory: str):
        self.directory = directory

    def list_documents(self, extensions: List[str] = [".pdf", ".jpg", ".png", ".jpeg"]) -> List[Document]:
        """Escanea el directorio y devuelve una lista de objetos Document."""
        documents = []
        
        if not os.path.exists(self.directory):
            print(f"⚠️ El directorio {self.directory} no existe.")
            return []

        for f in os.listdir(self.directory):
            if any(f.lower().endswith(ext) for ext in extensions):
                full_path = os.path.join(self.directory, f)
                # En un caso real, aquí generaríamos un ID único o hash del archivo
                doc_id = f"local_{f}" 
                
                doc = Document(
                    id=doc_id,
                    filename=f,
                    filepath=full_path,
                    source="local"
                )
                documents.append(doc)
        
        return documents
