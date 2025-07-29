# pages/History.py

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
protect_page(allowed_roles=["admin", "manager", "hr", "employee", "super_manager"])
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
    /* NEW STYLES FOR 3-COLUMN LAYOUT */
    .eval-column {
        padding: 1rem;
        border-radius: 8px;
        background-color: rgba(240, 242, 246, 0.5);
        height: 100%;
    }
    .eval-column h6 {
        font-weight: bold;
        color: #333;
        border-bottom: 2px solid #ddd;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .comment-box {
        background-color: #e9ecef;
        border-left: 3px solid #007bff;
        padding: 0.5rem 0.75rem;
        margin-top: 0.5rem;
        font-size: 0.85rem;
        font-style: italic;
        color: #495057;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTION TO RENDER 2-COLUMN RATINGS (Q1 & Q3) ---
def render_two_column_history(cursor, ratings, remark_data, criteria_list):
    """Renders the scores for a given set of criteria in the old 2-column format."""
    if not ratings and not remark_data:
        st.info("No submission found for this period.")
        return

    submission_info_source = remark_data if remark_data else (ratings[0] if ratings else None)
    if submission_info_source:
        rater_email = submission_info_source.get('rater')
        rater_name = 'N/A'
        if rater_email:
            cursor.execute("SELECT username FROM users WHERE email = %s", (rater_email,))
            rater_result = cursor.fetchone()
            if rater_result:
                rater_name = rater_result['username']

        submitted_on_ts = submission_info_source.get('created_at') or submission_info_source.get('timestamp')
        if submitted_on_ts:
            submitted_on = submitted_on_ts.strftime('%B %d, %Y')
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

# --- NEW HELPER FUNCTION TO RENDER 3-COLUMN RATINGS (Q2 & Q4) ---
def render_three_column_history(ratings_data, comments_data, criteria_list):
    """Renders the 3-column evaluation view for Q2 and Q4."""
    
    self_ratings = ratings_data.get('self', {})
    manager_ratings = ratings_data.get('manager', {})
    super_manager_ratings = ratings_data.get('super_manager', {})

    for category_name, criteria in criteria_list.items():
        st.subheader(category_name)
        for crit_info in criteria:
            crit_name = crit_info[0]
            
            self_rating_id = self_ratings.get(crit_name, {}).get('id')
            manager_rating_id = manager_ratings.get(crit_name, {}).get('id')

            col1, col2, col3 = st.columns(3)
            
            with col1:
                with st.container(border=True, height=155):
                    st.markdown("<h6>👤 Self-Evaluation</h6>", unsafe_allow_html=True)
                    score = self_ratings.get(crit_name, {}).get('score', 'N/A')
                    st.markdown(f"**{crit_name}:** {score}/10")
                    
                    if self_rating_id in comments_data:
                        st.markdown(f"<div class='comment-box'><b>Super Manager's Comment:</b> {comments_data[self_rating_id]}</div>", unsafe_allow_html=True)

            with col2:
                with st.container(border=True, height=155):
                    st.markdown("<h6>👔 Manager's Evaluation</h6>", unsafe_allow_html=True)
                    score = manager_ratings.get(crit_name, {}).get('score', 'N/A')
                    st.markdown(f"**{crit_name}:** {score}/10")
                    
                    if manager_rating_id in comments_data:
                        st.markdown(f"<div class='comment-box'><b>Super Manager's Comment:</b> {comments_data[manager_rating_id]}</div>", unsafe_allow_html=True)

            with col3:
                with st.container(border=True, height=155):
                    st.markdown("<h6>Super Manager's Evaluation</h6>", unsafe_allow_html=True)
                    score = super_manager_ratings.get(crit_name, {}).get('score', 'N/A')
                    st.markdown(f"**{crit_name}:** {score}/10")

        st.divider()

def render_manager_q2_q4_history(ratings_data, comments_data, criteria_list):
    """Renders a 2-column evaluation view for Managers (Self vs Super Manager) for Q2 & Q4."""
    self_ratings, super_manager_ratings = ratings_data.get('self', {}), ratings_data.get('super_manager', {})
    for category_name, criteria in criteria_list.items():
        st.subheader(category_name)
        for crit_info in criteria:
            crit_name = crit_info[0]
            self_rating_id = self_ratings.get(crit_name, {}).get('id')
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True, height=100):
                    st.markdown("<h6>👤 Self-Evaluation</h6>", unsafe_allow_html=True)
                    score = self_ratings.get(crit_name, {}).get('score', 'N/A')
                    st.markdown(f"**{crit_name}:** {score}/10")
                    if self_rating_id in comments_data: 
                        st.markdown(f"<div class='comment-box'><b>Super Manager's Comment:</b> {comments_data[self_rating_id]}</div>", unsafe_allow_html=True)
            with col2:
                with st.container(border=True, height=100):
                    st.markdown("<h6>Super Manager's Evaluation</h6>", unsafe_allow_html=True)
                    score = super_manager_ratings.get(crit_name, {}).get('score', 'N/A')
                    st.markdown(f"**{crit_name}:** {score}/10")
        st.divider()

# --- BACK BUTTON ---
if st.button("⬅️ Back to Dashboard"):
    if role == 'admin':
        st.session_state.admin_page = "User Management"
        st.switch_page("pages/4_Admin_Panel.py")
    elif role == 'manager':
        st.session_state.mgr_section = "Evaluate Team"
        st.switch_page("pages/2_Manager_Dashboard.py")
    elif role == 'hr':
        st.session_state.hr_section = "Add Employee"
        st.switch_page("pages/3_HR_Dashboard.py")
    elif role == 'employee':
        st.session_state.emp_section = "Dashboard"
        st.switch_page("pages/1_Employee_Dashboard.py")
    elif role == 'super_manager':
        st.switch_page("pages/5_Super_Manager_Dashboard.py")
    else:
        st.switch_page("Home.py")

st.title("📜 Evaluation History")

# --- USER SELECTION LOGIC ---
selected_user_email = None
selected_user_name = None

if role in ['admin', 'hr']:
    st.subheader("Select a User to View History")
    cursor.execute("SELECT username, email, is_dormant FROM users WHERE role != 'admin' ORDER BY username")
    all_users_data = cursor.fetchall()
    user_options = {f"{row['username']} ({'Dormant' if row['is_dormant'] else row['email']})": row['email'] for row in all_users_data}
    selected_display_name = st.selectbox("Search for an employee or manager", options=user_options.keys(), index=None, placeholder="Type to search...")
    if selected_display_name:
        selected_user_email = user_options[selected_display_name]
        selected_user_name = selected_display_name.split(" (")[0]
elif role == 'super_manager':
    st.subheader("Select a User to View History")
    cursor.execute("""
        (SELECT username, email, is_dormant FROM users WHERE managed_by = %s)
        UNION
        (SELECT u.username, u.email, u.is_dormant FROM users u JOIN users m ON u.managed_by = m.username WHERE m.managed_by = %s)
    """, (name, name))
    all_users_data = cursor.fetchall()
    user_options = {f"{row['username']} ({'Dormant' if row['is_dormant'] else row['email']})": row['email'] for row in all_users_data}
    selected_display_name = st.selectbox("Search for an employee or manager in your hierarchy", options=user_options.keys(), index=None, placeholder="Type to search...")
    if selected_display_name:
        selected_user_email = user_options[selected_display_name]
        selected_user_name = selected_display_name.split(" (")[0]
elif role == 'manager':
    st.subheader("Select whose history you want to view")
    history_choice = st.radio("Choose an option:", ["My History", "My Team's History"], horizontal=True, key="manager_history_choice")
    if history_choice == "My History":
        selected_user_email = st.session_state.get("email")
        selected_user_name = name
    else:
        cursor.execute("SELECT username, email FROM users WHERE managed_by = %s AND is_dormant = FALSE ORDER BY username", (name,))
        team_members_data = cursor.fetchall()
        if team_members_data:
            team_options = {row['username']: row['email'] for row in team_members_data}
            selected_display_name = st.selectbox("Select a team member", options=team_options.keys(), index=None, placeholder="Select an employee...")
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
    
    # --- NEW: Get the role of the person being viewed ---
    cursor.execute("SELECT role FROM users WHERE email = %s", (selected_user_email,))
    selected_user_role_result = cursor.fetchone()
    selected_user_role = selected_user_role_result['role'] if selected_user_role_result else None

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
        for p in periods: evaluations_by_year[p['year']].append(p['quarter'])
        all_criteria_groups = {"Development (70%)": development_criteria, "Other Aspects (30%)": other_aspects_criteria, "Foundational Progress": foundational_criteria, "Futuristic Progress": futuristic_criteria}

        for year, quarters in evaluations_by_year.items():
            with st.expander(f"🗓️ Evaluations from {year}", expanded=(year == datetime.datetime.now().year)):
                for quarter in quarters:
                    st.markdown(f"<h4>Quarter {quarter}</h4>", unsafe_allow_html=True)
                    
                    if quarter in [2, 4]:
                        # Fetch all ratings and comments for the period
                        cursor.execute("SELECT id, rater, criteria, score, rating_type FROM user_ratings WHERE ratee = %s AND year = %s AND quarter = %s", (selected_user_email, year, quarter))
                        all_ratings = cursor.fetchall()
                        rating_ids = [r['id'] for r in all_ratings if r['id']]
                        comments_data = {}
                        if rating_ids:
                            format_strings = ','.join(['%s'] * len(rating_ids))
                            cursor.execute(f"SELECT rating_id, comment_text FROM evaluation_comments WHERE rating_id IN ({format_strings})", tuple(rating_ids))
                            comments_data = {c['rating_id']: c['comment_text'] for c in cursor.fetchall()}
                        
                        ratings_data = {
                            'self': {r['criteria']: {'score': r['score'], 'id': r['id']} for r in all_ratings if r['rating_type'] == 'self'},
                            'manager': {r['criteria']: {'score': r['score'], 'id': r['id']} for r in all_ratings if r['rating_type'] == 'manager'},
                            'super_manager': {r['criteria']: {'score': r['score'], 'id': r['id']} for r in all_ratings if r['rating_type'] == 'super_manager'}
                        }

                        # --- Render based on the user's role ---
                        if selected_user_role == 'manager':
                            render_manager_q2_q4_history(ratings_data, comments_data, all_criteria_groups)
                        else: # Default to employee view, which uses the 3-column layout
                            render_three_column_history(ratings_data, comments_data, all_criteria_groups)

                    else: # For Q1 and Q3, use the original 2-column view
                        col1, col2 = st.columns(2)
                        with col1:
                            with st.container(border=True):
                                st.markdown("<h5>👤 Self-Evaluation</h5>", unsafe_allow_html=True)
                                cursor.execute("SELECT rater, criteria, score, timestamp FROM user_ratings WHERE ratee = %s AND rating_type = 'self' AND year = %s AND quarter = %s", (selected_user_email, year, quarter))
                                self_ratings = cursor.fetchall()
                                cursor.execute("SELECT rater, remark, created_at FROM remarks WHERE ratee = %s AND rating_type = 'self' AND year = %s AND quarter = %s LIMIT 1", (selected_user_email, year, quarter))
                                self_remark = cursor.fetchone()
                                render_two_column_history(cursor, self_ratings, self_remark, all_criteria_groups)
                        with col2:
                            with st.container(border=True):
                                st.markdown("<h5>👔 Manager's Evaluation</h5>", unsafe_allow_html=True)
                                cursor.execute("SELECT rater, criteria, score, timestamp FROM user_ratings WHERE ratee = %s AND rating_type = 'manager' AND year = %s AND quarter = %s", (selected_user_email, year, quarter))
                                mgr_ratings = cursor.fetchall()
                                cursor.execute("SELECT rater, remark, created_at FROM remarks WHERE ratee = %s AND rating_type = 'manager' AND year = %s AND quarter = %s LIMIT 1", (selected_user_email, year, quarter))
                                mgr_remark = cursor.fetchone()
                                render_two_column_history(cursor, mgr_ratings, mgr_remark, all_criteria_groups)
                    st.divider()
else:
    if role in ['admin', 'hr', 'manager', 'super_manager']:
        st.info("Please make a search above to proceed.")