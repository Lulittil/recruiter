"""
SQLAlchemy модели для менеджерской панели.
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class ManagerSettings(Base):
    """Настройки менеджера для календаря."""
    __tablename__ = "manager_calendar_settings"
    
    settings_id = Column(Integer, primary_key=True, autoincrement=True)
    manager_id = Column(BigInteger, nullable=False, unique=True, index=True)  