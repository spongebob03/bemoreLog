import logging
from sqlalchemy.orm import Session
from ..models.base import Base
from .session import engine
from ..models.epic import Epic  # Import all models here

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize the database with all tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

if __name__ == "__main__":
    logger.info("Creating initial database tables")
    init_db()
    logger.info("Database initialization completed") 