import streamlit as st
import mysql.connector as connector
import datetime
import uuid
from core.auth import protect_page, render_logout_button, get_db_connection, get_token_store
from core.constants import (
    foundational_criteria,
    futuristic_criteria,
    development_criteria,
    other_aspects_criteria,
    all_criteria_names
)

# Page Config
st.set_page_config(page_title="Evaluation Report", layout="wide")

protect_page(allowed_roles=["HR", "manager", "admin"])

db = get_db_connection()
token_store = get_token_store()

# Define session variables for easy use in the rest of the page
name = st.session_state["name"]
role = st.session_state["role"]
cursor = db.cursor(buffered=True)

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

# ADD THIS BLOCK TO CREATE THE QUARTERLY FILTER
now = datetime.datetime.now()
# Determine the current quarter to set as the default
quarter = (now.month - 1) // 3 + 1
quarters = [1, 2, 3, 4]
selected_quarter = st.selectbox(
    "Select Quarter to View Evaluations",
    quarters,
    index=quarter - 1, # Default to the current quarter
    key="evaluation_report_quarter"
)
# END OF ADDED BLOCK

col1, col2 = st.columns(2)

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

# Fetch user's role and manager details
cursor.execute("SELECT role, managed_by FROM users WHERE username=%s", (employee,))
user_details = cursor.fetchone()
user_role, managed_by = user_details if user_details else (None, None)


# --- Manager Ratings Section (Conditionally Displayed) ---
with col1:
    st.markdown("<h2 style='text-align: center;'>Self Ratings</h2>", unsafe_allow_html=True)
    cursor.execute("""
        SELECT criteria, score, timestamp FROM user_ratings
        WHERE ratee = %s AND rating_type = 'self' AND quarter = %s
        ORDER BY timestamp DESC
    """, (employee, selected_quarter))
    self_ratings = cursor.fetchall()

    if self_ratings:
        submission_date = self_ratings[0][2]
        st.write(f"**Submitted on:** {submission_date.strftime('%B %d, %Y')}")
        
        ratings_by_criteria = {crit: (score, ts) for crit, score, ts in self_ratings}

        st.markdown("### Development (70%)")
        for crit, _ in development_criteria:
            if crit in ratings_by_criteria:
                score, timestamp = ratings_by_criteria[crit]
                st.markdown(f"""
                    <div class='rating-card'>
                        <b>{crit}</b>: <span class='rating-score'>{score}/10</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("### Foundational Progress")
        for crit, _ in foundational_criteria:
            if crit in ratings_by_criteria:
                score, timestamp = ratings_by_criteria[crit]
                st.markdown(f"""
                    <div class='rating-card'>
                        <b>{crit}</b>: <span class='rating-score'>{score}/10</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("### Other Aspects (30%)")
        for crit, _ in other_aspects_criteria:
            if crit in ratings_by_criteria:
                score, timestamp = ratings_by_criteria[crit]
                st.markdown(f"""
                    <div class='rating-card'>
                        <b>{crit}</b>: <span class='rating-score'>{score}/10</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("### Futuristic Progress")
        for crit, _ in futuristic_criteria:
            if crit in ratings_by_criteria:
                score, timestamp = ratings_by_criteria[crit]
                st.markdown(f"""
                    <div class='rating-card'>
                        <b>{crit}</b>: <span class='rating-score'>{score}/10</span>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"No self ratings submitted for Quarter {selected_quarter}.")

with col2:
    st.markdown("<h2 style='text-align: center;'>Manager Ratings</h2>", unsafe_allow_html=True)

    if user_role == 'employee' and managed_by and managed_by != 'XYZ':
        # Check for existing manager ratings for the SELECTED quarter
        cursor.execute("""
            SELECT rater, role, criteria, score, timestamp FROM user_ratings
            WHERE ratee = %s AND rating_type = 'manager' AND quarter = %s
            ORDER BY timestamp DESC
        """, (employee, selected_quarter))
        manager_ratings = cursor.fetchall()

        # Fetch remark for the SELECTED quarter
        cursor.execute("""
            SELECT remark FROM remarks
            WHERE ratee = %s AND rating_type = 'manager' AND quarter = %s AND year = %s LIMIT 1
        """, (employee, selected_quarter, datetime.datetime.now().year))
        manager_remark_result = cursor.fetchone()
        manager_remark = manager_remark_result[0] if manager_remark_result else None

        # --- DISPLAY MODE: If ratings for this quarter exist, show them ---
        if manager_ratings:
            rater_name = manager_ratings[0][0]
            submission_date = manager_ratings[0][4]
            st.write(f"**Submitted by:** {rater_name} on {submission_date.strftime('%B %d, %Y')}")

            ratings_by_criteria = {crit: (score, ts, rater, r_role) for rater, r_role, crit, score, ts in manager_ratings}

            # Loop through and display all rating cards (same as your original code)
            st.markdown("### Development (70%)")
            for crit, _ in development_criteria:
                if crit in ratings_by_criteria:
                    score, _, _, _ = ratings_by_criteria[crit]
                    st.markdown(f"<div class='rating-card'><b>{crit}</b>: <span class='rating-score'>{score}/10</span></div>", unsafe_allow_html=True)
            # ... (Repeat for Foundational, Other Aspects, Futuristic)
            st.markdown("### Foundational Progress")
            for crit, _ in foundational_criteria:
                if crit in ratings_by_criteria:
                    score, _, _, _ = ratings_by_criteria[crit]
                    st.markdown(f"<div class='rating-card'><b>{crit}</b>: <span class='rating-score'>{score}/10</span></div>", unsafe_allow_html=True)

            st.markdown("### Other Aspects (30%)")
            for crit, _ in other_aspects_criteria:
                if crit in ratings_by_criteria:
                    score, _, _, _ = ratings_by_criteria[crit]
                    st.markdown(f"<div class='rating-card'><b>{crit}</b>: <span class='rating-score'>{score}/10</span></div>", unsafe_allow_html=True)

            st.markdown("### Futuristic Progress")
            for crit, _ in futuristic_criteria:
                if crit in ratings_by_criteria:
                    score, _, _, _ = ratings_by_criteria[crit]
                    st.markdown(f"<div class='rating-card'><b>{crit}</b>: <span class='rating-score'>{score}/10</span></div>", unsafe_allow_html=True)
            
            if manager_remark:
                st.divider()
                st.markdown("### Manager's Remark")
                st.markdown(f"<div class='rating-card'>{manager_remark}</div>", unsafe_allow_html=True)

        # --- INPUT MODE: If no ratings exist, show the input form for the manager ---
        else:
            # First, check if the employee has completed their self-evaluation for this quarter
            cursor.execute("""
                SELECT criteria FROM user_ratings
                WHERE ratee = %s AND rating_type = 'self' AND quarter = %s
            """, (employee, selected_quarter))
            employee_submitted_criteria = {row[0] for row in cursor.fetchall()}
            is_self_evaluation_complete = all_criteria_names.issubset(employee_submitted_criteria)
            tooltips = {
                "Humility": "How well does the employee demonstrate humility in their interactions?",
                "Integrity": "Does the employee consistently act with integrity and honesty?",
                "Collegiality": "How well does the employee collaborate with colleagues?",
                "Attitude": "What is the employee's general attitude towards work and colleagues?",
                "Time Management": "How effectively does the employee manage their time?",
                "Initiative": "Does the employee take initiative in their work?",
                "Communication": "How well does the employee communicate with others?",
                "Compassion": "Does the employee show compassion towards colleagues and clients?",
                "Knowledge & Awareness": "How knowledgeable is the employee about their field?",
                "Future readiness": "Is the employee prepared for future challenges in their role?",
                "Informal leadership": "Does the employee demonstrate informal leadership qualities?",
                "Team Development": "How well does the employee contribute to team development?",
                "Process adherence": "Does the employee adhere to established processes?",
                "Quality of Work": "How would you rate the overall quality of the employee's work?",
                "Task Completion": "How effectively does the employee complete assigned tasks?",
                "Timeline Adherence": "Does the employee adhere to project timelines?",
                "Collaboration": "How well does the employee collaborate with others?",
                "Innovation": "Does the employee demonstrate innovation in their work?",
                "Special Situation": "How does the employee handle special situations or challenges?"
            }
            # Only show the rating form if the viewer is a manager AND the employee has finished their part
            if role == 'manager' and is_self_evaluation_complete:
                # Fetch employee self-ratings for reference
                cursor.execute("SELECT criteria, score FROM user_ratings WHERE rater = %s AND rating_type = 'self' AND quarter = %s", (employee, selected_quarter))
                employee_self_ratings = dict(cursor.fetchall())

                # ADD THIS NEW BLOCK INSTEAD
                all_scores = {}

                st.write("")
                # --- Development Section ---
                st.markdown("#### Development (70%)")
                for crit, _ in development_criteria:
                    st.write("")
                    tooltip_text = tooltips.get(crit, "")
                    all_scores[crit] = st.number_input(
                        f"{crit} (Your Rating)",
                        min_value=0,
                        max_value=10,
                        value=0,
                        step=1,
                        key=f"input_{crit}",
                        help = tooltip_text
                    )
                st.write("")
  
                # --- Foundational Progress Section ---
                st.markdown("#### Foundational Progress")
                for crit, _ in foundational_criteria:
                    tooltip_text = tooltips.get(crit, "")
                    all_scores[crit] = st.number_input(
                        f"{crit} (Your Rating)",
                        min_value=0,
                        max_value=10,
                        value=0,
                        step=1,
                        key=f"input_{crit}",
                        help=tooltip_text
                    )
                st.write("")
                st.write("")
                # --- Other Aspects Section ---
                st.markdown("#### Other Aspects (30%)")
                for crit, _ in other_aspects_criteria:
                    tooltip_text = tooltips.get(crit, "")
                    all_scores[crit] = st.number_input(
                        f"{crit} (Your Rating)",
                        min_value=0,
                        max_value=10,
                        value=0,
                        step=1,
                        key=f"input_{crit}",
                        help=tooltip_text
                    )
                st.write("")
                st.write("")
                # --- Futuristic Progress Section ---
                st.markdown("#### Futuristic Progress")
                for crit, _ in futuristic_criteria:
                    tooltip_text = tooltips.get(crit, "")
                    all_scores[crit] = st.number_input(
                        f"{crit} (Your Rating)",
                        min_value=0,
                        max_value=10,
                        value=0,
                        step=1,
                        key=f"input_{crit}",
                        help=tooltip_text
                    )

                remark = st.text_area("Add Overall Remark", key=f"remark_{employee}_{selected_quarter}")

                if st.button(f"Submit Rating for Quarter {selected_quarter}", type="primary"):
                    current_year = datetime.datetime.now().year # The year of the evaluation submission

                    # Insert ratings
                    for crit, score in all_scores.items():
                        cursor.execute(
                            "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type, quarter, year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                            (name, employee, role, crit, score, "manager", selected_quarter, current_year)
                        )
                    # Insert remark if provided
                    if remark:
                        cursor.execute(
                            "INSERT INTO remarks (rater, ratee, rating_type, remark, quarter, year) VALUES (%s, %s, %s, %s, %s, %s)",
                            (name, employee, "manager", remark, selected_quarter, current_year)
                        )
                    db.commit()
                    st.success("Rating submitted successfully!")
                    st.rerun()

            # If the employee has NOT completed their self-rating, show an error message
            else:
                st.warning(f"Cannot proceed. {employee} has not submitted their self-evaluation for Quarter {selected_quarter} yet.")

    else:
        st.info("This user does not have a manager assigned.")