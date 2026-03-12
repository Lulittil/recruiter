import json
import logging

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from datetime import datetime, timezone
import bcrypt

from .database import Base, engine, get_session

def hash_password(password: str) -> str:
    """Хешировать пароль с помощью bcrypt."""

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
from .models import UserProfile, Vacancy, Applicant, VacancyManager, StepScreen, Admin
from .distribution_service import (
    assign_manager_to_applicant,
    get_available_managers,
    calculate_manager_load,
    balance_workload
)
from .schemas import (
    UserProfileCreate,
    UserProfileDTO,
    VacancyCreate,
    VacancyDTO,
    ApplicantCreate,
    ApplicantDTO,
    ApplicantUpdate,
    TokenResponse,
    VacancyManagerCreate,
    VacancyManagerDTO,
    VacancyManagersBulkCreate,
    VacancyManagersListResponse,
    StepScreenDTO,
    ResumeUpdate,
    AdminCreate,
    AdminDTO,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="db-core")


@app.on_event("startup")
async def startup() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")
        

        try:
            async with engine.begin() as conn:

                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'vacancy_managers' AND column_name = 'email'
                """)
                result = await conn.execute(check_query)
                column_exists = result.fetchone() is not None
                
                if not column_exists:
                    logger.info("Adding email column to vacancy_managers table")
                    await conn.execute(text("ALTER TABLE vacancy_managers ADD COLUMN email VARCHAR(255)"))
                    await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_vacancy_managers_email ON vacancy_managers(email)"))
                    logger.info("Successfully added email column to vacancy_managers table")
                else:
                    logger.debug("Email column already exists in vacancy_managers table")
        except Exception as e:
            error_str = str(e).lower()
            if "already exists" not in error_str and "duplicate" not in error_str:
                logger.warning(f"Could not add email column to vacancy_managers: {e}")
            else:
                logger.debug(f"Email column already exists or minor error: {e}")
        

        try:
            async with engine.begin() as conn:

                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'vacancy_managers' AND column_name = 'hashed_password'
                """)
                result = await conn.execute(check_query)
                column_exists = result.fetchone() is not None
                
                if not column_exists:
                    logger.info("Adding hashed_password column to vacancy_managers table")
                    await conn.execute(text("ALTER TABLE vacancy_managers ADD COLUMN hashed_password TEXT"))
                    logger.info("Successfully added hashed_password column to vacancy_managers table")
                else:
                    logger.debug("hashed_password column already exists in vacancy_managers table")
        except Exception as e:
            error_str = str(e).lower()
            if "already exists" not in error_str and "duplicate" not in error_str:
                logger.warning(f"Could not add hashed_password column to vacancy_managers: {e}")
            else:
                logger.debug(f"hashed_password column already exists or minor error: {e}")
        

        try:
            async with engine.begin() as conn:

                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'vacancy_managers' AND column_name = 'full_name'
                """)
                result = await conn.execute(check_query)
                column_exists = result.fetchone() is not None
                
                if not column_exists:
                    logger.info("Adding full_name column to vacancy_managers table")
                    await conn.execute(text("ALTER TABLE vacancy_managers ADD COLUMN full_name VARCHAR(255)"))
                    logger.info("Successfully added full_name column to vacancy_managers table")
                else:
                    logger.debug("full_name column already exists in vacancy_managers table")
        except Exception as e:
            error_str = str(e).lower()
            if "already exists" not in error_str and "duplicate" not in error_str:
                logger.warning(f"Could not add full_name column to vacancy_managers: {e}")
            else:
                logger.debug(f"full_name column already exists or minor error: {e}")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown() -> None:
    await engine.dispose()


@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/profiles/{user_id}", response_model=UserProfileDTO)
async def get_profile(user_id: str, session: AsyncSession = Depends(get_session)) -> UserProfileDTO:
    result = await session.execute(select(UserProfile).where(UserProfile.id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    data = json.loads(profile.profile_data)
    return UserProfileDTO(id=profile.id, full_name=profile.full_name, profile_data=data)


@app.put("/profiles/{user_id}", response_model=UserProfileDTO, status_code=status.HTTP_201_CREATED)
async def upsert_profile(
    user_id: str, payload: UserProfileCreate, session: AsyncSession = Depends(get_session)
) -> UserProfileDTO:
    if payload.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID in path and payload must match",
        )
    profile = await session.get(UserProfile, user_id)
    if profile is None:
        profile = UserProfile(
            id=user_id,
            full_name=payload.full_name,
            profile_data=json.dumps(payload.profile_data),
        )
        session.add(profile)
    else:
        profile.full_name = payload.full_name
        profile.profile_data = json.dumps(payload.profile_data)
    await session.commit()
    return UserProfileDTO(id=profile.id, full_name=profile.full_name, profile_data=payload.profile_data)


@app.delete("/profiles/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(user_id: str, session: AsyncSession = Depends(get_session)) -> None:
    await session.execute(delete(UserProfile).where(UserProfile.id == user_id))
    await session.commit()


# Vacancy endpoints
@app.post("/vacancies", response_model=VacancyDTO, status_code=status.HTTP_201_CREATED)
async def upsert_vacancy(
    vacancy: VacancyCreate, session: AsyncSession = Depends(get_session)
) -> VacancyDTO:
    """Create or update a vacancy."""
    try:
        if vacancy.vacancy_id:
            # Update existing vacancy
            db_vacancy = await session.get(Vacancy, vacancy.vacancy_id)
            if db_vacancy:
                for key, value in vacancy.model_dump(exclude={"vacancy_id"}).items():
                    setattr(db_vacancy, key, value)
            else:
                db_vacancy = Vacancy(**vacancy.model_dump())
                session.add(db_vacancy)
        else:
            # Create new vacancy
            vacancy_dict = vacancy.model_dump(exclude={"vacancy_id"})
            logger.info(f"Creating vacancy with data: {vacancy_dict}")
            db_vacancy = Vacancy(**vacancy_dict)
            session.add(db_vacancy)
        
        await session.commit()
        await session.refresh(db_vacancy)
        return VacancyDTO.model_validate(db_vacancy)
    except Exception as e:
        logger.error(f"Error creating/updating vacancy: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating vacancy: {str(e)}"
        )


@app.get("/vacancies/active", response_model=list[VacancyDTO])
async def get_active_vacancies(
    owner_id: int | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_session)
) -> list[VacancyDTO]:
    """Get all active vacancies, optionally filtered by owner_id and search query."""
    try:
        from sqlalchemy import or_
        query = select(Vacancy).where(Vacancy.is_closed == False)
        
        # Filter by owner_id if provided
        if owner_id is not None:
            query = query.where(Vacancy.owner_id == owner_id)
        
        # Search by company_name or vacancy text if search query provided
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Vacancy.company_name.ilike(search_pattern),
                    Vacancy.vacancy.ilike(search_pattern)
                )
            )
        
        query = query.order_by(Vacancy.vacancy_id)
        
        result = await session.execute(query)
        vacancies = result.scalars().all()
        logger.info(f"Found {len(vacancies)} active vacancies" + (f" for owner_id={owner_id}" if owner_id else "") + (f" with search='{search}'" if search else ""))
        return [VacancyDTO.model_validate(vacancy) for vacancy in vacancies]
    except Exception as e:
        logger.error(f"Error getting active vacancies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active vacancies: {str(e)}"
        )


@app.get("/vacancies/active/first", response_model=VacancyDTO)
async def get_active_vacancy(session: AsyncSession = Depends(get_session)) -> VacancyDTO:
    """Get the first active vacancy."""
    result = await session.execute(
        select(Vacancy).where(Vacancy.is_closed == False).order_by(Vacancy.vacancy_id).limit(1)
    )
    vacancy = result.scalar_one_or_none()
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active vacancy found")
    return VacancyDTO.model_validate(vacancy)


@app.get("/vacancies/{vacancy_id}", response_model=VacancyDTO)
async def get_vacancy_by_id(
    vacancy_id: int,
    owner_id: int | None = None,
    session: AsyncSession = Depends(get_session)
) -> VacancyDTO:
    """Get vacancy by ID, optionally checking ownership."""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    
    # If owner_id is provided, check ownership
    if owner_id is not None and vacancy.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this vacancy"
        )
    
    return VacancyDTO.model_validate(vacancy)


@app.get("/vacancies/active/bot-token", response_model=TokenResponse)
async def get_bot_token(session: AsyncSession = Depends(get_session)) -> TokenResponse:
    """Get bot token from active vacancy."""
    result = await session.execute(
        select(Vacancy).where(Vacancy.is_closed == False).order_by(Vacancy.vacancy_id).limit(1)
    )
    vacancy = result.scalar_one_or_none()
    if not vacancy or not vacancy.bot_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active vacancy with bot_token found",
        )
    return TokenResponse(token=vacancy.bot_token)


@app.get("/vacancies/active/open-api-token", response_model=TokenResponse)
async def get_open_api_token(session: AsyncSession = Depends(get_session)) -> TokenResponse:
    """Get OpenAI API token from active vacancy."""
    result = await session.execute(
        select(Vacancy).where(Vacancy.is_closed == False).order_by(Vacancy.vacancy_id).limit(1)
    )
    vacancy = result.scalar_one_or_none()
    if not vacancy or not vacancy.open_api_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active vacancy with open_api_token found",
        )
    return TokenResponse(token=vacancy.open_api_token)


@app.get("/vacancies/{vacancy_id}/open-api-token", response_model=TokenResponse)
async def get_open_api_token_by_vacancy_id(
    vacancy_id: int, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Get OpenAI API token by vacancy ID."""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy or not vacancy.open_api_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="open_api_token not found for vacancy_id",
        )
    return TokenResponse(token=vacancy.open_api_token)


@app.get("/vacancies/active/deepseek-token", response_model=TokenResponse)
async def get_deepseek_token(session: AsyncSession = Depends(get_session)) -> TokenResponse:
    """Get DeepSeek token from active vacancy."""
    result = await session.execute(
        select(Vacancy).where(Vacancy.is_closed == False).order_by(Vacancy.vacancy_id).limit(1)
    )
    vacancy = result.scalar_one_or_none()
    if not vacancy or not vacancy.deepseek_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active vacancy with deepseek_token found",
        )
    return TokenResponse(token=vacancy.deepseek_token)


@app.get("/vacancies/{vacancy_id}/deepseek-token", response_model=TokenResponse)
async def get_deepseek_token_by_vacancy_id(
    vacancy_id: int, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Get DeepSeek token by vacancy ID."""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy or not vacancy.deepseek_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="deepseek_token not found for vacancy_id",
        )
    return TokenResponse(token=vacancy.deepseek_token)


@app.post("/vacancies/{vacancy_id}/decrement-offer-count", response_model=VacancyDTO)
async def decrement_offer_count(
    vacancy_id: int, session: AsyncSession = Depends(get_session)
) -> VacancyDTO:
    """Decrement count_report_offers for a vacancy."""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found"
        )
    
    # Decrement count, but don't go below 0
    if vacancy.count_report_offers > 0:
        vacancy.count_report_offers -= 1
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No offer analysis attempts available"
        )
    
    await session.commit()
    await session.refresh(vacancy)
    return VacancyDTO.model_validate(vacancy)


# Applicant endpoints
@app.post("/applicants", response_model=ApplicantDTO, status_code=status.HTTP_201_CREATED)
async def upsert_applicant(
    applicant: ApplicantCreate, session: AsyncSession = Depends(get_session)
) -> ApplicantDTO:
    """Create or update an applicant."""
    # Check if applicant exists
    # Handle NULL vacancy_id properly in WHERE clause
    if applicant.vacancy_id is not None:
        result = await session.execute(
            select(Applicant).where(
                Applicant.telegram_id == applicant.telegram_id,
                Applicant.vacancy_id == applicant.vacancy_id,
            )
        )
    else:
        result = await session.execute(
            select(Applicant).where(
                Applicant.telegram_id == applicant.telegram_id,
                Applicant.vacancy_id.is_(None),
            )
        )
    db_applicant = result.scalar_one_or_none()
    
    if db_applicant:
        # Update existing applicant
        if applicant.full_name is not None:
            db_applicant.full_name = applicant.full_name
        if applicant.phone_number is not None:
            db_applicant.phone_number = applicant.phone_number
        if applicant.vacancy_id is not None:
            db_applicant.vacancy_id = applicant.vacancy_id
        if applicant.date_consent is not None:
            db_applicant.date_consent = applicant.date_consent
        if applicant.is_sended is not None:
            db_applicant.is_sended = applicant.is_sended
        if applicant.resume is not None:
            db_applicant.resume = applicant.resume
        if applicant.step_screen_id is not None:
            db_applicant.step_screen_id = applicant.step_screen_id
        if applicant.assigned_manager_id is not None:
            db_applicant.assigned_manager_id = applicant.assigned_manager_id
        if applicant.final_manager_id is not None:
            db_applicant.final_manager_id = applicant.final_manager_id
        
        # Auto-assign manager if vacancy_id is set, no manager is manually assigned, and applicant doesn't have a manager yet
        if db_applicant.vacancy_id and not applicant.assigned_manager_id and not db_applicant.assigned_manager_id:
            vacancy = await session.get(Vacancy, db_applicant.vacancy_id)
            if vacancy:
                assigned_manager_id = await assign_manager_to_applicant(
                    session,
                    db_applicant.vacancy_id,
                    db_applicant.applicant_id,
                    vacancy.distribution_strategy,
                    vacancy.max_candidates_per_manager
                )
                if assigned_manager_id:
                    db_applicant.assigned_manager_id = assigned_manager_id
                    logger.info(
                        f"Auto-assigned manager {assigned_manager_id} to existing applicant {db_applicant.applicant_id} "
                        f"using strategy '{vacancy.distribution_strategy}'"
                    )
    else:
        # Create new applicant
        # Set step_screen_id to 0 if not provided
        applicant_data = applicant.model_dump()
        if applicant_data.get("step_screen_id") is None:
            applicant_data["step_screen_id"] = 0
        
        db_applicant = Applicant(**applicant_data)
        session.add(db_applicant)
        await session.flush()  # Flush to get applicant_id
        
        # Auto-assign manager if vacancy_id is set and no manager is manually assigned
        if db_applicant.vacancy_id and not applicant.assigned_manager_id:
            vacancy = await session.get(Vacancy, db_applicant.vacancy_id)
            if vacancy:
                assigned_manager_id = await assign_manager_to_applicant(
                    session,
                    db_applicant.vacancy_id,
                    db_applicant.applicant_id,
                    vacancy.distribution_strategy,
                    vacancy.max_candidates_per_manager
                )
                if assigned_manager_id:
                    db_applicant.assigned_manager_id = assigned_manager_id
                    logger.info(
                        f"Auto-assigned manager {assigned_manager_id} to applicant {db_applicant.applicant_id} "
                        f"using strategy '{vacancy.distribution_strategy}'"
                    )
    
    await session.commit()
    await session.refresh(db_applicant)
    return ApplicantDTO.model_validate(db_applicant)


@app.get("/applicants/telegram/{telegram_id}", response_model=ApplicantDTO)
async def get_applicant_by_telegram_id(
    telegram_id: int, session: AsyncSession = Depends(get_session)
) -> ApplicantDTO:
    """Get applicant by telegram_id."""
    result = await session.execute(
        select(Applicant).where(Applicant.telegram_id == telegram_id)
    )
    applicant = result.scalar_one_or_none()
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    return ApplicantDTO.model_validate(applicant)


@app.get("/applicants/telegram/{telegram_id}/vacancy/{vacancy_id}", response_model=ApplicantDTO)
async def get_applicant_by_telegram_and_vacancy(
    telegram_id: int, vacancy_id: int, session: AsyncSession = Depends(get_session)
) -> ApplicantDTO:
    """Get applicant by telegram_id and vacancy_id."""
    result = await session.execute(
        select(Applicant).where(
            Applicant.telegram_id == telegram_id, Applicant.vacancy_id == vacancy_id
        )
    )
    applicant = result.scalar_one_or_none()
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    return ApplicantDTO.model_validate(applicant)


@app.patch("/applicants/telegram/{telegram_id}", response_model=ApplicantDTO)
async def update_applicant(
    telegram_id: int,
    applicant_update: ApplicantUpdate,
    vacancy_id: int | None = None,
    session: AsyncSession = Depends(get_session)
) -> ApplicantDTO:
    """Update applicant fields."""
    # Find applicant
    if vacancy_id is not None:
        result = await session.execute(
            select(Applicant).where(
                Applicant.telegram_id == telegram_id,
                Applicant.vacancy_id == vacancy_id
            )
        )
    else:
        result = await session.execute(
            select(Applicant).where(Applicant.telegram_id == telegram_id)
        )
    applicant = result.scalar_one_or_none()
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )
    
    # Update fields
    update_data = applicant_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(applicant, key, value)
    
    await session.commit()
    await session.refresh(applicant)
    return ApplicantDTO.model_validate(applicant)


@app.post("/applicants/{applicant_id}/assign-manager", response_model=ApplicantDTO)
async def assign_manager_to_applicant_endpoint(
    applicant_id: int,
    session: AsyncSession = Depends(get_session)
) -> ApplicantDTO:
    """Automatically assign manager to applicant based on vacancy distribution strategy."""
    applicant = await session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )
    
    if not applicant.vacancy_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Applicant has no vacancy_id"
        )
    
    # Get vacancy to check distribution strategy
    vacancy = await session.get(Vacancy, applicant.vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    # Assign manager using distribution service
    assigned_manager_id = await assign_manager_to_applicant(
        session,
        applicant.vacancy_id,
        applicant_id,
        vacancy.distribution_strategy,
        vacancy.max_candidates_per_manager
    )
    
    if assigned_manager_id:
        applicant.assigned_manager_id = assigned_manager_id
        await session.commit()
        await session.refresh(applicant)
        logger.info(f"Assigned manager {assigned_manager_id} to applicant {applicant_id}")
    else:
        logger.info(f"Could not assign manager to applicant {applicant_id} (strategy: {vacancy.distribution_strategy})")
    
    return ApplicantDTO.model_validate(applicant)


@app.put("/applicants/{applicant_id}/assign-manager/{vacancy_manager_id}", response_model=ApplicantDTO)
async def manually_assign_manager(
    applicant_id: int,
    vacancy_manager_id: int,
    session: AsyncSession = Depends(get_session)
) -> ApplicantDTO:
    """Manually assign specific manager to applicant."""
    applicant = await session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )
    
    # Verify manager exists
    manager = await session.get(VacancyManager, vacancy_manager_id)
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )
    
    # Verify manager is assigned to the same vacancy
    if applicant.vacancy_id and manager.vacancy_id != applicant.vacancy_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manager is not assigned to applicant's vacancy"
        )
    
    applicant.assigned_manager_id = vacancy_manager_id
    await session.commit()
    await session.refresh(applicant)
    logger.info(f"Manually assigned manager {vacancy_manager_id} to applicant {applicant_id}")
    
    return ApplicantDTO.model_validate(applicant)


@app.put("/vacancies/{vacancy_id}/distribution-strategy", response_model=VacancyDTO)
async def set_distribution_strategy(
    vacancy_id: int,
    strategy: str,
    session: AsyncSession = Depends(get_session)
) -> VacancyDTO:
    """Set distribution strategy for a vacancy."""
    from .schemas import DistributionStrategy
    
    # Validate strategy
    valid_strategies = [s.value for s in DistributionStrategy]
    if strategy not in valid_strategies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid strategy. Must be one of: {', '.join(valid_strategies)}"
        )
    
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    vacancy.distribution_strategy = strategy
    await session.commit()
    await session.refresh(vacancy)
    logger.info(f"Set distribution strategy '{strategy}' for vacancy {vacancy_id}")
    
    return VacancyDTO.model_validate(vacancy)


@app.delete("/applicants/telegram/{telegram_id}", status_code=status.HTTP_200_OK)
async def delete_applicant_by_telegram_id(
    telegram_id: int, 
    vacancy_id: int | None = None,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Delete applicant records by telegram_id. If vacancy_id is provided, delete only for that vacancy."""
    if vacancy_id is not None:
        result = await session.execute(
            delete(Applicant).where(
                Applicant.telegram_id == telegram_id,
                Applicant.vacancy_id == vacancy_id
            )
        )
    else:
        result = await session.execute(delete(Applicant).where(Applicant.telegram_id == telegram_id))
    await session.commit()
    return {"deleted_count": result.rowcount}


@app.put("/applicants/telegram/{telegram_id}/resume", response_model=ApplicantDTO)
async def save_applicant_resume(
    telegram_id: int,
    resume_data: ResumeUpdate,
    session: AsyncSession = Depends(get_session)
) -> ApplicantDTO:
    """Save resume for an applicant."""
    # Find applicant by telegram_id and optionally vacancy_id
    if resume_data.vacancy_id is not None:
        result = await session.execute(
            select(Applicant).where(
                Applicant.telegram_id == telegram_id,
                Applicant.vacancy_id == resume_data.vacancy_id
            )
        )
    else:
        result = await session.execute(
            select(Applicant).where(Applicant.telegram_id == telegram_id)
        )
    applicant = result.scalar_one_or_none()
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )
    
    applicant.resume = resume_data.resume
    await session.commit()
    await session.refresh(applicant)
    return ApplicantDTO.model_validate(applicant)


@app.put("/applicants/telegram/{telegram_id}/step/{step_id}", response_model=ApplicantDTO)
async def set_applicant_step(
    telegram_id: int,
    step_id: int,
    vacancy_id: int | None = None,
    session: AsyncSession = Depends(get_session)
) -> ApplicantDTO:
    """Set step_screen_id for an applicant."""
    # Verify step exists
    step = await session.get(StepScreen, step_id)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step with id {step_id} not found"
        )
    

    # Find or create applicant
    if vacancy_id is not None:
        result = await session.execute(
            select(Applicant).where(
                Applicant.telegram_id == telegram_id,
                Applicant.vacancy_id == vacancy_id
            )
        )
    else:
        result = await session.execute(
            select(Applicant).where(
                Applicant.telegram_id == telegram_id,
                Applicant.vacancy_id.is_(None)
            )
        )
    applicant = result.scalar_one_or_none()
    
    if not applicant:
        # Create new applicant with consent
        applicant = Applicant(
            telegram_id=telegram_id,
            vacancy_id=vacancy_id,
            step_screen_id=0,
            date_consent=datetime.now(timezone.utc),
            is_sended=False
        )
        session.add(applicant)
    else:


    """
    if stage not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage must be 1 or 2"
        )
    
    step_id = 2 if stage == 1 else 4
    

    """
    if stage not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage must be 1 or 2"
        )
    
    step_id = 3 if stage == 1 else 5
    
    # Find applicant
    if vacancy_id is not None:
        result = await session.execute(
            select(Applicant).where(
                Applicant.telegram_id == telegram_id,
                Applicant.vacancy_id == vacancy_id
            )
        )
    else:
        result = await session.execute(
            select(Applicant).where(Applicant.telegram_id == telegram_id)
        )
    applicant = result.scalar_one_or_none()
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )
    
    applicant.step_screen_id = step_id
    await session.commit()
    await session.refresh(applicant)
    return ApplicantDTO.model_validate(applicant)


# StepScreen endpoints
@app.get("/steps-screen", response_model=list[StepScreenDTO])
async def get_all_steps(session: AsyncSession = Depends(get_session)) -> list[StepScreenDTO]:
    """Get all interview steps."""
    result = await session.execute(select(StepScreen).order_by(StepScreen.id))
    steps = result.scalars().all()
    return [StepScreenDTO.model_validate(step) for step in steps]


@app.get("/steps-screen/{step_id}", response_model=StepScreenDTO)
async def get_step_by_id(
    step_id: int, session: AsyncSession = Depends(get_session)
) -> StepScreenDTO:
    """Get step by ID."""
    step = await session.get(StepScreen, step_id)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step with id {step_id} not found"
        )
    return StepScreenDTO.model_validate(step)


@app.get("/vacancies/{vacancy_id}/distribution-stats")
async def get_distribution_stats(
    vacancy_id: int,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Get distribution statistics for a vacancy."""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    managers = await get_available_managers(session, vacancy_id)
    stats = []
    
    for manager in managers:
        load_info = await calculate_manager_load(
            session,
            manager.manager_chat_id,
            vacancy_id,
            vacancy.max_candidates_per_manager
        )
        stats.append({
            "vacancy_manager_id": manager.vacancy_manager_id,
            "manager_chat_id": manager.manager_chat_id,
            "active_count": load_info['active_count'],
            "is_available": load_info['is_available'],
            "max_candidates": load_info['max_candidates']
        })
    
    return {
        "vacancy_id": vacancy_id,
        "distribution_strategy": vacancy.distribution_strategy,
        "max_candidates_per_manager": vacancy.max_candidates_per_manager,
        "managers": stats
    }


@app.post("/vacancies/{vacancy_id}/balance-workload")
async def balance_vacancy_workload(
    vacancy_id: int,
    threshold: int = 3,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Balance workload between managers for a vacancy."""
    try:
        result = await balance_workload(session, vacancy_id, threshold)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/applicants", response_model=list[ApplicantDTO])
async def get_all_applicants(
    owner_id: int | None = None,
    session: AsyncSession = Depends(get_session)
) -> list[ApplicantDTO]:
    """Get list of all applicants, optionally filtered by owner_id of vacancies."""
    query = select(Applicant).join(Vacancy, Applicant.vacancy_id == Vacancy.vacancy_id)
    
    
                    f"Manager data: vacancy_id={getattr(manager, 'vacancy_id', 'N/A')}, "
                    f"manager_chat_id={getattr(manager, 'manager_chat_id', 'N/A')}",
                    exc_info=True
                )
                # Skip invalid manager records
                continue
        
        logger.info(f"Returning {len(manager_dtos)} valid managers for vacancy {vacancy_id}")
        return VacancyManagersListResponse(
            vacancy_id=vacancy_id,
            managers=manager_dtos
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error getting vacancy managers for vacancy {vacancy_id}: {e}",
            exc_info=True
        )
        # Return empty list instead of 500 error to allow system to continue working
        return VacancyManagersListResponse(
            vacancy_id=vacancy_id,
            managers=[]
        )


@app.get("/vacancy-managers/manager/{manager_chat_id}", response_model=list[VacancyManagerDTO])
async def get_vacancies_by_manager(
    manager_chat_id: int, session: AsyncSession = Depends(get_session)
) -> list[VacancyManagerDTO]:
    """Get all vacancies (companies) for a specific manager."""
    result = await session.execute(
        select(VacancyManager).where(
            VacancyManager.manager_chat_id == manager_chat_id
        ).order_by(VacancyManager.created_at)
    )
    managers = result.scalars().all()
    
    return [VacancyManagerDTO.model_validate(manager) for manager in managers]


@app.get("/vacancy-managers/by-email/{email}", response_model=VacancyManagerDTO)
async def get_manager_by_email(
    email: str, session: AsyncSession = Depends(get_session)
) -> VacancyManagerDTO:
    """Get manager by email address (returns first match if multiple exist)."""
    result = await session.execute(
        select(VacancyManager).where(
            VacancyManager.email == email
        ).order_by(VacancyManager.created_at)
    )
    manager = result.scalar_one_or_none()
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manager with email {email} not found"
        )
    return VacancyManagerDTO.model_validate(manager)


@app.delete("/vacancy-managers/{vacancy_manager_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy_manager(
    vacancy_manager_id: int, session: AsyncSession = Depends(get_session)
) -> None:
    """Remove a manager from a vacancy and redistribute assigned applicants."""
    manager = await session.get(VacancyManager, vacancy_manager_id)
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VacancyManager with id {vacancy_manager_id} not found"
        )
    
    vacancy_id = manager.vacancy_id
    
    # Find all applicants assigned to this manager
    result = await session.execute(
        select(Applicant).where(
            Applicant.assigned_manager_id == vacancy_manager_id
        )
    )
    assigned_applicants = result.scalars().all()
    
    # Get vacancy to check distribution strategy
    vacancy = await session.get(Vacancy, vacancy_id)
    
    # Redistribute applicants if there are other managers and strategy is not manual
    if assigned_applicants and vacancy:
        other_managers = await get_available_managers(session, vacancy_id)
        # Filter out the manager being deleted
        other_managers = [m for m in other_managers if m.vacancy_manager_id != vacancy_manager_id]
        
        if other_managers and vacancy.distribution_strategy != "manual":
            logger.info(
                f"Redistributing {len(assigned_applicants)} applicants "
                f"from deleted manager {vacancy_manager_id} to other managers"
            )
            
            for applicant in assigned_applicants:
                # Only redistribute if no final decision was made
                if not applicant.final_manager_id:
                    new_manager_id = await assign_manager_to_applicant(
                        session,
                        vacancy_id,
                        applicant.applicant_id,
                        vacancy.distribution_strategy,
                        vacancy.max_candidates_per_manager
                    )
                    if new_manager_id:
                        applicant.assigned_manager_id = new_manager_id
                        logger.info(
                            f"Redistributed applicant {applicant.applicant_id} "
                            f"from manager {vacancy_manager_id} to manager {new_manager_id}"
                        )
                    else:
                        # No manager available, unassign
                        applicant.assigned_manager_id = None
                        logger.warning(
                            f"Could not redistribute applicant {applicant.applicant_id}, "
                            f"unassigning manager"
                        )
                else:
                    # Final decision was made, just unassign (don't redistribute)
                    applicant.assigned_manager_id = None
                    logger.info(
                        f"Unassigning applicant {applicant.applicant_id} "
                        f"(final decision already made by deleted manager)"
                    )
        else:
            # No other managers or manual strategy - just unassign
            for applicant in assigned_applicants:
                applicant.assigned_manager_id = None
            logger.info(
                f"Unassigning {len(assigned_applicants)} applicants "
                f"(no other managers or manual strategy)"
            )
    
    # Delete the manager
    await session.delete(manager)
    await session.commit()
    
    logger.info(f"Deleted manager {vacancy_manager_id} from vacancy {vacancy_id}")


@app.delete("/vacancy-managers/vacancy/{vacancy_id}/manager/{manager_chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy_manager_by_vacancy_and_chat(
    vacancy_id: int, manager_chat_id: int, session: AsyncSession = Depends(get_session)
) -> None:
    """Remove a specific manager from a specific vacancy and redistribute assigned applicants."""
    result = await session.execute(
        select(VacancyManager).where(
            VacancyManager.vacancy_id == vacancy_id,
            VacancyManager.manager_chat_id == manager_chat_id
        )
    )
    manager = result.scalar_one_or_none()
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VacancyManager not found for vacancy_id={vacancy_id} and manager_chat_id={manager_chat_id}"
        )
    
    vacancy_manager_id = manager.vacancy_manager_id
    
    # Find all applicants assigned to this manager
    result = await session.execute(
        select(Applicant).where(
            Applicant.assigned_manager_id == vacancy_manager_id
        )
    )
    assigned_applicants = result.scalars().all()
    
    # Get vacancy to check distribution strategy
    vacancy = await session.get(Vacancy, vacancy_id)
    
    # Redistribute applicants if there are other managers and strategy is not manual
    if assigned_applicants and vacancy:
        other_managers = await get_available_managers(session, vacancy_id)
        # Filter out the manager being deleted
        other_managers = [m for m in other_managers if m.vacancy_manager_id != vacancy_manager_id]
        
        if other_managers and vacancy.distribution_strategy != "manual":
            logger.info(
                f"Redistributing {len(assigned_applicants)} applicants "
                f"from deleted manager {vacancy_manager_id} to other managers"
            )
            
            for applicant in assigned_applicants:
                # Only redistribute if no final decision was made
                if not applicant.final_manager_id:
                    new_manager_id = await assign_manager_to_applicant(
                        session,
                        vacancy_id,
                        applicant.applicant_id,
                        vacancy.distribution_strategy,
                        vacancy.max_candidates_per_manager
                    )
                    if new_manager_id:
                        applicant.assigned_manager_id = new_manager_id
                        logger.info(
                            f"Redistributed applicant {applicant.applicant_id} "
                            f"from manager {vacancy_manager_id} to manager {new_manager_id}"
                        )
                    else:
                        # No manager available, unassign
                        applicant.assigned_manager_id = None
                        logger.warning(
                            f"Could not redistribute applicant {applicant.applicant_id}, "
                            f"unassigning manager"
                        )
                else:
                    # Final decision was made, just unassign (don't redistribute)
                    applicant.assigned_manager_id = None
                    logger.info(
                        f"Unassigning applicant {applicant.applicant_id} "
                        f"(final decision already made by deleted manager)"
                    )
        else:
            # No other managers or manual strategy - just unassign
            for applicant in assigned_applicants:
                applicant.assigned_manager_id = None
            logger.info(
                f"Unassigning {len(assigned_applicants)} applicants "
                f"(no other managers or manual strategy)"
            )
    
    await session.delete(manager)
    await session.commit()


@app.delete("/vacancy-managers/vacancy/{vacancy_id}", status_code=status.HTTP_200_OK)
async def delete_all_vacancy_managers_by_vacancy(
    vacancy_id: int, session: AsyncSession = Depends(get_session)
) -> dict:
    """Remove all managers from a vacancy."""
    result = await session.execute(
        delete(VacancyManager).where(VacancyManager.vacancy_id == vacancy_id)
    )
    await session.commit()
    return {"deleted_count": result.rowcount}



@app.get("/admins/{admin_id}", response_model=AdminDTO)
async def get_admin_by_id(
    admin_id: str, session: AsyncSession = Depends(get_session)
) -> AdminDTO:
    """Get admin by ID."""
    admin = await session.get(Admin, admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    return AdminDTO.model_validate(admin)


@app.get("/admins/username/{username}", response_model=AdminDTO)
async def get_admin_by_username_endpoint(
    username: str, session: AsyncSession = Depends(get_session)
) -> AdminDTO:
    """Get admin by username."""
    result = await session.execute(
        select(Admin).where(Admin.username == username)
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    return AdminDTO.model_validate(admin)


# Manager password management endpoints
class ManagerPasswordUpdate(BaseModel):
    password: str


@app.put("/vacancy-managers/{vacancy_manager_id}/password", response_model=VacancyManagerDTO)
async def update_manager_password(
    vacancy_manager_id: int,
    password_data: ManagerPasswordUpdate,
    session: AsyncSession = Depends(get_session)
) -> VacancyManagerDTO:
    """Update manager password."""
    manager = await session.get(VacancyManager, vacancy_manager_id)
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manager with id {vacancy_manager_id} not found"
        )
    
    # Hash password
    manager.hashed_password = hash_password(password_data.password)
    
    await session.commit()
    await session.refresh(manager)
    return VacancyManagerDTO.model_validate(manager)


@app.get("/vacancy-managers/all", response_model=list[VacancyManagerDTO])
async def get_all_managers(
    session: AsyncSession = Depends(get_session)
) -> list[VacancyManagerDTO]:
    """Get all managers (for admin panel)."""
    result = await session.execute(
        select(VacancyManager).order_by(VacancyManager.created_at.desc())
    )
    managers = result.scalars().all()
    
    # Group by manager_chat_id to get unique managers
    unique_managers = {}
    for manager in managers:
        if manager.manager_chat_id not in unique_managers:
            unique_managers[manager.manager_chat_id] = manager
    
    return [VacancyManagerDTO.model_validate(m) for m in unique_managers.values()]

