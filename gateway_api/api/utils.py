from passlib.context import CryptContext
import hashlib
import hashlib
import logging
from datetime import datetime

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
logger = logging.getLogger(__name__)

# ====================== HASH UTILS FOR PASSWORD =========================


# ====================== HASH UTILS FOR PASSWORD =========================

def hash(password: str):
    return pwd_context.hash(password)

# compare the raw password with the database's hashed password
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_value(value: str) -> str:
    """
    Hashes a given string value using bcrypt.
    """
    return pwd_context.hash(value)




