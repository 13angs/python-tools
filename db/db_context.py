from sqlalchemy.orm import sessionmaker, declarative_base
import streamlit as st
from models.base import Base


class DatabaseContext:
    def __init__(self):
        """
        Initialize the configuration manager
        Sets up database connection and session
        """
        self.engine = st.connection("sqlite", type="sql").engine
        self.Session = sessionmaker(bind=self.engine)


        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session