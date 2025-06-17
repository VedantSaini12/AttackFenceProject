import streamlit as st
import bcrypt
import mysql.connector as connector

# MySQL connection settings
db = connector.connect(
        host="localhost",         # change if needed
        user="root",              # your MySQL Email
        password="password", # your MySQL password
    )
cursor = db.cursor()
cursor.execute("USE auth")

# Streamlit app for user login
st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered",
)
st.image("./logo.png", width=2000)
st.write("<center><h1>Login 🔐</h1></center>", unsafe_allow_html=True)
Email = st.text_input("Email")
password = st.text_input("Password", type="password")
if st.button("Login", type="primary"):
    if Email and password:
        cursor.execute("SELECT * FROM users WHERE Email = %s", (Email,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode(), user[2].encode()):
            # Redirect to dashboard or another page
            if "name" not in st.session_state:
                st.session_state.name = user[5]
            st.switch_page("pages/Dashboard.py")
        else:
            st.error("Invalid Email or password")
    else:
        st.error("Please enter both Email and password")

