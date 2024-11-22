from sqlalchemy import Column, Integer, String
from models.base import Base

# Database Model
class ObjectStorageConfig(Base):
    __tablename__ = 'object_storage_configs'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    endpoint = Column(String, nullable=False)
    port = Column(String)
    access_key = Column(String, nullable=False)
    secret_key = Column(String, nullable=False)
    region = Column(String)
    bucket_name = Column(String, nullable=False)