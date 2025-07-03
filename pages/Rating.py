import streamlit as st
import mysql.connector as connector
import datetime
import uuid

# Page Config
st.set_page_config(page_title="Evaluation Report", layout="wide")

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
development_criteria = [
    "Quality of Work", "Task Completion", "Timeline Adherence"
]

other_aspects_criteria = [
    "Collaboration", "Innovation", "Special Situation"
]

# Fetch user's role and manager details
cursor.execute("SELECT role, managed_by FROM users WHERE username=%s", (employee,))
user_details = cursor.fetchone()
user_role, managed_by = user_details if user_details else (None, None)


# --- Manager Ratings Section (Conditionally Displayed) ---
st.markdown("<h2 style='text-align: center;'>Manager Ratings</h2>", unsafe_allow_html=True)

if user_role == 'employee' and managed_by and managed_by != 'XYZ':
    # Fetch ratings separately
    cursor.execute("""
        SELECT rater, role, criteria, score, timestamp
        FROM user_ratings
        WHERE ratee = %s AND rating_type = 'manager'
        ORDER BY timestamp DESC
    """, (employee,))
    manager_ratings = cursor.fetchall()

    # Fetch remark separately
    cursor.execute("""
        SELECT remark FROM remarks
        WHERE ratee = %s AND rating_type = 'manager'
        LIMIT 1
    """, (employee,))
    manager_remark_result = cursor.fetchone()
    manager_remark = manager_remark_result[0] if manager_remark_result else None

    if manager_ratings:
        ratings_by_criteria = {
            crit: (score, timestamp, rater, r_role)
            for rater, r_role, crit, score, timestamp in manager_ratings
        }

        col1, col2 = st.columns(2)

        # Display Development and Foundational in the first column
        with col1:
            st.markdown("### Development (70%)")
            for crit in development_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.write(f"""
                        <div class='rating-card'>
                            <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                            <small>by <b>{rater}</b> on {timestamp.strftime('%Y-%m-%d')}</small>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("### Foundational Progress")
            for crit in foundational_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.write(f"""
                        <div class='rating-card'>
                            <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                            <small>by <b>{rater}</b> on {timestamp.strftime('%Y-%m-%d')}</small>
                        </div>
                    """, unsafe_allow_html=True)

        # Display Other Aspects and Futuristic in the second column
        with col2:
            st.markdown("### Other Aspects (30%)")
            for crit in other_aspects_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.write(f"""
                        <div class='rating-card'>
                            <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                            <small>by <b>{rater}</b> on {timestamp.strftime('%Y-%m-%d')}</small>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("### Futuristic Progress")
            for crit in futuristic_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.write(f"""
                        <div class='rating-card'>
                            <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                            <small>by <b>{rater}</b> on {timestamp.strftime('%Y-%m-%d')}</small>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Display the remark after the ratings
        if manager_remark:
            st.divider()
            st.markdown("### Manager's Remark")
            st.markdown(f"<div class='rating-card'>{manager_remark}</div>", unsafe_allow_html=True)

    else:
        st.info("No manager ratings have been submitted yet.")

    # This handles the case where a remark exists but no ratings were submitted
    if not manager_ratings and manager_remark:
        st.markdown("### Manager's Remark")
        st.markdown(f"<div class='rating-card'>{manager_remark}</div>", unsafe_allow_html=True)

else:
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
        ratings_by_criteria = {crit: (score, ts) for crit, score, ts in self_ratings}
        
        col1, col2 = st.columns(2)

        # Display Development and Foundational in the first column
        with col1:
            st.markdown("### Development (70%)")
            for crit in development_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp = ratings_by_criteria[crit]
                    st.markdown(f"""
                        <div class='rating-card'>
                            <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                            <small>submitted on {timestamp.strftime('%Y-%m-%d')}</small>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("### Foundational Progress")
            for crit in foundational_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp = ratings_by_criteria[crit]
                    st.markdown(f"""
                        <div class='rating-card'>
                            <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                            <small>submitted on {timestamp.strftime('%Y-%m-%d')}</small>
                        </div>
                    """, unsafe_allow_html=True)

        # Display Other Aspects and Futuristic in the second column
        with col2:
            st.markdown("### Other Aspects (30%)")
            for crit in other_aspects_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp = ratings_by_criteria[crit]
                    st.markdown(f"""
                        <div class='rating-card'>
                            <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                            <small>submitted on {timestamp.strftime('%Y-%m-%d')}</small>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("### Futuristic Progress")
            for crit in futuristic_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp = ratings_by_criteria[crit]
                    st.markdown(f"""
                        <div class='rating-card'>
                            <b>{crit}</b>: <span class='rating-score'>{score}/10</span><br>
                            <small>submitted on {timestamp.strftime('%Y-%m-%d')}</small>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No self ratings submitted yet.")
