from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

ENGINE = create_engine(DATABASE_URL)
Base = declarative_base()

Base.metadata.create_all(ENGINE)
print("Tables succesfully created!")

SessionLocal = sessionmaker(bind=ENGINE)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()