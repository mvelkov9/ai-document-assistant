from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base


settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Create tables if they do not yet exist.

    In production, prefer running ``alembic upgrade head`` before starting
    the application.  The ``create_all`` call here is kept as a convenience
    for local development and tests where Alembic may not be available.
    """
    from app.models.document import Document  # noqa: F401
    from app.models.processing_job import ProcessingJob  # noqa: F401
    from app.models.question_answer import QuestionAnswer  # noqa: F401
    from app.models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
