# core/auth.py
import streamlit as st
import mysql.connector as connector
import datetime
import uuid

# --- SINGLETONS FOR DB CONNECTION AND TOKEN STORE ---
@st.cache_resource
def get_db_connection():
    """Establishes and caches the database connection."""
    try:
        return connector.connect(
            host="localhost",
            user="root",
            password="sqladi@2710",
            database="auth"
        )
    except connector.Error as e:
        st.error(f"Database connection failed: {e}. Please contact an administrator.")
        st.stop()

@st.cache_resource
def get_token_store():
    """Initializes and caches a dictionary to store authentication tokens."""
    return {}

# --- AUTHENTICATION GUARD ---
def protect_page(allowed_roles: list):
    token_store = get_token_store()
    # --- This authentication part remains the same ---
    if "name" not in st.session_state:
        if "token" in st.query_params:
            token = st.query_params["token"]
            if token in token_store:
                token_data = token_store[token]
                if datetime.datetime.now() - token_data['timestamp'] < datetime.timedelta(hours=24):
                    st.session_state["name"] = token_data['username']
                    st.session_state["role"] = token_data['role']
                    st.session_state["token"] = token
                    st.rerun()
                else:
                    del token_store[token]
                    st.query_params.clear()
            else:
                st.query_params.clear()

    if "name" not in st.session_state:
        st.error("🚨 Access Denied. Please log in first.")
        if st.button("Go to Login Page"):
            st.switch_page("Home.py")
        st.stop()
    
    # --- CHANGE 2: Added this new authorization block ---
    user_role = st.session_state.get("role")
    if user_role not in allowed_roles:
        st.error(f"🚫 Access Denied. Your role ('{user_role}') does not have permission to view this page.")
        if st.button("Go to My Dashboard"):
            # Redirect user to their correct dashboard
            if user_role == 'employee':
                st.switch_page("pages/1_Employee_Dashboard.py")
            elif user_role == 'manager':
                st.switch_page("pages/2_Manager_Dashboard.py")
            elif user_role == 'hr':
                st.switch_page("pages/3_HR_Dashboard.py")
            elif user_role == 'admin':
                st.switch_page("pages/4_Admin_Panel.py")
            else:
                st.switch_page("Home.py")
        st.stop() # This is crucial to stop the unauthorized page from loading

    # If authorized, ensure the token stays in the URL
    if "token" in st.session_state:
        st.query_params["token"] = st.session_state["token"]

# --- LOGOUT COMPONENT ---
def render_logout_button():
    """Renders the logout button and handles the logout logic."""
    st.write("---")
    if st.button("Logout", type="primary"):
        token_store = get_token_store()
        token_to_remove = st.session_state.get("token")

        if token_to_remove and token_to_remove in token_store:
            del token_store[token_to_remove]

        st.session_state.clear()
        st.query_params.clear()
        st.switch_page("Home.py")