"""
База данных для админов с использованием PostgreSQL через SQLAlchemy.
"""
from datetime import datetime
from typing import Optional
from passlib.context import CryptContext
import secrets
from sqlalchemy import select, String, Text, Boolean, DateTime, func, BigInteger, text, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from .config import settings
import bcrypt



        return f"<Admin(username='{self.username}', email='{self.email}')>"



    if engine is None:
        init_database()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        

            async with engine.begin() as conn:

                try:
                    check_query = text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'admins' AND column_name = 'owner_id'
                    """)
                    result = await conn.execute(check_query)
                    column_exists = result.fetchone() is not None
                    
                    if not column_exists:
                        await conn.execute(text("ALTER TABLE admins ADD COLUMN owner_id BIGINT"))
                        await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_admins_owner_id_unique ON admins(owner_id) WHERE owner_id IS NOT NULL"))
                        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_admins_owner_id ON admins(owner_id)"))
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info("Added owner_id column to admins table")
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    error_str = str(e).lower()
                    if "already exists" not in error_str and "duplicate" not in error_str and "column" not in error_str:
                        logger.warning(f"Could not add owner_id column: {e}")
                    else:
                        logger.debug(f"Column owner_id already exists or error: {e}")
                

                try:
                    check_query = text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'admins' AND column_name = 'is_global_admin'
                    """)
                    result = await conn.execute(check_query)
                    column_exists = result.fetchone() is not None
                    
                    if not column_exists:
                        await conn.execute(text("ALTER TABLE admins ADD COLUMN is_global_admin BOOLEAN DEFAULT FALSE"))
                        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_admins_is_global_admin ON admins(is_global_admin)"))
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info("Added is_global_admin column to admins table")
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    error_str = str(e).lower()
                    if "already exists" not in error_str and "duplicate" not in error_str and "column" not in error_str:
                        logger.warning(f"Could not add is_global_admin column: {e}")
                    else:
                        logger.debug(f"Column is_global_admin already exists or error: {e}")
                

    if SessionLocal is None:
        init_database()
    

    existing_username = await get_admin_by_username(username)
    if existing_username:
        raise ValueError("Username already exists")
    
    existing_email = await get_admin_by_email(email)
    if existing_email:
        raise ValueError("Email already exists")
    


    password_encoded = password.encode('utf-8')
    if len(password_encoded) > 72:

        max_chars = min(72, len(password))
        while max_chars > 0:
            truncated = password[:max_chars]
            if len(truncated.encode('utf-8')) <= 72:
                password = truncated
                break
            max_chars -= 1
        else:

            password = password_encoded[:72].decode('utf-8', errors='replace')
    

    final_encoded = password.encode('utf-8')
    if len(final_encoded) > 72:
        password = final_encoded[:72].decode('utf-8', errors='replace')

        final_encoded = password.encode('utf-8')
        if len(final_encoded) > 72:

            password = final_encoded[:72].decode('utf-8', errors='replace')
    

    final_check = password.encode('utf-8')
    if len(final_check) > 72:

        password = final_check[:72].decode('utf-8', errors='replace')
    

    try:

        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error hashing password (length: {len(password.encode('utf-8'))} bytes): {e}")
        raise ValueError(f"Failed to hash password: {str(e)}")
    admin_id = secrets.token_urlsafe(16)


    import hashlib
    owner_id_hash = int(hashlib.sha256(admin_id.encode()).hexdigest()[:15], 16) % (10**15)  
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

    try:
        existing = await get_admin_by_username("admin")
        if existing:

            if not existing.owner_id:
                async with SessionLocal() as session:
                    result = await session.execute(
                        select(AdminModel).where(AdminModel.admin_id == existing.admin_id)
                    )
                    db_admin = result.scalar_one_or_none()
                    if db_admin:
                        db_admin.owner_id = 1
                        await session.commit()
            return
        

        admin_id = secrets.token_urlsafe(16)
        password_bytes = "admin123".encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        async with SessionLocal() as session:
            db_admin = AdminModel(
                admin_id=admin_id,
                username="admin",
                email="admin@recruiter.local",
                hashed_password=hashed_password,
                is_active=True,
                owner_id=1  