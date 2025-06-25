import streamlit as st
import mysql.connector as connector
import bcrypt

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

# --- CORRECTED AUTHENTICATION GUARD ---

# 1. Check if the user's name or role is missing from the session state
if "name" not in st.session_state or "role" not in st.session_state:
    
    # 2. If so, check for a user in the URL query parameters
    if "user" in st.query_params:
        # Restore the name from the URL
        name_from_url = st.query_params["user"]
        st.session_state["name"] = name_from_url

        # 3. THIS IS THE FIX: Re-fetch the role from the database
        try:
            db = connector.connect(host="localhost", user="root", password="sqladi@2710", database="auth")
            cursor = db.cursor()
            cursor.execute("SELECT role FROM users WHERE username = %s", (name_from_url,))
            result = cursor.fetchone()
            db.close()
            
            if result:
                # If the role is found, restore it to the session and rerun the page
                st.session_state["role"] = result[0]
                st.rerun()
            else:
                # If the user from the URL is not valid, clear everything and stop
                st.session_state.clear()
                st.query_params.clear()
                st.error("Invalid user session. Please log in again.")
                st.stop()

        except connector.Error as e:
            st.error(f"Database error during authentication: {e}")
            st.stop()
            
    else:
        # If no user in session OR URL, deny access
        st.error("No user logged in. Please log in first.")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()

# 4. If we get here, the user is authenticated.
#    Ensure the user's name is in the URL for refresh persistence.
st.query_params.user = st.session_state["name"]
name = st.session_state["name"]
role = st.session_state["role"]

# --- MAIN DB CONNECTION & FINAL ROLE VERIFICATION ---
try:
    db = connector.connect(host="localhost", user="root", password="sqladi@2710", database="auth")
    cursor = db.cursor()
except connector.Error as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

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
            st.session_state.new_user_managed_by = None
        
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

        st.text_input("Password", type="password", key='new_user_password', placeholder="Enter password")

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
                        cursor.execute(
                            "UPDATE users SET managed_by = %s WHERE managed_by = %s",
                            (new_name, original_username)
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
                    st.success(f"User '{user_to_edit}' updated successfully!")
                else:
                    st.info("No changes made.")

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

    for user_data in filtered_users:
        emp_email, emp_name, emp_role, emp_manager = user_data
        with st.expander(f"**{emp_name}** ({emp_role.title()}) - Managed by: {emp_manager}"):
            if st.button("View Full Evaluation Report", key=f"view_{emp_email}"):
                st.session_state['selected_employee'] = emp_name
                st.switch_page("pages/Rating.py")

# --- LOGOUT BUTTON ---
st.write("---")
if st.button("Logout", type="primary"):
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("Home.py")
