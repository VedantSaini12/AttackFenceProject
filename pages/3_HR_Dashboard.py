import streamlit as st
import mysql.connector as connector
import bcrypt
import datetime
import uuid
from notifications import notification_bell_component, add_notification
from validators import validate_password, validate_email, validate_name, ALLOWED_DOMAINS
from utils import generate_random_password
from core.auth import protect_page, render_logout_button, get_db_connection, get_token_store

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="HR Dashboard", page_icon="📋", layout="wide")

protect_page(allowed_roles=["HR"])

db = get_db_connection()
token_store = get_token_store()

# Define session variables for easy use in the rest of the page
name = st.session_state["name"]
email = st.session_state["email"]
role = st.session_state["role"]
cursor = db.cursor(buffered=True)

# --- END OF THE NEW SECURE AUTHENTICATION GUARD ---

notification_bell_component()

if "hr_section" not in st.session_state:
    st.session_state.hr_section = "Add Employee"

with st.sidebar:
    st.title("HR Dashboard 📋")
    st.write(f"<h2>Welcome {name}!</h2>", unsafe_allow_html=True)
    st.divider()

    if st.button("➕ Add New Employee", use_container_width=True, type="primary" if st.session_state.hr_section == "Add Employee" else "secondary"):
        st.session_state.hr_section = "Add Employee"; st.rerun()
    if st.button("✏️ Edit Employees", use_container_width=True, type="primary" if st.session_state.hr_section == "Edit Employees" else "secondary"):
        st.session_state.hr_section = "Edit Employees"; st.rerun()
    if st.button("📊 View All Evaluations", use_container_width=True, type="primary" if st.session_state.hr_section == "View Evaluations" else "secondary"):
        st.session_state.hr_section = "View Evaluations"; st.rerun()
    if st.button("📜 View History", use_container_width=True, type="primary" if st.session_state.hr_section == "History" else "secondary"):
        st.session_state.hr_section = "History"
        st.switch_page("pages/History.py")

    st.divider()

    if st.button("Logout", use_container_width=True):
        token_store = get_token_store()
        token_to_remove = st.session_state.get("token")

        if token_to_remove and token_to_remove in token_store:
            del token_store[token_to_remove]

        st.session_state.clear()
        st.query_params.clear()
        st.switch_page("Home.py")



quarter_map = {
    1: "January - March",
    2: "April - June",
    3: "July - September",
    4: "October - December"
}
current_quarter = (datetime.datetime.now().month - 1) // 3 + 1
current_months = quarter_map[current_quarter]
st.info(f"🗓️ The current evaluation period is **Quarter {current_quarter}** ({current_months}).")

# Add New Employee Form
if st.session_state.hr_section == "Add Employee":
    st.subheader("Add New Employee")

    # Display any message that was stored in the session state from the previous run
    if 'form_message' in st.session_state:
        msg_type, msg_text = st.session_state.form_message
        if msg_type == "success":
            st.success(msg_text)
        # This also allows you to show errors in the same way, e.g., else: st.error(msg_text)
        # Clear the message so it doesn't appear again
        del st.session_state.form_message

    # On the rerun after a success, this block will run first
    if st.session_state.get('form_submitted_successfully', False):
        # Clear the form input states from the previous run
        st.session_state.add_email_local = ''
        st.session_state.add_emp_name = ''
        st.session_state.add_emp_password = ''
        # Reset the flag so this doesn't run again
        st.session_state.form_submitted_successfully = False

    if st.button("✨ Generate Secure Password", key="hr_add_pwd_gen"):
        st.session_state.add_emp_password = generate_random_password()
        st.rerun()

    # Placeholders for error messages
    name_error_ph = st.empty()
    email_error_ph = st.empty()
    password_error_ph = st.empty()
    form_error_ph = st.empty()

    with st.form("add_employee_form", clear_on_submit=False):
        col1, col2 = st.columns([3, 3])
        with col1:
            email_local = st.text_input("Email Username", placeholder="Enter email username", key="add_email_local")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True) # Spacer for alignment
            st.selectbox("Domain", options=ALLOWED_DOMAINS, key="add_email_domain", label_visibility="collapsed")

        first_name = st.text_input("Full Name", placeholder="Enter user's full name", key="add_emp_name")
        password = st.text_input("Password", type="password", key="add_emp_password", placeholder="Enter or generate a password")

        cursor.execute("SELECT username FROM users WHERE role = 'manager'")
        managers = [row[0] for row in cursor.fetchall()]
        manager = st.selectbox("Assign Manager", managers, key="add_emp_manager")

        submitted = st.form_submit_button("Add Employee")

    # Handle form submission
    if submitted:
        # Clear previous errors
        name_error_ph.empty()
        email_error_ph.empty()
        password_error_ph.empty()
        form_error_ph.empty()

        full_email = f"{st.session_state.add_email_local}@{st.session_state.add_email_domain}" if st.session_state.add_email_local else ''
        is_name_valid = validate_name(st.session_state.add_emp_name)
        is_email_valid = validate_email(full_email)
        password_errors = validate_password(st.session_state.add_emp_password)
        all_fields = st.session_state.add_email_local and st.session_state.add_emp_name and st.session_state.add_emp_password and st.session_state.add_emp_manager

        if not all_fields:
            form_error_ph.error("Please fill all fields and select a manager.")
        elif not is_name_valid:
            name_error_ph.error("Please enter a valid full name (letters and spaces only).")    
        elif not is_email_valid:
            email_error_ph.error(f"Email must be in the format username@domain. Enter username only.")
        elif password_errors:
            password_error_ph.error(" & ".join(password_errors))
        else:
            # Check if email exists and get its dormant status
            cursor.execute("SELECT is_dormant FROM users WHERE email = %s", (full_email,))
            user_status = cursor.fetchone()

            if user_status:
                # --- Case 1: User Exists ---
                is_dormant = user_status[0]

                if is_dormant:
                    # --- REACTIVATE AND UPDATE THE DORMANT ACCOUNT ---
                    hashed_pw = bcrypt.hashpw(st.session_state.add_emp_password.encode(), bcrypt.gensalt())
                    # The "username = %s" part has been REMOVED from the query
                    cursor.execute(
                        """
                        UPDATE users
                        SET
                            is_dormant = FALSE,
                            password = %s,
                            role = 'employee',
                            managed_by = %s
                        WHERE email = %s
                        """,
                        (hashed_pw, st.session_state.add_emp_manager, full_email)
                    )
                    db.commit()
                    st.session_state.form_message = ("success", f"Dormant account for email '{full_email}' has been successfully reactivated!")
                    st.session_state.form_submitted_successfully = True
                    st.rerun()

                else:
                    # --- BLOCK: User exists and is already active ---
                    email_error_ph.error("An active account with this email already exists.")

            else:
                # --- Case 2: User Does Not Exist, CREATE NEW ---
                hashed_pw = bcrypt.hashpw(st.session_state.add_emp_password.encode(), bcrypt.gensalt())
                cursor.execute(
                    "INSERT INTO users (email, password, role, managed_by, username) VALUES (%s, %s, %s, %s, %s)",
                    (full_email, hashed_pw, "employee", st.session_state.add_emp_manager, st.session_state.add_emp_name)
                )
                db.commit()
                st.session_state.form_message = ("success", f"Successfully created new user: {st.session_state.add_emp_name}")
                st.session_state.form_submitted_successfully = True
                st.rerun()

# Edit Existing Employees Section
elif st.session_state.hr_section == "Edit Employees":
    st.subheader("Edit Existing Employees")

    # Your existing logic for listing, searching, and editing employees.
    # This includes the search bar, pagination, expanders for each employee,
    # and the update button.
    def handle_hr_update(original_email, original_name, original_role, new_name, new_role, new_manager, new_password):
        # --- Validation ---
        if not validate_name(new_name):
            st.error(f"Invalid new name. Please use letters and spaces only.")
            return
        if new_password and validate_password(new_password):
            st.error(f"Password Error: {' & '.join(validate_password(new_password))}")
            return

        # --- START: DEMOTION LOGIC ---
        if new_role == 'employee' and original_role == 'manager':
            # 1. Unassign employees. Uses manager's original_name, which is correct for managed_by column.
            cursor.execute("UPDATE users SET managed_by = NULL WHERE managed_by = %s", (original_name,))
            # 2. Delete ratings given BY this person AS a manager, using their EMAIL.
            cursor.execute("DELETE FROM user_ratings WHERE rater = %s AND rating_type = 'manager'", (original_email,))
            cursor.execute("DELETE FROM remarks WHERE rater = %s AND rating_type = 'manager'", (original_email,))
            cursor.execute("DELETE FROM notifications WHERE sender = %s AND notification_type = 'evaluation_completed'", (original_email,))
            db.commit()
        # --- END: DEMOTION LOGIC ---

        update_fields, params = [], []
        if new_name != original_name:
            update_fields.append("username = %s"); params.append(new_name)
        if new_role != original_role:
            update_fields.append("role = %s"); params.append(new_role)
        if new_manager is not None:
             update_fields.append("managed_by = %s"); params.append(new_manager)
        if new_password:
            update_fields.append("password = %s"); params.append(bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()))

        if not update_fields:
            st.info("No changes were made."); return

        params.append(original_email)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE email = %s"
        cursor.execute(query, tuple(params))
        db.commit()
        
        # --- The ONLY necessary cascading update ---
        if new_name != original_name and new_role == 'manager':
             cursor.execute("UPDATE users SET managed_by = %s WHERE managed_by = %s", (new_name, original_name))
             db.commit()

        st.success(f"Updated details for {new_name}")


    def generate_and_set_password(key):
        """Callback function to update the password in session state."""
        st.session_state[key] = generate_random_password()

    cursor.execute(f"SELECT email, username, role, managed_by FROM users WHERE role != 'admin' and username != '{name}' AND is_dormant = FALSE")
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
        for emp_email, emp_name, emp_role, emp_manager in employees_to_show_edit:
            with st.expander(f"**{emp_name}** ({emp_role})", icon="👤", expanded=False):
                new_name = st.text_input(f"Full Name", value=emp_name, key=f"name_{emp_email}")
                new_role = st.selectbox(f"Role", ["employee", "manager", "hr"], index=["employee", "manager", "hr"].index(emp_role), key=f"role_{emp_email}")
                
                new_manager = emp_manager
                if new_role == "employee":
                    cursor.execute("SELECT username FROM users WHERE role = 'manager'")
                    managers = [row[0] for row in cursor.fetchall()]
                    if managers:
                        current_manager_index = managers.index(emp_manager) if emp_manager in managers else 0
                        new_manager = st.selectbox(f"Manager", managers, index=current_manager_index, key=f"mgr_{emp_email}")
                elif new_role == "manager":
                    new_manager = 'XYZ'

                pwd_key = f"pwd_{emp_email}"
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
                st.button(
                    f"Update {emp_name}",
                    key=f"update_{emp_email}",
                    on_click=handle_hr_update,
                    args=(emp_email, emp_name, emp_role, new_name, new_role, new_manager, new_password)
                )

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

# --- NEW: VIEW ALL EVALUATIONS FOR HR ---
elif st.session_state.hr_section == "View Evaluations":
    st.subheader("All Employee & Manager Evaluations")
    st.info("As an HR, you can view all evaluation data. Use the search below to find a user.")

    cursor.execute("SELECT email, username, role, managed_by FROM users WHERE role != 'admin'")
    all_users = cursor.fetchall()

    search_query = st.text_input("🔍 Search Any User by Name or Email", key="hr_search")
    filtered = [u for u in all_users if search_query.lower() in u[1].lower() or search_query.lower() in u[0].lower()] if search_query else all_users

    # Pagination
    USERS_PER_PAGE = 6
    total = len(filtered)
    total_pages = (total + USERS_PER_PAGE - 1) // USERS_PER_PAGE
    page = st.session_state.get('hr_user_page', 1)
    start = (page-1)*USERS_PER_PAGE
    end = start + USERS_PER_PAGE
    for u in filtered[start:end]:
        email, uname, urole, umgr = u
        with st.expander(f"**{uname}** ({urole.title()}) - Managed by: {umgr}"):
            if st.button("View Full Evaluation Report", key=f"hr_view_{email}"):
                st.session_state['selected_employee_email'] = email # CORRECTED
                st.switch_page("pages/Rating.py")

    col1, col2, col3 = st.columns([2,5,2])
    with col1:
        if st.button("⬅️ Previous", disabled=(page<=1)):
            st.session_state['hr_user_page'] = page-1
            st.rerun()
    with col2:
        st.markdown(f"<p style='text-align:center;'>Page {page} of {total_pages}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ➡️", disabled=(page>=total_pages)):
            st.session_state['hr_user_page'] = page+1
            st.rerun()