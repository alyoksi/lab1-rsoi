import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# По умолчанию — локальный Postgres из docker-compose.
# На Render/Railway переменная DATABASE_URL подставляется платформой автоматически.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://program:test@localhost:5432/persons",
)

# Render/Railway иногда отдают URL с префиксом postgres:// — SQLAlchemy 2.x требует postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
