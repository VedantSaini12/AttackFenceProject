<<<<<<< HEAD
import streamlit as st
import mysql.connector as connector
import bcrypt
import datetime
import uuid
import random
import string

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

# --- DATABASE AND TOKEN STORE (This part is crucial and must be in every file) ---
@st.cache_resource
def get_db_connection():
    try:
        return connector.connect(host="localhost", user="root", password="password", database="auth")
    except connector.Error:
        st.error("Database connection failed. Please contact an administrator.")
        st.stop()

@st.cache_resource
def get_token_store():
    return {}

db = get_db_connection()
token_store = get_token_store()

# --- START OF NEW, SECURE AUTHENTICATION GUARD ---
def authenticate_user():
    """
    Checks session state and URL token to authenticate the user.
    This function must be present in every protected page.
    """
    # 1. Check for a token in the URL's query parameters.
    if "token" in st.query_params:
        token = st.query_params["token"]
        
        # 2. Validate the token against the server-side token_store.
        if token in token_store:
            token_data = token_store[token]
            
            # 3. Check if the token has expired (e.g., 5-minute timeout).
            if datetime.datetime.now() - token_data['timestamp'] < datetime.timedelta(hours=24):
                # SUCCESS: Token is valid. Populate session state.
                st.session_state["name"] = token_data['username']
                st.session_state["role"] = token_data['role']
                st.session_state["token"] = token # Keep the token in the session
                return True
            else:
                # Token expired. Remove it from the store and URL.
                del token_store[token]
                st.query_params.clear()
        else:
            # Invalid token. Clear it from the URL.
             st.query_params.clear()

    # 4. If no valid token is found, deny access.
    st.error("🚨 Access Denied. Please log in first.")
    if st.button("Go to Login Page"):
        st.switch_page("Home.py")
    st.stop() # Halt execution of the page.

# Run the authentication check at the very start of the script.
if "name" not in st.session_state:
    authenticate_user()

# If authentication is successful, ensure the token remains in the URL.
if "token" in st.session_state:
    st.query_params.token = st.session_state["token"]

# Define session variables for easy use in the rest of the page
name = st.session_state["name"]
role = st.session_state["role"]
cursor = db.cursor()

# --- END OF THE NEW SECURE AUTHENTICATION GUARD ---

# --- ADMIN PANEL UI ---
st.title("Admin Control Panel ⚙️")
st.write(f"<center><h2>Welcome, Admin {name}!</h2></center>", unsafe_allow_html=True)
st.write("---")

# Tabbed interface for better organization
tab1, tab2 = st.tabs(["User & Team Management", "View All Evaluations"])

with tab1:
    st.header("Manage User Accounts and Teams")
    # The user management logic from your original Admin.py goes here.
    # This includes the selectbox for Create/Delete/Edit actions and the forms for each.
    # ...
    # (The full user management code from your old Admin.py is assumed here)
    # ...
    option = st.selectbox(
    "Select an action",
    ("Create Employee/Manager", "Delete Employee/Manager", "Edit Employee/Manager")
    )
    st.write("---")
    if option == "Create Employee/Manager":
        st.subheader("Create New Employee/Manager")

        # --- NEW, CONSOLIDATED CALLBACK FUNCTION ---
        def create_user_callback():
            # 1. Read values directly from session state inside the callback
            name = st.session_state.new_user_name
            email = st.session_state.new_user_email
            password = st.session_state.new_user_password
            create_role = st.session_state.new_user_role
            managed_by = st.session_state.get("new_user_managed_by") # Use .get() for safety

            # 2. Perform validation
            if name and password and email and (create_role == "Manager" or (create_role == "Employee" and managed_by)):
                # 3. If validation passes, run the database logic
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                if create_role == "Employee":
                    cursor.execute(
                        "INSERT INTO users (username, email, password, role, managed_by) VALUES (%s, %s, %s, %s, %s)",
                        (name, email, hashed_pw, create_role.lower(), managed_by)
                    )
                else: # Manager
                    cursor.execute(
                        "INSERT INTO users (username, email, password, role, managed_by) VALUES (%s, %s, %s, %s, %s)",
                        (name, email, hashed_pw, create_role.lower(), 'XYZ')
                    )
                db.commit()
                
                # Show success message
                st.session_state.show_success_dialog = True
                st.session_state.success_message = f"{create_role} '{name}' created successfully!"
                
                # 4. Clear the input fields in session state for the next entry
                st.session_state.new_user_name = ''
                st.session_state.new_user_email = ''
                st.session_state.new_user_password = ''
                st.session_state.new_user_role = 'Employee'
                if 'new_user_managed_by' in st.session_state:
                    st.session_state.new_user_managed_by = None
            else:
                # If validation fails, show an error message.
                st.error("Please enter all fields.")

        # Initialize session state if it doesn't exist
        if 'new_user_name' not in st.session_state:
            st.session_state.new_user_name = ''
            st.session_state.new_user_role = 'Employee'
            st.session_state.new_user_email = ''
            st.session_state.new_user_password = ''
            st.session_state.new_user_managed_by = ''
        
        # --- WIDGETS ---
        st.text_input("Name", key='new_user_name', placeholder="Enter name")
        st.text_input("Assign an email", key='new_user_email', placeholder="Enter email")
        st.selectbox("Role", ("Employee", "Manager"), key='new_user_role')

        # Manager selection logic
        if st.session_state.new_user_role == "Employee":
            cursor.execute("SELECT username FROM users WHERE role = 'manager'")
            managers = [row[0] for row in cursor.fetchall()]
            if managers:
                current_manager_index = managers.index(st.session_state.new_user_managed_by) if st.session_state.new_user_managed_by in managers else 0
                st.selectbox("Managed By", managers, key='new_user_managed_by', index=current_manager_index)
            else:
                st.warning("No managers available. Please create a manager first.")

        def generate_random_password(length=8):
            chars = string.ascii_letters + string.digits
            return ''.join(random.choices(chars, k=length))

        col1, col2 = st.columns([5, 1])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some space
            if st.button("Generate Random Password", type="primary"):
                # Only update session state and rerun, do not update after widget instantiation
                st.session_state.new_user_password = generate_random_password()
                st.rerun()
        with col1:
            password_input = st.text_input(
                "Password",
                type="password",
                key='new_user_password',
                placeholder="Enter password"
            )

        # --- BUTTON ---
        # The button's only job is to trigger the comprehensive callback.
        st.button("Create", on_click=create_user_callback)
        
        # Dialog logic moved outside the callback
        if st.session_state.get("show_success_dialog"):
            @st.dialog("Confirmation")
            def show_dialog():
                st.success(st.session_state.get("success_message", "Created Successfully!"))
                if st.button("Close"):
                    st.rerun()
            show_dialog()
            # Reset the dialog flag
            st.session_state.show_success_dialog = False
                
    elif option == "Delete Employee/Manager":
        st.subheader("Delete Employee/Manager")
        
        cursor.execute("SELECT username, role FROM users WHERE role != 'admin'")
        users = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]
        
        if not users:
            st.warning("No employees or managers available to delete.")
        else:
            user_to_delete = st.selectbox("Select user to delete", users)

            if st.button("Delete", type="primary"):
                # Extract username and role from the selected string
                username = user_to_delete.split(" (")[0]
                role = user_to_delete.split("(")[-1].replace(")", "").strip().lower()

                # --- NEW LOGIC ---
                # First, check if the user is a manager
                if role == 'manager':
                    # If they are a manager, check if they have any employees
                    cursor.execute("SELECT COUNT(*) FROM users WHERE managed_by = %s", (username,))
                    employee_count = cursor.fetchone()[0]
                    
                    if employee_count > 0:
                        # If they have employees, block the deletion and show an error
                        st.error(f"Cannot delete '{username}'. They still manage {employee_count} employee(s). Please edit and reassign their employees to another manager first.")
                    else:
                        # If they have no employees, it's safe to delete them
                        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
                        db.commit()
                        st.session_state['show_delete_dialog'] = True
                        st.session_state['delete_message'] = f"Manager '{username}' has been deleted successfully."
                        st.rerun()
                else:
                    # If the user is an employee, it's safe to delete them directly
                    cursor.execute("DELETE FROM users WHERE username = %s", (username,)) #
                    db.commit()
                    st.session_state['show_delete_dialog'] = True
                    st.session_state['delete_message'] = f"Employee '{username}' has been deleted successfully."
                    st.rerun()

        # Show modal dialog if deletion was successful
        if st.session_state.get("show_delete_dialog"):
            @st.dialog("Confirmation")
            def show_delete_dialog():
                st.success(st.session_state.get("delete_message", "User deleted successfully!"))
                if st.button("Close"):
                    st.session_state["show_delete_dialog"] = False
                    st.rerun()
            show_delete_dialog()

    elif option == "Edit Employee/Manager":
        st.subheader("Edit Employee/Manager Details")
        # Replace with actual employee/manager list from your database
        
        cursor.execute("SELECT username, role FROM users")
        users = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]
        user_to_edit = st.selectbox("Select user to edit", users)

        # Extract original username and role correctly
        original_username = user_to_edit.split(" (")[0]
        role = user_to_edit.split("(")[-1].replace(")", "").strip().lower()

        new_name = st.text_input("New Name", key=f"new_name_{original_username}")
        new_password = st.text_input("New Password", type="password", key=f"new_password_{original_username}")

        update_fields = []
        params = []

        if role == "admin":
            # Only allow name and password change for admin
            if st.button("Update"):
                if new_name:
                    update_fields.append("username = %s")
                    params.append(new_name)
                if new_password:
                    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                    update_fields.append("password = %s")
                    params.append(hashed_pw)
                if update_fields:
                    params.append(original_username)
                    cursor.execute(
                        f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s",
                        tuple(params)
                    )
                    db.commit()
                if new_name and new_name != original_username:
                    cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_username))
                    cursor.execute("UPDATE user_ratings SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                    cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_username))
                    cursor.execute("UPDATE remarks SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                    db.commit()
                    st.success(f"Admin '{user_to_edit}' updated successfully!")
                else:
                    st.info("No changes made.")
        elif role == "manager":
            # Only allow name and password change for manager, managed_by is set to 'XYZ'
            if st.button("Update"):
                if new_name:
                    update_fields.append("username = %s")
                    params.append(new_name)
                if new_password:
                    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                    update_fields.append("password = %s")
                    params.append(hashed_pw)
                # Always set managed_by to 'XYZ' for managers
                update_fields.append("managed_by = %s")
                params.append('XYZ')
                if update_fields:
                    params.append(original_username)
                    cursor.execute(
                        f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s",
                        tuple(params)
                    )
                    db.commit()
                    if new_name and new_name != original_username:
                        cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_username))
                        cursor.execute("UPDATE user_ratings SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                        cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_username))
                        cursor.execute("UPDATE remarks SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                        db.commit()
                    if new_name and new_name != original_username:
                        cursor.execute(
                            "UPDATE users SET managed_by = %s WHERE managed_by = %s",
                            (new_name, original_username)
                        )
                        db.commit()
                        if new_name and new_name != original_username:
                            cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_username))
                            cursor.execute("UPDATE user_ratings SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                            cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_username))
                            cursor.execute("UPDATE remarks SET ratee = %s WHERE ratee = %s", (new_name, original_username))
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
                    update_fields.append("username = %s")
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
                    params.append(original_username)
                    cursor.execute(
                        f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s",
                        tuple(params)
                    )
                    db.commit()
                    if new_name and new_name != original_username:
                        cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_username))
                        cursor.execute("UPDATE user_ratings SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                        cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_username))
                        cursor.execute("UPDATE remarks SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                        db.commit()
                    st.success(f"User '{user_to_edit}' updated successfully!")
                else:
                    st.info("No changes made.")

with tab2:
    st.header("View All Employee & Manager Evaluations")
    # This is where we implement the Admin's read-only view, as per your requirements.
    st.info("As an Admin, you can view all evaluation data. Use the search below to find a user.")
    
    cursor.execute("SELECT email, username, role, managed_by FROM users WHERE role != 'admin'")
    all_users = cursor.fetchall()
    
    search_query = st.text_input("🔍 Search Any User by Name", key="admin_search")
    
    if search_query:
        filtered_users = [
            u for u in all_users 
            if search_query.lower() in u[1].lower()
        ]
    else:
        filtered_users = all_users

    # --- PAGINATION LOGIC ---
    USERS_PER_PAGE = 6
    total_users = len(filtered_users)
    total_pages = (total_users - 1) // USERS_PER_PAGE + 1 if total_users else 1

    page_number = st.session_state.get("admin_user_page", 1)
    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        if st.button("⬅️ Prev", disabled=page_number <= 1,use_container_width=True):
            st.session_state["admin_user_page"] = max(1, page_number - 1)
            st.rerun()
    with col2:
        st.markdown(f"<center>Page {page_number} of {total_pages}</center>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ➡️", disabled=page_number >= total_pages, use_container_width=True):
            st.session_state["admin_user_page"] = min(total_pages, page_number + 1)
            st.rerun()

    start_idx = (page_number - 1) * USERS_PER_PAGE
    end_idx = start_idx + USERS_PER_PAGE
    paginated_users = filtered_users[start_idx:end_idx]

    for user_data in paginated_users:
        emp_email, emp_name, emp_role, emp_manager = user_data
        with st.expander(f"**{emp_name}** ({emp_role.title()}) - Managed by: {emp_manager}"):
            if st.button("View Full Evaluation Report", key=f"view_{emp_email}"):
                st.session_state['selected_employee'] = emp_name
                st.switch_page("pages/Rating.py")

# --- LOGOUT BUTTON ---
st.write("---")
if st.button("Logout", type="primary"):
    # Get the token from session state before clearing it
    token_to_remove = st.session_state.get("token")
    
    # Remove the token from the server-side store if it exists
    if token_to_remove and token_to_remove in token_store:
        del token_store[token_to_remove]
    
    # Clear the session state and URL
    st.session_state.clear()
    st.query_params.clear()
=======
import streamlit as st
import mysql.connector as connector
import bcrypt
import datetime
import uuid
import random
import string
from validators import validate_password, validate_email
from utils import generate_random_password

def generate_and_set_password(key):
    """Callback function to update the password in session state."""
    st.session_state[key] = generate_random_password()

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

# --- DATABASE AND TOKEN STORE (This part is crucial and must be in every file) ---
@st.cache_resource
def get_db_connection():
    try:
        return connector.connect(host="localhost", user="root", password="password", database="auth")
    except connector.Error:
        st.error("Database connection failed. Please contact an administrator.")
        st.stop()

@st.cache_resource
def get_token_store():
    return {}

db = get_db_connection()
token_store = get_token_store()

# --- START OF NEW, SECURE AUTHENTICATION GUARD ---
def authenticate_user():
    """
    Checks session state and URL token to authenticate the user.
    This function must be present in every protected page.
    """
    # 1. Check for a token in the URL's query parameters.
    if "token" in st.query_params:
        token = st.query_params["token"]
        
        # 2. Validate the token against the server-side token_store.
        if token in token_store:
            token_data = token_store[token]
            
            # 3. Check if the token has expired (e.g., 5-minute timeout).
            if datetime.datetime.now() - token_data['timestamp'] < datetime.timedelta(hours=24):
                # SUCCESS: Token is valid. Populate session state.
                st.session_state["name"] = token_data['username']
                st.session_state["role"] = token_data['role']
                st.session_state["token"] = token # Keep the token in the session
                return True
            else:
                # Token expired. Remove it from the store and URL.
                del token_store[token]
                st.query_params.clear()
        else:
            # Invalid token. Clear it from the URL.
             st.query_params.clear()

    # 4. If no valid token is found, deny access.
    st.error("🚨 Access Denied. Please log in first.")
    if st.button("Go to Login Page"):
        st.switch_page("Home.py")
    st.stop() # Halt execution of the page.

# Run the authentication check at the very start of the script.
if "name" not in st.session_state:
    authenticate_user()

# If authentication is successful, ensure the token remains in the URL.
if "token" in st.session_state:
    st.query_params.token = st.session_state["token"]

# Define session variables for easy use in the rest of the page
name = st.session_state["name"]
role = st.session_state["role"]
cursor = db.cursor()

# --- END OF THE NEW SECURE AUTHENTICATION GUARD ---

# --- ADMIN PANEL UI ---
st.title("Admin Control Panel ⚙️")
st.write(f"<center><h2>Welcome, Admin {name}!</h2></center>", unsafe_allow_html=True)
st.write("---")

# Tabbed interface for better organization
tab1, tab2 = st.tabs(["User & Team Management", "View All Evaluations"])

with tab1:
    st.header("Manage User Accounts and Teams")
    # The user management logic from your original Admin.py goes here.
    # This includes the selectbox for Create/Delete/Edit actions and the forms for each.
    # ...
    # (The full user management code from your old Admin.py is assumed here)
    # ...
    option = st.selectbox(
    "Select an action",
    ("Create Employee/Manager", "Delete Employee/Manager", "Edit Employee/Manager")
    )
    st.write("---")
    if option == "Create Employee/Manager":
        st.subheader("Create New Employee/Manager")

        # --- UPDATED CALLBACK FUNCTION ---
        # This function now writes errors to session_state instead of calling st.error()
        def create_user_callback():
            # Clear previous errors first
            st.session_state.email_error = ""
            st.session_state.password_error = ""
            st.session_state.form_error = ""

            name = st.session_state.new_user_name
            email = st.session_state.new_user_email
            password = st.session_state.new_user_password
            create_role = st.session_state.new_user_role
            managed_by = st.session_state.get("new_user_managed_by")

            is_email_valid = validate_email(email)
            password_errors = validate_password(password)

            if not (name and password and email and (create_role == "Manager" or (create_role == "Employee" and managed_by))):
                st.session_state.form_error = "Please fill all fields."
            elif not is_email_valid:
                st.session_state.email_error = "Please enter a valid email address."
            elif password_errors:
                st.session_state.password_error = " & ".join(password_errors)
            else:
                cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    st.session_state.email_error = "An account with this email already exists."
                else:
                    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                    managed_by_value = 'XYZ' if create_role == "Manager" else managed_by
                    cursor.execute(
                        "INSERT INTO users (username, email, password, role, managed_by) VALUES (%s, %s, %s, %s, %s)",
                        (name, email, hashed_pw, create_role.lower(), managed_by_value)
                    )
                    db.commit()
                    st.session_state.show_success_dialog = True
                    st.session_state.success_message = f"{create_role} '{name}' created successfully!"
                    # Clear input fields after success
                    st.session_state.new_user_name, st.session_state.new_user_email, st.session_state.new_user_password = '', '', ''

        # Initialize session state keys
        for key in ['new_user_name', 'new_user_email', 'new_user_password', 'email_error', 'password_error', 'form_error']:
            if key not in st.session_state: st.session_state[key] = ''
        if 'new_user_role' not in st.session_state: st.session_state.new_user_role = 'Employee'
        if 'new_user_managed_by' not in st.session_state: st.session_state.new_user_managed_by = ''

        # --- WIDGETS WITH ERROR DISPLAYS ---
        st.text_input("Name", key='new_user_name', placeholder="Enter name")

        st.text_input("Assign an email", key='new_user_email', placeholder="Enter email")
        if st.session_state.email_error:
            st.error(st.session_state.email_error) # Display email error here

        st.selectbox("Role", ("Employee", "Manager"), key='new_user_role')

        if st.session_state.new_user_role == "Employee":
            cursor.execute("SELECT username FROM users WHERE role = 'manager'")
            managers = [row[0] for row in cursor.fetchall()]
            if managers:
                st.selectbox("Managed By", managers, key='new_user_managed_by', index=0)
            else:
                st.warning("No managers available to assign.")

        col1, col2 = st.columns([5, 1.4])
        with col1:
            st.text_input("Password", type="password", key='new_user_password', placeholder="Enter password")
        with col2:
            st.button("Generate Random", on_click=generate_and_set_password, args=('new_user_password',))
        
        if st.session_state.password_error:
            st.error(st.session_state.password_error) # Display password error here

        if st.session_state.form_error:
            st.error(st.session_state.form_error) # Display general form error here

        st.button("Create User", on_click=create_user_callback, type="primary")

        # Success dialog logic
        if st.session_state.get("show_success_dialog"):
            @st.dialog("Confirmation")
            def show_dialog():
                st.success(st.session_state.get("success_message", "Success!"))
                if st.button("Close"):
                    st.session_state.show_success_dialog = False
                    st.rerun()
            show_dialog()
            # Reset the dialog flag
                
    elif option == "Delete Employee/Manager":
        st.subheader("Delete Employee/Manager")
        
        cursor.execute("SELECT username, role FROM users WHERE role != 'admin'")
        users = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]
        
        if not users:
            st.warning("No employees or managers available to delete.")
        else:
            user_to_delete = st.selectbox("Select user to delete", users)

            if st.button("Delete", type="primary"):
                # Extract username and role from the selected string
                username = user_to_delete.split(" (")[0]
                role = user_to_delete.split("(")[-1].replace(")", "").strip().lower()

                # --- NEW LOGIC ---
                # First, check if the user is a manager
                if role == 'manager':
                    # If they are a manager, check if they have any employees
                    cursor.execute("SELECT COUNT(*) FROM users WHERE managed_by = %s", (username,))
                    employee_count = cursor.fetchone()[0]
                    
                    if employee_count > 0:
                        # If they have employees, block the deletion and show an error
                        st.error(f"Cannot delete '{username}'. They still manage {employee_count} employee(s). Please edit and reassign their employees to another manager first.")
                    else:
                        # If they have no employees, it's safe to delete them
                        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
                        db.commit()
                        st.success(f"Manager '{username}' has been deleted successfully.")
                        st.rerun()
                else:
                    # If the user is an employee, it's safe to delete them directly
                    cursor.execute("DELETE FROM users WHERE username = %s", (username,)) #
                    db.commit()
                    st.success(f"Employee '{username}' has been deleted successfully.")
                    st.rerun()

    elif option == "Edit Employee/Manager":
        st.subheader("Edit Employee/Manager Details")
        
        cursor.execute("SELECT username, role FROM users")
        users = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]

        # First, check if there are any users in the list to edit
        if not users:
            st.warning("There are no users available to edit.")
        else:
            user_to_edit = st.selectbox("Select user to edit", users)

            # --- THIS IS THE CORRECT PLACEMENT ---
            # Define these variables right after the selectbox. This ensures they always exist.
            original_username = user_to_edit.split(" (")[0]
            role = user_to_edit.split("(")[-1].replace(")", "").strip().lower()

            # All the input widgets follow
            new_name = st.text_input("New Name", key=f"new_name_{original_username}")
            
            pwd_key = f"new_password_{original_username}"
            if pwd_key not in st.session_state:
                st.session_state[pwd_key] = ""

            col1, col2 = st.columns([4, 1])
            with col1:
                new_password = st.text_input("New Password (leave blank to keep unchanged)", type="password", key=pwd_key)
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.button(
                    "Generate",
                    key=f"gen_{pwd_key}",
                    on_click=generate_and_set_password,
                    args=(pwd_key,)
                )

            update_fields = []
            params = []

            if role == "admin":
                # Only allow name and password change for admin
                if st.button("Update", key=f"update_admin_{original_username}"):
                    validation_errors = []
                    if new_password:
                        validation_errors = validate_password(new_password)

                    if validation_errors:
                        for error in validation_errors:
                            st.error(f"Password Error: {error}")
                    else:
                        if new_name:
                            update_fields.append("username = %s")
                            params.append(new_name)
                        if new_password:
                            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                            update_fields.append("password = %s")
                            params.append(hashed_pw)

                        if update_fields:
                            params.append(original_username)
                            # Update the main user details
                            cursor.execute(f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s", tuple(params))
                            db.commit()

                            # If the name changed, update related records
                            if new_name and new_name != original_username:
                                cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_username))
                                cursor.execute("UPDATE user_ratings SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                                cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_username))
                                cursor.execute("UPDATE remarks SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                                db.commit()

                            st.success(f"Admin '{user_to_edit}' updated successfully!")
                            st.rerun()
                        else:
                            st.info("No changes were made.")
            elif role == "manager":
                # Allow name and password change for manager
                if st.button("Update", key=f"update_mgr_{original_username}"):
                    validation_errors = []
                    if new_password:
                        validation_errors = validate_password(new_password)

                    if validation_errors:
                        for error in validation_errors:
                            st.error(f"Password Error: {error}")
                    else:
                        if new_name:
                            update_fields.append("username = %s")
                            params.append(new_name)
                        if new_password:
                            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                            update_fields.append("password = %s")
                            params.append(hashed_pw)

                        if update_fields:
                            params.append(original_username)
                            cursor.execute(f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s", tuple(params))
                            db.commit()

                            # If the manager's name was changed, update it for their employees
                            if new_name and new_name != original_username:
                                cursor.execute("UPDATE users SET managed_by = %s WHERE managed_by = %s", (new_name, original_username))
                                cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_username))
                                cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_username))
                                db.commit()

                            st.success(f"Manager '{user_to_edit}' updated successfully!")
                            st.rerun()
                        else:
                            st.info("No changes made.")
            else:
                # This block handles users with the 'employee' role
                new_role = st.selectbox("New Role", ("Employee", "Manager"), key=f"role_{original_username}")

                # Fetch all managers for reassignment if the role is 'Employee'
                cursor.execute("SELECT username FROM users WHERE role = 'manager'")
                managers = [row[0] for row in cursor.fetchall()]
                new_managed_by = None

                if new_role == "Employee":
                    if managers:
                        # Get the employee's current manager to set as the default
                        cursor.execute("SELECT managed_by FROM users WHERE username = %s", (original_username,))
                        current_manager_result = cursor.fetchone()
                        current_manager = current_manager_result[0] if current_manager_result else None
                        manager_index = managers.index(current_manager) if current_manager in managers else 0

                        new_managed_by = st.selectbox("Managed By", managers, key="edit_managed_by", index=manager_index)
                    else:
                        st.warning("No managers available. Please create a manager first.")

                if st.button("Update", key=f"update_employee_{original_username}"):
                    validation_errors = []
                    # 1. VALIDATE PASSWORD (only if a new one is entered)
                    if new_password:
                        validation_errors = validate_password(new_password)

                    if validation_errors:
                        for error in validation_errors:
                            st.error(f"Password Error: {error}")
                    else:
                        # 2. PROCEED WITH DATABASE UPDATE
                        if new_name:
                            update_fields.append("username = %s")
                            params.append(new_name)
                        if new_role:
                            update_fields.append("role = %s")
                            params.append(new_role.lower()) # Ensure role is lowercase
                        if new_role == "Employee" and new_managed_by:
                            update_fields.append("managed_by = %s")
                            params.append(new_managed_by)
                        elif new_role == "Manager":
                            update_fields.append("managed_by = %s")
                            params.append('XYZ') # Managers are assigned 'XYZ'
                        if new_password:
                            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                            update_fields.append("password = %s")
                            params.append(hashed_pw)

                        if update_fields:
                            params.append(original_username)
                            query = f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s"
                            cursor.execute(query, tuple(params))
                            db.commit()

                            # Update related records if the username changed
                            if new_name and new_name != original_username:
                                cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_username))
                                cursor.execute("UPDATE user_ratings SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                                cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_username))
                                cursor.execute("UPDATE remarks SET ratee = %s WHERE ratee = %s", (new_name, original_username))
                                db.commit()

                            st.success(f"User '{user_to_edit}' updated successfully!")
                            st.rerun() # Refresh the page to show updated info
                        else:
                            st.info("No changes were made.")
with tab2:
    st.header("View All Employee & Manager Evaluations")
    # This is where we implement the Admin's read-only view, as per your requirements.
    st.info("As an Admin, you can view all evaluation data. Use the search below to find a user.")
    
    cursor.execute("SELECT email, username, role, managed_by FROM users WHERE role != 'admin'")
    all_users = cursor.fetchall()
    
    search_query = st.text_input("🔍 Search Any User by Name or Email", key="admin_search")
    
    if search_query:
        filtered_users = [
            u for u in all_users 
            if search_query.lower() in u[1].lower() or search_query.lower() in u[0].lower()
        ]
    else:
        filtered_users = all_users

    # --- PAGINATION LOGIC ---
    USERS_PER_PAGE = 6
    total_users = len(filtered_users)
    total_pages = (total_users + USERS_PER_PAGE - 1) // USERS_PER_PAGE if total_users > 0 else 1

    if "admin_user_page" not in st.session_state:
        st.session_state.admin_user_page = 1
    page_number = st.session_state.admin_user_page

    start_idx = (page_number - 1) * USERS_PER_PAGE
    end_idx = start_idx + USERS_PER_PAGE
    paginated_users = filtered_users[start_idx:end_idx]

    for user_data in paginated_users:
        emp_email, emp_name, emp_role, emp_manager = user_data
        with st.expander(f"**{emp_name}** ({emp_role.title()}) - Managed by: {emp_manager}"):
            if st.button("View Full Evaluation Report", key=f"view_{emp_email}"):
                st.session_state['selected_employee'] = emp_name
                st.switch_page("pages/Rating.py")

    st.write("---")
    # Display pagination controls at the bottom
    col1, col2, col3 = st.columns([2, 5, 2])
    with col1:
        if st.button("⬅️ Previous", disabled=(page_number <= 1), use_container_width=True):
            st.session_state.admin_user_page -= 1
            st.rerun()
    with col2:
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Page {page_number} of {total_pages}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ➡️", disabled=(page_number >= total_pages), use_container_width=True):
            st.session_state.admin_user_page += 1
            st.rerun()

# --- LOGOUT BUTTON ---
st.write("---")
if st.button("Logout", type="primary"):
    # Get the token from session state before clearing it
    token_to_remove = st.session_state.get("token")
    
    # Remove the token from the server-side store if it exists
    if token_to_remove and token_to_remove in token_store:
        del token_store[token_to_remove]
    
    # Clear the session state and URL
    st.session_state.clear()
    st.query_params.clear()
>>>>>>> ad36bc2ce526f9155ff92c7da963ce122d333d69
    st.switch_page("Home.py")