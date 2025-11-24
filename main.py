import os
import sys
import typer
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

# Importamos nuestros módulos (la arquitectura modular)
from src.ingestor import LocalFileIngestor
from src.llm_extractor import LLMExtractor
from src.validator import validate_invoice
from src.storage import Storage

# Cargar variables de entorno (.env)
load_dotenv()

import logging
from rich.logging import RichHandler

# Configuración de Logging para Producción
# 1. Archivo: Para tener un historial persistente de qué pasó (app.log)
# 2. Consola: Para que el usuario vea el progreso bonito (Rich)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),
        RichHandler(rich_tracebacks=True)
    ]
)
logger = logging.getLogger("main")

app = typer.Typer()
console = Console()

# -----------------------------------------------------------------------------
# 0. CLI ENTRY POINT (ORQUESTADOR)
# -----------------------------------------------------------------------------
# ¿QUÉ ES ESTO?
# Es el "Director de Orquesta". Su única función es coordinar a los músicos 
# (Ingestor, Extractor, Validador, Storage) para que toquen la sinfonía.
#
# ¿POR QUÉ ASÍ EN PRODUCCIÓN?
# 1. Desacoplamiento: Si mañana cambias la base de datos (Storage) o el modelo de IA (Extractor),
#    este archivo NO debería cambiar apenas.
# 2. Manejo de Errores Centralizado: Aquí capturamos los fallos de alto nivel para
#    que el programa no "explote" sin dejar rastro.
# 3. CLI vs API: Ahora es un CLI (línea de comandos), pero esta misma lógica
#    se puede envolver en una API (FastAPI) fácilmente porque los módulos son independientes.
# -----------------------------------------------------------------------------

@app.command()
def process_folder(
    folder_path: str = typer.Argument(..., help="Carpeta con facturas (PDF/Imágenes)"),
    extensions: str = typer.Option("pdf,jpg,png,jpeg", help="Extensiones a buscar separadas por coma")
):
    """
    Procesa todas las facturas de una carpeta.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[bold red]❌ Error:[/bold red] No se encontró OPENAI_API_KEY en .env")
        raise typer.Exit(code=1)

    # 1. Setup
    console.print(f"[bold blue]🚀 Iniciando Agente de Facturas v1.0[/bold blue]")
    ingestor = LocalFileIngestor(folder_path)
    extractor = LLMExtractor(api_key)
    storage = Storage() # Conecta a SQLite data/facturas.db

    # 2. Ingesta
    ext_list = [f".{e.strip()}" for e in extensions.split(",")]
    docs = ingestor.list_documents(ext_list)
    
    if not docs:
        console.print(f"[yellow]No se encontraron archivos en {folder_path}[/yellow]")
        return

    console.print(f"📂 Encontrados [bold]{len(docs)}[/bold] documentos para procesar.\n")

    # 3. Bucle de Procesamiento
    table = Table(title="Resumen de Procesamiento")
    table.add_column("Archivo", style="cyan")
    table.add_column("Proveedor", style="magenta")
    table.add_column("Total", justify="right", style="green")
    table.add_column("Estado", justify="center")
    table.add_column("Notas", style="red")

    for doc in docs:
        try:
            # A. Extracción (IA)
            console.print(f"🤖 Extrayendo: [italic]{doc.filename}[/italic]...")
            factura = extractor.extract(doc)
            
            # B. Validación (Lógica)
            val_result = validate_invoice(factura)
            
            status = "OK"
            notes = ""
            
            if not val_result.is_valid:
                status = "ERROR"
                notes = "; ".join(val_result.errors)
            elif val_result.warnings:
                status = "REVIEW"
                notes = "; ".join(val_result.warnings)

            # C. Persistencia (DB + CSV)
            storage.save_invoice(doc.id, factura, status, notes)
            storage.export_to_csv(factura)

            # UI Update
            status_style = "green" if status == "OK" else "yellow" if status == "REVIEW" else "red"
            table.add_row(
                doc.filename, 
                factura.nombre_proveedor, 
                f"{factura.total_factura:.2f} {factura.moneda}", 
                f"[{status_style}]{status}[/{status_style}]",
                notes
            )

        except Exception as e:
            console.print(f"[bold red]💥 Fallo crítico en {doc.filename}: {e}[/bold red]")
            table.add_row(doc.filename, "ERROR", "0.00", "[red]CRASH[/red]", str(e))

    console.print("\n")
    console.print(table)
    console.print(f"\n[bold green]✅ Proceso completado.[/bold green] Datos guardados en 'data/facturas.db' y 'output/facturas.csv'")

if __name__ == "__main__":
    app()
