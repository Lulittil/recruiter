"""
База данных для админов с использованием PostgreSQL через SQLAlchemy.
"""
from datetime import datetime
from typing import Optional
from passlib.context import CryptContext
import secrets
from sqlalchemy import select, Column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import String, Text, Boolean, DateTime, func

from .config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    __tablename__ = "admins"

    admin_id = Column(String(64), primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Admin(username='{self.username}', email='{self.email}')>"



    if SessionLocal is None:
        init_database()
    

    existing_username = await get_admin_by_username(username)
    if existing_username:
        raise ValueError("Username already exists")
    
    existing_email = await get_admin_by_email(email)
    if existing_email:
        raise ValueError("Email already exists")
    

    try:
        existing = await get_admin_by_username("admin")
        if existing:
            return
        
        await create_admin(
            username="admin",
            email="admin@recruiter.local",
            password="admin123"
        )
    except ValueError:

        pass
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not create default admin: {e}")

