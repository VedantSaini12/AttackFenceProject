import streamlit as st
import mysql.connector as connector

# Page Config
st.set_page_config(page_title="Employee Ratings Dashboard", layout="wide")

# --- NEW AUTHENTICATION GUARD using Query Params ---
# 1. Check session state first
if "name" not in st.session_state:
    # 2. If not in session state, check the URL query parameters
    if "user" in st.query_params:
        # If a user is found in the URL, restore the session state from it
        st.session_state["name"] = st.query_params["user"]
    else:
        # If no user in session OR URL, deny access
        st.error("No user logged in. Please log in first.")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()

# 3. At this point, the user is authenticated.
#    Ensure the user's name is in the URL for refresh persistence.
st.query_params.user = st.session_state["name"]
name = st.session_state["name"]

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

# --- MySQL connection ---
try:
    db = connector.connect(
        host="localhost",
        user="root",
        password="sqladi@2710"
    )
    cursor = db.cursor()
    cursor.execute("USE auth")
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# --- Session check for selected employee ---
# This check now runs AFTER the main authentication check.
employee = st.session_state.get("selected_employee")
if not employee:
    st.error("No employee selected. Please go to the dashboard to select an employee.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/Dashboard.py")
    st.stop()

foundational_criteria = [
    "Humility", "Integrity", "Collegiality", "Attitude",
    "Time Management", "Initiative", "Communication", "Compassion"
]
futuristic_criteria = [
    "Knowledge & Awareness", "Future readiness",
    "Informal leadership", "Team Development", "Process adherence"
]

cursor.execute("SELECT role FROM users WHERE username=%s", (employee,))
role = cursor.fetchone()[0]

with st.container():
    # Admin Ratings
    cursor.execute("""
    SELECT rater, role, criteria, score, rating_type, timestamp
    FROM user_ratings
    WHERE ratee = %s AND rating_type = 'admin'
    ORDER BY timestamp DESC
    """, (employee,))
    admin_ratings = cursor.fetchall()
    st.markdown("<h2 style='text-align: center;'>Admin Ratings</h2>", unsafe_allow_html=True)
    if admin_ratings:
        ratings_by_criteria = {
            crit: (score, timestamp, rater, r_role)
            for rater, r_role, crit, score, r_type, timestamp in admin_ratings
        }
        col1, col2 = st.columns(2)
        for col, section, criteria_list in [(col1, "Foundational", foundational_criteria), (col2, "Futuristic", futuristic_criteria)]:
            with col:
                st.markdown(f"### {section} Progress")
                for crit in criteria_list:
                    if crit in ratings_by_criteria:
                        score, timestamp, rater, r_role = ratings_by_criteria[crit]
                        st.markdown(f"""
                            <div class='rating-card'>
                                <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                                <small>by <b>{rater}</b> ({r_role}) on {timestamp.strftime('%Y-%m-%d %H:%M')}</small>
                            </div>
                        """, unsafe_allow_html=True)
        st.write("### Remark: ")
        cursor.execute("Select remark from remarks where ratee = %s and rating_type = 'admin'", (employee,))
        feedback = cursor.fetchone()
        if feedback:
            st.markdown(f"{feedback[0]}", unsafe_allow_html=True)
        else:
            st.info("No feedback provided by admin.")
    else:
        st.info("No admin ratings received yet.")
st.divider()
if role == 'employee':
    foundational_criteria = [
    "Humility", "Integrity", "Collegiality", "Attitude",
    "Time Management", "Initiative", "Communication", "Compassion"
    ]
    futuristic_criteria = [
        "Knowledge & Awareness", "Future readiness",
        "Informal leadership", "Team Development", "Process adherence"
    ]
    cursor.execute("""
    SELECT rater, role, criteria, score, rating_type, timestamp
    FROM user_ratings
    WHERE ratee = %s AND rating_type = 'manager'
    ORDER BY timestamp DESC
    """, (employee,))
    manager_ratings = cursor.fetchall()
    st.markdown("<h2 style='text-align: center;'>Manager Ratings</h2>", unsafe_allow_html=True)
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
        st.info("No manager ratings received yet.")
    st.divider()
# Self Ratings
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