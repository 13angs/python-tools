from sqlalchemy.orm import sessionmaker, declarative_base
import streamlit as st


class DatabaseContext:
    def __init__(self):
        """
        Initialize the configuration manager
        Sets up database connection and session
        """
        self.Base = declarative_base()
        self.engine = st.connection("sqlite", type="sql").engine
        self.Session = sessionmaker(bind=self.engine)