from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from core.settings import settings

# engine=create_engine(settings.DATABASE_URL)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)
Base=declarative_base()
SessionLocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()