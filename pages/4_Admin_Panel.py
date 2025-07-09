import streamlit as st
import mysql.connector as connector
import bcrypt
import datetime
from validators import validate_password, validate_email, ALLOWED_DOMAINS
from utils import generate_random_password

# ## FIX: Moved this function to the top level for better organization.
def generate_and_set_password(key):
    """Callback function to update the password in session state."""
    st.session_state[key] = generate_random_password()

# Defining functions inside conditional blocks is not a good practice.
def handle_update(original_email, original_name, original_role, new_name, new_role, new_manager, new_password):
    """Callback to handle updating a user in the database, including demotion."""
    # 1. Validate password if a new one was entered
    if new_password:
        validation_errors = validate_password(new_password)
        if validation_errors:
            st.error(f"Password Error: {' & '.join(validation_errors)}")
            return # Stop the update if password is weak

    cursor = db.cursor() # Get a fresh cursor

    # --- START: DEMOTION LOGIC ---
    # This block handles the specific case of a manager being demoted.
    if new_role != 'manager' and original_role == 'manager':
        # 1. Unassign all employees who reported to this manager
        cursor.execute("UPDATE users SET managed_by = NULL WHERE managed_by = %s", (original_name,))
        # 2. Delete all ratings given BY this person AS a manager
        cursor.execute("DELETE FROM user_ratings WHERE rater = %s AND rating_type = 'manager'", (original_name,))
        # 3. Delete all remarks given BY this person AS a manager
        cursor.execute("DELETE FROM remarks WHERE rater = %s AND rating_type = 'manager'", (original_name,))
        # 4. Clean up related notifications
        cursor.execute("""
            DELETE FROM notifications 
            WHERE 
                (recipient = %s AND notification_type = 'self_evaluation_completed')
            OR
                (sender = %s AND notification_type = 'evaluation_completed')
        """, (original_name, original_name))
        db.commit() # Commit these deletions
    # --- END: DEMOTION LOGIC ---

    # 2. Build and execute the main database query to update the user's record
    update_params = [new_name, new_role, new_manager]
    update_query = "UPDATE users SET username = %s, role = %s, managed_by = %s"

    if new_password:
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        update_query += ", password = %s"
        update_params.append(hashed.decode('utf-8'))

    update_query += " WHERE email = %s"
    update_params.append(original_email)

    cursor.execute(update_query, tuple(update_params))
    db.commit()

    # 3. Handle cascading updates if the username changed
    if new_name != original_name:
        # ## FIX: Logic corrected. If the original role was manager, update their former employees.
        if original_role == 'manager':
            cursor.execute("UPDATE users SET managed_by = %s WHERE managed_by = %s", (new_name, original_name))
        
        # Update their name in all other records.
        cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_name))
        cursor.execute("UPDATE user_ratings SET ratee = %s WHERE ratee = %s", (new_name, original_name))
        cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_name))
        cursor.execute("UPDATE remarks SET ratee = %s WHERE ratee = %s", (new_name, original_name))
        cursor.execute("UPDATE notifications SET recipient = %s WHERE recipient = %s", (new_name, original_name))
        cursor.execute("UPDATE notifications SET sender = %s WHERE sender = %s", (new_name, original_name))
        db.commit()

    st.success(f"Updated details for {new_name}")
    # Clear the password field from session state after use
    pwd_key = f"pwd_{original_email}"
    if pwd_key in st.session_state:
        st.session_state[pwd_key] = ""

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

# --- DATABASE AND TOKEN STORE ---
@st.cache_resource
def get_db_connection():
    try:
        # ## NOTE: Make sure your database credentials are correct.
        return connector.connect(host="localhost", user="root", password="sqladi@2710", database="auth")
    except connector.Error:
        st.error("Database connection failed. Please contact an administrator.")
        st.stop()

@st.cache_resource
def get_token_store():
    return {}

db = get_db_connection()
token_store = get_token_store()

# --- AUTHENTICATION GUARD ---
def authenticate_user():
    if "token" in st.query_params:
        token = st.query_params["token"]
        if token in token_store:
            token_data = token_store[token]
            if datetime.datetime.now() - token_data['timestamp'] < datetime.timedelta(hours=24):
                st.session_state["name"] = token_data['username']
                st.session_state["role"] = token_data['role']
                st.session_state["token"] = token
                return True
            else:
                del token_store[token]
        st.query_params.clear()

    st.error("🚨 Access Denied. Please log in first.")
    if st.button("Go to Login Page"):
        st.switch_page("Home.py")
    st.stop()

if 'name' not in st.session_state:
    authenticate_user()

name = st.session_state['name']
role = st.session_state['role']
cursor = db.cursor(dictionary=True) # Use dictionary cursor for easier data access

# --- ADMIN PANEL UI ---
st.title("Admin Control Panel ⚙️")
st.write(f"<center><h2>Welcome, Admin {name}!</h2></center>", unsafe_allow_html=True)
st.write("---")

tab1, tab2 = st.tabs(["User & Team Management", "Evaluation Status Dashboard"])

with tab1:
    st.header("Manage User Accounts and Teams")
    action = st.selectbox(
        "Select an Action",
        ("Create New User", "Edit Existing User", "Delete User"),
        key="admin_action"
    )
    st.write("---")

    # --- CREATE NEW USER ---
    if action == "Create New User":
        st.subheader("Create New Employee or Manager")

        if 'admin_form_message' in st.session_state:
            st.success(st.session_state.admin_form_message)
            del st.session_state.admin_form_message

        if st.session_state.get('admin_form_success', False):
            for key in ['admin_add_local', 'admin_add_name', 'admin_add_password']:
                if key in st.session_state:
                    st.session_state[key] = ''
            st.session_state.admin_form_success = False

        if st.button("✨ Generate Secure Password", key="admin_generate_pwd"):
            st.session_state.admin_add_password = generate_random_password()
            st.rerun()

        with st.form("admin_add_user_form", clear_on_submit=False):
            st.text_input("First Name", key="admin_add_name")
            col1, col2 = st.columns([3, 2])
            with col1:
                st.text_input("Email Username", key="admin_add_local")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.selectbox("Domain", options=ALLOWED_DOMAINS, key="admin_add_domain", label_visibility="collapsed")

            st.text_input("Password", type="password", key="admin_add_password")
            role_to_create = st.selectbox("Role", ["Employee", "Manager", "HR"], key="admin_add_role")
            
            manager_to_assign = None
            if role_to_create == "Employee":
                cursor.execute("SELECT username FROM users WHERE role = 'manager'")
                managers = [row['username'] for row in cursor.fetchall()]
                if managers:
                    manager_to_assign = st.selectbox("Assign Manager", managers, key="admin_add_manager")
                else:
                    st.warning("No managers exist to assign.")
            
            submitted = st.form_submit_button("Create User")

        if submitted:
            name_val = st.session_state.admin_add_name
            local_val = st.session_state.admin_add_local
            domain_val = st.session_state.admin_add_domain
            password_val = st.session_state.admin_add_password
            full_email = f"{local_val}@{domain_val}".strip()

            all_fields_filled = name_val and local_val and password_val and (role_to_create != "Employee" or manager_to_assign)
            
            # ## FIX: Store result of validation to avoid calling the function twice.
            password_errors = validate_password(password_val)

            if not all_fields_filled:
                st.error("Please fill all fields.")
            elif not validate_email(full_email):
                st.error("Invalid email format.")
            elif password_errors:
                st.error(" & ".join(password_errors))
            else:
                cursor.execute("SELECT email FROM users WHERE email = %s", (full_email,))
                if cursor.fetchone():
                    st.error("An account with this email already exists.")
                else:
                    # ## FIX: CRITICAL SECURITY FLAW. Never use a static salt. Always use gensalt().
                    hashed_pw = bcrypt.hashpw(password_val.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    managed_by = manager_to_assign if role_to_create == "Employee" else 'XYZ'
                    
                    cursor.execute(
                        "INSERT INTO users (username, email, password, role, managed_by) VALUES (%s, %s, %s, %s, %s)",
                        (name_val, full_email, hashed_pw, role_to_create.lower(), managed_by)
                    )
                    db.commit()
                    st.session_state.admin_form_message = f"Successfully created new user: {name_val}"
                    st.session_state.admin_form_success = True
                    st.rerun()

    # --- EDIT EXISTING USER ---
    elif action == "Edit Existing User":
        st.subheader("Edit Existing User Details")
        
        cursor.execute("SELECT email, username, role, managed_by FROM users WHERE role != 'admin' and username != %s", (name,))
        employees = cursor.fetchall()

        search_query_edit = st.text_input("🔍 Search Employee by Name or Email", value="", key="search_employee_edit")
        filtered_employees_edit = [
            emp for emp in employees
            if search_query_edit.lower() in emp['username'].lower() or search_query_edit.lower() in emp['email'].lower()
        ] if search_query_edit else employees

        page_size_edit = 6
        total_employees_edit = len(filtered_employees_edit)
        total_pages_edit = (total_employees_edit + page_size_edit - 1) // page_size_edit
        st.session_state.employee_edit_page = st.session_state.get("employee_edit_page", 1)

        if search_query_edit and st.session_state.get("last_search_query_edit") != search_query_edit:
            st.session_state.employee_edit_page = 1
        st.session_state.last_search_query_edit = search_query_edit

        current_page_edit = st.session_state.employee_edit_page
        start_idx_edit = (current_page_edit - 1) * page_size_edit
        employees_to_show_edit = filtered_employees_edit[start_idx_edit : start_idx_edit + page_size_edit]

        if not employees_to_show_edit:
            st.info("No employees found.")
        else:
            for emp in employees_to_show_edit:
                # ## FIX: Use clear variable names based on the dictionary keys.
                emp_email = emp['email']
                emp_name = emp['username']
                emp_role = emp['role']
                emp_manager = emp['managed_by']

                with st.expander(f"**{emp_name}** ({emp_email}) - Role: {emp_role.title()}", icon="👤"):
                    new_name = st.text_input("Name", value=emp_name, key=f"name_{emp_email}")
                    
                    role_options = ["employee", "manager", "hr"]
                    current_role_index = role_options.index(emp_role) if emp_role in role_options else 0
                    new_role = st.selectbox(
                        "Role",
                        role_options,
                        index=current_role_index,
                        key=f"role_{emp_email}"
                    )
                    
                    new_manager = emp_manager # Default to current manager
                    if new_role == "employee":
                        cursor.execute("SELECT username FROM users WHERE role = 'manager'")
                        managers = [row['username'] for row in cursor.fetchall()]
                        # Also allow assigning to managers who are being edited on the same page
                        if emp_name not in managers and emp_role == 'manager':
                            managers.append(emp_name)
                        
                        if managers:
                            current_manager_index = managers.index(emp_manager) if emp_manager in managers else 0
                            new_manager = st.selectbox(
                                "Manager", managers,
                                index=current_manager_index,
                                key=f"mgr_{emp_email}"
                            )
                        else:
                            st.warning("No managers available to assign.")
                    # ## FIX: Correctly set 'managed_by' for non-employee roles
                    elif new_role in ["manager", "hr"]:
                        new_manager = 'XYZ'

                    pwd_key = f"pwd_{emp_email}"
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        new_password = st.text_input("New Password (leave blank if no change)", type="password", key=pwd_key)
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.button("Generate", key=f"gen_{pwd_key}", on_click=generate_and_set_password, args=(pwd_key,))
                    
                    st.button(
                        f"Update {emp_name}",
                        key=f"update_{emp_email}",
                        on_click=handle_update,
                        args=(
                            emp_email,     # original_email
                            emp_name,      # original_name
                            emp_role,      # original_role
                            new_name,
                            new_role,
                            new_manager,
                            new_password
                        )
                    )

            st.write("---")
            col1, col2, col3 = st.columns([2, 3, 2])
            if total_pages_edit > 1:
                with col1:
                    if st.button("⬅️ Previous", disabled=(current_page_edit <= 1), use_container_width=True, key="edit_prev_btn"):
                        st.session_state.employee_edit_page -= 1
                        st.rerun()
                with col2:
                    st.markdown(f"<p style='text-align: center; font-weight: bold;'>Page {current_page_edit} of {total_pages_edit}</p>", unsafe_allow_html=True)
                with col3:
                    if st.button("Next ➡️", disabled=(current_page_edit >= total_pages_edit), use_container_width=True, key="edit_next_btn"):
                        st.session_state.employee_edit_page += 1
                        st.rerun()

    # --- DELETE USER ---
    elif action == "Delete User":
        st.subheader("Delete User Account")
        cursor.execute("SELECT username, role FROM users WHERE role != 'admin'")
        users = [f"{row['username']} ({row['role']})" for row in cursor.fetchall()]
        
        if not users:
            st.warning("No users available to delete.")
        else:
            user_to_delete = st.selectbox("Select user to delete", users, key="admin_delete_user")
            if st.button("Delete User", type="primary"):
                username = user_to_delete.split(" (")[0]
                role_to_delete = user_to_delete.split("(")[-1].replace(")", "").strip().lower()

                if role_to_delete == 'manager':
                    cursor.execute("SELECT COUNT(*) as count FROM users WHERE managed_by = %s", (username,))
                    if cursor.fetchone()['count'] > 0:
                        st.error(f"Cannot delete '{username}'. Reassign their employees first.")
                    else:
                        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
                        db.commit()
                        st.success(f"Manager '{username}' has been deleted.")
                        st.rerun()
                else: # Employee or HR
                    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
                    db.commit()
                    st.success(f"User '{username}' has been deleted.")
                    st.rerun()

# --- Everything below this line seems logically sound. ---
with tab2:
    ALL_CRITERIA_NAMES = {
        "Humility", "Integrity", "Collegiality", "Attitude", "Time Management", "Initiative", "Communication", "Compassion",
        "Knowledge & Awareness", "Future readiness", "Informal leadership", "Team Development", "Process adherence",
        "Quality of Work", "Task Completion", "Timeline Adherence",
        "Collaboration", "Innovation", "Special Situation"
    }
    TOTAL_CRITERIA_COUNT = len(ALL_CRITERIA_NAMES)
    
    st.markdown("---")
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

    cursor.execute("""
        SELECT DISTINCT managed_by 
        FROM users 
        WHERE managed_by IS NOT NULL AND managed_by != 'XYZ'
        ORDER BY managed_by
    """)
    managers = [row['managed_by'].strip() for row in cursor.fetchall()]

    st.markdown('<div class="checklist-container">', unsafe_allow_html=True)
    for manager in managers:
        cursor.execute("""
            SELECT COUNT(DISTINCT criteria) as count
            FROM user_ratings 
            WHERE rater = %s AND ratee = %s AND rating_type = 'self'
        """, (manager, manager))
        manager_self_eval_count = cursor.fetchone()['count']
        manager_self_eval = manager_self_eval_count >= TOTAL_CRITERIA_COUNT

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

        cursor.execute("""
            SELECT username FROM users 
            WHERE managed_by = %s AND role = 'employee' ORDER BY username
        """, (manager,))
        employees = [row['username'].strip() for row in cursor.fetchall()]

        if employees:
            with st.expander(f"📋 Employees under {manager}"):
                for employee in employees:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT criteria) as count 
                        FROM user_ratings 
                        WHERE rater = %s AND ratee = %s AND rating_type = 'self'
                    """, (employee, employee))
                    emp_self_eval_count = cursor.fetchone()['count']
                    emp_self_eval = emp_self_eval_count >= TOTAL_CRITERIA_COUNT 

                    cursor.execute("""
                        SELECT COUNT(DISTINCT criteria) as count 
                        FROM user_ratings 
                        WHERE ratee = %s AND rating_type = 'manager'
                    """, (employee,))
                    manager_eval_ratings = cursor.fetchone()['count']

                    cursor.execute("SELECT COUNT(*) as count FROM remarks WHERE ratee = %s AND rating_type = 'manager'", (employee,))
                    manager_eval_remarks = cursor.fetchone()['count']

                    cursor.execute("SELECT rater FROM remarks WHERE ratee = %s AND rating_type = 'manager' LIMIT 1", (employee,))
                    actual_evaluator_row = cursor.fetchone()
                    evaluator_name = actual_evaluator_row['rater'] if actual_evaluator_row else manager

                    manager_eval = (manager_eval_ratings >= TOTAL_CRITERIA_COUNT) and (manager_eval_remarks > 0)
                    
                    # ## FIX: Removed leftover debug code block for 'Adam'.

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
    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGOUT BUTTON ---
st.write("---")
if st.button("Logout", type="primary"):
    token_to_remove = st.session_state.get("token")
    if token_to_remove and token_to_remove in token_store:
        del token_store[token_to_remove]
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("Home.py")
