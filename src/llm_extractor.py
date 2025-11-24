import base64
import instructor
from openai import OpenAI
from .models import Factura
from .ingestor import Document

# -----------------------------------------------------------------------------
# 3. MOTOR DE EXTRACCIÓN (LLM + Instructor)
# -----------------------------------------------------------------------------
# ¿QUÉ ES ESTO?
# Es el cerebro. Toma una imagen y devuelve un objeto Python validado.
# Usa la librería 'instructor' para parchear el cliente de OpenAI.
#
# ¿POR QUÉ ASÍ EN PRODUCCIÓN?
# 1. Salida Estructurada Garantizada: No le pedimos "dame un JSON", le pedimos
#    "rellena esta clase Pydantic". Si el LLM falla, 'instructor' reintenta
#    automáticamente pasándole el error de validación al LLM para que se corrija.
# 2. Visión Multimodal: Usamos GPT-4o porque "ve" la factura como un humano.
#    OCR tradicional (Tesseract) falla mucho con tablas y formatos raros.
# 3. Reintentos (Retries): En producción, las APIs fallan. Instructor maneja
#    automáticamente los reintentos si la validación de Pydantic falla.
# -----------------------------------------------------------------------------

def encode_image(image_path: str) -> str:
    """Codifica una imagen a base64 para enviarla a GPT-4o."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class LLMExtractor:
    def __init__(self, api_key: str):
        # Inicializamos el cliente "parcheado" por instructor
        self.client = instructor.from_openai(OpenAI(api_key=api_key))
        # Modelo a usar. GPT-4o es ideal para visión + texto.
        self.model_name = "gpt-4o" 

    def extract(self, document: Document) -> Factura:
        """
        Toma un documento (PDF o Imagen) y extrae los datos en estructura Factura.
        Nota: Para este MVP, asumimos que si es PDF, GPT-4o puede leerlo si se convierte a imagen
        o si usamos un parser de texto antes. 
        Para simplificar el MVP, trataremos todo como "visión" (ideal para imágenes) 
        o texto crudo si pudiéramos extraerlo.
        
        *TRUCO*: GPT-4o funciona muy bien con imágenes. Si el PDF es de una página,
        lo ideal es convertirlo a imagen. Si es texto seleccionable, mejor pasar el texto.
        Aquí, para simplificar, asumiremos que el usuario nos da imágenes o PDFs que 
        podemos tratar (en un MVP real usaríamos 'pdf2image' para convertir PDFs).
        """
        
        print(f"🧠 Analizando documento: {document.filename}...")

        # Construimos el mensaje para el LLM
        # Si es una imagen (jpg, png), la enviamos como payload de visión.
        # Si fuera un PDF complejo, habría que extraer texto o convertir a imagen.
        # Aquí haremos una implementación básica que asume que si es imagen, enviamos imagen.
        
        extension = document.filename.split('.')[-1].lower()
        messages = []

        if extension in ['jpg', 'jpeg', 'png', 'webp']:
            # Flujo de Visión
            base64_image = encode_image(document.filepath)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extrae la información de esta factura. Si algún campo no está claro, déjalo vacío o infiérelo con sentido común."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ]
        else:
            # Flujo de Texto (asumiendo PDF de texto o fallback)
            # En un caso real: usaríamos pypdf para extraer texto.
            # Para este MVP educativo: Le decimos al usuario que use imágenes o 
            # implementamos un extractor de texto simple si fuera necesario.
            # Por ahora, simularemos que leemos el archivo como texto si no es imagen,
            # (esto fallará con PDFs binarios, pero sirve para explicar el concepto).
            messages = [
                {
                    "role": "user", 
                    "content": f"Extrae los datos de esta factura (nombre archivo: {document.filename}). [Aquí iría el contenido OCR o texto extraído]"
                }
            ]
            print("⚠️ AVISO: Este MVP básico está optimizado para imágenes (JPG/PNG). Para PDFs reales, necesitaríamos 'pdf2image' o 'pypdf'.")

        # Llamada mágica a Instructor
        factura_extraida = self.client.chat.completions.create(
            model=self.model_name,
            response_model=Factura, # <--- AQUÍ ESTÁ LA CLAVE
            messages=messages,
            temperature=0.0, # Determinista
        )
        
        return factura_extraida
