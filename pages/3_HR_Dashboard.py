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
st.subheader("Edit Existing Employees")
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
            new_name = st.text_input(f"Full Name for {emp_name}", value=emp_name, key=f"name_{emp_username}")
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
                        "UPDATE users SET managed_by = %s WHERE managed_by = %s",
                        (new_name, original_emp_username)
                    )
                    db.commit()
                
                confirm_submit()

# Pagination controls for edit section
st.markdown(
    """
    <style>
    div[data-testid="column"] > div {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.write("---")

# View All Employee Ratings Section
st.subheader("View All Employee Ratings")
# Your existing logic for displaying a searchable, paginated grid of employees,
# with a "View Ratings" button that switches to Rating.py.
# This is copied directly from your original file's "HR" section.
# ...
# (The full "View All Employee Ratings" code from your file is assumed here)
# ...
search_query = st.text_input("🔍 Search Employee by Name or Email", value="", key="search_employee")
filtered_employees = [
    emp for emp in employees
    if search_query.lower() in emp[1].lower()] if search_query else employees

# Pagination setup
page_size = 9
total_employees = len(filtered_employees)
total_pages = (total_employees + page_size - 1) // page_size

if "employee_page" not in st.session_state:
    st.session_state["employee_page"] = 1

# Reset page if search changes
if search_query and st.session_state.get("last_search_query") != search_query:
    st.session_state["employee_page"] = 1
st.session_state["last_search_query"] = search_query

current_page = st.session_state["employee_page"]
start_idx = (current_page - 1) * page_size
end_idx = start_idx + page_size
employees_to_show = filtered_employees[start_idx:end_idx]
if not employees_to_show:
    st.warning("No employees found matching your search criteria.")

# Display employee cards in a grid (3 per row)
card_cols = st.columns(3)
for idx, emp in enumerate(employees_to_show):
    emp_username, emp_name, emp_role, emp_manager = emp
    with card_cols[idx % 3]:
        with st.container(border=True):
            st.subheader(emp_name)
            st.write(f"**Role:** {emp_role.title()}")
            st.write(f"**Email:** {emp_username}")
            st.write(f"**Manager:** {emp_manager if emp_manager else 'N/A'}")
            if st.button(
            "View Ratings  ↗",
            key=f"view_ratings_{emp_username}",
            use_container_width=True,
            help="View rating summary for this employee"
            ):
                st.session_state["selected_employee"] = emp_name
                st.switch_page("pages/Rating.py")

# Pagination controls
# Center align the row of buttons using markdown
st.markdown(
"""
<style>
div[data-testid="column"] > div {
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
""",
unsafe_allow_html=True,
)
st.write("")
if total_pages > 1:
    btn_cols = st.columns(total_pages, gap="small")
    for i in range(total_pages):
        page_num = i + 1
        with btn_cols[i]:
            if st.button(f"{page_num}",use_container_width=True, key=f"employee_page_btn_{page_num}",type="primary" if page_num == current_page else "secondary"):
                st.session_state["employee_page"] = page_num
                st.rerun()
else:
    st.write("Unknown role.")

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
