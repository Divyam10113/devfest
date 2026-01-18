try:
    import argon2
    print(f"argon2 imported: {argon2.__file__}")
except ImportError as e:
    print(f"argon2 import failed: {e}")

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    h = pwd_context.hash("test")
    print(f"Hash success: {h}")
except Exception as e:
    print(f"Hash failed: {e}")
