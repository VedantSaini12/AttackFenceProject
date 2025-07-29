import streamlit as st
import datetime
from collections import defaultdict
from core.auth import protect_page, get_db_connection
from core.constants import (
    foundational_criteria,
    futuristic_criteria,
    development_criteria,
    other_aspects_criteria
)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Evaluation History", page_icon="📜", layout="wide")

# --- AUTHENTICATION & DATABASE ---
protect_page(allowed_roles=["admin", "manager", "HR", "employee"])
db = get_db_connection()
cursor = db.cursor(dictionary=True) # Use dictionary cursor for easier data handling
name = st.session_state.get("name")
email = st.session_state.get("email")
role = st.session_state.get("role")

# --- STYLING ---
st.markdown("""
<style>
    .history-card {
        background-color: #f8f9fa;
        border-left: 5px solid #1f4e79;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .history-card h5 {
        margin-bottom: 0.5rem;
        color: #1f4e79;
    }
    .history-card .meta-info {
        font-size: 0.85rem;
        color: #6c757d;
        margin-bottom: 1rem;
    }
    .no-data {
        text-align: center;
        color: #6c757d;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTION TO RENDER RATINGS ---
def render_evaluation_details(cursor, ratings, remark_data, criteria_list):
    """Renders the scores for a given set of criteria."""
    if not ratings and not remark_data:
        st.info("No submission found for this period.")
        return

    # Use remark_data for submission info if available, otherwise use ratings
    submission_info_source = remark_data if remark_data else (ratings[0] if ratings else None)
    if submission_info_source:
        rater_email = submission_info_source.get('rater')
        rater_name = 'N/A' # Default name

        # If we have the rater's email, look up their username
        if rater_email:
            cursor.execute("SELECT username FROM users WHERE email = %s", (rater_email,))
            rater_result = cursor.fetchone()
            if rater_result:
                rater_name = rater_result['username']

        submitted_on_ts = submission_info_source.get('created_at') or submission_info_source.get('timestamp')
        if submitted_on_ts:
            submitted_on = submitted_on_ts.strftime('%B %d, %Y')
            # Display the fetched username
            st.markdown(f"<div class='meta-info'>Submitted by: <strong>{rater_name}</strong> on {submitted_on}</div>", unsafe_allow_html=True)

    ratings_dict = {r['criteria']: r['score'] for r in ratings}

    for category_name, criteria in criteria_list.items():
        st.markdown(f"<h6>{category_name}</h6>", unsafe_allow_html=True)
        for crit_info in criteria:
            crit_name = crit_info[0]
            score = ratings_dict.get(crit_name)
            if score is not None:
                st.markdown(f"<span><strong>{crit_name}:</strong> {score}/10</span>", unsafe_allow_html=True)
        st.write("")

    if remark_data and remark_data.get('remark'):
        st.markdown("---")
        st.markdown("<h6>Overall Remark</h6>", unsafe_allow_html=True)
        st.markdown(f"> {remark_data['remark']}")


# --- BACK BUTTON ---
if st.button("⬅️ Back to Dashboard"):
    # Reset the session state for the specific role to its default view
    if role == 'admin':
        st.session_state.admin_page = "User Management" # Reset to default
        st.switch_page("pages/4_Admin_Panel.py")
    elif role == 'manager':
        st.session_state.mgr_section = "Evaluate Team" # Reset to default
        st.switch_page("pages/2_Manager_Dashboard.py")
    elif role == 'HR':
        st.session_state.hr_section = "Add Employee" # Reset to default
        st.switch_page("pages/3_HR_Dashboard.py")
    elif role == 'employee':
        st.session_state.emp_section = "Dashboard" # Reset to default
        st.switch_page("pages/1_Employee_Dashboard.py")
    else:
        st.switch_page("Home.py")

st.title("📜 Evaluation History")

# --- USER SELECTION LOGIC ---
selected_user_email = None
selected_user_name = None

if role in ['admin', 'HR']:
    st.subheader("Select a User to View History")
    # Fetch username, email, and dormant status
    cursor.execute("SELECT username, email, is_dormant FROM users WHERE role != 'admin' ORDER BY username")
    all_users_data = cursor.fetchall()

    # Create a dictionary to map the display name to the email: {display_name: email}
    user_options = {}
    for row in all_users_data:
        display_name = row['username']
        if row['is_dormant']:
            display_name += " (Account Dormant)"
        user_options[display_name] = row['email']

    # Let the user select from the display names
    selected_display_name = st.selectbox(
        "Search for an employee or manager",
        options=user_options.keys(), # Show names
        index=None,
        placeholder="Type to search..."
    )

    if selected_display_name:
        # Get the email corresponding to the selected name
        selected_user_email = user_options[selected_display_name]
        # Get the clean username for display purposes
        selected_user_name = selected_display_name.replace(" (Account Dormant)", "")

elif role == 'manager':
    st.subheader("Select whose history you want to view")
    history_choice = st.radio("Choose an option:", ["My History", "My Team's History"], horizontal=True, key="manager_history_choice")
    
    if history_choice == "My History":
        selected_user_email = st.session_state.get("email")
        selected_user_name = name
    else:
        # Fetch both username and email for the manager's team
        cursor.execute("SELECT username, email FROM users WHERE managed_by = %s AND is_dormant = FALSE ORDER BY username", (name,))
        team_members_data = cursor.fetchall()
        
        if team_members_data:
            # Create a dictionary for the selectbox: {username: email}
            team_options = {row['username']: row['email'] for row in team_members_data}
            
            selected_display_name = st.selectbox(
                "Select a team member",
                options=team_options.keys(), # Show names
                index=None,
                placeholder="Select an employee..."
            )

            if selected_display_name:
                selected_user_email = team_options[selected_display_name]
                selected_user_name = selected_display_name
        else:
            st.info("You do not currently manage any active employees.")

elif role == 'employee':
    selected_user_email = st.session_state.get("email")
    selected_user_name = name

# --- MAIN DISPLAY ---
if selected_user_email:
    st.divider()
    st.header(f"Displaying History For: {selected_user_name}")

    # CORRECTED QUERY: Fetch all evaluation periods from BOTH tables using the 'year' column
    cursor.execute("""
        (SELECT DISTINCT year, quarter FROM user_ratings WHERE ratee = %(email)s AND year IS NOT NULL)
        UNION
        (SELECT DISTINCT year, quarter FROM remarks WHERE ratee = %(email)s AND year IS NOT NULL)
        ORDER BY year DESC, quarter DESC
    """, {'email': selected_user_email})
    periods = cursor.fetchall()


    if not periods:
        st.markdown("<div class='no-data'><h3>No evaluation history found.</h3></div>", unsafe_allow_html=True)
    else:
        evaluations_by_year = defaultdict(list)
        for p in periods:
            evaluations_by_year[p['year']].append(p['quarter'])

        all_criteria_groups = {
            "Development (70%)": development_criteria,
            "Other Aspects (30%)": other_aspects_criteria,
            "Foundational Progress": foundational_criteria,
            "Futuristic Progress": futuristic_criteria
        }

        for year, quarters in evaluations_by_year.items():
            with st.expander(f"🗓️ Evaluations from {year}", expanded=(year == datetime.datetime.now().year)):
                for quarter in quarters:
                    st.markdown(f"<h4>Quarter {quarter}</h4>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)

                    # --- Self-Evaluation Column ---
                    with col1:
                        with st.container(border=True):
                            st.markdown("<h5>👤 Self-Evaluation</h5>", unsafe_allow_html=True)
                            # CORRECTED QUERY: Filter by year and quarter
                            cursor.execute("SELECT rater, criteria, score, timestamp FROM user_ratings WHERE ratee = %s AND rating_type = 'self' AND year = %s AND quarter = %s", (selected_user_email, year, quarter))
                            self_ratings = cursor.fetchall()
                            # CORRECTED QUERY: Filter by year/quarter and use 'created_at'
                            cursor.execute("SELECT rater, remark, created_at FROM remarks WHERE ratee = %s AND rating_type = 'self' AND year = %s AND quarter = %s LIMIT 1", (selected_user_email, year, quarter))
                            self_remark = cursor.fetchone()
                            render_evaluation_details(cursor, self_ratings, self_remark, all_criteria_groups)


                    # --- Manager Evaluation Column ---
                    with col2:
                        with st.container(border=True):
                            st.markdown("<h5>👔 Manager's Evaluation</h5>", unsafe_allow_html=True)
                            # CORRECTED QUERY: Filter by year and quarter
                            cursor.execute("SELECT rater, criteria, score, timestamp FROM user_ratings WHERE ratee = %s AND rating_type = 'manager' AND year = %s AND quarter = %s", (selected_user_email, year, quarter))
                            mgr_ratings = cursor.fetchall()
                            # CORRECTED QUERY: Filter by year/quarter and use 'created_at'
                            cursor.execute("SELECT rater, remark, created_at FROM remarks WHERE ratee = %s AND rating_type = 'manager' AND year = %s AND quarter = %s LIMIT 1", (selected_user_email, year, quarter))
                            mgr_remark = cursor.fetchone()
                            render_evaluation_details(cursor, mgr_ratings, mgr_remark, all_criteria_groups)

                    st.divider()
else:
    if role in ['admin', 'HR', 'manager']:
        st.info("Please make a search above to proceed.")