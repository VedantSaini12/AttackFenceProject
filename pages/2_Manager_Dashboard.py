import streamlit as st
import mysql.connector as connector
import datetime
import uuid
from notifications import notification_bell_component, add_notification
from core.auth import protect_page, render_logout_button, get_db_connection, get_token_store
from core.constants import (
    foundational_criteria,
    futuristic_criteria,
    development_criteria,
    other_aspects_criteria,
    all_criteria_names
)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Manager Dashboard", page_icon="👔", layout="wide")

protect_page(allowed_roles=["manager"])

# --- DATABASE AND TOKEN STORE (This part is crucial and must be in every file) ---
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

# Define session variables for easy use in the rest of the page
name = st.session_state["name"]
role = st.session_state["role"]
cursor = db.cursor()

# --- END OF THE NEW SECURE AUTHENTICATION GUARD ---
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
# --- PAGINATION LOGIC FOR EMPLOYEE LIST ---
EMPLOYEES_PER_PAGE = 6  # Adjust as needed

if employees:
    total_employees = len(employees)
    total_pages = max((total_employees - 1) // EMPLOYEES_PER_PAGE + 1, 1)

    # Use session state to remember the current page
    if "emp_page" not in st.session_state:
        st.session_state.emp_page = 0

    # Clamp the current page to valid range
    max_page = total_pages - 1
    st.session_state.emp_page = min(max(st.session_state.emp_page, 0), max_page)

    start_idx = st.session_state.emp_page * EMPLOYEES_PER_PAGE
    end_idx = min(start_idx + EMPLOYEES_PER_PAGE, total_employees)
    paginated_employees = employees[start_idx:end_idx]

    st.subheader("Your co-workers:")

    # --- Quarterly System Implementation for Employees ---
    now = datetime.datetime.now()
    quarter = (now.month - 1) // 3 + 1
    quarters = [1, 2, 3, 4]
    selected_emp_quarter = st.selectbox("Select Quarter for Employee Evaluations", quarters, index=quarter - 1, key="manager_emp_quarter")

    for emp in paginated_employees:
        employee_name = emp[0]

        # Check if employee has completed self-evaluation for the selected quarter
        cursor.execute("""
            SELECT criteria FROM user_ratings 
            WHERE rater = %s AND rating_type = 'self' AND quarter = %s
        """, (employee_name, selected_emp_quarter))
        employee_submitted_criteria = {row[0] for row in cursor.fetchall()}
        is_self_evaluation_complete = all_criteria_names.issubset(employee_submitted_criteria)

        with st.expander(f"Evaluate: **{employee_name}** (Quarter {selected_emp_quarter})"):

            if not is_self_evaluation_complete:
                st.markdown(f"""
                <div class="status-card not-ready">
                    <div class="status-icon">⏳</div>
                    <div class="status-text">
                        <b>Pending Self-Evaluation:</b><br>
                        {employee_name} has not submitted their self-evaluation form for Quarter {selected_emp_quarter} yet. The rating form will unlock once they have completed it.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-card ready">
                    <div class="status-icon">✅</div>
                    <div class="status-text">
                        <b>Ready for Manager Review:</b><br>
                        {employee_name} has completed their self-evaluation for Quarter {selected_emp_quarter}. You may now proceed with your rating.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Fetch manager ratings for this employee and quarter
                cursor.execute("""
                    SELECT criteria, score, timestamp FROM user_ratings
                    WHERE rater = %s AND ratee = %s AND rating_type = 'manager' AND quarter = %s
                """, (name, employee_name, selected_emp_quarter))
                manager_ratings = cursor.fetchall()
                manager_submitted_criteria = {crit for crit, _, _ in manager_ratings}

                if all_criteria_names.issubset(manager_submitted_criteria):
                    st.info(f"You have already submitted a rating for {employee_name} (Quarter {selected_emp_quarter}). Here is a summary:")
                    if manager_ratings:
                        # Get the timestamp from the first record
                        submission_date = manager_ratings[0][2]
                        st.write(f"**Submitted on:** {submission_date.strftime('%B %d, %Y')}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<h5>Development (70%)</h5>", unsafe_allow_html=True)
                        for crit, _ in development_criteria:
                            score, timestamp = next((s, t) for c, s, t in manager_ratings if c == crit)
                            st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)
                        st.markdown("<h5>Foundational Progress</h5>", unsafe_allow_html=True)
                        for crit, _ in foundational_criteria:
                            score, timestamp = next((s, t) for c, s, t in manager_ratings if c == crit)
                            st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)
                    with col2:
                        st.markdown("<h5>Other Aspects (30%)</h5>", unsafe_allow_html=True)
                        for crit, _ in other_aspects_criteria:
                            score, timestamp = next((s, t) for c, s, t in manager_ratings if c == crit)
                            st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)
                        st.markdown("<h5>Futuristic Progress</h5>", unsafe_allow_html=True)
                        for crit, _ in futuristic_criteria:
                            score, timestamp = next((s, t) for c, s, t in manager_ratings if c == crit)
                            st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)
                    st.divider()
                    cursor.execute("SELECT remark FROM remarks WHERE rater = %s AND ratee = %s AND rating_type = 'manager' AND quarter = %s;", (name, employee_name, selected_emp_quarter))
                    feedback = cursor.fetchone()
                    st.subheader("Your Remark:")
                    st.success(feedback[0] if feedback else "No remark was provided.")

                else:
                    # Fetch employee self-ratings for the selected quarter
                    cursor.execute("SELECT criteria, score FROM user_ratings WHERE rater = %s AND rating_type = 'self' AND quarter = %s", (employee_name, selected_emp_quarter))
                    employee_self_ratings = dict(cursor.fetchall())

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"<div class='eval-column'><h5 style='text-align: center;'>{employee_name}'s Self-Evaluation</h5>", unsafe_allow_html=True)
                        st.markdown("<h6>Development (70%)</h6>", unsafe_allow_html=True)
                        for crit, weight in development_criteria:
                            st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee_name}_{crit}_dev_{selected_emp_quarter}", disabled=True)
                        st.markdown("<h6>Other Aspects (30%)</h6>", unsafe_allow_html=True)
                        for crit, weight in other_aspects_criteria:
                            st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee_name}_{crit}_other_{selected_emp_quarter}", disabled=True)
                        st.markdown("<h6>Foundational Progress</h6>", unsafe_allow_html=True)
                        for crit, weight in foundational_criteria:
                            st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee_name}_{crit}_found_{selected_emp_quarter}", disabled=True)
                        st.markdown("<h6>Futuristic Progress</h6>", unsafe_allow_html=True)
                        for crit, weight in futuristic_criteria:
                            st.slider(f"{crit} ({weight}%)", 0, 10, employee_self_ratings.get(crit, 0), key=f"self_{employee_name}_{crit}_fut_{selected_emp_quarter}", disabled=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    with col2:
                        st.markdown("<div class='eval-column'><h5 style='text-align: center;'>Your Review</h5>", unsafe_allow_html=True)
                        all_scores = {}
                        st.markdown("<h6>Development (70%)</h6>", unsafe_allow_html=True)
                        for crit, weight in development_criteria:
                            all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee_name}_{crit}_dev_manager_{selected_emp_quarter}")
                        st.markdown("<h6>Other Aspects (30%)</h6>", unsafe_allow_html=True)
                        for crit, weight in other_aspects_criteria:
                            all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee_name}_{crit}_other_manager_{selected_emp_quarter}")
                        st.markdown("<h6>Foundational Progress</h6>", unsafe_allow_html=True)
                        for crit, weight in foundational_criteria:
                            all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee_name}_{crit}_found_manager_{selected_emp_quarter}")
                        st.markdown("<h6>Futuristic Progress</h6>", unsafe_allow_html=True)
                        for crit, weight in futuristic_criteria:
                            all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{employee_name}_{crit}_fut_manager_{selected_emp_quarter}")
                        st.markdown("</div>", unsafe_allow_html=True)

                    remark = st.text_area("Add Overall Remark/Feedback", placeholder="Enter your feedback here...", key=f"remark_{employee_name}_{selected_emp_quarter}")

                    if st.button(f"Submit Final Rating for {employee_name} (Quarter {selected_emp_quarter})", key=f"submit_{employee_name}_manager_{selected_emp_quarter}", type="primary"):
                        # Prevent duplicate submissions for the same quarter
                        cursor.execute(
                            "SELECT criteria FROM user_ratings WHERE rater = %s AND ratee = %s AND rating_type = 'manager' AND quarter = %s",
                            (name, employee_name, selected_emp_quarter)
                        )
                        already_submitted = {row[0] for row in cursor.fetchall()}
                        for crit, score in all_scores.items():
                            if crit not in already_submitted:
                                cursor.execute(
                                    "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type, quarter) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                    (name, employee_name, role, crit, score, "manager", selected_emp_quarter)
                                )
                        if remark:
                            cursor.execute(
                                "INSERT INTO remarks (rater, ratee, rating_type, remark, quarter) VALUES (%s, %s, %s, %s, %s)",
                                (name, employee_name, "manager", remark, selected_emp_quarter)
                            )
                        db.commit()
                        add_notification(
                            recipient=employee_name,
                            sender=name,
                            message=f"Your manager, {name}, has completed your evaluation for Quarter {selected_emp_quarter}.",
                            notification_type='evaluation_completed'
                        )
                        st.success(f"Rating for {employee_name} (Quarter {selected_emp_quarter}) submitted successfully!")
                        st.rerun()

    # --- PAGINATION CONTROLS BELOW THE EMPLOYEE LIST ---
    col_prev, col_page, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅️ Previous", disabled=st.session_state.emp_page == 0, key="emp_prev_btn", use_container_width=True):
            st.session_state.emp_page = max(st.session_state.emp_page - 1, 0)
            st.rerun()
    with col_page:
        st.markdown(
            f"<div style='text-align:center; font-weight:bold;'>Page {st.session_state.emp_page + 1} of {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with col_next:
        if st.button("Next ➡️", disabled=st.session_state.emp_page >= (total_pages - 1), key="emp_next_btn", use_container_width=True):
            st.session_state.emp_page = min(st.session_state.emp_page + 1, total_pages - 1)
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

    # --- Quarterly System Implementation ---
    # Determine the current quarter
    now = datetime.datetime.now()
    quarter = (now.month - 1) // 3 + 1

    # Allow manager to select which quarter's self-evaluation to view/submit
    quarters = [1, 2, 3, 4]
    selected_quarter = st.selectbox("Select Quarter", quarters, index=quarter - 1, key="manager_self_quarter")

    # Fetch self-ratings for the selected quarter
    cursor.execute("""
        SELECT criteria, score, timestamp FROM user_ratings
        WHERE rater = %s AND ratee = %s AND rating_type = 'self' AND quarter = %s
        ORDER BY timestamp DESC
    """, (name, name, selected_quarter))
    self_ratings = cursor.fetchall()

    all_criteria = [crit for crit, _ in development_criteria + other_aspects_criteria + foundational_criteria + futuristic_criteria]
    submitted_criteria = set([crit for crit, _, _ in self_ratings])

    if set(all_criteria).issubset(submitted_criteria):
        st.info(f"You have already submitted your self-rating for Quarter {selected_quarter}. Here is a summary:")

        if self_ratings:
            submission_date = self_ratings[0][2]
            st.write(f"**Submitted on:** {submission_date.strftime('%B %d, %Y')}")

        # Create columns for the summary view
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Development (70%)")
            for crit, _ in development_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)

            st.markdown("### Foundational Progress")
            for crit, _ in foundational_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)

        with col2:
            st.markdown("### Other Aspects (30%)")
            for crit, _ in other_aspects_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)

            st.markdown("### Futuristic Progress")
            for crit, _ in futuristic_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)

        st.write("---")
        # Fetch self remark for the selected quarter
        cursor.execute(
            "SELECT remark FROM remarks WHERE rater = %s AND ratee = %s AND rating_type = 'self' AND quarter = %s;",
            (name, name, selected_quarter)
        )
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
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_dev_self_{selected_quarter}")

        st.markdown("#### Other Aspects (30%)")
        for crit, weight in other_aspects_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_other_self_{selected_quarter}")

        st.markdown("#### Foundational Progress")
        for crit, weight in foundational_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_found_self_{selected_quarter}")

        st.markdown("#### Futuristic Progress")
        for crit, weight in futuristic_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_fut_self_{selected_quarter}")

        @st.dialog("Confirmation")
        def self_submit():
            st.success("Your self-rating has been submitted.")
            if st.button("Close"):
                st.rerun()

        if all_scores and st.button(f"Submit Your Self-Rating for Quarter {selected_quarter}"):
            # Check for already submitted criteria one last time to prevent duplicates
            cursor.execute(
                "SELECT criteria FROM user_ratings WHERE rater = %s AND rating_type = 'self' AND quarter = %s",
                (name, selected_quarter)
            )
            already_submitted = {row[0] for row in cursor.fetchall()}
            # Insert all new scores in a single loop
            for crit, score in all_scores.items():
                if crit not in already_submitted:
                    cursor.execute(
                        "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type, quarter) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (name, name, role, crit, score, "self", selected_quarter)
                    )
            db.commit()
            self_submit()
            st.rerun()

render_logout_button()
