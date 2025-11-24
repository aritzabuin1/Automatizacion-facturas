# =============================================================================
# GENERADOR DE CONTRASEÑAS HASHEADAS
# =============================================================================
# Este script genera hashes bcrypt para las contraseñas del dashboard.
#
# ¿POR QUÉ HASHEAR CONTRASEÑAS?
# NUNCA guardes contraseñas en texto plano. Si alguien accede al código,
# no podrá ver las contraseñas reales.
#
# USO:
# python generate_passwords.py
# =============================================================================

import streamlit_authenticator as stauth

# Contraseñas en texto plano (SOLO para generar hashes, luego borrar)
passwords_to_hash = ['admin123', 'demo123', 'cliente123']

# Generar hashes
hashed_passwords = stauth.Hasher(passwords_to_hash).generate()

print("=" * 60)
print("CONTRASEÑAS HASHEADAS (Copiar a dashboard.py)")
print("=" * 60)

users = ['admin', 'usuario', 'cliente']
for user, hashed in zip(users, hashed_passwords):
    print(f"\n'{user}': {{")
    print(f"    'name': '{user.capitalize()}',")
    print(f"    'password': '{hashed}',")
    print("},")

print("\n" + "=" * 60)
print("IMPORTANTE: Borra este script después de copiar los hashes")
print("=" * 60)
