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
if 'name' not in st.session_state:
    authenticate_user()
if 'token' in st.session_state:
    st.query_params.token = st.session_state['token']

name = st.session_state['name']
role = st.session_state['role']
cursor = db.cursor()

# --- ADMIN PANEL UI ---
st.title("Admin Control Panel ⚙️")
st.write(f"<center><h2>Welcome, Admin {name}!</h2></center>", unsafe_allow_html=True)
st.write("---")

tab1, tab2 = st.tabs(["User & Team Management", "Evaluation Status Dashboard"])

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

    # CHECKLIST-CODE-STARTS-HERE
    st.markdown("---")
    # --- EVALUATION STATUS CHECKLIST ---
    st.markdown("## 📊 Evaluation Status Dashboard")

    # Custom CSS for the checklist
    st.markdown("""
    <style>
    .checklist-container {
        background: transparent;
        padding: 0px;
        border-radius: 0px;
        margin: 0px;
        box-shadow: none;
    }

    .manager-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 10px;
        padding: 1px;
        margin: 0px 0;
    }

    .employee-section {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1px;
        margin: 8px 0;
        margin-left: 20px;
    }

    .status-complete {
        color: #4CAF50;
        font-weight: bold;
    }

    .status-pending {
        color: #FF9800;
        font-weight: bold;
    }

    .status-not-started {
        color: #F44336;
        font-weight: bold;
    }

    .manager-title {
        color: #2E3440;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .employee-name {
        color: #2E3440;
        font-size: 16px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)


    # Fetch all managers and their employees
    cursor.execute("""
        SELECT DISTINCT managed_by 
        FROM users 
        WHERE managed_by IS NOT NULL AND managed_by != 'XYZ'
        ORDER BY managed_by
    """)
    managers = [row[0] for row in cursor.fetchall()]

    st.markdown('<div class="checklist-container">', unsafe_allow_html=True)

    for manager in managers:
        # Get manager's self-evaluation status (where rater = ratee)
        cursor.execute("""
            SELECT COUNT(DISTINCT criteria) 
            FROM user_ratings 
            WHERE rater = %s AND ratee = %s AND rating_type = 'self'
        """, (manager, manager))
        manager_self_eval_count = cursor.fetchone()[0]
        manager_self_eval = manager_self_eval_count > 0

        # Manager section
        st.markdown('<div class="manager-section">', unsafe_allow_html=True)

        manager_status = "✅ Complete" if manager_self_eval else "⏳ Pending"
        status_class = "status-complete" if manager_self_eval else "status-pending"

        st.markdown(f"""
        <div class="manager-title">
            👔 Manager: {manager}
        <div class="{status_class}">
            Self-Evaluation: {manager_status}
        </div>
        </div>
        """, unsafe_allow_html=True)

        # Get employees under this manager
        cursor.execute("""
            SELECT username 
            FROM users 
            WHERE managed_by = %s AND role = 'employee'
            ORDER BY username
        """, (manager,))
        employees = [row[0] for row in cursor.fetchall()]

        if employees:
            with st.expander(f"📋 Employees under {manager}"):
                for employee in employees:
                    # Check employee's self-evaluation status
                    cursor.execute("""
                        SELECT COUNT(DISTINCT criteria) 
                        FROM user_ratings 
                        WHERE rater = %s AND ratee = %s AND rating_type = 'self'
                    """, (employee, employee))
                    emp_self_eval_count = cursor.fetchone()[0]
                    emp_self_eval = emp_self_eval_count > 0

                    # Check if ANY manager has evaluated this employee
                    cursor.execute("""
                        SELECT COUNT(DISTINCT criteria) 
                        FROM user_ratings 
                        WHERE ratee = %s AND rating_type = 'manager'
                    """, (employee,))
                    manager_eval_ratings = cursor.fetchone()[0]

                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM remarks 
                        WHERE ratee = %s AND rating_type = 'manager'
                    """, (employee,))
                    manager_eval_remarks = cursor.fetchone()[0]

                    # Get the actual manager who evaluated (for display)
                    cursor.execute("""
                        SELECT rater 
                        FROM remarks 
                        WHERE ratee = %s AND rating_type = 'manager' 
                        LIMIT 1
                    """, (employee,))
                    actual_evaluator = cursor.fetchone()
                    evaluator_name = actual_evaluator[0] if actual_evaluator else manager

                    manager_eval = (manager_eval_ratings > 0) or (manager_eval_remarks > 0)

                    # Determine overall status
                    if emp_self_eval and manager_eval:
                        overall_status = "✅ Fully Complete"
                        status_class = "status-complete"
                        eval_text = f"Have been evaluated by manager {evaluator_name} too."
                    elif emp_self_eval and not manager_eval:
                        overall_status = "🔄 Self-Evaluation Done, Manager Pending"
                        status_class = "status-pending"
                        eval_text = f"Awaiting evaluation from manager {manager}."
                    elif not emp_self_eval and manager_eval:
                        overall_status = "🔄 Manager Done, Self-Evaluation Pending"
                        status_class = "status-pending"
                        eval_text = f"Have been evaluated by manager {evaluator_name}, but self-evaluation pending."
                    else:
                        overall_status = "❌ Not Started"
                        status_class = "status-not-started"
                        eval_text = f"No evaluations completed yet. Manager: {manager}"

                    st.markdown(f"""
                    <div class="employee-section">
                        <div class="employee-name">👤 {employee}</div>
                        <div class="{status_class}">{overall_status}</div>
                        <div style="color: #B0BEC5; font-size: 14px; margin-top: 5px;">
                            {eval_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


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
    st.switch_page("Home.py")