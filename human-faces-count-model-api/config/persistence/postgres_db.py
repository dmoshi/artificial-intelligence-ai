from sqlalchemy.orm import declarative_base, sessionmaker
from ..base_config import DATABASE_URL
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine(DATABASE_URL, echo=False, future=True)
SyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
