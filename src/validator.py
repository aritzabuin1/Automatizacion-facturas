from dataclasses import dataclass
from typing import List
from .models import Factura

# -----------------------------------------------------------------------------
# 4. VALIDADOR DE NEGOCIO
# -----------------------------------------------------------------------------
# ¿QUÉ ES ESTO?
# Es el "Auditor". Verifica que los datos, aunque sean del tipo correcto (Pydantic),
# tengan sentido para el negocio.
#
# ¿POR QUÉ ASÍ EN PRODUCCIÓN?
# 1. Separación de Responsabilidades: Pydantic dice "esto es un número".
#    Este módulo dice "este número está mal calculado".
# 2. Reglas Complejas: Aquí puedes programar reglas que dependen de otros sistemas
#    (ej: "¿Existe este proveedor en mi ERP?", "¿La fecha es del ejercicio fiscal abierto?").
# 3. Confianza: Si el LLM se inventa un número, la validación matemática (Total = Suma items)
#    lo detectará y marcará la factura para revisión humana (REVIEW).
# -----------------------------------------------------------------------------

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

def validate_invoice(factura: Factura) -> ValidationResult:
    errors = []
    warnings = []

    # 1. Validación de Totales (Matemáticas)
    # Permitimos un pequeño margen de error por redondeos (0.05 céntimos)
    calculado = factura.base_imponible + factura.total_impuestos
    diferencia = abs(calculado - factura.total_factura)
    
    if diferencia > 0.05:
        errors.append(f"Error matemático: Base ({factura.base_imponible}) + Impuestos ({factura.total_impuestos}) != Total ({factura.total_factura}). Dif: {diferencia:.2f}")

    # 2. Validación de Campos Obligatorios Críticos (más allá del tipo)
    if not factura.numero_factura:
        warnings.append("Falta el número de factura. Se ha extraído vacío.")
    
    if not factura.fecha_emision:
        warnings.append("Falta la fecha de emisión.")

    # 3. Validación de Líneas
    if not factura.items:
        warnings.append("La factura no tiene líneas de detalle (items).")
    else:
        # Comprobar que la suma de las líneas cuadra con la base imponible
        suma_lineas = sum(item.total_linea for item in factura.items)
        # Esto es delicado porque a veces total_linea incluye IVA y a veces no.
        # Lo ponemos como warning si la diferencia es muy grande.
        if abs(suma_lineas - factura.base_imponible) > 1.0 and abs(suma_lineas - factura.total_factura) > 1.0:
            warnings.append(f"La suma de líneas ({suma_lineas:.2f}) no coincide ni con Base ni con Total.")

    return ValidationResult(
        is_valid=(len(errors) == 0),
        errors=errors,
        warnings=warnings
    )
