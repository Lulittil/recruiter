"""
FastAPI приложение для менеджерской панели.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import logging

from .config import settings, get_cors_origins
from .auth import create_access_token, verify_manager_email, get_current_manager
from .db_client import get_db_client
from .database import get_session, create_tables
from .models import CalendarEvent as CalendarEventModel, ManagerSettings as ManagerSettingsModel
from .schemas import (
    ManagerLogin,
    Token,
    ManagerInfo,
    CandidateListItem,
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEvent,
    ManagerSettingsCreate,
    ManagerSettings as ManagerSettingsSchema
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Manager Panel API",
    description="API для менеджерской панели",
    version="1.0.0"
)


    logger.info("Manager Panel API started")
    await create_tables()
    

    manager = await verify_manager_email(manager_login.email, manager_login.password)
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    

    manager_chat_id = current_manager["manager_chat_id"]
    db_client = get_db_client()
    

    applicants = await db_client.get_applicants_by_manager(manager_chat_id, vacancy_id)
    

    result = []
    for applicant in applicants:
        candidate_data = CandidateListItem(**applicant)
        

        if applicant.get("vacancy_id"):
            vacancy = await db_client.get_vacancy(applicant["vacancy_id"])
            if vacancy:
                candidate_data.vacancy_name = vacancy.get("vacancy") or vacancy.get("company_name")
        

        if applicant.get("step_screen_id"):
            step = await db_client.get_step_screen(applicant["step_screen_id"])
            if step:
                candidate_data.step_screen_name = step.get("name")
        


    manager_chat_id = current_manager["manager_chat_id"]
    db_client = get_db_client()
    

    applicants = await db_client.get_applicants_by_manager(manager_chat_id)
    

    applicant = next((a for a in applicants if a.get("applicant_id") == candidate_id), None)
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    candidate_data = CandidateListItem(**applicant)
    

    if applicant.get("vacancy_id"):
        vacancy = await db_client.get_vacancy(applicant["vacancy_id"])
        if vacancy:
            candidate_data.vacancy_name = vacancy.get("vacancy") or vacancy.get("company_name")
    
    if applicant.get("step_screen_id"):
        step = await db_client.get_step_screen(applicant["step_screen_id"])
        if step:
            candidate_data.step_screen_name = step.get("name")
    
    return candidate_data



    manager_chat_id = current_manager["manager_chat_id"]
    

    if event.candidate_id is not None:
        db_client = get_db_client()
        applicants = await db_client.get_applicants_by_manager(manager_chat_id)
        candidate_exists = any(a.get("applicant_id") == event.candidate_id for a in applicants)
        if not candidate_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Candidate not found or not assigned to you"
            )
    

    settings_result = await session.execute(
        select(ManagerSettingsModel).where(ManagerSettingsModel.manager_id == manager_chat_id)
    )
    settings = settings_result.scalar_one_or_none()
    default_duration = (settings.default_duration_minutes if settings else None) or 60
    

    if event.event_type == "slot" and event.end_time:

        slot_duration = event.duration_minutes or default_duration
        slot_times = []
        current_slot_time = event.event_date
        
        while current_slot_time < event.end_time:
            slot_times.append(current_slot_time)
            current_slot_time += timedelta(minutes=slot_duration)
        

        dates = []
        if event.recurrence_type and event.recurrence_type != "none" and event.recurrence_end_date:
            current_date = event.event_date
            while current_date <= event.recurrence_end_date:

                for slot_time in slot_times:

                    time_offset = slot_time - event.event_date
                    dates.append(current_date + time_offset)
                
                if event.recurrence_type == "daily":
                    current_date += timedelta(days=event.recurrence_interval or 1)
                elif event.recurrence_type == "weekly":
                    current_date += timedelta(weeks=event.recurrence_interval or 1)
                elif event.recurrence_type == "monthly":
                    current_date += relativedelta(months=event.recurrence_interval or 1)
                else:
                    break
        else:
            dates = slot_times
    else:

        dates = []
        current_date = event.event_date
        
        if event.recurrence_type and event.recurrence_type != "none" and event.recurrence_end_date:
            while current_date <= event.recurrence_end_date:
                dates.append(current_date)
                if event.recurrence_type == "daily":
                    current_date += timedelta(days=event.recurrence_interval or 1)
                elif event.recurrence_type == "weekly":
                    current_date += timedelta(weeks=event.recurrence_interval or 1)
                elif event.recurrence_type == "monthly":
                    current_date += relativedelta(months=event.recurrence_interval or 1)
                else:
                    break
        else:
            dates = [event.event_date]
    

    """
    from datetime import datetime, timedelta, timezone, time, date
    
    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=days)
    

    settings_result = await session.execute(
        select(ManagerSettingsModel).where(ManagerSettingsModel.manager_id == manager_chat_id)
    )
    settings = settings_result.scalar_one_or_none()
    
    if not settings:

        return {"slots": []}
    
    default_duration = settings.default_duration_minutes or 60
    

    query = select(CalendarEventModel).where(
        CalendarEventModel.manager_id == manager_chat_id
    ).where(
        CalendarEventModel.event_date >= start_date
    ).where(
        CalendarEventModel.event_date <= end_date
    ).where(
        CalendarEventModel.candidate_id.isnot(None)  
            detail="Event not found or you don't have permission"
        )
    
    candidate_chat_id = None

    if event.candidate_id:
        db_client = get_db_client()
        try:
            await db_client.connect()
            applicants = await db_client.get_applicants_by_manager(manager_chat_id)
            for applicant in applicants:
                if applicant.get("applicant_id") == event.candidate_id:
                    candidate_chat_id = applicant.get("telegram_id")
                    break
        except Exception as e:
            logger.error(f"Error getting candidate chat_id: {e}")
        finally:
            await db_client.close()
    

    from datetime import time as dt_time
    
    manager_chat_id = current_manager["manager_chat_id"]
    
    result = await session.execute(
        select(ManagerSettingsModel).where(ManagerSettingsModel.manager_id == manager_chat_id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:

        settings = ManagerSettingsModel(
            manager_id=manager_chat_id,
            default_duration_minutes=60
        )
        session.add(settings)
        await session.commit()
        await session.refresh(settings)
    

    from datetime import time as dt_time, timezone
    
    manager_chat_id = current_manager["manager_chat_id"]
    
    result = await session.execute(
        select(ManagerSettingsModel).where(ManagerSettingsModel.manager_id == manager_chat_id)
    )
    settings = result.scalar_one_or_none()
    
    def str_to_time(s):
        if not s:
            return None
        try:
            parts = s.split(":")
            return dt_time(int(parts[0]), int(parts[1]))
        except:
            return None
    
    if not settings:

        settings = ManagerSettingsModel(
            manager_id=manager_chat_id,
            monday_start=str_to_time(settings_data.monday_start),
            monday_end=str_to_time(settings_data.monday_end),
            tuesday_start=str_to_time(settings_data.tuesday_start),
            tuesday_end=str_to_time(settings_data.tuesday_end),
            wednesday_start=str_to_time(settings_data.wednesday_start),
            wednesday_end=str_to_time(settings_data.wednesday_end),
            thursday_start=str_to_time(settings_data.thursday_start),
            thursday_end=str_to_time(settings_data.thursday_end),
            friday_start=str_to_time(settings_data.friday_start),
            friday_end=str_to_time(settings_data.friday_end),
            saturday_start=str_to_time(settings_data.saturday_start),
            saturday_end=str_to_time(settings_data.saturday_end),
            sunday_start=str_to_time(settings_data.sunday_start),
            sunday_end=str_to_time(settings_data.sunday_end),
            default_duration_minutes=settings_data.default_duration_minutes
        )
        session.add(settings)
    else:

        if settings_data.monday_start is not None:
            settings.monday_start = str_to_time(settings_data.monday_start)
        if settings_data.monday_end is not None:
            settings.monday_end = str_to_time(settings_data.monday_end)
        if settings_data.tuesday_start is not None:
            settings.tuesday_start = str_to_time(settings_data.tuesday_start)
        if settings_data.tuesday_end is not None:
            settings.tuesday_end = str_to_time(settings_data.tuesday_end)
        if settings_data.wednesday_start is not None:
            settings.wednesday_start = str_to_time(settings_data.wednesday_start)
        if settings_data.wednesday_end is not None:
            settings.wednesday_end = str_to_time(settings_data.wednesday_end)
        if settings_data.thursday_start is not None:
            settings.thursday_start = str_to_time(settings_data.thursday_start)
        if settings_data.thursday_end is not None:
            settings.thursday_end = str_to_time(settings_data.thursday_end)
        if settings_data.friday_start is not None:
            settings.friday_start = str_to_time(settings_data.friday_start)
        if settings_data.friday_end is not None:
            settings.friday_end = str_to_time(settings_data.friday_end)
        if settings_data.saturday_start is not None:
            settings.saturday_start = str_to_time(settings_data.saturday_start)
        if settings_data.saturday_end is not None:
            settings.saturday_end = str_to_time(settings_data.saturday_end)
        if settings_data.sunday_start is not None:
            settings.sunday_start = str_to_time(settings_data.sunday_start)
        if settings_data.sunday_end is not None:
            settings.sunday_end = str_to_time(settings_data.sunday_end)
        if settings_data.default_duration_minutes is not None:
            settings.default_duration_minutes = settings_data.default_duration_minutes
        
        settings.updated_at = datetime.now(timezone.utc)
    
    await session.commit()
    await session.refresh(settings)
    

    def time_to_str(t):
        return t.strftime("%H:%M") if t else None
    
    return ManagerSettingsSchema(
        settings_id=settings.settings_id,
        manager_id=settings.manager_id,
        monday_start=time_to_str(settings.monday_start),
        monday_end=time_to_str(settings.monday_end),
        tuesday_start=time_to_str(settings.tuesday_start),
        tuesday_end=time_to_str(settings.tuesday_end),
        wednesday_start=time_to_str(settings.wednesday_start),
        wednesday_end=time_to_str(settings.wednesday_end),
        thursday_start=time_to_str(settings.thursday_start),
        thursday_end=time_to_str(settings.thursday_end),
        friday_start=time_to_str(settings.friday_start),
        friday_end=time_to_str(settings.friday_end),
        saturday_start=time_to_str(settings.saturday_start),
        saturday_end=time_to_str(settings.saturday_end),
        sunday_start=time_to_str(settings.sunday_start),
        sunday_end=time_to_str(settings.sunday_end),
        default_duration_minutes=settings.default_duration_minutes,
        created_at=settings.created_at,
        updated_at=settings.updated_at
    )


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}

