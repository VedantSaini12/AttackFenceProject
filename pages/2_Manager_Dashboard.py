# File: pages/2_Manager_Dashboard.py

import streamlit as st
import mysql.connector as connector

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Manager Dashboard", page_icon="👔", layout="wide")

# --- AUTHENTICATION GUARD ---
if "name" not in st.session_state:
    if "user" in st.query_params:
        st.session_state["name"] = st.query_params["user"]
    else:
        st.error("No user logged in. Please log in first.")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()
st.query_params.user = st.session_state["name"]
name = st.session_state["name"]

# --- DATABASE CONNECTION ---
db = connector.connect(host="localhost", user="root", password="sqladi@2710", database="auth")
cursor = db.cursor()
cursor.execute("SELECT * FROM users WHERE username = %s", (name,))
user = cursor.fetchone()

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
    st.subheader("Your employees:")
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
    for emp in employees:
        with st.expander(f"- {emp[0]}"):
            cursor.execute("""
        SELECT criteria, score, timestamp FROM user_ratings
        WHERE rater = %s AND ratee = %s ORDER BY timestamp DESC
    """, (name, emp[0]))
            self_ratings = cursor.fetchall()
            all_criteria = [crit for crit, _ in foundational_criteria + futuristic_criteria]
            submitted_criteria = set([crit for crit, _, _ in self_ratings])
            if set(all_criteria).issubset(submitted_criteria):
                st.info(f"You have already submitted a rating for {emp[0]}. Here is a summary:")
                # Display summary in two columns for better readability
                summary = {}
                col1, col2 = st.columns(2)
                # Foundational criteria in col1
                with col1:
                    st.markdown("### Foundational Progress")
                    for crit, _ in foundational_criteria:
                        if crit in [c for c, _, _ in self_ratings]:
                            score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                            st.markdown(
                                f"**{crit}**: {score}/10  \n<small>(submitted on {timestamp.strftime('%Y-%m-%d %H:%M')})</small>",
                                unsafe_allow_html=True
                            )
                # Futuristic criteria in col2
                with col2:
                    st.markdown("### Futuristic Progress")
                    for crit, _ in futuristic_criteria:
                        if crit in [c for c, _, _ in self_ratings]:
                            score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                            st.markdown(
                                f"**{crit}**: {score}/10  \n<small>(submitted on {timestamp.strftime('%Y-%m-%d %H:%M')})</small>",
                                unsafe_allow_html=True
                            )
                st.divider()
                cursor.execute("SELECT remark FROM remarks WHERE rater = %s AND ratee = %s AND rating_type = 'manager';", (name, emp[0]))
                feedback = cursor.fetchone()
                st.subheader("Remark:")
                if feedback:
                    st.write(feedback[0])
                else:
                    st.write("No remarks found.")
            else:
                st.write("### Foundational Progress")
                
                foundational_scores = {}
                for crit, weight in foundational_criteria:
                    foundational_scores[crit] = st.slider(
                        f"{crit} ({weight}%)", 0, 10, 0, key=f"{emp[0]}_{crit}_manager"
                    )

                st.write("### Futuristic Progress")
                futuristic_scores = {}
                for crit, weight in futuristic_criteria:
                    futuristic_scores[crit] = st.slider(
                        f"{crit} ({weight}%)", 0, 10, 0, key=f"{emp[0]}_{crit}_fut_manager"
                    )
                # Add a text area for remarks/feedback
                st.write("### Add Remark/Feedback")
                remark = st.text_area(label="Remark", placeholder="Enter your feedback here...", key=f"remark_{emp[0]}")
                @st.dialog("Confirmation")
                def confirm_submit():
                    st.success(f"Ranking submitted for {emp[0]}")
                    if st.button("Close"):
                        st.rerun()
                if st.button(f"Submit Ranking for {emp[0]}", key=f"submit_{emp[0]}_manager"):
                    # Save the manager's ratings for the employee in the database
                    for crit, score in foundational_scores.items():
                        cursor.execute(
                            "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type) VALUES (%s, %s, %s, %s, %s, %s)",
                            (name, emp[0], user[3], crit, score, "manager")
                        )
                    for crit, score in futuristic_scores.items():
                        cursor.execute(
                            "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type) VALUES (%s, %s, %s, %s, %s, %s)",
                            (name, emp[0], user[3], crit, score, "manager")
                        )
                    cursor.execute(
                            "INSERT INTO remarks (rater, ratee, rating_type, remark) VALUES (%s, %s, %s, %s)",
                            (name, emp[0], "manager", remark)
                        )
                    db.commit()
                    confirm_submit()
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

    all_criteria = [crit for crit, _ in foundational_criteria + futuristic_criteria]
    submitted_criteria = set([crit for crit, _, _ in self_ratings])
    if set(all_criteria).issubset(submitted_criteria):
        st.info("You have already submitted your self-rating. Here is a summary:")
        # Display summary in two columns for better readability
        summary = {}
        col1, col2 = st.columns(2)
        # Foundational criteria in col1
        with col1:
            st.markdown("### Foundational Progress")
            for crit, _ in foundational_criteria:
                if crit in [c for c, _, _ in self_ratings]:
                    score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                    st.markdown(
                        f"**{crit}**: {score}/10  \n<small>(submitted on {timestamp.strftime('%Y-%m-%d %H:%M')})</small>",
                        unsafe_allow_html=True
                    )
        # Futuristic criteria in col2
        with col2:
            st.markdown("### Futuristic Progress")
            for crit, _ in futuristic_criteria:
                if crit in [c for c, _, _ in self_ratings]:
                    score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                    st.markdown(
                        f"**{crit}**: {score}/10  \n<small>(submitted on {timestamp.strftime('%Y-%m-%d %H:%M')})</small>",
                        unsafe_allow_html=True
                    )
        st.write("---")
        cursor.execute("SELECT remark FROM remarks WHERE rater = %s AND ratee = %s AND rating_type = 'admin';", (name, emp[0]))   
        feedback = cursor.fetchone()
        st.subheader("Remark:")
        if feedback:
            st.write(feedback[0])
        else:
            st.write("No remarks found.")
    else:
        foundational_scores = {}
        st.write("### Foundational Progress")
        for crit, weight in foundational_criteria:
            if crit not in submitted_criteria:
                foundational_scores[crit] = st.slider(
                    f"{crit} ({weight}%)", 0, 10, 0, key=f"{unique_prefix}_{name}_{crit}_self_manager"
                )

        futuristic_scores = {}
        st.write("### Futuristic Progress")
        for crit, weight in futuristic_criteria:
            if crit not in submitted_criteria:
                futuristic_scores[crit] = st.slider(
                    f"{crit} ({weight}%)", 0, 10, 0, key=f"{unique_prefix}_{name}_{crit}_fut_self_manager"
                )
        @st.dialog("Confirmation")
        def self_submit():
            st.success("Your self-rating has been submitted.")
            if st.button("Close"):
                st.rerun()
        if (foundational_scores or futuristic_scores) and st.button("Submit Your Self-Rating", key=f"{unique_prefix}_submit_self_rating_manager"):
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
if st.button("⚠️ Logout", type="primary"):
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("Home.py")