import streamlit as st
from db.object_storage_repo import ObjectStorageRepository
import pandas as pd
from utils.object_storage_utils import ObjectStorageUtil
from models.object_storage_config import ObjectStorageConfig

class ObjectStorageApp:
    def __init__(self):
        # Initialize the repository

        self.object_storage_repo = ObjectStorageRepository()
        
        # Initialize session state
        if 'page' not in st.session_state:
            st.session_state.page = "list"
        if 'selected_config' not in st.session_state:
            st.session_state.selected_config = None

    @st.dialog("Create Object Storage")
    def create_object_storage(self):
        """Dialog for creating a new object storage configuration"""
        with st.form("object_storage_form"):
            name = st.text_input(label="Name", help="Unique name for this storage configuration")
            col1, col2 = st.columns(2)
            
            with col1:
                endpoint = st.text_input(label="Endpoint", help="S3 compatible endpoint URL")
                bucket_name = st.text_input(label="Bucket Name", help="Name of the bucket to use")
            
            access_key = st.text_input(label="Access Key", type="password")
            secret_key = st.text_input(label="Secret Key", type="password")

            with col2:
                port = st.text_input(label="Port", help="Port number for the endpoint")
                region = st.text_input(label="Region", help="Optional region for the storage")

            if st.form_submit_button("Save Configuration", type="primary"):
                # Validate inputs
                if not all([name, endpoint, access_key, secret_key, bucket_name]):
                    st.error("Please fill in all required fields")
                    return

                # Prepare configuration dictionary
                config = {
                    'name': name,
                    'endpoint': endpoint,
                    'port': port,
                    'access_key': access_key,
                    'secret_key': secret_key,
                    'region': region,
                    'bucket_name': bucket_name
                }

                # Save configuration
                self.object_storage_repo.save_config(config)
                st.success(f"Configuration '{name}' saved successfully!")
                st.rerun()
        # with st.dialog("Create Object Storage"):

    def show_object_storage_detail(self, config_id: str):
        """Display detailed view of a specific object storage configuration"""
        config = self.object_storage_repo.get_config_by_id(config_id)

        st.header(f"Object Storage / {config.name}")

        # Tabs for Object, Access, SSL/TLS
        tabs = st.tabs(["Objects", "Access", "SSL/TLS"])

        # Objects tab content
        with tabs[0]:
            st.markdown(f"**{config.name}**")
            # Add button for uploading files or dropping them
            st.markdown("You can browse your device to upload files or drop them here.")
            uploaded_file = st.file_uploader("Browse Files")
            # Implement file upload logic here if needed
            
            # Create Folder button
            with st.columns([4.5, 1])[1]:
                st.button("Create Folder")

            # Display a table of files and folders
            object_storage_util = ObjectStorageUtil(
                config.access_key,
                config.secret_key,
                config.endpoint
            )


            if 'prefix' not in st.query_params:
                st.query_params['prefix'] = ''

            prefix = st.query_params['prefix']

            objects = object_storage_util.list_objects(config.bucket_name, prefix)

            transformed_objects = object_storage_util.transform_object_list(objects, prefix)

            selection = self.display_contents(transformed_objects)

            self.handle_prefix(transformed_objects, selection)
            
        # Access tab content (placeholder, implement real logic)
        with tabs[1]:
            st.write("Access tab content")

        # SSL/TLS tab content (placeholder, implement real logic)
        with tabs[2]:
            st.write("SSL/TLS tab content")

    def list_object_storage_configs(self):
        """List all object storage configurations with interactive elements"""
        st.header("Object Storage Configurations")
        
        # Create New Configuration Button
        if st.button("Add New Configuration", type="primary"):
            self.create_object_storage()
        
        # Fetch configurations from the database
        saved_configs = self.object_storage_repo.list_configs()
        
        # Check if no configurations exist
        if not saved_configs:
            st.info("No object storage configurations found. Add a new configuration to get started.")
            return

        # Display configurations
        for config in saved_configs:
            with st.container(border=True):
                col1, col2, col3 = st.columns([5, 1, 1])
                
                # Configuration basic info
                with col1:
                    st.markdown(f"### {config.name}")
                    st.write(f"**Endpoint:** {config.endpoint}")
                    st.write(f"**Region:** {config.region or 'Not specified'}")
                
                # Details button
                with col2:
                    if st.button(f"Details", key=f"detail_{config.name}"):
                        st.query_params['page'] = "detail"
                        st.query_params['config_id'] = config.id
                        st.rerun()
                
                # Delete button
                with col3:
                    if st.button(f"Delete", key=f"delete_{config.name}", type="secondary"):
                        # Implement delete logic
                        self.object_storage_repo.delete_config(config.name)
                        st.success(f"Configuration '{config.name}' deleted successfully!")
                        st.rerun()

    def display_contents(self, contents):
        """Display contents of the selected configuration"""
        df = pd.DataFrame(
                    contents,
                    columns=["Object", "Size", "Last Modified", ""],
                )

        df['Last Modified'] = pd.to_datetime(df['Last Modified'], format='%Y-%m-%d %H:%M:%S', errors="coerce")
        
        event = st.dataframe(df, hide_index=True, use_container_width=True, on_select="rerun", selection_mode="single-row")
        return event.selection

    def handle_prefix(self, contents, selection):
        """Handle prefix filtering"""
        rows = selection.rows
        if len(rows) == 0:
            return
        
        row_ind = rows[0]
        column_ind = 0

        object_name = contents[row_ind][column_ind]
        if '📂' in object_name:
            current_prefix = st.query_params['prefix']
            # Update query params to include the new prefix
            new_prefix = current_prefix + object_name.replace('📂', '').strip() + '/'
            st.query_params['prefix'] = new_prefix
            st.rerun()

    def run(self):
        """Main application runner"""
        # Determine which page to show based on session state
        if "page" not in st.query_params:
            st.query_params['page'] = 'list'
        if "config_id" not in st.query_params:
            st.query_params['config_id'] = ''
        
        page = st.query_params['page']

        if page == 'list':
            self.list_object_storage_configs()
        
        elif page == 'detail':
            config_id = st.query_params['config_id']
            if config_id:
                self.show_object_storage_detail(config_id)
            else:
                st.query_params['page'] = 'list'
                st.rerun()

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Object Storage Configurations",
        page_icon="🗄️",
        # layout="wide"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
    .stContainer {
        border: 5px solid #e0e0e0;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize and run the app
    app = ObjectStorageApp()
    app.run()

main()