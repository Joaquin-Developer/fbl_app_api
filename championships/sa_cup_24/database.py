from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from championships.sa_cup_24.schemas import Base
from core.settings import settings


engine = create_engine(settings.SA_CUP_24_DATABASE_DSN)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
