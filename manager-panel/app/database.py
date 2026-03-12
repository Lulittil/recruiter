"""
Подключение к базе данных и управление таблицами.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from .config import settings
from .models import Base
import logging

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Получить сессию БД."""
    async with async_session_maker() as session:
        yield session


async def create_tables():
    """Создать таблицы в БД."""
    async with engine.begin() as conn:

        result_settings = await conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'manager_calendar_settings'
                );
            """)
        )
        settings_table_exists = result_settings.scalar()
        
        if not settings_table_exists:

            await conn.execute(
                text("""
                    CREATE TABLE manager_calendar_settings (
                        settings_id SERIAL PRIMARY KEY,
                        manager_id BIGINT NOT NULL UNIQUE,
                        monday_start TIME,
                        monday_end TIME,
                        tuesday_start TIME,
                        tuesday_end TIME,
                        wednesday_start TIME,
                        wednesday_end TIME,
                        thursday_start TIME,
                        thursday_end TIME,
                        friday_start TIME,
                        friday_end TIME,
                        saturday_start TIME,
                        saturday_end TIME,
                        sunday_start TIME,
                        sunday_end TIME,
                        default_duration_minutes INTEGER NOT NULL DEFAULT 60,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    );
                """)
            )
            await conn.execute(
                text("CREATE INDEX idx_manager_calendar_settings_manager_id ON manager_calendar_settings(manager_id)")
            )
            logger.info("Created manager_calendar_settings table")
        else:
            logger.info("manager_calendar_settings table already exists")
        

        result = await conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'manager_calendar_events'
                );
            """)
        )
        table_exists = result.scalar()
        
        if not table_exists:

            await conn.execute(
                text("""
                    CREATE TABLE manager_calendar_events (
                        event_id SERIAL PRIMARY KEY,
                        manager_id BIGINT NOT NULL,
                        candidate_id INTEGER,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        event_date TIMESTAMP WITH TIME ZONE NOT NULL,
                        duration_minutes INTEGER,
                        event_type VARCHAR(50) DEFAULT 'call',
                        recurrence_type VARCHAR(20),
                        recurrence_end_date TIMESTAMP WITH TIME ZONE,
                        recurrence_interval INTEGER DEFAULT 1,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    );
                """)
            )

            await conn.execute(
                text("CREATE INDEX idx_manager_calendar_events_manager_id ON manager_calendar_events(manager_id)")
            )
            await conn.execute(
                text("CREATE INDEX idx_manager_calendar_events_candidate_id ON manager_calendar_events(candidate_id)")
            )
            await conn.execute(
                text("CREATE INDEX idx_manager_calendar_events_event_date ON manager_calendar_events(event_date)")
            )
            logger.info("Created manager_calendar_events table")
        else:

            logger.info("manager_calendar_events table already exists, checking for migrations...")
            

            try:
                check_result = await conn.execute(
                    text("""
                        SELECT column_name, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = 'manager_calendar_events' AND column_name = 'candidate_id'
                    """)
                )
                candidate_id_info = check_result.fetchone()
                
                if candidate_id_info:

                    is_nullable = candidate_id_info[1] == 'YES'
                    if not is_nullable:

                        logger.info("Removing NOT NULL constraint from candidate_id column")
                        await conn.execute(
                            text("ALTER TABLE manager_calendar_events ALTER COLUMN candidate_id DROP NOT NULL")
                        )
                        logger.info("Successfully removed NOT NULL constraint from candidate_id")
                else:

                    logger.info("Adding candidate_id column as nullable")
                    await conn.execute(
                        text("ALTER TABLE manager_calendar_events ADD COLUMN candidate_id INTEGER")
                    )
                    await conn.execute(
                        text("CREATE INDEX idx_manager_calendar_events_candidate_id ON manager_calendar_events(candidate_id)")
                    )
                    logger.info("Successfully added candidate_id column")
            except Exception as e:
                error_str = str(e).lower()
                if "does not exist" not in error_str and "not found" not in error_str:
                    logger.warning(f"Could not migrate candidate_id column: {e}")
                else:
                    logger.debug(f"candidate_id column migration issue: {e}")
            

            columns_to_add = [
                ("recurrence_type", "ADD COLUMN recurrence_type VARCHAR(20)"),
                ("recurrence_end_date", "ADD COLUMN recurrence_end_date TIMESTAMP WITH TIME ZONE"),
                ("recurrence_interval", "ADD COLUMN recurrence_interval INTEGER DEFAULT 1"),
                ("duration_minutes", "ADD COLUMN duration_minutes INTEGER")
            ]
            
            for column_name, alter_sql in columns_to_add:
                try:

                    check_result = await conn.execute(
                        text(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = 'manager_calendar_events' AND column_name = '{column_name}'
                        """)
                    )
                    column_exists = check_result.fetchone() is not None
                    
                    if not column_exists:
                        await conn.execute(
                            text(f"ALTER TABLE manager_calendar_events {alter_sql}")
                        )
                        logger.info(f"Added column {column_name} to manager_calendar_events table")
                except Exception as e:
                    error_str = str(e).lower()
                    if "already exists" not in error_str and "duplicate" not in error_str:
                        logger.warning(f"Could not add column {column_name}: {e}")
                    else:
                        logger.debug(f"Column {column_name} already exists or minor error: {e}")

