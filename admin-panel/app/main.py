"""
FastAPI приложение для админ-панели.
"""
from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import timedelta
from typing import List, Optional
import logging

from .config import settings
from .auth import authenticate_admin, create_access_token, get_current_admin
from .database import Admin
from .db_client import db_client
from .payment_gateway_client import get_payment_gateway_client
from .schemas import (
    Token,
    AdminLogin,
    AdminRegister,
    AdminResponse,
    VacancyCreate,
    VacancyUpdate,
    ManagerCreate,
    ManagerPasswordUpdate
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Admin Panel API",
    description="Веб-админка для управления рекрутер-ботом",
    version="1.0.0"
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации для детального логирования."""
    try:
        body = await request.body()
        body_str = body.decode('utf-8') if body else 'No body'
    except:
        body_str = "Could not read body"
    
    logger.error(f"=== VALIDATION ERROR ===")
    logger.error(f"Method: {request.method}, URL: {request.url}")
    logger.error(f"Validation errors: {exc.errors()}")
    logger.error(f"Request body: {body_str}")
    logger.error(f"========================")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors(), "body": body_str}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений для логирования."""
    logger.error(f"=== HTTP EXCEPTION ===")
    logger.error(f"Method: {request.method}, URL: {request.url}")
    logger.error(f"Status: {exc.status_code}")
    logger.error(f"Detail: {exc.detail}")
    logger.error(f"======================")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )



    logger.info("Admin Panel API started")

    from .database import init_database, create_tables, init_default_admin
    init_database()
    

    try:
        await create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}", exc_info=True)
    

    try:
        await init_default_admin()
        logger.info("Default admin initialization completed")
    except Exception as e:
        logger.warning(f"Could not initialize default admin at startup: {e}")
        logger.info("You can create default admin via POST /api/auth/init-default-admin or /api/auth/register")
    

    await db_client.close()

    try:
        payment_client = get_payment_gateway_client()
        await payment_client.close()
    except Exception as e:
        logger.warning(f"Error closing Payment Gateway client: {e}")


@app.get("/health")
async def healthcheck():
    """Health check endpoint."""
    return {"status": "ok"}



    from .database import get_admin_by_username, create_admin
    

            )
    

    existing_admin = await get_admin_by_username("admin")
    



    from .database import init_default_admin, get_admin_by_username
    

    return AdminResponse(
        admin_id=current_admin.admin_id,
        username=current_admin.username,
        email=current_admin.email,
        owner_id=current_admin.owner_id,
        created_at=current_admin.created_at,
        is_active=current_admin.is_active,
        is_global_admin=current_admin.is_global_admin,
        is_legal_entity=current_admin.is_legal_entity,
        company_name=current_admin.company_name,
        inn=current_admin.inn
    )



    try:

        owner_id = None if current_admin.is_global_admin else current_admin.owner_id
        if not current_admin.is_global_admin and not owner_id:

    try:
        vacancy = await db_client.get_vacancy(vacancy_id)

    logger.info("=== CREATE VACANCY ENDPOINT CALLED ===")
    try:
        if not current_admin.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin must have owner_id to create vacancies"
            )
        

        logger.info(f"Creating vacancy for admin {current_admin.username} (owner_id={current_admin.owner_id})")
        logger.info(f"Vacancy data received: {vacancy.model_dump()}")
        
        vacancy_data = vacancy.model_dump(exclude_none=True)

        if not vacancy_data.get("owner_id"):
            if current_admin.is_global_admin:

                vacancy_data["owner_id"] = current_admin.owner_id or vacancy_data.get("owner_id")
            else:
                vacancy_data["owner_id"] = current_admin.owner_id
        
        logger.info(f"Vacancy data to send to db-core: {vacancy_data}")
        new_vacancy = await db_client.create_vacancy(vacancy_data)
        

        if new_vacancy and not vacancy.is_closed:
            try:
                vacancy_id = new_vacancy.get('vacancy_id')
                bot_token = new_vacancy.get('bot_token')
                
                if vacancy_id and bot_token:
                    await db_client.start_bot({
                        "vacancy_id": vacancy_id,
                        "bot_token": bot_token
                    })
                    logger.info(f"Bot started for vacancy {vacancy_id}")
            except Exception as e:
                logger.error(f"Failed to start bot for vacancy {new_vacancy.get('vacancy_id')}: {e}", exc_info=True)

        
        return new_vacancy
    except HTTPException:
        raise
    except ValueError as e:

    try:

        existing_vacancy = await db_client.get_vacancy(vacancy_id)
        if not current_admin.is_global_admin and existing_vacancy.get("owner_id") != current_admin.owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this vacancy"
            )
        vacancy_data = vacancy.model_dump(exclude_none=True)

        vacancy_data.pop("owner_id", None)
        updated_vacancy = await db_client.update_vacancy(vacancy_id, vacancy_data)
        return updated_vacancy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vacancy {vacancy_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



    try:

    try:

        vacancy = await db_client.get_vacancy(vacancy_id)
        if not current_admin.is_global_admin and vacancy.get("owner_id") != current_admin.owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this vacancy"
            )
        applicants = await db_client.get_applicants_by_vacancy(vacancy_id)
        return applicants
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting applicants for vacancy {vacancy_id}: {e}", exc_info=True)

    try:
        applicant = await db_client.update_applicant(telegram_id, applicant_data, vacancy_id)
        return applicant
    except Exception as e:
        logger.error(f"Error updating applicant {telegram_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



    try:

        vacancy = await db_client.get_vacancy(vacancy_id)
        if not current_admin.is_global_admin and vacancy.get("owner_id") != current_admin.owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this vacancy"
            )
        managers = await db_client.get_vacancy_managers(vacancy_id)

    try:

    try:

        vacancy = await db_client.get_vacancy(vacancy_id)
        if not current_admin.is_global_admin and vacancy.get("owner_id") != current_admin.owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this vacancy"
            )
        await db_client.delete_vacancy_manager(vacancy_manager_id)
        return {"message": "Manager deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting manager {vacancy_manager_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



    try:

    try:
        updated_manager = await db_client.update_manager_password(vacancy_manager_id, password_data.password)
        return updated_manager
    except Exception as e:
        logger.error(f"Error updating manager password: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



    try:

    from .tariffs import get_all_tariffs
    try:
        tariffs = get_all_tariffs()
        return [tariff.to_dict() for tariff in tariffs]
    except Exception as e:
        logger.error(f"Error getting tariffs: {e}", exc_info=True)
        return []



            detail="payment_type must be 'individual' or 'legal_entity'"
        )
    

        )
    

    company_name = payment_data.company_name
    inn = payment_data.inn
    if payment_data.payment_type == "legal_entity":

            )
    
    try:
        payment_client = get_payment_gateway_client()
        

        company_info = {
            "tariff_id": tariff.id,
            "tariff_name": tariff.name,
            "vacancies_count": tariff.vacancies_count,
            "offer_analyses_count": tariff.offer_analyses_count
        }
        
        if payment_data.payment_type == "legal_entity":
            company_info.update({
                "name": company_name,
                "inn": inn,
            })
            if payment_data.kpp:
                company_info["kpp"] = payment_data.kpp
            if payment_data.legal_address:
                company_info["legal_address"] = payment_data.legal_address
            if payment_data.email:
                company_info["email"] = payment_data.email
        

        telegram_data = {
            "username": current_admin.username,
            "full_name": current_admin.username  