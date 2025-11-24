from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# -----------------------------------------------------------------------------
# 1. MODELOS DE DATOS (Pydantic) - EL CONTRATO
# -----------------------------------------------------------------------------
# ¿QUÉ ES ESTO?
# Es el "Contrato" que debe cumplir la IA. Si la IA devuelve algo que no encaja
# aquí, el sistema lo rechaza automáticamente.
#
# ¿POR QUÉ ASÍ EN PRODUCCIÓN?
# 1. Validación Estricta: En producción, "casi bien" no sirve. O es un float, o falla.
#    Pydantic garantiza que si el objeto se crea, los tipos son correctos.
# 2. Documentación Viva: Los campos 'description' NO son solo para humanos.
#    Son el PROMPT que lee el LLM. Si cambias la descripción, cambias cómo se comporta la IA.
# 3. Interoperabilidad: Estos modelos se pueden exportar a JSON Schema automáticamente,
#    lo que facilita integrarse con Frontends (React) o APIs externas.
# -----------------------------------------------------------------------------

class ItemFactura(BaseModel):
    """Representa una línea de detalle dentro de la factura."""
    descripcion: str = Field(
        ..., 
        description="Descripción del producto o servicio. Ejemplo: 'Consultoría horas extra' o 'Monitor 24 pulgadas'"
    )
    cantidad: float = Field(
        ..., 
        description="Cantidad de unidades. Si no se especifica, asumir 1."
    )
    precio_unitario: float = Field(
        ..., 
        description="Precio por unidad sin impuestos."
    )
    total_linea: float = Field(
        ..., 
        description="Total de la línea (cantidad * precio_unitario). A veces incluye impuestos, a veces no, depende de la factura."
    )

class Factura(BaseModel):
    """Modelo principal que representa una factura completa."""
    # Identificación
    numero_factura: Optional[str] = Field(
        None, 
        description="El identificador único de la factura. Ejemplo: 'F-2023-001'"
    )
    fecha_emision: Optional[date] = Field(
        None, 
        description="Fecha en que se emitió la factura. Formato YYYY-MM-DD."
    )
    
    # Entidades
    nombre_proveedor: str = Field(
        ..., 
        description="Nombre de la empresa o persona que emite la factura."
    )
    cif_proveedor: Optional[str] = Field(
        None, 
        description="Identificación fiscal del proveedor (CIF, NIF, VAT ID)."
    )
    nombre_cliente: Optional[str] = Field(
        None, 
        description="Nombre del cliente receptor de la factura."
    )

    # Totales
    base_imponible: float = Field(
        ..., 
        description="Suma de los importes antes de impuestos (Subtotal)."
    )
    total_impuestos: float = Field(
        0.0, 
        description="Total de impuestos (IVA, IRPF, etc)."
    )
    total_factura: float = Field(
        ..., 
        description="Importe final a pagar (Base + Impuestos)."
    )
    moneda: str = Field(
        "EUR", 
        description="Código de moneda ISO 4217. Ejemplo: EUR, USD, MXN."
    )

    # Detalle
    items: List[ItemFactura] = Field(
        default_factory=list,
        description="Lista de líneas o conceptos de la factura."
    )
