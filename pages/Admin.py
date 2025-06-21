import streamlit as st
import bcrypt
import mysql.connector as connector

# st.html(
# """
# <style>
#     div[data-testid='element-container']:has(iframe[title='streamlit_cookies_controller.cookie_controller']) {
#         display: none;
#     }
# </style>
# """
# )

# --- Initialize Cookie Controller ---
# controller = CookieController()

# --- NEW AUTHENTICATION GUARD using Query Params ---

# 1. Check session state first
if "name" not in st.session_state:
    # 2. If not in session state, check the URL query parameters
    if "user" in st.query_params:
        # If a user is found in the URL, restore the session state from it
        st.session_state["name"] = st.query_params["user"]
    else:
        # If no user in session OR URL, deny access
        st.error("No user logged in. Please log in first.")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()

# 3. At this point, the user is authenticated.
#    Ensure the user's name is in the URL for refresh persistence.
st.query_params.user = st.session_state["name"]
name = st.session_state["name"]

# After authentication, verify the role
db = connector.connect(
    host="localhost", user="root", password="sqladi@2710", database="auth")
cursor = db.cursor()
cursor.execute("SELECT role FROM users WHERE username = %s", (name,))
user_role = cursor.fetchone()

if not user_role or user_role[0] not in ['admin', 'HR']:
    st.error("Access Denied: You do not have permission to view this page.")
    st.stop()

# Ensure the user has the correct role to access this page
if not user_role or user_role[0] not in ['admin', 'HR']:
    st.error("Access Denied: You do not have permission to view this page.")
    st.stop()


# --- START OF PAGE CONTENT ---
st.write(f"<center><h1>{user_role[0].title()} Page</h1></center>", unsafe_allow_html=True)

option = st.selectbox(
    "Select an action",
    ("Create Employee/Manager", "Delete Employee/Manager", "Edit Employee/Manager")
)
st.write("---")
if option == "Create Employee/Manager":
    st.subheader("Create New Employee/Manager")
    # Set a default value if it's not already in session_state
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ''
        st.session_state.role = ''
        st.session_state.email = ''
        st.session_state.password = ''
        st.session_state.managed_by = None

    # Define a function to clear the text input
    def clear_input():
        st.session_state.user_input = ''
        st.session_state.role = ''
        st.session_state.email = ''
        st.session_state.password = ''
        st.session_state.managed_by = None

    name = st.text_input("Name", key='user_input',
                         placeholder="Enter name")
    email = st.text_input("Assign an email",key='email',placeholder="Enter email")
    role = st.selectbox("Role", ("Employee", "Manager"),key='role')

    # Fetch all managers from the database
    cursor.execute("SELECT username FROM users WHERE role = 'manager'")
    managers = [row[0] for row in cursor.fetchall()]

    managed_by = None
    if role == "Employee":
        if managers:
            managed_by = st.selectbox("Managed By", managers)
        else:
            st.warning("No managers available. Please create a manager first.")

    password = st.text_input("Password", type="password",key='password',placeholder="Enter password")
    if st.button("Create"):
        if name and password and email and (role == "Manager" or (role == "Employee" and managed_by)):
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            # Save name, email, role, hashed_pw, and managed_by to your database here
            # Example insert (adjust table/column names as needed):
            if role == "Employee":
                cursor.execute(
                    "INSERT INTO users (username, email, password, role, managed_by) VALUES (%s, %s, %s, %s, %s)",
                    (name, email, hashed_pw, role.lower(), managed_by)
                )
            else:
                cursor.execute(
                    "INSERT INTO users (username, email, password, role, managed_by) VALUES (%s, %s, %s, %s,%s)",
                    (name, email, hashed_pw, role.lower(),'XYZ')
                )
            db.commit()
            @st.dialog("Confirmation")
            def new_emp(role,name):
                st.success(f"{role} '{name}' created successfully!")
                if st.button("Close"):
                    st.rerun()
            new_emp(role, name)
            clear_input()
            
        else:
            st.error("Please enter all fields.")

elif option == "Delete Employee/Manager":
    st.subheader("Delete Employee/Manager")
    # Replace with actual employee/manager list from your database
    cursor.execute("SELECT username, role FROM users where role != 'admin'")
    users = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]
    user_to_delete = st.selectbox("Select user to delete", users)
    @st.dialog("Confirmation")
    def new_emp(user):
        st.success(f"{user} deleted successfully!")
        if st.button("Close"):
            st.rerun()
    if st.button("Delete"):
        # Delete user from your database here
        username = user_to_delete.split(" (")[0]
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        db.commit()
        new_emp(user_to_delete)
        

elif option == "Edit Employee/Manager":
    st.subheader("Edit Employee/Manager Details")
    # Replace with actual employee/manager list from your database
    cursor.execute("SELECT username, role FROM users")
    users = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]
    user_to_edit = st.selectbox("Select user to edit", users)
    username = user_to_edit.split(" (")[0]
    role = user_to_edit.split("(")[-1].replace(")", "").strip().lower()

    new_name = st.text_input("New Name")
    new_password = st.text_input("New Password", type="password")

    update_fields = []
    params = []

    if role == "admin":
        # Only allow name and password change for admin
        if st.button("Update"):
            if new_name:
                update_fields.append("name = %s")
                params.append(new_name)
            if new_password:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                update_fields.append("password = %s")
                params.append(hashed_pw)
            if update_fields:
                params.append(username)
                cursor.execute(
                    f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s",
                    tuple(params)
                )
                db.commit()
                st.success(f"Admin '{user_to_edit}' updated successfully!")
            else:
                st.info("No changes made.")
    elif role == "manager":
        # Only allow name and password change for manager, managed_by is set to 'XYZ'
        if st.button("Update"):
            if new_name:
                update_fields.append("name = %s")
                params.append(new_name)
            if new_password:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                update_fields.append("password = %s")
                params.append(hashed_pw)
            # Always set managed_by to 'XYZ' for managers
            update_fields.append("managed_by = %s")
            params.append('XYZ')
            if update_fields:
                params.append(username)
                cursor.execute(
                    f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s",
                    tuple(params)
                )
                db.commit()
                st.success(f"Manager '{user_to_edit}' updated successfully!")
            else:
                st.info("No changes made.")
    else:
        # Employee: allow name, password, role, managed_by
        new_role = st.selectbox("New Role", ("Employee", "Manager"))
        # Fetch all managers for reassignment if needed
        cursor.execute("SELECT username FROM users WHERE role = 'manager'")
        managers = [row[0] for row in cursor.fetchall()]
        new_managed_by = None
        if new_role == "Employee":
            if managers:
                new_managed_by = st.selectbox("Managed By", managers, key="edit_managed_by")
            else:
                st.warning("No managers available. Please create a manager first.")

        if st.button("Update"):
            if new_name:
                update_fields.append("name = %s")
                params.append(new_name)
            if new_role:
                update_fields.append("role = %s")
                params.append(new_role)
            if new_role == "Employee" and new_managed_by:
                update_fields.append("managed_by = %s")
                params.append(new_managed_by)
            elif new_role == "Manager":
                update_fields.append("managed_by = %s")
                params.append('XYZ')
            if new_password:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                update_fields.append("password = %s")
                params.append(hashed_pw)
            if update_fields:
                params.append(username)
                cursor.execute(
                    f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s",
                    tuple(params)
                )
                db.commit()
                st.success(f"User '{user_to_edit}' updated successfully!")
            else:
                st.info("No changes made.")