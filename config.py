# config.py

# import streamlit as st
# db_user = st.secrets["db_config"]["user"]
# db_password = st.secrets["db_config"]["password"]
# db_host = st.secrets["db_config"]["host"]
# db_database = st.secrets["db_config"]["database"]
# db_port = st.secrets["db_config"]["port"]

# # Database configuration
# DATABASE_CONFIG = {
#     'user': db_user,
#     'password': db_password,
#     'host': db_host,
#     'database': db_database,
#     'port': db_port
# }


# import streamlit as st

# def get_database_config():
#     # Fetching database configuration from Streamlit secrets
DATABASE_CONFIG = {
    'user': st.secrets["db_config"]["user"],
    'password': st.secrets["db_config"]["password"],
    'host': st.secrets["db_config"]["host"],
    'database': st.secrets["db_config"]["database"],
    'port': st.secrets["db_config"]["port"]
}
    # return DATABASE_CONFIG
