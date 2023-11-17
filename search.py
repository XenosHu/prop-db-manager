import streamlit as st
import mysql.connector
import pandas as pd

# Database configuration
config = {
    'user': 'propbotics',
    'password': 'Propbotics123',
    'host': 'chatbot.c0xmynwsxhmo.us-east-1.rds.amazonaws.com',
    'database': 'chatbot',
    'port': 3306
}

# Function to get database connection
def get_db_connection():
    connection = mysql.connector.connect(**config)
    return connection

def search_data():
    st.title("SQL Query Executor")

    # Text area for SQL query
    query = st.text_area("Enter your SQL query", height=150)
    execute_query = st.button("Execute Query")

    if execute_query:
        if query:
            try:
                # Connection to the database
                connection = get_db_connection()
                # Executing the query
                df = pd.read_sql(query, connection)
                st.write(df)
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                connection.close()
        else:
            st.error("Please enter a SQL query.")

if __name__ == "__main__":
    search_data()
