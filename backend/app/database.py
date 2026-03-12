from sqlalchemy import create_engine, Boolean, Column, DateTime, func
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, DeclarativeBase
from datetime import datetime
from sqlmodel import SQLModel

# name of sqlite file being made for the database
DATABASE_URL = "sqlite:///./main.db"
# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(Boolean)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
