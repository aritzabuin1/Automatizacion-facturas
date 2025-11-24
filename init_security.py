#!/usr/bin/env python
"""
SCRIPT DE INICIALIZACIÓN DE SEGURIDAD
======================================

Este script configura todos los aspectos de seguridad del sistema:
1. Genera encryption key
2. Genera JWT secret key
3. Crea usuarios por defecto
4. Verifica configuración de seguridad

USO:
python init_security.py
"""

import os
import sys
import secrets
from pathlib import Path

# Añadir directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from src.encryption import generate_encryption_key, DataEncryption
from src.auth import UserManager, init_default_users

def generate_jwt_secret() -> str:
    """Genera un JWT secret key aleatorio."""
    return secrets.token_urlsafe(32)

def check_env_file():
    """Verifica si existe .env y lo crea si no."""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists():
        if env_example_path.exists():
            print("📋 Copiando .env.example a .env...")
            env_path.write_text(env_example_path.read_text())
        else:
            print("⚠️ No se encontró .env ni .env.example")
            env_path.write_text("# Configuración generada automáticamente\n")
    
    return env_path

def update_env_file(env_path: Path, key: str, value: str):
    """Actualiza una variable en el archivo .env."""
    content = env_path.read_text()
    lines = content.split('\n')
    
    # Buscar si la key ya existe
    key_found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            key_found = True
            break
    
    # Si no existe, añadir al final
    if not key_found:
        lines.append(f"{key}={value}")
    
    env_path.write_text('\n'.join(lines))

def main():
    print("=" * 70)
    print("🔒 INICIALIZACIÓN DE SEGURIDAD - Agente de Facturas Pro")
    print("=" * 70)
    print()
    
    # 1. Verificar/crear .env
    print("1️⃣ Verificando archivo .env...")
    env_path = check_env_file()
    print(f"   ✅ Archivo .env: {env_path.absolute()}")
    print()
    
    # 2. Generar Encryption Key
    print("2️⃣ Generando Encryption Key...")
    encryption_key = generate_encryption_key()
    print(f"   ✅ Encryption Key generada")
    print(f"   📝 {encryption_key}")
    update_env_file(env_path, "ENCRYPTION_KEY", encryption_key)
    print()
    
    # 3. Generar JWT Secret
    print("3️⃣ Generando JWT Secret Key...")
    jwt_secret = generate_jwt_secret()
    print(f"   ✅ JWT Secret generado")
    print(f"   📝 {jwt_secret}")
    update_env_file(env_path, "JWT_SECRET_KEY", jwt_secret)
    print()
    
    # 4. Configurar contraseña admin
    print("4️⃣ Configurando contraseña de administrador...")
    admin_password = input("   Introduce contraseña para 'admin' (mín. 8 caracteres): ").strip()
    
    if len(admin_password) < 8:
        print("   ⚠️ Contraseña muy corta. Usando 'admin123' por defecto.")
        print("   ⚠️ CÁMBIALA INMEDIATAMENTE después de primer login!")
        admin_password = "admin123"
    
    update_env_file(env_path, "ADMIN_PASSWORD", admin_password)
    print(f"   ✅ Contraseña configurada")
    print()
    
    # 5. Crear usuarios por defecto
    print("5️⃣ Creando usuarios por defecto...")
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Crear usuarios
    manager = UserManager(secret_key=jwt_secret)
    
    # Usuario admin
    if manager.create_user(
        username="admin",
        password=admin_password,
        email="admin@empresa.com",
        role="admin"
    ):
        print("   ✅ Usuario 'admin' creado")
    else:
        print("   ℹ️ Usuario 'admin' ya existe")
    
    # Usuario demo
    if manager.create_user(
        username="demo",
        password="demo123",
        email="demo@empresa.com",
        role="user"
    ):
        print("   ✅ Usuario 'demo' creado")
    else:
        print("   ℹ️ Usuario 'demo' ya existe")
    
    print()
    
    # 6. Test de encriptación
    print("6️⃣ Verificando encriptación...")
    encryptor = DataEncryption(encryption_key)
    test_data = "TEST_DATA_123"
    encrypted = encryptor.encrypt(test_data)
    decrypted = encryptor.decrypt(encrypted)
    
    if test_data == decrypted:
        print("   ✅ Encriptación funcionando correctamente")
    else:
        print("   ❌ ERROR: Encriptación no funciona")
        sys.exit(1)
    print()
    
    # 7. Test de autenticación
    print("7️⃣ Verificando autenticación...")
    result = manager.authenticate("admin", admin_password, "127.0.0.1")
    
    if result:
        print("   ✅ Autenticación funcionando correctamente")
        print(f"   Token generado: {result['token'][:50]}...")
    else:
        print("   ❌ ERROR: Autenticación no funciona")
        sys.exit(1)
    print()
    
    # Resumen final
    print("=" * 70)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print("📋 Resumen de configuración:")
    print(f"   • Archivo .env: {env_path.absolute()}")
    print(f"   • Encryption Key: Configurada ✅")
    print(f"   • JWT Secret: Configurado ✅")
    print(f"   • Usuario admin: Creado ✅")
    print(f"   • Usuario demo: Creado ✅")
    print()
    print("🔐 Credenciales de acceso:")
    print(f"   • Username: admin")
    print(f"   • Password: {admin_password}")
    print()
    print("⚠️ IMPORTANTE:")
    print("   1. Guarda una copia de seguridad de .env")
    print("   2. NUNCA subas .env a git")
    print("   3. Cambia la contraseña después del primer login")
    print("   4. La encryption key es IRRECUPERABLE si se pierde")
    print()
    print("🚀 Ya puedes iniciar el sistema:")
    print("   • Dashboard: streamlit run dashboard.py")
    print("   • Watcher: python watcher_service.py")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Inicialización cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
