from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from services.connection_postgres import Base
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")
database = os.getenv("DATABASEBDD")
schema = os.getenv("SCHEMA")
table_name = os.getenv("TABLENAME")
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")

SessionLocal = sessionmaker(bind=engine)

def init_db():
    with engine.connect() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
    Base.metadata.create_all(bind=engine)
