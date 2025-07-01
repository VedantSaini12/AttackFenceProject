import streamlit as st
import mysql.connector as connector
import datetime
import uuid

from notifications import notification_bell_component, add_notification

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Manager Dashboard", page_icon="👔", layout="wide")

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

# --- ADD THIS NEW CSS BLOCK ---
st.markdown("""
<style>
.status-card {
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    border-left: 5px solid;
}
.status-card.not-ready {
    background-color: #fcf3f3; /* Light red */
    border-left-color: #d9534f; /* Bootstrap's danger color */
    color: #a94442;
}
.status-card.ready {
    background-color: #f3fcf3; /* Light green */
    border-left-color: #5cb85c; /* Bootstrap's success color */
    color: #3c763d;
}
.status-icon {
    font-size: 2rem;
    line-height: 1;
}
.status-text {
    font-weight: 500;
}
.eval-column {
    padding: 0 1rem;
    border: 1px solid #e1e4e8;
    border-radius: 8px;
    background-color: #fafafa;
    height: 40px;
    margin-right: 8rem;
}
div[data-baseweb="slider"] {
    width: 80% !important;
}
</style>
""", unsafe_allow_html=True)
# --- END OF NEW CSS BLOCK ---

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

# --- MAIN DATABASE CONNECTION FOR THE PAGE ---
try:
    db = connector.connect(host="localhost", user="root", password="password", database="auth")
    cursor = db.cursor()
except connector.Error as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

notification_bell_component(st.session_state.name)

# --- MANAGER DASHBOARD UI ---
st.title("Manager Dashboard 👔")
st.write("---")
st.write(f"<center><h2>Welcome {name}!</h2></center>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# Section for managers to rate their employees
st.subheader("Evaluate Your Team Members")
cursor.execute("SELECT username FROM users WHERE managed_by = %s", (name,))
employees = cursor.fetchall()
if employees:
    # Your existing logic for the manager to rate employees.
    # This includes the loop `for emp in employees:`, the expanders for each employee,
    # the sliders, the remark box, and the submit button.
    # All of this is copied directly from your original file's "manager" section.
    # ...
    # (The full team evaluation code from your file is assumed here)
    # ...
    st.subheader("Your co-workers:")
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

    # Create a set of just the CRITERIA NAMES (strings)
    all_criteria_names = {crit[0] for crit in (development_criteria + other_aspects_criteria + foundational_criteria + futuristic_criteria)}

    for emp in employees:
        employee_name = emp[0]
        
        cursor.execute("""
            SELECT criteria FROM user_ratings 
            WHERE rater = %s AND rating_type = 'self'
        """, (employee_name,))
        employee_submitted_criteria = {row[0] for row in cursor.fetchall()}
        is_self_evaluation_complete = all_criteria_names.issubset(employee_submitted_criteria)
        
        with st.expander(f"Evaluate: **{employee_name}**"):

            if not is_self_evaluation_complete:
                st.markdown(f"""
                <div class="status-card not-ready">
                    <div class="status-icon">⏳</div>
                    <div class="status-text">
                        <b>Pending Self-Evaluation:</b><br>
                        {employee_name} has not submitted their self-evaluation form yet. The rating form will unlock once they have completed it.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-card ready">
                    <div class="status-icon">✅</div>
                    <div class="status-text">
                        <b>Ready for Manager Review:</b><br>
                        {employee_name} has completed their self-evaluation. You may now proceed with your rating.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                cursor.execute("""
                    SELECT criteria, score, timestamp FROM user_ratings
                    WHERE rater = %s AND ratee = %s AND rating_type = 'manager'
                """, (name, employee_name))
                manager_ratings = cursor.fetchall()
                manager_submitted_criteria = {crit for crit, _, _ in manager_ratings}

                if all_criteria_names.issubset(manager_submitted_criteria):
                    st.info(f"You have already submitted a rating for {employee_name}. Here is a summary:")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<h5>Development (70%)</h5>", unsafe_allow_html=True)
                        for crit, _ in development_criteria:
                            score, timestamp = next((s, t) for c, s, t in manager_ratings if c == crit)
                            st.markdown(f"**{crit}**: {score}/10 <small>(on {timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)
                        st.markdown("<h5>Foundational Progress</h5>", unsafe_allow_html=True)
                        for crit, _ in foundational_criteria:
                            score, timestamp = next((s, t) for c, s, t in manager_ratings if c == crit)
                            st.markdown(f"**{crit}**: {score}/10 <small>(on {timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)
                    with col2:
                        st.markdown("<h5>Other Aspects (30%)</h5>", unsafe_allow_html=True)
                        for crit, _ in other_aspects_criteria:
                            score, timestamp = next((s, t) for c, s, t in manager_ratings if c == crit)
                            st.markdown(f"**{crit}**: {score}/10 <small>(on {timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)
                        st.markdown("<h5>Futuristic Progress</h5>", unsafe_allow_html=True)
                        for crit, _ in futuristic_criteria:
                            score, timestamp = next((s, t) for c, s, t in manager_ratings if c == crit)
                            st.markdown(f"**{crit}**: {score}/10 <small>(on {timestamp.strftime('%Y-%m-%d')})</small>", unsafe_allow_html=True)
                    st.divider()
                    cursor.execute("SELECT remark FROM remarks WHERE rater = %s AND ratee = %s AND rating_type = 'manager';", (name, employee_name))
                    feedback = cursor.fetchone()
                    st.subheader("Your Remark:")
                    st.success(feedback[0] if feedback else "No remark was provided.")
                
                else:
                    cursor.execute("SELECT criteria, score FROM user_ratings WHERE rater = %s AND rating_type = 'self'", (employee_name,))
                    employee_self_ratings = dict(cursor.fetchall())

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"<div class='eval-column'><h5 style='text-align: center;'>{employee_name}'s Self-Evaluation</h5>", unsafe_allow_html=True)
                        st.markdown("<h6>Development (70%)</h6>", unsafe_allow_html=True)
                        for crit, weight in development_criteria:
                            st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee_name}_{crit}_dev", disabled=True)
                        st.markdown("<h6>Other Aspects (30%)</h6>", unsafe_allow_html=True)
                        for crit, weight in other_aspects_criteria:
                            st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee_name}_{crit}_other", disabled=True)
                        st.markdown("<h6>Foundational Progress</h6>", unsafe_allow_html=True)
                        for crit, weight in foundational_criteria:
                            st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee_name}_{crit}_found", disabled=True)
                        st.markdown("<h6>Futuristic Progress</h6>", unsafe_allow_html=True)
                        for crit, weight in futuristic_criteria:
                            st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee_name}_{crit}_fut", disabled=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    with col2:
                        st.markdown("<div class='eval-column'><h5 style='text-align: center;'>Your Review</h5>", unsafe_allow_html=True)
                        all_scores = {}
                        st.markdown("<h6>Development (70%)</h6>", unsafe_allow_html=True)
                        for crit, weight in development_criteria:
                            all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee_name}_{crit}_dev_manager")
                        st.markdown("<h6>Other Aspects (30%)</h6>", unsafe_allow_html=True)
                        for crit, weight in other_aspects_criteria:
                            all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee_name}_{crit}_other_manager")
                        st.markdown("<h6>Foundational Progress</h6>", unsafe_allow_html=True)
                        for crit, weight in foundational_criteria:
                            all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee_name}_{crit}_found_manager")
                        st.markdown("<h6>Futuristic Progress</h6>", unsafe_allow_html=True)
                        for crit, weight in futuristic_criteria:
                            all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee_name}_{crit}_fut_manager")
                        st.markdown("</div>", unsafe_allow_html=True)

                    remark = st.text_area("Add Overall Remark/Feedback", placeholder="Enter your feedback here...", key=f"remark_{employee_name}")

                    if st.button(f"Submit Final Rating for {employee_name}", key=f"submit_{employee_name}_manager", type="primary"):
                        for crit, score in all_scores.items():
                            cursor.execute(
                                "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type) VALUES (%s, %s, %s, %s, %s, %s)",
                                (name, employee_name, role, crit, score, "manager")
                            )
                        if remark:
                            cursor.execute(
                                "INSERT INTO remarks (rater, ratee, rating_type, remark) VALUES (%s, %s, %s, %s)",
                                (name, employee_name, "manager", remark)
                            )
                        db.commit()
                        add_notification(
                            recipient=employee_name,
                            sender=name, # 'name' is the manager's name from session_state
                            message=f"Your manager, {name}, has completed your evaluation.",
                            notification_type='evaluation_completed'
                        )
                        st.success(f"Rating for {employee_name} submitted successfully!")
                        st.rerun()
else:
    st.info("You do not currently manage any employees.")

# Manager self-rating form
st.write("---")
st.subheader("Submit Your Self-Evaluation")
with st.expander("Open Self-Evaluation Form", expanded=False):
    # Your existing, detailed self-rating form logic for managers goes here.
    # This is copied directly from your original file's "manager" section.
    # ...
    # (The full manager self-rating form code from your file is assumed here)
    # ...
    unique_prefix = "manager_self_rating"
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
        st.info("You have already submitted your self-rating. Here is a summary:")
        
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

        st.write("---")
        cursor.execute("SELECT remark FROM remarks WHERE rater = %s AND ratee = %s AND rating_type = 'admin';", (name, emp[0]))   
        feedback = cursor.fetchone()
        st.subheader("Remark:")
        if feedback:
            st.write(feedback[0])
        else:
            st.write("No remarks found.")
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
            # --- ADD THIS NOTIFICATION LOGIC ---
            add_notification(
                recipient=employee_name,
                sender=name,
                message=f"Your manager, {name}, has completed your evaluation.",
                notification_type='evaluation_completed'
            )
            # --- END OF NOTIFICATION LOGIC ---
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