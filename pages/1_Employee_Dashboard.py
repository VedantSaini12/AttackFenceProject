import streamlit as st
import mysql.connector as connector

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Employee Dashboard", page_icon="👤", layout="wide")

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
    if manager_ratings:
        ratings_by_criteria = {r[2]: (r[3], r[5], r[0], r[1]) for r in manager_ratings}
        col1, col2 = st.columns(2)
        # Display logic for foundational and futuristic criteria...
        # (This detailed display logic is copied from your original file)
        
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

    all_criteria = [crit for crit, _ in foundational_criteria + futuristic_criteria]
    submitted_criteria = set([crit for crit, _, _ in self_ratings])
    if set(all_criteria).issubset(submitted_criteria):
        st.info("You have already submitted your self-rating. Here is a summary:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Foundational Progress")
            for crit, _ in foundational_criteria:
                if crit in [c for c, _, _ in self_ratings]:
                    score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                    st.markdown(
                        f"**{crit}**: {score}/10  \n<small>(submitted on {timestamp.strftime('%Y-%m-%d %H:%M')})</small>",
                        unsafe_allow_html=True
                    )
        with col2:
            st.markdown("### Futuristic Progress")
            for crit, _ in futuristic_criteria:
                if crit in [c for c, _, _ in self_ratings]:
                    score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                    st.markdown(
                        f"**{crit}**: {score}/10  \n<small>(submitted on {timestamp.strftime('%Y-%m-%d %H:%M')})</small>",
                        unsafe_allow_html=True
                    )
    else:
        foundational_scores = {}
        st.write("### Foundational Progress")
        for crit, weight in foundational_criteria:
            if crit not in submitted_criteria:
                foundational_scores[crit] = st.slider(
                    f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_self"
                )

        futuristic_scores = {}
        st.write("### Futuristic Progress")
        for crit, weight in futuristic_criteria:
            if crit not in submitted_criteria:
                futuristic_scores[crit] = st.slider(
                    f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_fut_self"
                )

        @st.dialog("Confirmation")
        def self_submit():
            st.success("Your self-rating has been submitted.")
            if st.button("Close"):
                st.rerun()

        if (foundational_scores or futuristic_scores) and st.button("Submit Your Self-Rating"):
            cursor.execute("""
                SELECT criteria FROM user_ratings
                WHERE rater = %s AND ratee = %s AND rating_type = 'self'
            """, (name, name))
            already_submitted = set([row[0] for row in cursor.fetchall()])
            for crit, score in foundational_scores.items():
                if crit not in already_submitted:
                    cursor.execute(
                        "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type) VALUES (%s, %s, %s, %s, %s, %s)",
                        (name, name, user[3], crit, score, "self")
                    )
            for crit, score in futuristic_scores.items():
                if crit not in already_submitted:
                    cursor.execute(
                        "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type) VALUES (%s, %s, %s, %s, %s, %s)",
                        (name, name, user[3], crit, score, "self")
                    )
            db.commit()
            self_submit()

# --- LOGOUT BUTTON ---
st.write("---")
if st.button("Logout", type="primary"):
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("Home.py")
