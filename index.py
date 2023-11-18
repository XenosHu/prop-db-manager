import streamlit as st
import insert
import search
import sql_test
import manage
import hmac


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        entered_username = st.session_state["username"]
        entered_password = st.session_state["password"]
    
        # Check if the entered username exists in the secrets
        if entered_username in st.secrets["users"]:
            # Compare the entered password with the stored one
            correct_password = st.secrets["users"][entered_username]
            if hmac.compare_digest(entered_password, correct_password):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the username or password.
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

if not check_password():
    st.stop()

def logout():
    # Reset or remove login-related session state variables
    for key in ['password_correct', 'username', 'password']:
        if key in st.session_state:
            del st.session_state[key]

if 'password_correct' in st.session_state and st.session_state['password_correct']:
    def main():
        st.title("Rental Realtor Database Management System")
        st.sidebar.title("System Navigator")
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

    col1, col2 = st.columns([0.85, 0.15])
    with col2:
        if st.button('**Logout**', type="primary"):
            logout()
            st.experimental_rerun()
