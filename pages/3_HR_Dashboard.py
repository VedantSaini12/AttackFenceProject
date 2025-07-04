import streamlit as st
import mysql.connector as connector
import bcrypt
import datetime
import uuid
from notifications import notification_bell_component, add_notification
from validators import validate_password, validate_email
from utils import generate_random_password

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="HR Dashboard", page_icon="📋", layout="wide")

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

notification_bell_component(st.session_state.name)

# --- HR DASHBOARD UI ---
st.title("HR Dashboard 📋")
st.write("---")
st.write(f"<center><h2>Welcome {name}!</h2></center>", unsafe_allow_html=True)

# Add New Employee Form
st.subheader("Add New Employee")

# --- PASSWORD GENERATION LOGIC (This part is correct and stays the same) ---
if 'hr_add_pwd' not in st.session_state:
    st.session_state.hr_add_pwd = ''

if st.button("✨ Generate Secure Password", key="hr_add_pwd_gen"):
    st.session_state.hr_add_pwd = generate_random_password()
    st.rerun()

# --- THE FORM (with placeholders for errors) ---
with st.form("add_employee_form", clear_on_submit=False): # Set clear_on_submit to False
    new_emp_username = st.text_input("Email", placeholder="Enter user's email")
    email_error_placeholder = st.empty()  # 1. Placeholder for email errors

    new_emp_name = st.text_input("First Name", placeholder="Enter user's first name").title()

    new_emp_password = st.text_input("Password", type="password", key="hr_add_pwd", placeholder="Enter or generate a password")
    password_error_placeholder = st.empty() # 2. Placeholder for password errors

    cursor.execute("SELECT username FROM users WHERE role = 'manager'")
    managers = [row[0] for row in cursor.fetchall()]
    selected_manager = st.selectbox("Assign Manager", managers) if managers else None

    # General error placeholder at the bottom of the form
    form_error_placeholder = st.empty()

    submitted = st.form_submit_button("Add Employee")

    if submitted:
        # Perform all validations
        is_email_valid = validate_email(new_emp_username)
        password_errors = validate_password(new_emp_password)
        all_fields_filled = new_emp_username and new_emp_password and new_emp_name and selected_manager

        # 3. Write errors to the correct placeholder
        if not all_fields_filled:
            form_error_placeholder.error("Please fill all fields and select a manager.")
        elif not is_email_valid:
            email_error_placeholder.error("Please enter a valid email address.")
        elif password_errors:
            # Join all password validation messages into one
            password_error_placeholder.error(" & ".join(password_errors))
        else:
            # Check if email already exists
            cursor.execute("SELECT email FROM users WHERE email = %s", (new_emp_username,))
            if cursor.fetchone():
                email_error_placeholder.error("An account with this email already exists.")
            else:
                # If all checks pass, create the user
                hashed_pw = bcrypt.hashpw(new_emp_password.encode(), bcrypt.gensalt())
                cursor.execute(
                    "INSERT INTO users (email, password, role, managed_by, username) VALUES (%s, %s, %s, %s, %s)",
                    (new_emp_username, hashed_pw, "employee", selected_manager, new_emp_name)
                )
                db.commit()
                st.success(f"Successfully created new user: {new_emp_name}")

                # Clear the password from session state after success
                st.session_state.hr_add_pwd = ''

                @st.dialog("Confirmation")
                def add_submit(emp_name):
                    st.success(f"Created new user: {emp_name}")
                    if st.button("Close"):
                        st.rerun()
                add_submit(new_emp_name)

st.write("---")

# Edit Existing Employees Section
st.subheader("Edit Passwords for Existing Employees")
# Your existing logic for listing, searching, and editing employees.
# This includes the search bar, pagination, expanders for each employee,
# and the update button.
# All of this is copied directly from your original file's "HR" section.
# ...
# (The full "Edit Existing Employees" code from your file is assumed here)
# ...
def generate_and_set_password(key):
    """Callback function to update the password in session state."""
    st.session_state[key] = generate_random_password()

cursor.execute(f"SELECT email, username, role, managed_by FROM users WHERE role != 'admin' and username != '{name}'")
employees = cursor.fetchall()

# Search bar for employees
search_query_edit = st.text_input("🔍 Search Employee by Name", value="", key="search_employee_edit")
filtered_employees_edit = [
    emp for emp in employees
    if search_query_edit.lower() in emp[1].lower() or search_query_edit.lower() in emp[0].lower()
] if search_query_edit else employees

# Pagination setup
page_size_edit = 6
total_employees_edit = len(filtered_employees_edit)
total_pages_edit = (total_employees_edit + page_size_edit - 1) // page_size_edit

if "employee_edit_page" not in st.session_state:
    st.session_state["employee_edit_page"] = 1

# Reset page if search changes
if search_query_edit and st.session_state.get("last_search_query_edit") != search_query_edit:
    st.session_state["employee_edit_page"] = 1
st.session_state["last_search_query_edit"] = search_query_edit

current_page_edit = st.session_state["employee_edit_page"]
start_idx_edit = (current_page_edit - 1) * page_size_edit
end_idx_edit = start_idx_edit + page_size_edit
employees_to_show_edit = filtered_employees_edit[start_idx_edit:end_idx_edit]

if not employees_to_show_edit:
    st.info("No employees found.")
else:
    for emp in employees_to_show_edit:
        emp_username, emp_name, emp_role, emp_manager = emp
        # ALL editing controls now go INSIDE the expander
        with st.expander(f"**{emp_name}** ({emp_role})", icon="👤", expanded=False):
            new_name = st.text_input(f"New Name for {emp_name}", value=emp_name, key=f"name_{emp_username}")

            # Role and Manager select boxes
            if emp_role == "employee":
                cursor.execute("SELECT username FROM users WHERE role = 'manager'")
                managers = [row[0] for row in cursor.fetchall()]
                new_manager = st.selectbox(
                    f"Manager for {emp_name}", managers,
                    index=managers.index(emp_manager) if emp_manager in managers else 0,
                    key=f"mgr_{emp_name}"
                ) if managers else None
                new_role = st.selectbox(
                    f"Role for {emp_name}",
                    ["employee", "manager", "hr"],
                    index=["employee", "manager", "hr"].index(emp_role),
                    key=f"role_{emp_name}"
                )
            else:
                new_manager = emp_manager
                new_role = emp_role

            # Password input with Generate button
            pwd_key = f"pwd_{emp_username}"
            if pwd_key not in st.session_state:
                st.session_state[pwd_key] = ""

            col1, col2 = st.columns([4, 1])
            with col1:
                new_password = st.text_input(f"New Password for {emp_name} (leave blank)", type="password", key=pwd_key)
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.button(
                    "Generate",
                    key=f"gen_{pwd_key}",
                    on_click=generate_and_set_password,
                    args=(pwd_key,)  # Pass the specific key to our callback function
                )

            # Update button and logic
            if st.button(f"Update {emp_name}", key=f"update_{emp_name}"):
                validation_errors = []
                if new_password:
                    validation_errors = validate_password(new_password)

                if validation_errors:
                    for error in validation_errors:
                        st.error(f"Password Error: {error}")
                else:
                    original_emp_username = emp_name # Keep track of the old name for queries
                    update_params = [new_name, new_role, new_manager]
                    update_query = "UPDATE users SET username = %s, role = %s, managed_by = %s"

                    if new_password:
                        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                        update_query += ", password = %s"
                        update_params.append(hashed)

                    update_query += " WHERE email = %s"
                    update_params.append(emp_username)

                    cursor.execute(update_query, tuple(update_params))
                    db.commit()

                    if new_name != original_emp_username:
                        # Update all related tables if name changed
                        cursor.execute("UPDATE users SET managed_by = %s WHERE managed_by = %s", (new_name, original_emp_username))
                        cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_emp_username))
                        cursor.execute("UPDATE user_ratings SET ratee = %s WHERE ratee = %s", (new_name, original_emp_username))
                        cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_emp_username))
                        cursor.execute("UPDATE remarks SET ratee = %s WHERE ratee = %s", (new_name, original_emp_username))
                        db.commit()

                    st.success(f"Updated details for {emp_name}")
                    st.rerun()

    # --- Pagination Controls for Edit Section ---
    st.write("---")
    col1, col2, col3 = st.columns([2, 3, 2])
    
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