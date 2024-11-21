import streamlit as st
from sqlalchemy.exc import IntegrityError, DatabaseError

from db.db_context import DatabaseContext
from models.object_storage import ObjectStorage

class ObjectStorageRepository:
    def __init__(self):
        """
        Initialize the configuration manager
        Sets up database connection and session
        """
        db_context = DatabaseContext()
        self.Session = db_context.Session

        # Create tables
        db_context.Base.metadata.create_all(db_context.engine)

    def save_config(self, config):
        """
        Save configuration to database
        
        Args:
            config (dict): Configuration details to save
        """
        session = self.Session()
        try:
            new_config = ObjectStorage(
                name=config['name'],
                endpoint=config['endpoint'],
                port=config['port'],
                access_key=config['access_key'],
                secret_key=config['secret_key'],
                region=config['region']
            )
            session.add(new_config)
            session.commit()
            st.success("Configuration saved successfully!")
        except IntegrityError:
            st.error("Configuration with this name already exists.")
        except DatabaseError as e:
            st.error(f"Error saving configuration: {str(e)}")
        finally:
            session.close()

    def list_configs(self):
        """
        List all saved configurations
        
        Returns:
            list: List of configuration objects
        """
        session = self.Session()
        try:
            configs = session.query(ObjectStorage).all()
            return configs
        except DatabaseError as e:
            st.error(f"Error retrieving configurations: {str(e)}")
            return []
        finally:
            session.close()

    def delete_config(self, config_name):
        """
        Delete a configuration by name
        
        Args:
            config_name (str): Name of the configuration to delete
        """
        session = self.Session()
        try:
            config_to_delete = session.query(ObjectStorage).filter_by(name=config_name).first()
            if config_to_delete:
                session.delete(config_to_delete)
                session.commit()
                st.success(f"Configuration '{config_name}' deleted successfully!")
            else:
                st.warning(f"Configuration '{config_name}' not found.")
        except DatabaseError as e:
            st.error(f"Error deleting configuration: {str(e)}")
        finally:
            session.close()

    def update_config(self, config_name, updated_config):
        """
        Update an existing configuration
        
        Args:
            config_name (str): Name of the configuration to update
            updated_config (dict): Updated configuration details
        """
        session = self.Session()
        try:
            existing_config = session.query(ObjectStorage).filter_by(name=config_name).first()
            if existing_config:
                # Update fields
                existing_config.endpoint = updated_config.get('endpoint', existing_config.endpoint)
                existing_config.port = updated_config.get('port', existing_config.port)
                existing_config.access_key = updated_config.get('access_key', existing_config.access_key)
                existing_config.secret_key = updated_config.get('secret_key', existing_config.secret_key)
                existing_config.region = updated_config.get('region', existing_config.region)
                
                session.commit()
                st.success(f"Configuration '{config_name}' updated successfully!")
            else:
                st.warning(f"Configuration '{config_name}' not found.")
        except DatabaseError as e:
            st.error(f"Error updating configuration: {str(e)}")
        finally:
            session.close()