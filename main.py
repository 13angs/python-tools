import streamlit as st

def main():
    object_storage_page = st.Page('tools/object_storage.py', url_path='object-storage', title="Object storages", icon=":material/help:", default=True)

    pg = st.navigation({
        "Tools": [object_storage_page],
    })
    pg.run()

if __name__ == "__main__":
    main()