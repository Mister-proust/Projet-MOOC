from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class embeddings(Base):
    __tablename__ = "embeddings_pgvector"

    id = Column(UUID, primary_key=True)
    text = Column(Text)
    title = Column(String)
    course_id = Column(String)
    username = Column(String)
    created_at = Column(DateTime)
    embedding = Column(Vector(384))  