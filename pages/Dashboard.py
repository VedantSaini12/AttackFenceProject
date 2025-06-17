import streamlit as st
import hashlib
import bcrypt
import mysql.connector as connector

try:
    name = st.session_state["name"]
except:
    st.error("No username provided. Please log in first.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()
db = connector.connect(
        host="localhost",         # change if needed
        user="root",              # your MySQL Email
        password="password", # your MySQL password
    )
cursor = db.cursor()
cursor.execute("USE auth")
cursor.execute("SELECT * FROM users WHERE username = %s", (name,))
user = cursor.fetchone()

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
)
st.title("Dashboard 📊")
st.write("---")
try:
    st.write(f"<center><h2>Welcome {name} - {user[3]}!</h2></center>", unsafe_allow_html=True)
except:
    st.error("No username provided. Please log in first.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()
st.write("<br>", unsafe_allow_html=True)
if user[3] == "employee":
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

    # Admin Ratings Dropdown
    with st.expander("⭐ Admin Ratings", expanded=False):
        # Group ratings by criteria for summary
        foundational_criteria = [
            "Humility", "Integrity", "Collegiality", "Attitude",
            "Time Management", "Initiative", "Communication", "Compassion"
        ]
        futuristic_criteria = [
            "Knowledge & Awareness", "Future readiness",
            "Informal leadership", "Team Development", "Process adherence"
        ]
        if admin_ratings:
            # Organize ratings by criteria
            ratings_by_criteria = {}
            for rater, role, criteria, score, rating_type, timestamp in admin_ratings:
                ratings_by_criteria[criteria] = (score, timestamp, rater, role)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Foundational Progress")
                for crit in foundational_criteria:
                    if crit in ratings_by_criteria:
                        score, timestamp, rater, role = ratings_by_criteria[crit]
                        st.markdown(
                            f"<div style='padding:8px; border-bottom:1px solid #eee;'>"
                            f"<b>{crit}</b>: <span style='color:#1f77b4;'>{score}/10</span> "
                            f"<br><small>by <b>{rater}</b> ({role}), {timestamp.strftime('%Y-%m-%d %H:%M')}</small>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
            with col2:
                st.markdown("### Futuristic Progress")
                for crit in futuristic_criteria:
                    if crit in ratings_by_criteria:
                        score, timestamp, rater, role = ratings_by_criteria[crit]
                        st.markdown(
                            f"<div style='padding:8px; border-bottom:1px solid #eee;'>"
                            f"<b>{crit}</b>: <span style='color:#1f77b4;'>{score}/10</span> "
                            f"<br><small>by <b>{rater}</b> ({role}), {timestamp.strftime('%Y-%m-%d %H:%M')}</small>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
        else:
            st.info("No admin ratings received yet.")

    # Manager Ratings Dropdown
    with st.expander("👔 Manager Ratings", expanded=False):
        if manager_ratings:
            # Organize ratings by criteria
            ratings_by_criteria = {}
            for rater, role, criteria, score, rating_type, timestamp in manager_ratings:
                ratings_by_criteria[criteria] = (score, timestamp, rater, role)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Foundational Progress")
                for crit in foundational_criteria:
                    if crit in ratings_by_criteria:
                        score, timestamp, rater, role = ratings_by_criteria[crit]
                        st.markdown(
                            f"<div style='padding:8px; border-bottom:1px solid #eee;'>"
                            f"<b>{crit}</b>: <span style='color:#ff7f0e;'>{score}/10</span> "
                            f"<br><small>by <b>{rater}</b> ({role}), {timestamp.strftime('%Y-%m-%d %H:%M')}</small>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
            with col2:
                st.markdown("### Futuristic Progress")
                for crit in futuristic_criteria:
                    if crit in ratings_by_criteria:
                        score, timestamp, rater, role = ratings_by_criteria[crit]
                        st.markdown(
                            f"<div style='padding:8px; border-bottom:1px solid #eee;'>"
                            f"<b>{crit}</b>: <span style='color:#ff7f0e;'>{score}/10</span> "
                            f"<br><small>by <b>{rater}</b> ({role}), {timestamp.strftime('%Y-%m-%d %H:%M')}</small>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
        else:
            st.info("No manager ratings received yet.")
    ratings = cursor.fetchall()
    if ratings:
        for rater, role, criteria, score, rating_type, timestamp in ratings:
            st.write(f"**{criteria}**: {score}/10 (by {rater}, {role}, {rating_type}, {timestamp.strftime('%Y-%m-%d %H:%M')})")
    st.write("---")
    # Employee self-rating form
    st.write("## Submit Your Self-Rating")
    # Self-rating form in an expander (dropdown style)
    with st.expander("Open Self-Rating Form", expanded=False):
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
elif user[3] == "manager":
    cursor.execute("SELECT username FROM users WHERE managed_by = %s", (name,))
    employees = cursor.fetchall()
    # Show ratings given to the manager by the admin
    
    cursor.execute("""
        SELECT rater, role, criteria, score, rating_type, timestamp
        FROM user_ratings
        WHERE ratee = %s AND rating_type = 'admin'
        ORDER BY timestamp DESC
    """, (name,))
    admin_ratings = cursor.fetchall()
    with st.expander("⭐ Admin Ratings for You", expanded=False):
        if admin_ratings:
            # Organize ratings by criteria
            foundational_criteria = [
                "Humility", "Integrity", "Collegiality", "Attitude",
                "Time Management", "Initiative", "Communication", "Compassion"
            ]
            futuristic_criteria = [
                "Knowledge & Awareness", "Future readiness",
                "Informal leadership", "Team Development", "Process adherence"
            ]
            ratings_by_criteria = {}
            for rater, role, criteria, score, rating_type, timestamp in admin_ratings:
                ratings_by_criteria[criteria] = (score, timestamp, rater, role)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Foundational Progress")
                for crit in foundational_criteria:
                    if crit in ratings_by_criteria:
                        score, timestamp, rater, role = ratings_by_criteria[crit]
                        st.markdown(
                            f"<div style='padding:8px; border-bottom:1px solid #eee;'>"
                            f"<b>{crit}</b>: <span style='color:#1f77b4;'>{score}/10</span> "
                            f"<br><small>by <b>{rater}</b> ({role}), {timestamp.strftime('%Y-%m-%d %H:%M')}</small>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
            with col2:
                st.markdown("### Futuristic Progress")
                for crit in futuristic_criteria:
                    if crit in ratings_by_criteria:
                        score, timestamp, rater, role = ratings_by_criteria[crit]
                        st.markdown(
                            f"<div style='padding:8px; border-bottom:1px solid #eee;'>"
                            f"<b>{crit}</b>: <span style='color:#1f77b4;'>{score}/10</span> "
                            f"<br><small>by <b>{rater}</b> ({role}), {timestamp.strftime('%Y-%m-%d %H:%M')}</small>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
        else:
            st.info("No admin ratings received yet.")
    st.write("---")
    if employees:
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
                        db.commit()
                        confirm_submit()
    else:
        st.write("You do not manage any employees.")

    # Manager self-rating form
    st.write("---")
    st.write("## Submit Your Self-Rating")
    # Self-rating form in an expander (modal not available in Streamlit)
    with st.expander("Open Self-Rating Form", expanded=False):
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
                

elif user[3] == "admin":
    cursor.execute("SELECT username FROM users where username != %s", (name,))
    employees = cursor.fetchall()
    st.write("You are an admin and manage all users:")
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
    if employees:
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
                                (name, emp[0], user[3], crit, score, "admin")
                            )
                        for crit, score in futuristic_scores.items():
                            cursor.execute(
                                "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type) VALUES (%s, %s, %s, %s, %s, %s)",
                                (name, emp[0], user[3], crit, score, "admin")
                            )
                        db.commit()
                        confirm_submit()
    else:
        st.write("No employees found.")
    st.write("---")
    # Admin button to create new employee or manager
    st.write("## Manage Employees")
    if st.button("Go to Employee Management"):
        st.switch_page("pages/Admin.py")
elif user[3] == "hr":
    @st.dialog("Confirmation")
    def add_submit(emp_name):
        st.success(f"Created new user: {emp_name}")
        if st.button("Close"):
            st.rerun()
    st.write("You are an HR and have access to employee data.")
    st.subheader("Add New Employee")
    with st.form("add_employee_form", clear_on_submit=True):
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
                    add_submit(new_emp_name)

    st.write("---")

    # Section 2: Edit Existing Employees (except admin)
    st.subheader("Edit Existing Employees")
    cursor.execute(f"SELECT email, username, role, managed_by FROM users WHERE role != 'admin' and username != '{name}'")
    employees = cursor.fetchall()
    if not employees:
        st.info("No employees found.")
    else:
        for emp in employees:
            emp_username, emp_name, emp_role, emp_manager = emp
            with st.expander(f"**{emp_name}** ({emp_role})",icon="👤", expanded=False):
                new_name = st.text_input(f"Full Name for {emp_name}", value=emp_name, key=f"name_{emp_username}")
                # Only allow changing manager for employees, not managers/HR
                if emp_role == "employee":
                    cursor.execute("SELECT username FROM users WHERE role = 'manager'")
                    managers = [row[0] for row in cursor.fetchall()]
                    new_manager = st.selectbox(
                        f"Manager for {emp_name}", managers, 
                        index=managers.index(emp_manager) if emp_manager in managers else 0,
                        key=f"mgr_{emp_name}"
                    ) if managers else None # Managers cannot have their manager changed
                    # Allow changing role except to admin
                    new_role = st.selectbox(
                        f"Role for {emp_name}", 
                        ["employee", "manager", "hr"], 
                        index=["employee", "manager", "hr"].index(emp_role),
                        key=f"role_{emp_name}"
                    )
                else:
                    new_manager = emp_manager
                @st.dialog("Confirmation")
                def confirm_submit():
                    st.success(f"Updated details for {emp_name}")
                    if st.button("Close"):
                        st.rerun()
                # Password update
                new_password = st.text_input(f"New Password for {emp_name} (leave blank to keep unchanged)", type="password", key=f"pwd_{emp_username}")
                if st.button(f"Update {emp_name}", key=f"update_{emp_name}"):
                    if new_password:
                        # Encrypt the password using bcrypt
                        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                        cursor.execute(
                            "UPDATE users SET username = %s, role = %s, managed_by = %s, password = %s WHERE email = %s",
                            (new_name, new_role, new_manager, hashed, emp_username)
                        )
                        cursor.execute("Update users set managed_by = 'XYZ' where role = 'manager'")
                    else:
                        cursor.execute(
                            "UPDATE users SET username = %s, role = %s, managed_by = %s WHERE email = %s",
                            (new_name, new_role, new_manager, emp_username)
                        )
                    db.commit()
                    confirm_submit()
else:
    st.write("Unknown role.")

# Add logout button
st.write("---")
if st.button("Logout",type="primary"):
    st.session_state.clear()
    st.stop
    st.switch_page("Home.py")
