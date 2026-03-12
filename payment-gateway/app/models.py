"""
SQLAlchemy модели для Payment Gateway Service.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Numeric, Boolean, Text, ForeignKey, JSON, TIMESTAMP, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Payment(Base):
    """Модель платежа."""
    __tablename__ = "payments"
    
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)  
    payment_type = Column(String(20), nullable=False)  # 'individual' или 'legal_entity'
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="RUB")
    status = Column(String(20), nullable=False, default="pending")  # 'pending', 'processing', 'completed', 'failed'
    provider = Column(String(50), nullable=True)  # 'robokassa', 'yookassa', 'paysto'
    provider_payment_id = Column(String(255), nullable=True, index=True)  
    client_type = Column(String(20), nullable=False)  # 'individual' или 'legal_entity'
    amount = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False)  
    status = Column(String(20), default="created")  # 'created', 'sent', 'paid'
    

    __tablename__ = "invoices"
    
    invoice_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey("payments.payment_id"), nullable=True)
    receipt_id = Column(Integer, ForeignKey("self_employed_receipts.receipt_id"), nullable=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    inn = Column(String(12), nullable=True)
    kpp = Column(String(9), nullable=True)
    legal_address = Column(Text, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    pdf_path = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())
    status = Column(String(20), default="draft")  # 'draft', 'sent', 'paid'
    

    __tablename__ = "acts"
    
    act_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey("payments.payment_id"), nullable=True)
    receipt_id = Column(Integer, ForeignKey("self_employed_receipts.receipt_id"), nullable=True)
    act_number = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    inn = Column(String(12), nullable=True)
    kpp = Column(String(9), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    pdf_path = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())
    status = Column(String(20), default="draft")  # 'draft', 'sent', 'signed'
    

    __tablename__ = "income_tracking"
    
    tracking_id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False, unique=True)
    total_income = Column(Numeric(12, 2), default=0)
    income_from_individuals = Column(Numeric(12, 2), default=0)
    income_from_legal_entities = Column(Numeric(12, 2), default=0)
    tax_paid = Column(Numeric(12, 2), default=0)
    limit_exceeded = Column(Boolean, default=False)  
    payer_type = Column(String(20), nullable=False)  # 'individual' или 'legal_entity'
    telegram_user_id = Column(BigInteger, nullable=False, index=True)  
    payment_provider = Column(String(50), nullable=True)  # 'selfwork', 'robokassa', 'yookassa', 'paysto'
    provider_payment_id = Column(String(255), nullable=True, index=True)  
    payment_status = Column(String(20), nullable=False, default="pending")  # 'pending', 'processing', 'completed', 'failed', 'cancelled'
    payment_date = Column(TIMESTAMP, nullable=True)  
    user_type = Column(String(20), nullable=False)  # 'individual' или 'legal_entity'
    

    company_name = Column(String(500), nullable=True)  