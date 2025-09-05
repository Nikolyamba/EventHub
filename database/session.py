from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

engine = create_engine('postgresql+psycopg2://user:password@hostname/database_name')
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()