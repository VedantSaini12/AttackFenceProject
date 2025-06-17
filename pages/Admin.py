import streamlit as st
import bcrypt
import mysql.connector as connector
# MySQL connection settings
db = connector.connect(
    host="localhost", 
    user="root",
    password="password",  
    database="auth" )
cursor = db.cursor()
st.write("<center><h1>Admin Page</h1></center>", unsafe_allow_html=True)

option = st.selectbox(
    "Select an action",
    ("Create Employee/Manager", "Delete Employee/Manager", "Edit Employee/Manager")
)
st.write("---")
if option == "Create Employee/Manager":
    st.subheader("Create New Employee/Manager")
    name = st.text_input("Name")
    email = st.text_input("Assign an email")
    password = st.text_input("Assign a password", type="password")
    role = st.selectbox("Role", ("Employee", "Manager"))
    password = st.text_input("Password", type="password")
    if st.button("Create"):
        if name and password:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            # Save name, role, and hashed_pw to your database here
            st.success(f"{role} '{name}' created successfully!")
        else:
            st.error("Please enter all fields.")

elif option == "Delete Employee/Manager":
    st.subheader("Delete Employee/Manager")
    # Replace with actual employee/manager list from your database
    users = ["Alice (Employee)", "Bob (Manager)"]
    user_to_delete = st.selectbox("Select user to delete", users)
    if st.button("Delete"):
        # Delete user from your database here
        st.success(f"User '{user_to_delete}' deleted successfully!")

elif option == "Edit Employee/Manager":
    st.subheader("Edit Employee/Manager Details")
    # Replace with actual employee/manager list from your database
    users = ["Alice (Employee)", "Bob (Manager)"]
    user_to_edit = st.selectbox("Select user to edit", users)
    new_name = st.text_input("New Name")
    new_role = st.selectbox("New Role", ("Employee", "Manager"))
    new_password = st.text_input("New Password", type="password")
    if st.button("Update"):
        # Update user details in your database here
        st.success(f"User '{user_to_edit}' updated successfully!")