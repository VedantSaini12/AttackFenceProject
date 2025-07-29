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
email = st.session_state["email"]
role = st.session_state['role']
cursor = db.cursor()

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
                # Check if email exists and get its dormant status
                cursor.execute("SELECT is_dormant FROM users WHERE email = %s", (full_email,))
                user_status = cursor.fetchone()

                if user_status:
                    # --- Case 1: User Exists ---
                    is_dormant = user_status[0]
                    
                    if is_dormant:
                        # --- REACTIVATE AND UPDATE THE DORMANT ACCOUNT ---
                        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                        managed_by_value = 'XYZ' if create_role == "Manager" else managed_by

                        # The "username = %s" part has been REMOVED from the query
                        cursor.execute(
                            """
                            UPDATE users 
                            SET 
                                is_dormant = FALSE, 
                                password = %s, 
                                role = %s, 
                                managed_by = %s
                            WHERE email = %s
                            """,
                            (hashed_pw, create_role.lower(), managed_by_value, full_email)
                        )
                        db.commit()
                        # Also update the success message for clarity
                        st.session_state.success_message = f"Dormant account for email '{full_email}' has been reactivated!"
                        st.session_state.show_success_dialog = True

                        # Clear input fields after success
                        st.session_state.new_user_name = ''
                        st.session_state.new_user_email_local = ''
                        st.session_state.new_user_password = ''

                    else:
                        # --- BLOCK: User exists and is already active ---
                        st.session_state.email_error = "An account with this email already exists."

                else:
                    # --- Case 2: User Does Not Exist, CREATE NEW ---
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
        
        cursor.execute("SELECT username, role FROM users WHERE role != 'admin' AND is_dormant = FALSE")
        users = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]
        
        if not users:
            st.warning("No employees or managers available to delete.")
        else:
            user_to_delete = st.selectbox("Select user to delete", users)

            # This is the NEW code for the Delete button's "if" statement
            if st.button("Deactivate Account", type="primary"):
                username = user_to_delete.split(" (")[0]
                role = user_to_delete.split("(")[-1].replace(")", "").strip().lower()

                # --- 1. Safety Check for Managers ---
                if role == 'manager':
                    # Check for ACTIVE employees managed by this person
                    cursor.execute("SELECT COUNT(*) FROM users WHERE managed_by = %s AND is_dormant = FALSE", (username,))
                    employee_count = cursor.fetchone()[0]
                    
                    if employee_count > 0:
                        st.error(f"Cannot deactivate '{username}'. They still manage {employee_count} active employee(s). Please reassign them first.")
                        st.stop() # Stop execution

                # --- 2. If the check passes, proceed with deactivation ---
                st.write(f"Deactivating account for **{username}**...")

                # Set the user's status to dormant instead of deleting
                cursor.execute("UPDATE users SET is_dormant = TRUE WHERE username = %s", (username,))

                # --- 3. Commit the Transaction and Show Confirmation ---
                db.commit()
                st.success(f"User account for '{username}' has been successfully deactivated. Their history is preserved.")
                st.rerun()

    elif option == "Edit Employee/Manager":
        st.subheader("Edit Employee/Manager Details")
        
        # Corrected Query: Now includes the 'admin' role for editing
        cursor.execute("SELECT username, email, role FROM users WHERE is_dormant = FALSE")
        all_users_data = cursor.fetchall()
        
        if not all_users_data:
            st.warning("There are no users available to edit.")
        else:
            user_options = {
                f"{username} ({role})": (username, email, role)
                for username, email, role in all_users_data
            }

            selected_display_name = st.selectbox("Select user to edit", user_options.keys())
            
            original_username, original_email, original_role = user_options[selected_display_name]

            # --- Input Fields for Editing ---
            new_name = st.text_input("Full Name", value=original_username, key=f"name_{original_email}")
            
            pwd_key = f"pwd_{original_email}"
            col1, col2 = st.columns([4, 1.4])
            with col1:
                new_password = st.text_input("New Password (leave blank to keep unchanged)", type="password", key=pwd_key)
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.button("Generate", key=f"gen_{pwd_key}", on_click=generate_and_set_password, args=(pwd_key,))

            # --- Role and Manager Assignment (Disabled for Admin) ---
            if original_role != 'admin':
                if original_role in ["employee", "manager", "hr"]:
                    new_role = st.selectbox(
                        "Role", ["employee", "manager", "hr"], 
                        index=["employee", "manager", "hr"].index(original_role), 
                        key=f"role_{original_email}"
                    )
                else:
                    new_role = original_role

                new_manager_username = None
                if new_role == "employee":
                    cursor.execute("SELECT username FROM users WHERE role = 'manager'")
                    managers = [row[0] for row in cursor.fetchall()]
                    if managers:
                        cursor.execute("SELECT managed_by FROM users WHERE email = %s", (original_email,))
                        current_manager = cursor.fetchone()[0]
                        manager_index = managers.index(current_manager) if current_manager in managers else 0
                        new_manager_username = st.selectbox("Managed By", managers, key=f"mgr_{original_email}", index=manager_index)
            else:
                # For admin, role and manager are not editable
                st.text(f"Role: {original_role.title()} (Cannot be changed)")
                new_role = original_role

            # --- Update Button Logic ---
            if st.button("Update User", key=f"update_{original_email}", type="primary"):
                if not validate_name(new_name):
                    st.error("Invalid Name: Please use letters and spaces only.")
                elif new_password and validate_password(new_password):
                    st.error(f"Password Error: {' & '.join(validate_password(new_password))}")
                else:
                    update_fields = []
                    params = []

                    if new_name != original_username:
                        update_fields.append("username = %s")
                        params.append(new_name)
                    
                    if new_password:
                        hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                        update_fields.append("password = %s")
                        params.append(hashed_pw)

                    # Only add role/manager updates if not an admin
                    if original_role != 'admin':
                        if new_role != original_role:
                            update_fields.append("role = %s")
                            params.append(new_role.lower())
                        
                        if new_role == 'employee' and new_manager_username:
                            update_fields.append("managed_by = %s")
                            params.append(new_manager_username)
                        elif new_role == 'manager':
                            update_fields.append("managed_by = %s")
                            params.append('XYZ')

                    if update_fields:
                        params.append(original_email) # Use email as the WHERE condition
                        query = f"UPDATE users SET {', '.join(update_fields)} WHERE email = %s"
                        cursor.execute(query, tuple(params))
                        db.commit()
                        
                        if new_name != original_username and original_role == 'manager':
                            cursor.execute("UPDATE users SET managed_by = %s WHERE managed_by = %s", (new_name, original_username))
                            db.commit()
                        
                        st.success(f"User '{new_name}' updated successfully!")
                        st.rerun()
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
    cursor.execute("SELECT username, email FROM users WHERE role = 'manager' ORDER BY username")
    managers = cursor.fetchall()

    st.markdown('<div class="checklist-container">', unsafe_allow_html=True)

    for manager_name, manager_email in managers:
        # Get manager's self-evaluation status using their EMAIL
        cursor.execute("""
            SELECT COUNT(DISTINCT criteria) 
            FROM user_ratings 
            WHERE rater = %s AND ratee = %s AND rating_type = 'self'
        """, (manager_email, manager_email))
        manager_self_eval = cursor.fetchone()[0] > 0
        
        # --- Manager Section Display (remains mostly the same) ---
        st.markdown('<div class="manager-section">', unsafe_allow_html=True)
        manager_status = "✅ Complete" if manager_self_eval else "⏳ Pending"
        status_class = "status-complete" if manager_self_eval else "status-pending"
        st.markdown(f"""
        <div class="manager-title">
            👔 Manager: {manager_name}
        <div class="{status_class}">
            Self-Evaluation: {manager_status}
        </div>
        </div>
        """, unsafe_allow_html=True)

        # Get employees (username and email) under this manager
        cursor.execute("SELECT username, email FROM users WHERE managed_by = %s AND is_dormant = FALSE", (manager_name,))
        employees = cursor.fetchall()

        if employees:
            with st.expander(f"📋 Employees under {manager_name}"):
                for emp_name, emp_email in employees:
                    # Check employee's self-evaluation status using EMAIL
                    cursor.execute("""
                        SELECT COUNT(DISTINCT criteria) 
                        FROM user_ratings 
                        WHERE rater = %s AND ratee = %s AND rating_type = 'self'
                    """, (emp_email, emp_email))
                    emp_self_eval = cursor.fetchone()[0] > 0

                    # Check manager evaluation status for the employee using EMAIL
                    cursor.execute("SELECT COUNT(DISTINCT criteria) FROM user_ratings WHERE ratee = %s AND rating_type = 'manager'", (emp_email,))
                    manager_eval_ratings = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM remarks WHERE ratee = %s AND rating_type = 'manager'", (emp_email,))
                    manager_eval_remarks = cursor.fetchone()[0]
                    manager_eval = (manager_eval_ratings > 0) or (manager_eval_remarks > 0)
                    
                    # Get the actual manager who evaluated (rater is now an email)
                    cursor.execute("SELECT rater FROM user_ratings WHERE ratee = %s AND rating_type = 'manager' LIMIT 1", (emp_email,))
                    evaluator_result = cursor.fetchone()
                    evaluator_name = manager_name # Default to the assigned manager
                    if evaluator_result:
                        evaluator_email = evaluator_result[0]
                        # Look up the name from the email
                        cursor.execute("SELECT username FROM users WHERE email = %s", (evaluator_email,))
                        name_result = cursor.fetchone()
                        if name_result:
                            evaluator_name = name_result[0]

                    # --- Status determination logic (remains the same) ---
                    if emp_self_eval and manager_eval:
                        overall_status = "✅ Fully Complete"
                        status_class = "status-complete"
                        eval_text = f"Have been evaluated by manager {evaluator_name}."
                    elif emp_self_eval and not manager_eval:
                        overall_status = "🔄 Self-Evaluation Done, Manager Pending"
                        status_class = "status-pending"
                        eval_text = f"Awaiting evaluation from manager {manager_name}."
                    elif not emp_self_eval and manager_eval:
                        overall_status = "🔄 Manager Done, Self-Evaluation Pending"
                        status_class = "status-pending"
                        eval_text = f"Have been evaluated by manager {evaluator_name}, but self-evaluation pending."
                    else:
                        overall_status = "❌ Not Started"
                        status_class = "status-not-started"
                        eval_text = f"No evaluations completed yet. Manager: {manager_name}"

                    # --- Employee Section Display (remains the same) ---
                    st.markdown(f"""
                    <div class="employee-section">
                        <div class="employee-name">👤 {emp_name}</div>
                        <div class="{status_class}">{overall_status}</div>
                        <div style="color: #B0BEC5; font-size: 14px; margin-top: 5px;">
                            {eval_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)