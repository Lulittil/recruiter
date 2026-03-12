"""
Сервис для автоматического распределения кандидатов между менеджерами.
"""
import logging
import random
from typing import Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Vacancy, VacancyManager, Applicant, StepScreen

logger = logging.getLogger(__name__)


async def get_available_managers(
    session: AsyncSession,
    vacancy_id: int
) -> list[VacancyManager]:
    """
    Получить список доступных менеджеров для вакансии.
    
    Args:
        session: Сессия базы данных
        vacancy_id: ID вакансии
        
    Returns:
        Список менеджеров для данной вакансии
    """
    result = await session.execute(
        select(VacancyManager).where(
            VacancyManager.vacancy_id == vacancy_id
        ).order_by(VacancyManager.created_at)
    )
    managers = result.scalars().all()
    logger.info(f"Found {len(managers)} managers for vacancy {vacancy_id}")
    return managers


async def calculate_manager_load(
    session: AsyncSession,
    manager_chat_id: int,
    vacancy_id: int,
    max_candidates: Optional[int] = None
) -> dict:
    """
    Рассчитать загрузку менеджера (количество активных кандидатов).
    
    Args:
        session: Сессия базы данных
        manager_chat_id: Chat ID менеджера
        vacancy_id: ID вакансии
        max_candidates: Максимальное количество кандидатов (если задано)
        
    Returns:
        Словарь с информацией о загрузке:
        {
            'manager_chat_id': int,
            'active_count': int,
            'is_available': bool,
            'max_candidates': Optional[int]
        }
    """

    manager_result = await session.execute(
        select(VacancyManager).where(
            and_(
                VacancyManager.vacancy_id == vacancy_id,
                VacancyManager.manager_chat_id == manager_chat_id
            )
        )
    )
    manager = manager_result.scalar_one_or_none()
    
    if not manager:
        return {
            'manager_chat_id': manager_chat_id,
            'active_count': 0,
            'is_available': False,
            'max_candidates': max_candidates
        }
    



    active_statuses = [0, 1, 2, 4]
    
    count_result = await session.execute(
        select(func.count(Applicant.applicant_id)).where(
            and_(
                Applicant.vacancy_id == vacancy_id,
                Applicant.assigned_manager_id == manager.vacancy_manager_id,
                or_(
                    Applicant.step_screen_id.in_(active_statuses),
                    Applicant.step_screen_id.is_(None)
                )
            )
        )
    )
    active_count = count_result.scalar_one() or 0
    

    is_available = True
    if max_candidates is not None and active_count >= max_candidates:
        is_available = False
    
    return {
        'manager_chat_id': manager_chat_id,
        'vacancy_manager_id': manager.vacancy_manager_id,
        'active_count': active_count,
        'is_available': is_available,
        'max_candidates': max_candidates
    }


async def assign_round_robin(
    session: AsyncSession,
    vacancy_id: int,
    managers: list[VacancyManager]
) -> Optional[VacancyManager]:
    """
    Стратегия Round Robin: распределение по кругу.
    
    Args:
        session: Сессия базы данных
        vacancy_id: ID вакансии
        managers: Список менеджеров
        
    Returns:
        Назначенный менеджер или None
    """
    if not managers:
        return None
    

    last_assigned_result = await session.execute(
        select(Applicant.assigned_manager_id)
        .where(Applicant.vacancy_id == vacancy_id)
        .order_by(Applicant.applicant_id.desc())
        .limit(1)
    )
    last_assigned_id = last_assigned_result.scalar_one_or_none()
    

    current_index = 0
    if last_assigned_id:
        for i, manager in enumerate(managers):
            if manager.vacancy_manager_id == last_assigned_id:
                current_index = (i + 1) % len(managers)
                break
    
    return managers[current_index]


async def assign_least_loaded(
    session: AsyncSession,
    vacancy_id: int,
    managers: list[VacancyManager],
    max_candidates: Optional[int] = None
) -> Optional[VacancyManager]:
    """
    Стратегия Least Loaded: назначение менеджеру с наименьшей загрузкой.
    
    Args:
        session: Сессия базы данных
        vacancy_id: ID вакансии
        managers: Список менеджеров
        max_candidates: Максимальное количество кандидатов на менеджера
        
    Returns:
        Назначенный менеджер или None
    """
    if not managers:
        return None
    

    manager_loads = []
    for manager in managers:
        load_info = await calculate_manager_load(
            session,
            manager.manager_chat_id,
            vacancy_id,
            max_candidates
        )
        manager_loads.append({
            'manager': manager,
            'load': load_info
        })
    

    available_managers = [
        ml for ml in manager_loads
        if ml['load']['is_available']
    ]
    
    if not available_managers:
        logger.warning(f"No available managers for vacancy {vacancy_id} (all at max capacity)")
        return None
    

    min_load_manager = min(available_managers, key=lambda x: x['load']['active_count'])
    return min_load_manager['manager']


async def assign_random(
    session: AsyncSession,
    vacancy_id: int,
    managers: list[VacancyManager],
    max_candidates: Optional[int] = None
) -> Optional[VacancyManager]:
    """
    Стратегия Random: случайное распределение.
    
    Args:
        session: Сессия базы данных
        vacancy_id: ID вакансии
        managers: Список менеджеров
        max_candidates: Максимальное количество кандидатов на менеджера
        
    Returns:
        Назначенный менеджер или None
    """
    if not managers:
        return None
    

    available_managers = []
    for manager in managers:
        load_info = await calculate_manager_load(
            session,
            manager.manager_chat_id,
            vacancy_id,
            max_candidates
        )
        if load_info['is_available']:
            available_managers.append(manager)
    
    if not available_managers:
        logger.warning(f"No available managers for vacancy {vacancy_id} (all at max capacity)")
        return None
    

    return random.choice(available_managers)


async def assign_manager_to_applicant(
    session: AsyncSession,
    vacancy_id: int,
    applicant_id: int,
    strategy: str = "manual",
    max_candidates: Optional[int] = None
) -> Optional[int]:
    """
    Назначить менеджера кандидату согласно стратегии распределения.
    
    Args:
        session: Сессия базы данных
        vacancy_id: ID вакансии
        applicant_id: ID кандидата
        strategy: Стратегия распределения ('round_robin', 'least_loaded', 'random', 'manual')
        max_candidates: Максимальное количество кандидатов на менеджера
        
    Returns:
        ID назначенного менеджера (vacancy_manager_id) или None
    """

    if strategy == "manual":
        logger.info(f"Strategy is 'manual', skipping automatic assignment for applicant {applicant_id}")
        return None
    

    managers = await get_available_managers(session, vacancy_id)
    

    if len(managers) < 2:
        logger.info(f"Less than 2 managers for vacancy {vacancy_id}, skipping assignment")
        return None
    

    assigned_manager = None
    
    if strategy == "round_robin":
        assigned_manager = await assign_round_robin(session, vacancy_id, managers)
    elif strategy == "least_loaded":
        assigned_manager = await assign_least_loaded(session, vacancy_id, managers, max_candidates)
    elif strategy == "random":
        assigned_manager = await assign_random(session, vacancy_id, managers, max_candidates)
    else:
        logger.warning(f"Unknown strategy: {strategy}, skipping assignment")
        return None
    
    if assigned_manager:
        logger.info(
            f"Assigned manager {assigned_manager.vacancy_manager_id} "
            f"(chat_id: {assigned_manager.manager_chat_id}) "
            f"to applicant {applicant_id} using strategy '{strategy}'"
        )
        return assigned_manager.vacancy_manager_id
    
    logger.warning(f"Could not assign manager to applicant {applicant_id} using strategy '{strategy}'")
    return None


async def balance_workload(
    session: AsyncSession,
    vacancy_id: int,
    threshold: int = 3
) -> dict:
    """
    Автоматическая балансировка нагрузки между менеджерами.
    
    Перераспределяет кандидатов, если разница в загрузке между менеджерами
    превышает порог.
    
    Args:
        session: Сессия базы данных
        vacancy_id: ID вакансии
        threshold: Порог разницы в количестве кандидатов для перераспределения
        
    Returns:
        Словарь с результатами балансировки:
        {
            'vacancy_id': int,
            'redistributed_count': int,
            'managers_affected': list[int],
            'details': list[dict]
        }
    """
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise ValueError(f"Vacancy {vacancy_id} not found")
    

    if vacancy.distribution_strategy == "manual":
        logger.info(f"Strategy is 'manual' for vacancy {vacancy_id}, skipping balance")
        return {
            'vacancy_id': vacancy_id,
            'redistributed_count': 0,
            'managers_affected': [],
            'details': []
        }
    
    managers = await get_available_managers(session, vacancy_id)
    if len(managers) < 2:
        logger.info(f"Less than 2 managers for vacancy {vacancy_id}, skipping balance")
        return {
            'vacancy_id': vacancy_id,
            'redistributed_count': 0,
            'managers_affected': [],
            'details': []
        }
    

    manager_loads = []
    for manager in managers:
        load_info = await calculate_manager_load(
            session,
            manager.manager_chat_id,
            vacancy_id,
            vacancy.max_candidates_per_manager
        )
        manager_loads.append({
            'manager': manager,
            'load': load_info
        })
    

    max_load_manager = max(manager_loads, key=lambda x: x['load']['active_count'])
    min_load_manager = min(manager_loads, key=lambda x: x['load']['active_count'])
    
    max_count = max_load_manager['load']['active_count']
    min_count = min_load_manager['load']['active_count']
    difference = max_count - min_count
    

    if difference < threshold:
        logger.info(
            f"Workload is balanced for vacancy {vacancy_id}: "
            f"max={max_count}, min={min_count}, difference={difference} < threshold={threshold}"
        )
        return {
            'vacancy_id': vacancy_id,
            'redistributed_count': 0,
            'managers_affected': [],
            'details': [],
            'current_balance': {
                'max_load': max_count,
                'min_load': min_count,
                'difference': difference
            }
        }
    
    logger.info(
        f"Starting workload balance for vacancy {vacancy_id}: "
        f"max={max_count}, min={min_count}, difference={difference} >= threshold={threshold}"
    )
    


    max_manager = max_load_manager['manager']
    min_manager = min_load_manager['manager']
    

    candidates_to_redistribute = (difference + 1) // 2
    


    active_statuses = [0, 1, 2, 4]
    candidates_result = await session.execute(
        select(Applicant).where(
            and_(
                Applicant.vacancy_id == vacancy_id,
                Applicant.assigned_manager_id == max_manager.vacancy_manager_id,
                Applicant.final_manager_id.is_(None),  
                or_(
                    Applicant.step_screen_id.in_(active_statuses),
                    Applicant.step_screen_id.is_(None)
                )
            )
        ).order_by(Applicant.applicant_id)  
        .limit(candidates_to_redistribute)
    )
    candidates_to_move = candidates_result.scalars().all()
    
    redistributed_count = 0
    details = []
    

    for candidate in candidates_to_move:

        min_load_info = await calculate_manager_load(
            session,
            min_manager.manager_chat_id,
            vacancy_id,
            vacancy.max_candidates_per_manager
        )
        
        if not min_load_info['is_available']:
            logger.warning(
                f"Min load manager {min_manager.manager_chat_id} is no longer available, "
                f"skipping redistribution for candidate {candidate.applicant_id}"
            )
            break
        

        candidate.assigned_manager_id = min_manager.vacancy_manager_id
        redistributed_count += 1
        details.append({
            'applicant_id': candidate.applicant_id,
            'from_manager': max_manager.vacancy_manager_id,
            'to_manager': min_manager.vacancy_manager_id
        })
        logger.info(
            f"Redistributed applicant {candidate.applicant_id} "
            f"from manager {max_manager.vacancy_manager_id} "
            f"to manager {min_manager.vacancy_manager_id}"
        )
    
    if redistributed_count > 0:
        await session.commit()
        logger.info(
            f"Workload balance completed for vacancy {vacancy_id}: "
            f"redistributed {redistributed_count} applicants"
        )
    
    return {
        'vacancy_id': vacancy_id,
        'redistributed_count': redistributed_count,
        'managers_affected': [max_manager.vacancy_manager_id, min_manager.vacancy_manager_id],
        'details': details,
        'current_balance': {
            'max_load': max_count,
            'min_load': min_count,
            'difference': difference
        }
    }

