import streamlit as st
import mysql.connector as connector
import bcrypt
import datetime
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="HR Dashboard", page_icon="📋", layout="wide")

# --- DATABASE AND TOKEN STORE (This part is crucial and must be in every file) ---
@st.cache_resource
def get_db_connection():
    try:
        return connector.connect(host="localhost", user="root", password="sqladi@2710", database="auth")
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

# --- HR DASHBOARD UI ---
st.title("HR Dashboard 📋")
st.write("---")
st.write(f"<center><h2>Welcome {name}!</h2></center>", unsafe_allow_html=True)

# Add New Employee Form
st.subheader("Add New Employee")
with st.form("add_employee_form", clear_on_submit=True):
    # Your existing form for adding employees goes here.
    # This is copied directly from your original file's "HR" section.
    # ...
    # (The full "Add New Employee" form code from your file is assumed here)
    # ...
    new_emp_username = st.text_input("Email")
    new_emp_password = st.text_input("Password", type="password")
    new_emp_name = st.text_input("First Name").title()
    # Fetch all managers from users table
    cursor.execute("SELECT username FROM users WHERE role = 'manager'")
    managers = [row[0] for row in cursor.fetchall()]
    selected_manager = st.selectbox("Assign Manager", managers) if managers else None
    submitted = st.form_submit_button("Add Employee")
    if submitted:
        if not (new_emp_username and new_emp_password and new_emp_name and selected_manager):
            st.error("Please fill all fields and select a manager.")
        else:
            # Check if username already exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (new_emp_username,))
            if cursor.fetchone():
                st.error("Username already exists.")
            else:
                hashed_pw = bcrypt.hashpw(new_emp_password.encode(), bcrypt.gensalt())
                cursor.execute(
                    "INSERT INTO users (email, password, role, managed_by, username) VALUES (%s, %s, %s, %s, %s)",
                    (new_emp_username, hashed_pw, "employee", selected_manager, new_emp_name)
                )
                db.commit()
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
        with st.expander(f"**{emp_name}** ({emp_role})", icon="👤", expanded=False):
            new_name = st.text_input(f"New Name for {emp_name}", value=emp_name, key=f"name_{emp_username}")
            # Only allow changing manager for employees, not managers/HR
            if emp_role == "employee":
                cursor.execute("SELECT username FROM users WHERE role = 'manager'")
                managers = [row[0] for row in cursor.fetchall()]
                new_manager = st.selectbox(
                    f"Manager for {emp_name}", managers, 
                    index=managers.index(emp_manager) if emp_manager in managers else 0,
                    key=f"mgr_{emp_name}"
                ) if managers else None
                # Allow changing role except to admin
                new_role = st.selectbox(
                    f"Role for {emp_name}", 
                    ["employee", "manager", "hr"], 
                    index=["employee", "manager", "hr"].index(emp_role),
                    key=f"role_{emp_name}"
                )
            else:
                new_manager = emp_manager
                new_role = emp_role
            @st.dialog("Confirmation")
            def confirm_submit():
                st.success(f"Updated details for {emp_name}")
                if st.button("Close"):
                    st.rerun()
            # Password update
            new_password = st.text_input(f"New Password for {emp_name} (leave blank to keep unchanged)", type="password", key=f"pwd_{emp_username}")
            if st.button(f"Update {emp_name}", key=f"update_{emp_name}"):
                original_emp_username = emp_name
                if new_password:
                    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                    cursor.execute(
                        "UPDATE users SET username = %s, role = %s, managed_by = %s, password = %s WHERE email = %s",
                        (new_name, new_role, new_manager, hashed, emp_username)
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET username = %s, role = %s, managed_by = %s WHERE email = %s",
                        (new_name, new_role, new_manager, emp_username)
                    )
                db.commit() 
                if new_name != original_emp_username and emp_role == 'manager':
                    cursor.execute(
                        "UPDATE users SET managed_by = %s WHER++" \
                        "E managed_by = %s",
                        (new_name, original_emp_username)
                    )
                    db.commit()
                if new_name and new_name != original_emp_username:
                    cursor.execute("UPDATE user_ratings SET rater = %s WHERE rater = %s", (new_name, original_emp_username))
                    cursor.execute("UPDATE user_ratings SET ratee = %s WHERE ratee = %s", (new_name, original_emp_username))
                    cursor.execute("UPDATE remarks SET rater = %s WHERE rater = %s", (new_name, original_emp_username))
                    cursor.execute("UPDATE remarks SET ratee = %s WHERE ratee = %s", (new_name, original_emp_username))
                    db.commit()
                
                confirm_submit()

# CHECKLIST-CODE-STARTS-HERE
# --- EVALUATION STATUS CHECKLIST ---
st.markdown("## 📊 Evaluation Status Dashboard")
st.markdown("---")

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
    padding: 15px;
    margin: 10px 0;
}

.employee-section {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 12px;
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
    WHERE managed_by IS NOT NULL AND managed_by != ''
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
    </div>
    <div class="{status_class}">
        Self-Evaluation: {manager_status}
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
        st.markdown("**📋 Employees under this manager:**")
        
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

# Summary statistics
st.markdown("---")
st.markdown("## 📈 Summary Statistics")

col1, col2, col3, col4 = st.columns(4)

# Calculate statistics
cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employee'")
total_employees = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(DISTINCT ratee) 
    FROM user_ratings 
    WHERE ratee IN (SELECT username FROM users WHERE role = 'employee') 
    AND rating_type = 'self'
""")
employees_self_evaluated = cursor.fetchone()[0]

# Check both user_ratings and remarks for manager evaluations
cursor.execute("""
    SELECT COUNT(DISTINCT emp.username)
    FROM users emp
    WHERE emp.role = 'employee' 
    AND (
        EXISTS (
            SELECT 1 FROM user_ratings ur 
            WHERE ur.ratee = emp.username AND ur.rating_type = 'manager'
        )
        OR EXISTS (
            SELECT 1 FROM remarks r 
            WHERE r.ratee = emp.username AND r.rating_type = 'manager'
        )
    )
""")
employees_manager_evaluated = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(DISTINCT emp.username)
    FROM users emp
    WHERE emp.role = 'employee' 
    AND EXISTS (
        SELECT 1 FROM user_ratings ur 
        WHERE ur.ratee = emp.username AND ur.rating_type = 'self'
    )
    AND (
        EXISTS (
            SELECT 1 FROM user_ratings ur2 
            WHERE ur2.ratee = emp.username AND ur2.rating_type = 'manager'
        )
        OR EXISTS (
            SELECT 1 FROM remarks r 
            WHERE r.ratee = emp.username AND r.rating_type = 'manager'
        )
    )
""")
fully_evaluated = cursor.fetchone()[0]

with col1:
    st.metric("Total Employees", total_employees)

with col2:
    st.metric("Self-Evaluations Done", f"{employees_self_evaluated}/{total_employees}")

with col3:
    st.metric("Manager Evaluations Done", f"{employees_manager_evaluated}/{total_employees}")

with col4:
    st.metric("Fully Evaluated", f"{fully_evaluated}/{total_employees}")


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
