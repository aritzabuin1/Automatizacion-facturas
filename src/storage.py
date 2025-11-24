import os
import csv
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Date, Integer, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from .models import Factura

# -----------------------------------------------------------------------------
# 5. PERSISTENCIA (SQLAlchemy)
# -----------------------------------------------------------------------------
# ¿QUÉ ES ESTO?
# Es la capa que guarda los datos para siempre. Usa SQLAlchemy (ORM).
#
# ¿POR QUÉ ASÍ EN PRODUCCIÓN?
# 1. Agnosticismo de DB: Hoy usas SQLite (fichero local). Mañana, con cambiar
#    una línea de configuración (string de conexión), usas PostgreSQL en la nube.
#    El código NO cambia.
# 2. Seguridad (SQL Injection): Al usar ORM, estás protegido automáticamente
#    contra ataques de inyección SQL.
# 3. Migraciones: En un proyecto real, usaríamos 'Alembic' junto con estos modelos
#    para gestionar cambios en la estructura de la tabla sin borrar datos.
# -----------------------------------------------------------------------------

Base = declarative_base()

# Definición de Tablas SQL (Espejo de nuestros modelos Pydantic pero para DB)
class DBFactura(Base):
    __tablename__ = 'facturas'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(String, unique=True) # Enlace con el archivo original
    numero_factura = Column(String, nullable=True)
    fecha_emision = Column(Date, nullable=True)
    nombre_proveedor = Column(String)
    cif_proveedor = Column(String, nullable=True)
    total_factura = Column(Float)
    status = Column(String) # OK, REVIEW, ERROR
    validation_notes = Column(Text, nullable=True) # Errores o warnings
    created_at = Column(Date, default=datetime.now)

    items = relationship("DBItemFactura", back_populates="factura")

class DBItemFactura(Base):
    __tablename__ = 'invoice_items'
    
    id = Column(Integer, primary_key=True)
    factura_id = Column(Integer, ForeignKey('facturas.id'))
    descripcion = Column(String)
    cantidad = Column(Float)
    precio_unitario = Column(Float)
    total_linea = Column(Float)
    
    factura = relationship("DBFactura", back_populates="items")

class Storage:
    def __init__(self, db_path: str = "sqlite:///data/facturas.db"):
        # Asegurar que el directorio existe
        if "sqlite:///" in db_path:
            file_path = db_path.replace("sqlite:///", "")
            # Si es ruta relativa, asumimos que es relativa al CWD
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
            
            db_dir = os.path.dirname(file_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"📁 Directorio creado: {db_dir}")

        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_invoice(self, document_id: str, factura: Factura, status: str, notes: str):
        """Guarda la factura en la base de datos SQL."""
        session = self.Session()
        try:
            # Crear cabecera
            db_factura = DBFactura(
                document_id=document_id,
                numero_factura=factura.numero_factura,
                fecha_emision=factura.fecha_emision,
                nombre_proveedor=factura.nombre_proveedor,
                cif_proveedor=factura.cif_proveedor,
                total_factura=factura.total_factura,
                status=status,
                validation_notes=notes
            )
            session.add(db_factura)
            session.flush() # Para obtener el ID autogenerado

            # Crear líneas
            for item in factura.items:
                db_item = DBItemFactura(
                    factura_id=db_factura.id,
                    descripcion=item.descripcion,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    total_linea=item.total_linea
                )
                session.add(db_item)
            
            session.commit()
            print(f"💾 Guardado en DB: {factura.numero_factura} (ID: {db_factura.id})")
            return True
        except IntegrityError:
            session.rollback()
            print(f"⚠️ DUPLICADO: La factura {document_id} ya existe en la base de datos.")
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ Error guardando en DB: {e}")
            return False
        finally:
            session.close()

    def export_to_csv(self, factura: Factura, filename: str = "output/facturas.csv"):
        """Añade una línea al CSV maestro de facturas."""
        # Asegurar directorio de salida
        out_dir = os.path.dirname(filename)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        file_exists = os.path.isfile(filename)
        
        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escribir cabecera si es archivo nuevo
            if not file_exists:
                writer.writerow([
                    "Fecha Emision", "Numero", "Proveedor", "CIF", 
                    "Base", "Impuestos", "Total", "Moneda", "Items Count"
                ])
            
            writer.writerow([
                factura.fecha_emision,
                factura.numero_factura,
                factura.nombre_proveedor,
                factura.cif_proveedor,
                factura.base_imponible,
                factura.total_impuestos,
                factura.total_factura,
                factura.moneda,
                len(factura.items)
            ])
        print(f"📊 Exportado a CSV: {filename}")
