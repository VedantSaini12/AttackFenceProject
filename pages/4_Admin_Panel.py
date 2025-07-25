import streamlit as st
import mysql.connector as connector
import bcrypt
import datetime
from validators import validate_password, validate_email, validate_name, ALLOWED_DOMAINS
from utils import generate_random_password
from core.auth import protect_page, render_logout_button, get_db_connection, get_token_store
from core.constants import (
    foundational_criteria,
    futuristic_criteria,
    development_criteria,
    other_aspects_criteria,
    all_criteria_names
)

def generate_and_set_password(key):
    """Callback function to update the password in session state."""
    st.session_state[key] = generate_random_password()

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

protect_page(allowed_roles=["admin"])

db = get_db_connection()
token_store = get_token_store()

name = st.session_state['name']
role = st.session_state['role']
cursor = db.cursor(buffered=True)

with st.sidebar:
    st.title("Admin Panel ⚙️")
    st.write(f"Welcome, **{name}**")
    st.divider()
    
    # Use session state to keep track of the selected page
    if "admin_page" not in st.session_state:
        st.session_state.admin_page = "User Management"

    # Buttons to switch pages
    if st.button("👤 User & Team Management", use_container_width=True, type="primary" if st.session_state.admin_page == "User Management" else "secondary"):
        st.session_state.admin_page = "User Management"
        st.rerun()
        
    if st.button("📊 Evaluation Status Dashboard", use_container_width=True, type="primary" if st.session_state.admin_page == "Evaluation Dashboard" else "secondary"):
        st.session_state.admin_page = "Evaluation Dashboard"
        st.rerun()

    if st.button("📜 Evaluation History", use_container_width=True, type="primary" if st.session_state.admin_page == "History" else "secondary"):
        st.session_state.admin_page = "History"
        st.switch_page("pages/History.py")

    st.divider()

    # Place the logout logic directly in the sidebar
    if st.button("Logout", use_container_width=True):
        # This logic is copied from your core/auth.py
        token_store = get_token_store()
        token_to_remove = st.session_state.get("token")

        if token_to_remove and token_to_remove in token_store:
            del token_store[token_to_remove]

        st.session_state.clear()
        st.query_params.clear()
        st.switch_page("Home.py")

# --- PAGE CONTENT BASED ON SIDEBAR SELECTION ---

# --- USER MANAGEMENT PAGE ---
if st.session_state.admin_page == "User Management":
    st.header("Manage User Accounts and Teams")
    quarter_map = {
        1: "January - March",
        2: "April - June",
        3: "July - September",
        4: "October - December"
    }
    current_quarter = (datetime.datetime.now().month - 1) // 3 + 1
    current_months = quarter_map[current_quarter]
    st.info(f"🗓️ The current evaluation period is **Quarter {current_quarter}** ({current_months}).")
    # FROM YOUR CODE: Using your well-structured selectbox and logic for Create/Edit/Delete.
    option = st.selectbox(
        "Select an action",
        ("Create Employee/Manager", "Delete Employee/Manager", "Edit Employee/Manager")
    )
    st.divider()

    if option == "Create Employee/Manager":
        st.subheader("Create New Employee/Manager")

        def create_user_callback():
            """Callback to handle user creation with robust validation."""
            # Clear previous errors
            st.session_state.name_error = ""
            st.session_state.email_error = ""
            st.session_state.password_error = ""
            st.session_state.form_error = ""

            # Get values from session state
            name = st.session_state.new_user_name
            email_local = st.session_state.new_user_email_local
            email_domain = st.session_state.new_user_email_domain
            password = st.session_state.new_user_password
            create_role = st.session_state.new_user_role
            managed_by = st.session_state.get("new_user_managed_by")

            # Construct the full email address
            full_email = f"{email_local}@{email_domain}" if email_local and email_domain else ""

            # Perform validation
            is_name_valid = validate_name(name)
            is_email_valid = validate_email(full_email)
            password_errors = validate_password(password)

            if not (name and password and email_local and (create_role == "Manager" or (create_role == "Employee" and managed_by))):
                st.session_state.form_error = "Please fill all required fields."
            elif not is_name_valid:
                st.session_state.name_error = "Please enter a valid full name (letters and spaces only)."
            elif not is_email_valid:
                st.session_state.email_error = "Please enter a valid email address from an allowed domain."
            elif password_errors:
                st.session_state.password_error = " & ".join(password_errors)
            else:
                # Check if email already exists
                cursor.execute("SELECT email FROM users WHERE email = %s", (full_email,))
                if cursor.fetchone():
                    st.session_state.email_error = "An account with this email already exists."
                else:
                    # If all checks pass, create the user
                    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                    managed_by_value = 'XYZ' if create_role == "Manager" else managed_by
                    cursor.execute(
                        "INSERT INTO users (username, email, password, role, managed_by) VALUES (%s, %s, %s, %s, %s)",
                        (name, full_email, hashed_pw, create_role.lower(), managed_by_value)
                    )
                    db.commit()
                    st.session_state.show_success_dialog = True
                    st.session_state.success_message = f"{create_role} '{name}' created successfully!"
                    
                    # Clear input fields after success
                    st.session_state.new_user_name = ''
                    st.session_state.new_user_email_local = ''
                    st.session_state.new_user_password = ''


        # Initialize session state keys for the form
        for key in ['new_user_name', 'new_user_email_local', 'new_user_password', 'name_error', 'email_error', 'password_error', 'form_error']:
            if key not in st.session_state: st.session_state[key] = ''
        if 'new_user_role' not in st.session_state: st.session_state.new_user_role = 'Employee'
        if 'new_user_managed_by' not in st.session_state: st.session_state.new_user_managed_by = ''
        if 'new_user_email_domain' not in st.session_state: st.session_state.new_user_email_domain = ALLOWED_DOMAINS[0]


        st.text_input("Full Name", key='new_user_name', placeholder="Enter Full Name")
        if st.session_state.name_error:
            st.error(st.session_state.name_error)

        st.markdown("Assign an email")
        col1, col2 = st.columns([3, 2])
        with col1:
            st.text_input("Email Username", key='new_user_email_local', placeholder="Enter email username", label_visibility="collapsed")
        with col2:
            st.selectbox("Domain", options=ALLOWED_DOMAINS, key="new_user_email_domain", label_visibility="collapsed")

        if st.session_state.email_error:
            st.error(st.session_state.email_error)

        st.selectbox("Role", ("Employee", "Manager"), key='new_user_role')

        if st.session_state.new_user_role == "Employee":
            cursor.execute("SELECT username FROM users WHERE role = 'manager'")
            managers = [row[0] for row in cursor.fetchall()]
            if managers:
                st.selectbox("Managed By", managers, key='new_user_managed_by', index=0)
            else:
                st.warning("No managers available to assign.")

        pwd_col1, pwd_col2 = st.columns([5, 1.4])
        with pwd_col1:
            st.text_input("Password", type="password", key='new_user_password', placeholder="Enter password")
        with pwd_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("Generate Random", on_click=generate_and_set_password, args=('new_user_password',))
        
        if st.session_state.password_error:
            st.error(st.session_state.password_error)

        if st.session_state.form_error:
            st.error(st.session_state.form_error)

        st.button("Create User", on_click=create_user_callback, type="primary")

        # Success dialog logic (remains the same)
        if st.session_state.get("show_success_dialog"):
            @st.dialog("Confirmation")
            def show_dialog():
                st.success(st.session_state.get("success_message", "Success!"))
                if st.button("Close"):
                    st.session_state.show_success_dialog = False
                    st.rerun()
            show_dialog()
                
    elif option == "Delete Employee/Manager":
        st.subheader("Delete Employee/Manager")
        
        cursor.execute("SELECT username, role FROM users WHERE role != 'admin'")
        users = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]
        
        if not users:
            st.warning("No employees or managers available to delete.")
        else:
            user_to_delete = st.selectbox("Select user to delete", users)

            # This is the NEW code for the Delete button's "if" statement
            if st.button("Delete", type="primary"):
                username = user_to_delete.split(" (")[0]
                role = user_to_delete.split("(")[-1].replace(")", "").strip().lower()

                # --- 1. Safety Check for Managers ---
                if role == 'manager':
                    cursor.execute("SELECT COUNT(*) FROM users WHERE managed_by = %s", (username,))
                    # Assuming your cursor is not a dictionary cursor here
                    employee_count = cursor.fetchone()[0] 
                    if employee_count > 0:
                        st.error(f"Cannot delete '{username}'. They still manage {employee_count} employee(s). Please reassign them first.")
                        st.stop() # Stop execution

                # --- 2. Fetch User's Email BEFORE Deletion ---
                # We need this to clean up the login_attempts table.
                cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
                user_email_result = cursor.fetchone()
                user_email = user_email_result[0] if user_email_result else None

                # --- 3. Perform Cascading Deletes from All Related Tables ---
                st.write(f"Deleting all records for **{username}**...")

                cursor.execute("DELETE FROM user_ratings WHERE rater = %s OR ratee = %s", (username, username))
                cursor.execute("DELETE FROM remarks WHERE rater = %s OR ratee = %s", (username, username))
                cursor.execute("DELETE FROM notifications WHERE sender = %s OR recipient = %s", (username, username))

                # Delete login attempts for this user's email
                if user_email:
                    cursor.execute("DELETE FROM login_attempts WHERE email = %s", (user_email,))

                # --- 4. Final Step: Delete the User from the 'users' Table ---
                cursor.execute("DELETE FROM users WHERE username = %s", (username,))

                # --- 5. Commit the Transaction and Show Confirmation ---
                db.commit()
                st.success(f"User '{username}' and all their associated data have been permanently deleted.")
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
            new_name = st.text_input("Full Name", key=f"new_name_{original_username}")
            
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
                    if new_name and not validate_name(new_name):
                        st.error("Invalid Name: Please use letters and spaces only.")
                    else:
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
                    if new_name and not validate_name(new_name):
                        st.error("Invalid Name: Please use letters and spaces only.")
                    else:
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
                    if new_name and not validate_name(new_name):
                        st.error("Invalid Name: Please use letters and spaces only.")
                    else:
                        validation_errors = []
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
                            
# --- EVALUATION DASHBOARD PAGE ---
elif st.session_state.admin_page == "Evaluation Dashboard":
    st.header("Evaluation Status Dashboard")
    
    quarter_map = {
        1: "January - March",
        2: "April - June",
        3: "July - September",
        4: "October - December"
    }
    current_quarter = (datetime.datetime.now().month - 1) // 3 + 1
    current_months = quarter_map[current_quarter]
    st.info(f"🗓️ The current evaluation period is **Quarter {current_quarter}** ({current_months}).")

    # FROM HIS CODE: This dashboard logic is more detailed and robust.
    # It correctly calculates completion status against a total count.
    TOTAL_CRITERIA_COUNT = len(all_criteria_names)

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