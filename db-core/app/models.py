from datetime import datetime
from sqlalchemy import String, Text, Integer, BigInteger, Boolean, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    profile_data: Mapped[str] = mapped_column(Text, default="{}")


class Vacancy(Base):
    __tablename__ = "vacancies"

    vacancy_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    bot_token: Mapped[str] = mapped_column(Text, nullable=False)
    open_api_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    vacancy: Mapped[str | None] = mapped_column(Text, nullable=True)
    gpt_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    need_buttons_approve: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_chatgpt: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deepseek_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    count_report_offers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    distribution_strategy: Mapped[str] = mapped_column(Text, nullable=False, default="manual")
    max_candidates_per_manager: Mapped[int | None] = mapped_column(Integer, nullable=True)
    owner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)

    applicants: Mapped[list["Applicant"]] = relationship("Applicant", back_populates="vacancy")
    vacancy_managers: Mapped[list["VacancyManager"]] = relationship("VacancyManager", back_populates="vacancy", cascade="all, delete-orphan")


class Applicant(Base):
    __tablename__ = "applicant"

    applicant_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    vacancy_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vacancies.vacancy_id", ondelete="SET NULL"), nullable=True)
    date_consent: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_sended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resume: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_screen_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("steps_screen.id", ondelete="SET NULL"), nullable=True)
    assigned_manager_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vacancy_managers.vacancy_manager_id", ondelete="SET NULL"), nullable=True)
    final_manager_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vacancy_managers.vacancy_manager_id", ondelete="SET NULL"), nullable=True)

    vacancy: Mapped["Vacancy | None"] = relationship("Vacancy", back_populates="applicants")
    step_screen: Mapped["StepScreen | None"] = relationship("StepScreen", back_populates="applicants")
    assigned_manager: Mapped["VacancyManager | None"] = relationship("VacancyManager", foreign_keys=[assigned_manager_id], back_populates="assigned_applicants")
    final_manager: Mapped["VacancyManager | None"] = relationship("VacancyManager", foreign_keys=[final_manager_id], back_populates="final_applicants")


class VacancyManager(Base):
    """
    Junction table for many-to-many relationship between vacancies and managers.
    Optimized with indexes for fast lookups.
    """
    __tablename__ = "vacancy_managers"
    
    vacancy_manager_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vacancy_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("vacancies.vacancy_id", ondelete="CASCADE"), 
        nullable=False,
        index=True  # Index for fast lookups by vacancy_id
    )
    manager_chat_id: Mapped[int] = mapped_column(
        BigInteger, 
        nullable=False,
        index=True  # Index for fast lookups by manager_chat_id
    )
    email: Mapped[str | None] = mapped_column(
        String(255), 
        nullable=True,
        index=True  # Index for fast lookups by email
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    hashed_password: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Unique constraint to prevent duplicate manager-vacancy pairs
    __table_args__ = (
        UniqueConstraint('vacancy_id', 'manager_chat_id', name='uq_vacancy_manager'),
        # Composite index for fast lookups by both fields
        Index('idx_vacancy_manager', 'vacancy_id', 'manager_chat_id'),
    )
    
    # Relationship to Vacancy (optional, for convenience)
    vacancy: Mapped["Vacancy"] = relationship("Vacancy", back_populates="vacancy_managers")

    __tablename__ = "admins"

    admin_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    owner_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)