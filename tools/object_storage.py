import streamlit as st
from db.object_storage_repo import ObjectStorageRepository
import pandas as pd

object_storage_repo = ObjectStorageRepository()

# Add a new function to handle the detail page
def show_object_storage_detail(config):
    st.header(f"Object Storage Details: {config.name}")
    
    # Display detailed information
    st.write(f"**Endpoint:** {config.endpoint}")
    st.write(f"**Port:** {config.port}")
    st.write(f"**Region:** {config.region}")
    
    # You might want to add more details or actions here
    if st.button("Back to Configurations"):
        st.session_state.page = "list"

@st.dialog("Create object storage")
def create_object_storage():
    with st.form("s3_form"):
        name = st.text_input(label="Name", help="Unique name for this storage configuration")
        col1, col2 = st.columns(2)
        endpoint = col1.text_input(label="Endpoint", help="S3 compatible endpoint URL")
        port = col2.text_input(label="Port", help="Port number for the endpoint")
        access_key = st.text_input(label="Access Key", type="password")
        secret_key = st.text_input(label="Secret Key", type="password")
        region = st.text_input(label="Region", help="Optional region for the storage")

        if st.form_submit_button("Save", type="primary"):
            # Validate inputs
            if not name or not endpoint or not access_key or not secret_key:
                st.error("Please fill in all required fields")
            else:
                config = {
                    'name': name,
                    'endpoint': endpoint,
                    'port': port,
                    'access_key': access_key,
                    'secret_key': secret_key,
                    'region': region
                }
                object_storage_repo.save_config(config)
                st.rerun()

# Use session state to manage page navigation
if 'page' not in st.session_state:
    st.session_state.page = "list"

if st.session_state.page == "list":
    st.header("Object Storage Configuration")
    st.write("S3 Compatible Storage Configuration")

    if st.button("Create New"):
        create_object_storage()

    # Fetch configurations from the database
    saved_configs = object_storage_repo.list_configs()

    # Convert configurations to a DataFrame with clickable names
    df = pd.DataFrame([
        {
            "Name": config.name, 
            "endpoint": config.endpoint, 
            "port": config.port, 
            "access_key": config.access_key,
            "region": config.region,
        } for config in saved_configs
    ])

    # Create a column with clickable names
    df_with_links = df.copy()
    df_with_links['Name'] = df['Name'].apply(lambda x: f"[{x}](#)")

    # Use data editor to display the configurations
    edited_df = st.data_editor(
        df_with_links, 
        column_config={
            "Name": st.column_config.TextColumn(disabled=True),
            "endpoint": st.column_config.TextColumn(disabled=True),
            "port": st.column_config.TextColumn(disabled=True),
            "access_key": st.column_config.TextColumn(disabled=True),
            "region": st.column_config.SelectboxColumn(
                options=["Asia", "Europe", "North America", "South America"]
            ),
        },
        use_container_width=True,
        key="object_storage_configs"
    )

    # Handle row selection
    selected_rows = st.session_state.get("object_storage_configs", {}).get("selected_rows", [])
    
    if selected_rows:
        # Get the selected configuration
        selected_config_name = df.iloc[selected_rows[0]]['Name']
        selected_config = next(
            (config for config in saved_configs if config.name == selected_config_name), 
            None
        )
        
        if selected_config:
            st.session_state.page = "detail"
            st.session_state.selected_config = selected_config
            st.rerun()

elif st.session_state.page == "detail":
    show_object_storage_detail(st.session_state.selected_config)