"""
Простая in-memory база данных для хранения админов.
В продакшене стоит использовать реальную БД.
"""
from datetime import datetime
from typing import Optional, Dict
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Admin:
    """Модель администратора."""
    def __init__(self, username: str, email: str, hashed_password: str, admin_id: Optional[str] = None):
        self.admin_id = admin_id or secrets.token_urlsafe(16)
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.created_at = datetime.utcnow()
        self.is_active = True




    if get_admin_by_username(username):
        raise ValueError("Username already exists")
    if get_admin_by_email(email):
        raise ValueError("Email already exists")
    

    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    try:
        hashed_password = pwd_context.hash(password)
    except Exception as e:

        if "72 bytes" in str(e):
            password = password[:20]  
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password = password_bytes[:72].decode('utf-8', errors='ignore')
            hashed_password = pwd_context.hash(password)
        else:
            raise
    
    admin = Admin(username=username, email=email, hashed_password=hashed_password)
    _admins_db[admin.admin_id] = admin
    return admin


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль."""
    return pwd_context.verify(plain_password, hashed_password)



    if not _admins_db:
        try:

            import time
            time.sleep(0.1)
            default_admin = create_admin(
                username="admin",
                email="admin@recruiter.local",
                password="admin123"
            )
            print(f"Created default admin: username=admin, password=admin123")
        except Exception as e:

            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not create default admin: {e}")





