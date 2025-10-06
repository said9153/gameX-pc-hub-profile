# app/models.py
import os
import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime
)
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------
# DATABASE_URL is set automatically in Render environment.
# For local testing, fallback to SQLite (data.db).
DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///data.db"

# ---------------------------------------------------------------------
# SQLAlchemy setup
# ---------------------------------------------------------------------
Base = declarative_base()

class Product(Base):
    """
    Product table — replaces data.json.
    Fields:
        id          (int, primary key)
        title       (str)
        desc        (str)
        photo       (str)
        category    (str)
        created_at  (datetime)
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    desc = Column(Text, default="")
    photo = Column(String(1024), default="")
    category = Column(String(120), default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Product id={self.id} title='{self.title}'>"


def get_engine(echo: bool = False):
    """
    Create a SQLAlchemy engine using DATABASE_URL.
    Works for both Postgres (Render) and SQLite (local).
    """
    # Render may provide a postgres:// URL which SQLAlchemy 2.0+ expects as postgresql://
    db_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return create_engine(db_url, echo=echo, future=True)


def create_db_and_tables(engine=None):
    """
    Create all tables if they don't exist (safe to call on startup).
    """
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(bind=engine)


def create_session(engine=None):
    """
    Create and return a new SQLAlchemy session bound to the engine.
    Usage:
        s = create_session()
        ... do queries ...
        s.close()
    """
    if engine is None:
        engine = get_engine()
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session()
