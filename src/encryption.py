# =============================================================================
# ENCRIPTACIÓN DE DATOS SENSIBLES
# =============================================================================
# Este módulo encripta datos sensibles antes de guardarlos en la base de datos.
#
# ¿POR QUÉ ENCRIPTAR?
# 1. GDPR/LOPD: Datos personales deben estar protegidos
# 2. Seguridad: Si alguien accede a la DB, no puede leer los datos
# 3. Compliance: Muchas industrias requieren encriptación en reposo
#
# ¿QUÉ SE ENCRIPTA?
# - CIF/NIF de proveedores (dato personal)
# - Números de factura (pueden contener info sensible)
# - Notas de validación (pueden contener comentarios internos)
#
# ALGORITMO: Fernet (AES-128 en modo CBC con HMAC)
# - Simétrico (misma key para encriptar/desencriptar)
# - Autenticado (detecta manipulación)
# - Estándar de la industria
# =============================================================================

import os
import base64
import logging
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional

logger = logging.getLogger("encryption")

class DataEncryption:
    """
    Gestor de encriptación de datos sensibles.
    
    SEGURIDAD:
    - Usa Fernet (AES-128 + HMAC)
    - Key debe venir de variable de entorno
    - Detecta manipulación de datos
    
    PRODUCCIÓN:
    - Generar key aleatoria: Fernet.generate_key()
    - Guardar en .env (ENCRYPTION_KEY)
    - NUNCA compartir la key
    - Hacer backup de la key (sin ella, datos irrecuperables)
    """
    
    def __init__(self, encryption_key: str = None):
        """
        Inicializa el encriptador.
        
        Args:
            encryption_key: Key de encriptación (base64). Si None, se genera una nueva.
        """
        if encryption_key:
            try:
                self.key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
                self.cipher = Fernet(self.key)
            except Exception as e:
                logger.error(f"Error inicializando cipher con key proporcionada: {e}")
                raise ValueError("Encryption key inválida. Debe ser una key Fernet válida en base64.")
        else:
            # Generar nueva key (SOLO para desarrollo/testing)
            logger.warning("⚠️ Generando nueva encryption key. En producción, usa una key fija desde .env")
            self.key = Fernet.generate_key()
            self.cipher = Fernet(self.key)
            logger.info(f"Nueva encryption key generada: {self.key.decode()}")
            logger.warning("⚠️ GUARDA ESTA KEY EN .env COMO ENCRYPTION_KEY")
    
    def encrypt(self, data: str) -> Optional[str]:
        """
        Encripta un string.
        
        Args:
            data: Texto a encriptar
        
        Returns:
            Texto encriptado en base64, o None si error
        """
        if not data:
            return None
        
        try:
            encrypted_bytes = self.cipher.encrypt(data.encode('utf-8'))
            encrypted_str = base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
            return encrypted_str
        except Exception as e:
            logger.error(f"Error encriptando datos: {e}")
            return None
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """
        Desencripta un string.
        
        Args:
            encrypted_data: Texto encriptado en base64
        
        Returns:
            Texto original, o None si error/manipulado
        """
        if not encrypted_data:
            return None
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode('utf-8')
            return decrypted_str
        except InvalidToken:
            logger.error("⚠️ ALERTA DE SEGURIDAD: Datos manipulados o key incorrecta")
            return None
        except Exception as e:
            logger.error(f"Error desencriptando datos: {e}")
            return None
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encripta campos específicos de un diccionario.
        
        Args:
            data: Diccionario con datos
            fields_to_encrypt: Lista de keys a encriptar
        
        Returns:
            Diccionario con campos encriptados
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Desencripta campos específicos de un diccionario.
        
        Args:
            data: Diccionario con datos encriptados
            fields_to_decrypt: Lista de keys a desencriptar
        
        Returns:
            Diccionario con campos desencriptados
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_value = self.decrypt(decrypted_data[field])
                if decrypted_value is not None:
                    decrypted_data[field] = decrypted_value
                else:
                    logger.warning(f"No se pudo desencriptar campo: {field}")
        
        return decrypted_data


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def generate_encryption_key() -> str:
    """
    Genera una nueva encryption key.
    
    USO:
    1. Ejecutar esta función UNA VEZ
    2. Copiar la key generada
    3. Añadir a .env como ENCRYPTION_KEY=<key>
    4. NUNCA regenerar (perderías acceso a datos encriptados)
    
    Returns:
        Encryption key en base64
    """
    key = Fernet.generate_key()
    return key.decode('utf-8')


def init_encryption_from_env() -> DataEncryption:
    """
    Inicializa encriptación desde variable de entorno.
    
    Returns:
        Instancia de DataEncryption configurada
    """
    encryption_key = os.getenv("ENCRYPTION_KEY")
    
    if not encryption_key:
        logger.warning("⚠️ ENCRYPTION_KEY no encontrada en .env. Generando una nueva...")
        logger.warning("⚠️ Esto es INSEGURO en producción. Añade ENCRYPTION_KEY a .env")
        new_key = generate_encryption_key()
        logger.warning(f"⚠️ Nueva key generada: {new_key}")
        logger.warning("⚠️ Añade esta línea a .env:")
        logger.warning(f"ENCRYPTION_KEY={new_key}")
        encryption_key = new_key
    
    return DataEncryption(encryption_key)


# =============================================================================
# CAMPOS A ENCRIPTAR EN FACTURAS
# =============================================================================

SENSITIVE_FIELDS = [
    'cif_proveedor',      # Dato personal (GDPR)
    'numero_factura',     # Puede contener info sensible
    'validation_notes'    # Comentarios internos
]


if __name__ == "__main__":
    # Test básico
    print("=" * 60)
    print("GENERADOR DE ENCRYPTION KEY")
    print("=" * 60)
    
    # Generar nueva key
    new_key = generate_encryption_key()
    print(f"\n✅ Nueva encryption key generada:")
    print(f"\nENCRYPTION_KEY={new_key}")
    print(f"\n⚠️ IMPORTANTE:")
    print("1. Copia esta key a tu archivo .env")
    print("2. NUNCA la compartas ni la subas a git")
    print("3. Haz un backup seguro (sin ella, datos irrecuperables)")
    print("4. Usa la MISMA key en todos los entornos (dev, prod)")
    print("\n" + "=" * 60)
    
    # Test de encriptación
    print("\n🧪 Test de encriptación:")
    encryptor = DataEncryption(new_key)
    
    test_data = "B12345678"  # CIF de ejemplo
    encrypted = encryptor.encrypt(test_data)
    decrypted = encryptor.decrypt(encrypted)
    
    print(f"Original:    {test_data}")
    print(f"Encriptado:  {encrypted}")
    print(f"Desencriptado: {decrypted}")
    print(f"✅ Match: {test_data == decrypted}")
