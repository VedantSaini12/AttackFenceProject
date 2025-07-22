import streamlit as st
import mysql.connector as connector
import datetime
import uuid
from core.auth import protect_page, render_logout_button, get_db_connection, get_token_store
from notifications import add_notification
from core.constants import (
    foundational_criteria,
    futuristic_criteria,
    development_criteria,
    other_aspects_criteria,
    all_criteria_names
)

# Page Config
st.set_page_config(page_title="Evaluation Report", layout="wide")

protect_page(allowed_roles=["HR", "admin","manager"])

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
now = datetime.datetime.now()
quarter = (now.month - 1) // 3 + 1
quarters = [1, 2, 3, 4]
selected_emp_quarter = st.selectbox("Select Quarter for Employee Evaluations", quarters, index=quarter - 1, key="manager_emp_quarter")


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
print(user_role, managed_by)


# --- Self Ratings Section (No changes needed here) ---

st.markdown("<h2 style='text-align: center;'>Manager Ratings</h2>", unsafe_allow_html=True)

if user_role == 'employee' and managed_by and managed_by != 'XYZ':
    # Fetch ratings separately
    cursor.execute("""
        SELECT rater, role, criteria, score, timestamp
        FROM user_ratings
        WHERE ratee = %s AND rating_type = 'manager' AND quarter = %s
        ORDER BY timestamp DESC
    """, (employee,selected_emp_quarter))
    manager_ratings = cursor.fetchall()
    print(manager_ratings)
    # Fetch remark separately
    cursor.execute("""
        SELECT remark FROM remarks
        WHERE ratee = %s AND rating_type = 'manager'
        LIMIT 1
    """, (employee,))
    manager_remark_result = cursor.fetchone()
    manager_remark = manager_remark_result[0] if manager_remark_result else None

    if manager_ratings:
        st.success(f"Manager ratings for {employee} (Quarter {selected_emp_quarter}) have already been submitted.")
        rater_name = manager_ratings[0][0]
        submission_date = manager_ratings[0][4]
        st.write(f"**Submitted by:** {rater_name} on {submission_date.strftime('%B %d, %Y')}")

        ratings_by_criteria = {
            crit: (score, timestamp, rater, r_role)
            for rater, r_role, crit, score, timestamp in manager_ratings
        }

        st.markdown("### Development (70%)")
        for crit, _ in development_criteria:
            if crit in ratings_by_criteria:
                score, timestamp, rater, r_role = ratings_by_criteria[crit]
                st.write(f"""
                    <div class='rating-card'>
                        <b>{crit}</b>: <span class='rating-score'>{score}/10</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("### Foundational Progress")
        for crit, _ in foundational_criteria:
            if crit in ratings_by_criteria:
                score, timestamp, rater, r_role = ratings_by_criteria[crit]
                st.write(f"""
                    <div class='rating-card'>
                        <b>{crit}</b>: <span class='rating-score'>{score}/10</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("### Other Aspects (30%)")
        for crit, _ in other_aspects_criteria:
            if crit in ratings_by_criteria:
                score, timestamp, rater, r_role = ratings_by_criteria[crit]
                st.write(f"""
                    <div class='rating-card'>
                        <b>{crit}</b>: <span class='rating-score'>{score}/10</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("### Futuristic Progress")
        for crit, _ in futuristic_criteria:
            if crit in ratings_by_criteria:
                score, timestamp, rater, r_role = ratings_by_criteria[crit]
                st.write(f"""
                    <div class='rating-card'>
                        <b>{crit}</b>: <span class='rating-score'>{score}/10</span>
                    </div>
                """, unsafe_allow_html=True)
        
        # Display the remark after the ratings
        if manager_remark:
            st.divider()
            st.markdown("### Manager's Remark")
            st.markdown(f"<div class='rating-card'>{manager_remark}</div>", unsafe_allow_html=True)

    else:
            st.info(f"No ratings submitted by {managed_by} for {employee} (Quarter {selected_emp_quarter}).")
           # Fetch employee self-ratings for the selected quarter
            cursor.execute("SELECT criteria, score FROM user_ratings WHERE rater = %s AND rating_type = 'self' AND quarter = %s", (employee, quarter))
            employee_self_ratings = dict(cursor.fetchall())

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"<div class='eval-column'><h5 style='text-align: center;'>{employee}'s Self-Evaluation</h5>", unsafe_allow_html=True)
                st.markdown("<h6>Development (70%)</h6>", unsafe_allow_html=True)
                for crit, weight in development_criteria:
                    st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee}_{crit}_dev_{quarter}", disabled=True)
                st.markdown("<h6>Other Aspects (30%)</h6>", unsafe_allow_html=True)
                for crit, weight in other_aspects_criteria:
                    st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee}_{crit}_other_{quarter}", disabled=True)
                st.markdown("<h6>Foundational Progress</h6>", unsafe_allow_html=True)
                for crit, weight in foundational_criteria:
                    st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee}_{crit}_found_{quarter}", disabled=True)
                st.markdown("<h6>Futuristic Progress</h6>", unsafe_allow_html=True)
                for crit, weight in futuristic_criteria:
                    st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee}_{crit}_fut_{quarter}", disabled=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div class='eval-column'><h5 style='text-align: center;'>Your Review</h5>", unsafe_allow_html=True)
                all_scores = {}
                st.markdown("<h6>Development (70%)</h6>", unsafe_allow_html=True)
                for crit, weight in development_criteria:
                    all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee}_{crit}_dev_manager_{quarter}")
                st.markdown("<h6>Other Aspects (30%)</h6>", unsafe_allow_html=True)
                for crit, weight in other_aspects_criteria:
                    all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee}_{crit}_other_manager_{quarter}")
                st.markdown("<h6>Foundational Progress</h6>", unsafe_allow_html=True)
                for crit, weight in foundational_criteria:
                    all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee}_{crit}_found_manager_{quarter}")
                st.markdown("<h6>Futuristic Progress</h6>", unsafe_allow_html=True)
                for crit, weight in futuristic_criteria:
                    all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee}_{crit}_fut_manager_{quarter}")
                st.markdown("</div>", unsafe_allow_html=True)

            remark = st.text_area("Add Overall Remark/Feedback", placeholder="Enter your feedback here...", key=f"remark_{employee}_{quarter}")

            if st.button(f"Submit Final Rating for {employee} (Quarter {quarter})", key=f"submit_{employee}_manager_{quarter}", type="primary"):
                # Prevent duplicate submissions for the same quarter
                cursor.execute(
                    "SELECT criteria FROM user_ratings WHERE rater = %s AND ratee = %s AND rating_type = 'manager' AND quarter = %s",
                    (name, employee, quarter)
                )
                already_submitted = {row[0] for row in cursor.fetchall()}
                for crit, score in all_scores.items():
                    if crit not in already_submitted:
                        cursor.execute(
                            "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type, quarter) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (name, employee, role, crit, score, "manager", quarter)
                        )
                if remark:
                    cursor.execute(
                        "INSERT INTO remarks (rater, ratee, rating_type, remark, quarter) VALUES (%s, %s, %s, %s, %s)",
                        (name, employee, "manager", remark, quarter)
                    )
                db.commit()
                add_notification(
                    recipient=employee,
                    sender=name,
                    message=f"Your manager, {name}, has completed your evaluation for Quarter {quarter}.",
                    notification_type='evaluation_completed'
                )
                st.success(f"Rating for {employee} (Quarter {quarter}) submitted successfully!")
                st.rerun()


    # This handles the case where a remark exists but no ratings were submitted
    if not manager_ratings and manager_remark:
        st.markdown("### Manager's Remark")
        st.markdown(f"<div class='rating-card'>{manager_remark}</div>", unsafe_allow_html=True)

else:
    st.info("This user does not have a manager assigned.")