from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# =========================================================
# ACTIVITY 91
# Database configuration
# =========================================================

DATABASE_URL = "mysql+pymysql://root:root@localhost/telecomdb"


# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)


# Create database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)