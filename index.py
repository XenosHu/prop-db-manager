import streamlit as st
import insert
import search

PAGES = {
    "Insert Data": insert,
    "Search Data": search
}

def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]
    page.app()

if __name__ == "__main__":
    main()
