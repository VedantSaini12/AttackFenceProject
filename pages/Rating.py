import streamlit as st
import mysql.connector as connector

# Page Config
st.set_page_config(page_title="Evaluation Report", layout="wide")

# If we already have a name but no role, go fetch it too
if "name" in st.session_state and "role" not in st.session_state:
    try:
        db_tmp = connector.connect(host="localhost", user="root", password="sqladi@2710", database="auth")
        cur_tmp = db_tmp.cursor()
        cur_tmp.execute("SELECT role FROM users WHERE username = %s", (st.session_state["name"],))
        r = cur_tmp.fetchone()
        db_tmp.close()
        if r:
            st.session_state["role"] = r[0]
    except connector.Error:
        pass

# Now the usual guard
if "name" not in st.session_state or "role" not in st.session_state:
    if "user" in st.query_params:
        # re-hydrate exactly as in your other dashboards...
        name_from_url = st.query_params["user"]
        st.session_state["name"] = name_from_url
        try:
            db = connector.connect(host="localhost", user="root", password="sqladi@2710", database="auth")
            cursor = db.cursor()
            cursor.execute("SELECT role FROM users WHERE username = %s", (name_from_url,))
            result = cursor.fetchone()
            db.close()
            if result:
                st.session_state["role"] = result[0]
                st.rerun()
            else:
                st.session_state.clear(); st.query_params.clear()
                st.error("Invalid user session. Please log in again."); st.stop()
        except connector.Error as e:
            st.error(f"Database error during authentication: {e}"); st.stop()
    else:
        st.error("No user logged in. Please log in first.")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()

# If we reach here, both name & role are in session_state
st.query_params.user = st.session_state["name"]
name = st.session_state["name"]
role = st.session_state["role"]

# --- MAIN DATABASE CONNECTION FOR THE PAGE ---
try:
    db = connector.connect(host="localhost", user="root", password="sqladi@2710", database="auth")
    cursor = db.cursor()
except connector.Error as e:
    st.error(f"Database connection failed: {e}")
    st.stop()
    
# --- BACK BUTTON ---
if st.button("←"):
    role = st.session_state.get("role")
    if role == 'HR':
        st.switch_page("pages/3_HR_Dashboard.py")
    elif role == 'admin':
        st.switch_page("pages/4_Admin_Panel.py")
    else:
        # Fallback for any other roles or edge cases
        st.switch_page("Home.py")

# --- Custom Styles ---
st.markdown("""
    <style>
    .rating-card {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .rating-score {
        color: #007BFF;
        font-weight: 600;
    }
    h2, h3 {
        color: #1f4e79;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session check for selected employee ---
# This check now runs AFTER the main authentication check.
employee = st.session_state.get("selected_employee")
if not employee:
    st.error("No employee selected. Please return to your dashboard to select an employee.")
    if st.button("Go to My Dashboard"):
        role = st.session_state.get("role")
        if role == 'HR':
            st.switch_page("pages/3_HR_Dashboard.py")
        elif role == 'admin':
            st.switch_page("pages/4_Admin_Panel.py")
        # Add other roles if they can access this page
        else:
            # Default fallback
            st.switch_page("Home.py")
    st.stop()

# Define criteria lists
foundational_criteria = [
    "Humility", "Integrity", "Collegiality", "Attitude",
    "Time Management", "Initiative", "Communication", "Compassion"
]
futuristic_criteria = [
    "Knowledge & Awareness", "Future readiness",
    "Informal leadership", "Team Development", "Process adherence"
]

# Fetch user's role and manager details
cursor.execute("SELECT role, managed_by FROM users WHERE username=%s", (employee,))
user_details = cursor.fetchone()
user_role, managed_by = user_details if user_details else (None, None)


# --- Manager Ratings Section (Conditionally Displayed) ---
st.markdown("<h2 style='text-align: center;'>Manager Ratings</h2>", unsafe_allow_html=True)

# NEW: Check if the user is an employee and has a valid manager
if user_role == 'employee' and managed_by and managed_by != 'XYZ':
    cursor.execute("""
    SELECT rater, role, criteria, score, rating_type, timestamp
    FROM user_ratings
    WHERE ratee = %s AND rating_type = 'manager'
    ORDER BY timestamp DESC
    """, (employee,))
    manager_ratings = cursor.fetchall()
    
    if manager_ratings:
        ratings_by_criteria = {
            crit: (score, timestamp, rater, r_role)
            for rater, r_role, crit, score, r_type, timestamp in manager_ratings
        }
        col1, col2 = st.columns(2)
        for col, section, criteria_list in [(col1, "Foundational", foundational_criteria), (col2, "Futuristic", futuristic_criteria)]:
            with col:
                st.markdown(f"### {section} Progress")
                for crit in criteria_list:
                    if crit in ratings_by_criteria:
                        score, timestamp, rater, r_role = ratings_by_criteria[crit]
                        st.write(f"""
                            <div class='rating-card'>
                                <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                                <small>by <b>{rater}</b> ({r_role}) on {timestamp.strftime('%Y-%m-%d %H:%M')}</small>
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("No manager ratings have been submitted yet.")
else:
    # Display message for users without a manager (e.g., other managers)
    st.info("This user does not have a manager assigned.")

st.divider()

# --- Self Ratings Section (No changes needed here) ---
with st.container():
    st.markdown("<h2 style='text-align: center;'>Self Ratings</h2>", unsafe_allow_html=True)
    cursor.execute("""
        SELECT criteria, score, timestamp FROM user_ratings
        WHERE ratee = %s AND rating_type = 'self' ORDER BY timestamp DESC
    """, (employee,))
    self_ratings = cursor.fetchall()

    if self_ratings:
        col1, col2 = st.columns(2)
        for col, section, criteria_list in [(col1, "Foundational", foundational_criteria), (col2, "Futuristic", futuristic_criteria)]:
            with col:
                st.markdown(f"### {section} Progress")
                for crit in criteria_list:
                    matches = [r for r in self_ratings if r[0] == crit]
                    if matches:
                        score, timestamp = matches[0][1], matches[0][2]
                        st.markdown(f"""
                            <div class='rating-card'>
                                <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                                <small>submitted on {timestamp.strftime('%Y-%m-%d %H:%M')}</small>
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("No self ratings submitted yet.")
