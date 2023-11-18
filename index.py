import streamlit as st
import insert
import search
import sql_test
import manage

def main():
    st.sidebar.title("Real Estate Database Management Navigation")
    choice = st.sidebar.selectbox("Choose a page", ["Manage","Insert Data", "Search Data","SQL test"])

    if choice == "Manage":
        manage.app()    
    elif choice == "Insert Data":
        insert.app()
    elif choice == "SQL test":
        sql_test.app()
    elif choice == "Search Data":
        search.app()

if __name__ == "__main__":
    main()
