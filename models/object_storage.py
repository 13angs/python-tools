from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# Database setup
Base = declarative_base()

# Database Model
class ObjectStorage(Base):
    __tablename__ = 'object_storage_configs'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    endpoint = Column(String, nullable=False)
    port = Column(String)
    access_key = Column(String, nullable=False)
    secret_key = Column(String, nullable=False)
    region = Column(String)