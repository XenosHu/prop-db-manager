import streamlit as st
import insert
import search

def main():
    st.sidebar.title("Real Estate Database Management Navigation")
    choice = st.sidebar.selectbox("Choose a page", ["Insert Data", "Search Data"])

    if choice == "Insert Data":
        insert.app()
    elif choice == "Search Data":
        search.app()

if __name__ == "__main__":
    main()
