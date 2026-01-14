import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)

# Создание таблиц
Base.metadata.create_all(bind=engine)