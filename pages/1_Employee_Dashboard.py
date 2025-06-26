import streamlit as st
import mysql.connector as connector
import datetime
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Employee Dashboard", page_icon="👤", layout="wide")

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

name = st.session_state["name"]
role = st.session_state["role"]

# --- MAIN DATABASE CONNECTION FOR THE PAGE ---
try:
    db = connector.connect(host="localhost", user="root", password="sqladi@2710", database="auth")
    cursor = db.cursor()
except connector.Error as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# --- EMPLOYEE DASHBOARD UI ---
st.title("Employee Dashboard 👤")
st.write("---")
st.write(f"<center><h2>Welcome {name}!</h2></center>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# Show ratings given to the employee by others
st.subheader("Ratings Received")
# Fetch all ratings for the employee
cursor.execute("""
    SELECT rater, role, criteria, score, rating_type, timestamp
    FROM user_ratings
    WHERE ratee = %s
    ORDER BY timestamp DESC
""", (name,))
ratings = cursor.fetchall()

# Separate ratings by admin and manager
admin_ratings = [r for r in ratings if r[4] == "admin"]
manager_ratings = [r for r in ratings if r[4] == "manager"]

foundational_criteria = ["Humility", "Integrity", "Collegiality", "Attitude", "Time Management", "Initiative", "Communication", "Compassion"]
futuristic_criteria = ["Knowledge & Awareness", "Future readiness", "Informal leadership", "Team Development", "Process adherence"]

# Manager Ratings/Remarks Dropdown (Changed from "Ratings" to "Remarks" as per requirements)
with st.expander("👔 Manager Remarks", expanded=False):
    development_criteria = [
        "Quality of Work", "Task Completion", "Timeline Adherence"
    ]
    other_aspects_criteria = [
        "Collaboration", "Innovation", "Special Situation"
    ]
    foundational_criteria = ["Humility", "Integrity", "Collegiality", "Attitude", "Time Management", "Initiative", "Communication", "Compassion"]
    futuristic_criteria = ["Knowledge & Awareness", "Future readiness", "Informal leadership", "Team Development", "Process adherence"]

    if manager_ratings:
        ratings_by_criteria = {r[2]: (r[3], r[5], r[0], r[1]) for r in manager_ratings}
        
        col1, col2 = st.columns(2)
        
        # --- THIS IS THE MISSING DISPLAY LOGIC ---
        with col1:
            st.markdown("<h3>Development (70%)</h3>", unsafe_allow_html=True)
            for crit in development_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.markdown(f"**{crit}**: {score}/10 <small>({timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)
            
            st.markdown("<h3>Foundational Progress</h3>", unsafe_allow_html=True)
            for crit in foundational_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.markdown(f"**{crit}**: {score}/10 <small>({timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)

        with col2:
            st.markdown("<h3>Other Aspects (30%)</h3>", unsafe_allow_html=True)
            for crit in other_aspects_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.markdown(f"**{crit}**: {score}/10 <small>({timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)

            st.markdown("<h3>Futuristic Progress</h3>", unsafe_allow_html=True)
            for crit in futuristic_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.markdown(f"**{crit}**: {score}/10 <small>({timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)
        # --- END OF MISSING LOGIC ---
        
        st.divider()
        cursor.execute("SELECT remark FROM remarks WHERE ratee = %s AND rating_type = 'manager';", (name, ))
        feedback = cursor.fetchone()
        st.subheader("Remark:")
        if feedback:
            st.write(feedback[0])
        else:
            st.write("No remarks found.")
    else:
        st.info("No manager remarks received yet.")

# Employee self-rating form
st.write("---")
st.subheader("Submit Your Self-Evaluation")
with st.expander("Open Self-Evaluation Form", expanded=False):
    # Your existing, detailed self-rating form logic goes here.
    # This includes checking if already submitted, showing sliders, and the submit button.
    # All of this is copied directly from your original file's "employee" section.
    # ...
    # (The full self-rating form code from your file is assumed here)
    # ...
    # Self-rating form in an expander (dropdown style)
    cursor.execute("""
        SELECT criteria, score, timestamp FROM user_ratings
        WHERE rater = %s AND ratee = %s AND rating_type = 'self'
        ORDER BY timestamp DESC
    """, (name, name))
    self_ratings = cursor.fetchall()

    foundational_criteria = [
        ("Humility", 12.5),
        ("Integrity", 12.5),
        ("Collegiality", 12.5),
        ("Attitude", 12.5),
        ("Time Management", 12.5),
        ("Initiative", 12.5),
        ("Communication", 12.5),
        ("Compassion", 12.5),
    ]

    futuristic_criteria = [
        ("Knowledge & Awareness", 20),
        ("Future readiness", 20),
        ("Informal leadership", 20),
        ("Team Development", 20),
        ("Process adherence", 20),
    ]
    development_criteria = [
        ("Quality of Work", 28),
        ("Task Completion", 14),
        ("Timeline Adherence", 28),
    ]

    other_aspects_criteria = [
        ("Collaboration", 10),
        ("Innovation", 10),
        ("Special Situation", 10),
    ]

    all_criteria = [crit for crit, _ in development_criteria + other_aspects_criteria + foundational_criteria + futuristic_criteria]
    submitted_criteria = set([crit for crit, _, _ in self_ratings])
    
    if set(all_criteria).issubset(submitted_criteria):
        st.info("You have already submitted your self-rating.")
        
        # Create columns for the summary view
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Development (70%)")
            for crit, _ in development_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10  <small>(on {timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)
            
            st.markdown("### Foundational Progress")
            for crit, _ in foundational_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10  <small>(on {timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Other Aspects (30%)")
            for crit, _ in other_aspects_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10  <small>(on {timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)

            st.markdown("### Futuristic Progress")
            for crit, _ in futuristic_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10  <small>(on {timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)

    else:
        # Dictionary to hold all scores
        all_scores = {}

        st.markdown("#### Development (70%)")
        for crit, weight in development_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_dev_self")
        
        st.markdown("#### Other Aspects (30%)")
        for crit, weight in other_aspects_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_other_self")

        st.markdown("#### Foundational Progress")
        for crit, weight in foundational_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_found_self")

        st.markdown("#### Futuristic Progress")
        for crit, weight in futuristic_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_fut_self")
        
        @st.dialog("Confirmation")
        def self_submit():
            st.success("Your self-rating has been submitted.")
            if st.button("Close"):
                st.rerun()

        if all_scores and st.button("Submit Your Self-Rating"):
            # Check for already submitted criteria one last time to prevent duplicates
            cursor.execute("SELECT criteria FROM user_ratings WHERE rater = %s AND rating_type = 'self'", (name,))
            already_submitted = {row[0] for row in cursor.fetchall()}
            
            # Insert all new scores in a single loop
            for crit, score in all_scores.items():
                if crit not in already_submitted:
                    cursor.execute(
                        "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type) VALUES (%s, %s, %s, %s, %s, %s)",
                        (name, name, role, crit, score, "self")
                    )
            db.commit()
            self_submit()

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
