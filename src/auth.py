# =============================================================================
# GESTIÓN DE USUARIOS Y AUTENTICACIÓN SEGURA
# =============================================================================
# Este módulo maneja la autenticación de usuarios de forma segura.
#
# ¿POR QUÉ ESTE ENFOQUE?
# 1. Passwords hasheados con bcrypt (nunca en texto plano)
# 2. Base de datos SQLite para usuarios (fácil de migrar a PostgreSQL)
# 3. Sesiones con JWT tokens
# 4. Logging de intentos de login (auditoría de seguridad)
#
# PRODUCCIÓN:
# - Cambiar SECRET_KEY por una aleatoria (ver .env)
# - Considerar 2FA para usuarios admin
# - Rate limiting en login (prevenir brute force)
# =============================================================================

import sqlite3
import bcrypt
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger("auth")

class UserManager:
    """
    Gestor de usuarios con autenticación segura.
    
    SEGURIDAD:
    - Passwords hasheados con bcrypt (salt automático)
    - JWT tokens con expiración
    - Logging de todos los intentos de login
    - Protección contra timing attacks
    """
    
    def __init__(self, db_path: str = "data/users.db", secret_key: str = None):
        """
        Inicializa el gestor de usuarios.
        
        Args:
            db_path: Ruta a la base de datos de usuarios
            secret_key: Clave secreta para JWT (debe venir de .env)
        """
        self.db_path = db_path
        self.secret_key = secret_key or "CHANGE_THIS_IN_PRODUCTION_USE_ENV"
        
        # Crear directorio si no existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar base de datos
        self._init_db()
    
    def _init_db(self):
        """Crea la tabla de usuarios si no existe."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Base de datos de usuarios inicializada")
    
    def create_user(self, username: str, password: str, email: str = None, role: str = "user") -> bool:
        """
        Crea un nuevo usuario con password hasheado.
        
        SEGURIDAD:
        - Password hasheado con bcrypt (12 rounds)
        - Username único (constraint en DB)
        - Validación de inputs
        
        Args:
            username: Nombre de usuario (único)
            password: Contraseña en texto plano (se hasheará)
            email: Email del usuario (opcional)
            role: Rol del usuario (user, admin)
        
        Returns:
            True si se creó correctamente, False si ya existe
        """
        # Validar inputs
        if not username or len(username) < 3:
            logger.warning("Intento de crear usuario con username inválido")
            return False
        
        if not password or len(password) < 8:
            logger.warning("Intento de crear usuario con password débil")
            return False
        
        # Hashear password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            """, (username, password_hash, email, role))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Usuario creado: {username} (rol: {role})")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"Intento de crear usuario duplicado: {username}")
            return False
    
    def authenticate(self, username: str, password: str, ip_address: str = None) -> Optional[Dict]:
        """
        Autentica un usuario y devuelve un token JWT.
        
        SEGURIDAD:
        - Timing attack protection (bcrypt.checkpw es constant-time)
        - Logging de todos los intentos (éxito y fallo)
        - JWT token con expiración
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            ip_address: IP del cliente (para auditoría)
        
        Returns:
            Dict con token y datos de usuario si éxito, None si fallo
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener usuario
        cursor.execute("""
            SELECT id, username, password_hash, role, is_active
            FROM users
            WHERE username = ?
        """, (username,))
        
        user = cursor.fetchone()
        
        # Verificar password
        success = False
        if user and user[4]:  # is_active
            user_id, username_db, password_hash, role, is_active = user
            
            # bcrypt.checkpw es constant-time (protege contra timing attacks)
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                success = True
                
                # Actualizar last_login
                cursor.execute("""
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (user_id,))
                conn.commit()
        
        # Registrar intento de login (auditoría)
        cursor.execute("""
            INSERT INTO login_attempts (username, success, ip_address)
            VALUES (?, ?, ?)
        """, (username, success, ip_address))
        conn.commit()
        conn.close()
        
        if success:
            # Generar JWT token
            token = self._generate_token(user_id, username_db, role)
            
            logger.info(f"Login exitoso: {username} desde {ip_address}")
            
            return {
                'token': token,
                'username': username_db,
                'role': role
            }
        else:
            logger.warning(f"Login fallido: {username} desde {ip_address}")
            return None
    
    def _generate_token(self, user_id: int, username: str, role: str) -> str:
        """
        Genera un JWT token con expiración.
        
        SEGURIDAD:
        - Token expira en 24 horas
        - Incluye timestamp de emisión
        - Firmado con secret_key
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verifica un JWT token y devuelve los datos del usuario.
        
        Args:
            token: JWT token a verificar
        
        Returns:
            Dict con datos del usuario si válido, None si inválido/expirado
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token inválido")
            return None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        SEGURIDAD:
        - Requiere contraseña antigua correcta
        - Nueva contraseña debe tener mínimo 8 caracteres
        - Hashea la nueva contraseña
        """
        # Validar nueva contraseña
        if not new_password or len(new_password) < 8:
            logger.warning(f"Intento de cambio a password débil: {username}")
            return False
        
        # Verificar contraseña antigua
        if not self.authenticate(username, old_password):
            logger.warning(f"Intento de cambio de password con contraseña incorrecta: {username}")
            return False
        
        # Hashear nueva contraseña
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET password_hash = ?
            WHERE username = ?
        """, (new_password_hash, username))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Contraseña cambiada: {username}")
        return True
    
    def get_login_history(self, username: str = None, limit: int = 100) -> list:
        """
        Obtiene el historial de intentos de login (auditoría).
        
        Args:
            username: Filtrar por usuario (None = todos)
            limit: Número máximo de registros
        
        Returns:
            Lista de intentos de login
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if username:
            cursor.execute("""
                SELECT username, success, ip_address, timestamp
                FROM login_attempts
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (username, limit))
        else:
            cursor.execute("""
                SELECT username, success, ip_address, timestamp
                FROM login_attempts
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results


# =============================================================================
# FUNCIÓN DE INICIALIZACIÓN
# =============================================================================

def init_default_users():
    """
    Crea usuarios por defecto si no existen.
    
    PRODUCCIÓN:
    - Cambiar estas contraseñas inmediatamente
    - Crear usuarios desde CLI o dashboard
    - Eliminar esta función después de primer uso
    """
    import os
    
    secret_key = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")
    manager = UserManager(secret_key=secret_key)
    
    # Usuario admin por defecto
    manager.create_user(
        username="admin",
        password=os.getenv("ADMIN_PASSWORD", "admin123"),  # CAMBIAR EN .env
        email="admin@empresa.com",
        role="admin"
    )
    
    # Usuario demo
    manager.create_user(
        username="demo",
        password="demo123",
        email="demo@empresa.com",
        role="user"
    )
    
    logger.info("Usuarios por defecto creados")


if __name__ == "__main__":
    # Test básico
    init_default_users()
    
    manager = UserManager()
    
    # Test login
    result = manager.authenticate("admin", "admin123", "127.0.0.1")
    if result:
        print(f"✅ Login exitoso: {result['username']}")
        print(f"Token: {result['token'][:50]}...")
        
        # Verificar token
        payload = manager.verify_token(result['token'])
        print(f"✅ Token válido: {payload['username']}")
    else:
        print("❌ Login fallido")
