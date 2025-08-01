# pages/5_Super_Manager_Dashboard.py
import streamlit as st
import mysql.connector as connector
import datetime
from core.auth import protect_page, get_db_connection
from core.constants import all_criteria_names, development_criteria, foundational_criteria, other_aspects_criteria, futuristic_criteria

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Super Manager Dashboard", page_icon="👑", layout="wide")

# --- AUTHENTICATION & DATABASE ---
protect_page(allowed_roles=["super_manager"])
db = get_db_connection()
cursor = db.cursor(dictionary=True)

name = st.session_state.get("name")
email = st.session_state.get("email")

# --- STYLING (No changes needed here) ---
st.markdown("""
<style>
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .manager-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4C8BF5;
        margin-bottom: 1rem;
        border-bottom: 2px solid #4C8BF5;
        padding-bottom: 0.5rem;
    }
    .employee-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FFFFFF;
    }
    .pending-notice {
        text-align: center;
        color: #FFC107; /* Amber */
        font-style: italic;
        padding: 2rem;
    }
    .eval-column-sm {
        padding: 1rem;
        border-radius: 8px;
        background-color: rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER AND SIDEBAR ---
with st.sidebar:
    st.title("👑 Super Manager")
    st.write(f"### Welcome, {name}")
    st.divider()
    if st.button("📜 View History"):
        st.switch_page("pages/History.py")
    st.divider()
    if st.button("Logout", type="primary"):
        st.session_state.clear()
        st.query_params.clear()
        st.switch_page("Home.py")


# --- QUARTER CHECK (MODIFIED FOR Q3 TESTING) ---
now = datetime.datetime.now()
# Original logic is commented out for easy restoration
# current_quarter = (now.month - 1) // 3 + 1
# is_evaluation_period = current_quarter in [2, 4]

# --- Temporary lines for testing ---
current_quarter = 2  # Pretend it's Quarter 2
is_evaluation_period = True # Force the evaluation period to be open

if is_evaluation_period:
    st.success(f"✅ Evaluation is OPEN for Quarter {current_quarter}.")
else:
    st.warning(f"⚠️ Evaluation is only open during Quarter 2 and Quarter 4. You are currently in view-only mode.")

# --- DATA FETCHING ---
# Fetch managers managed by the Super Manager
cursor.execute("SELECT username, email FROM users WHERE managed_by = %s AND role = 'manager'", (name,))
managers = cursor.fetchall()

# ==============================================================================
# --- NEW SECTION: EVALUATE YOUR MANAGERS ---
# ==============================================================================
st.divider()
st.header("Evaluate Your Managers")

if not managers:
    st.info("You do not have any managers assigned to you to evaluate.")
else:
    for manager in managers:
        manager_name = manager['username']
        manager_email = manager['email']

        with st.expander(f"Evaluate Manager: **{manager_name}** for Q{current_quarter}", expanded=False):

            # --- Locking Logic for Manager Evaluation ---
            # 1. Check if the manager has completed their own self-evaluation.
            cursor.execute("SELECT COUNT(DISTINCT criteria) FROM user_ratings WHERE rater = %s AND rating_type = 'self' AND quarter = %s", (manager_email, current_quarter))
            manager_self_eval_count = cursor.fetchone()['COUNT(DISTINCT criteria)']

            # 2. Check if the Super Manager has already evaluated this manager.
            cursor.execute("SELECT COUNT(DISTINCT criteria) FROM user_ratings WHERE rater = %s AND ratee = %s AND rating_type = 'super_manager' AND quarter = %s", (email, manager_email, current_quarter))
            sm_on_manager_eval_count = cursor.fetchone()['COUNT(DISTINCT criteria)']

            # --- Display lock/unlock status ---
            if manager_self_eval_count < len(all_criteria_names):
                st.markdown(f"<div class='pending-notice'>Evaluation is locked until Manager <b>{manager_name}</b> completes their own self-assessment.</div>", unsafe_allow_html=True)
                continue
            elif sm_on_manager_eval_count >= len(all_criteria_names):
                st.success(f"✅ You have already completed the evaluation for Manager {manager_name} for Quarter {current_quarter}.")
                continue

            # --- If unlocked, show the form ---
            # Fetch the manager's self-ratings for reference
            cursor.execute("SELECT criteria, score FROM user_ratings WHERE rater = %s AND rating_type = 'self' AND quarter = %s", (manager_email, current_quarter))
            manager_self_ratings = {row['criteria']: row['score'] for row in cursor.fetchall()}

            with st.form(key=f"form_eval_manager_{manager_email}"):
                st.markdown(f"### Evaluating Manager: {manager_name} for Quarter {current_quarter}")
                st.write("---")

                sm_ratings_for_manager = {}
                all_criteria_list = development_criteria + other_aspects_criteria + foundational_criteria + futuristic_criteria

                for criterion_name, _ in all_criteria_list:
                    col1, col2 = st.columns(2)
                    with col1: # Reference column
                        manager_score = manager_self_ratings.get(criterion_name, 'N/A')
                        st.markdown(f"**{criterion_name}**")
                        st.markdown(f"Manager's Self-Rating: <span style='font-weight:bold; color: #007BFF;'>{manager_score}/10</span>", unsafe_allow_html=True)

                    with col2: # Your input column
                        sm_ratings_for_manager[criterion_name] = st.number_input(
                            f"Your Score for {criterion_name}",
                            min_value=0, max_value=10, value=0, step=1,
                            key=f"sm_rating_for_mgr_{manager_email}_{criterion_name}",
                            label_visibility="collapsed"
                        )
                
                st.divider()
                submit_button = st.form_submit_button(f"Submit Evaluation for Manager {manager_name}", type="primary", disabled=not is_evaluation_period)

                if submit_button:
                    current_year = now.year
                    for criterion, score in sm_ratings_for_manager.items():
                        cursor.execute("""
                            INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type, quarter, year)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (email, manager_email, 'super_manager', criterion, score, 'super_manager', current_quarter, current_year))
                    db.commit()
                    st.success(f"Successfully submitted evaluation for Manager {manager_name}.")
                    st.rerun()

# ==============================================================================
# --- EXISTING SECTION: EVALUATE TEAM MEMBERS ---
# ==============================================================================
st.divider()
st.header("Evaluate Team Members")

if not managers:
    st.info("You do not have any managers assigned, so no employees can be shown.")
else:
    for manager in managers:
        manager_name = manager['username']
        manager_email = manager['email']
        st.markdown(f"<div class='manager-header'>👨‍💼 Manager: {manager_name}</div>", unsafe_allow_html=True)

        # Fetch employees under this manager
        cursor.execute("SELECT username, email FROM users WHERE managed_by = %s AND role = 'employee' AND is_dormant = FALSE", (manager_name,))
        employees = cursor.fetchall()

        if not employees:
            st.write(f"No active employees under {manager_name}.")
            continue

        for employee in employees:
            emp_name = employee['username']
            emp_email = employee['email']

            with st.expander(f"Evaluate Employee: **{emp_name}** for Q{current_quarter} (Under {manager_name})", expanded=False):

                # --- ROBUST EVALUATION LOCKING LOGIC ---
                # 1. Check if the employee has completed their self-evaluation.
                cursor.execute("SELECT COUNT(DISTINCT criteria) FROM user_ratings WHERE rater = %s AND rating_type = 'self' AND quarter = %s", (emp_email, current_quarter))
                employee_eval_count = cursor.fetchone()['COUNT(DISTINCT criteria)']
                # 2. Check if the manager has evaluated the employee.
                cursor.execute("SELECT COUNT(DISTINCT criteria) FROM user_ratings WHERE rater = %s AND ratee = %s AND rating_type = 'manager' AND quarter = %s", (manager_email, emp_email, current_quarter))
                manager_eval_count = cursor.fetchone()['COUNT(DISTINCT criteria)']
                # 3. Check if the Super Manager has already submitted their own evaluation.
                cursor.execute("SELECT COUNT(DISTINCT criteria) FROM user_ratings WHERE rater = %s AND ratee = %s AND rating_type = 'super_manager' AND quarter = %s", (email, emp_email, current_quarter))
                super_manager_eval_count = cursor.fetchone()['COUNT(DISTINCT criteria)']

                # --- Display status and lock/unlock the form accordingly ---
                if employee_eval_count < len(all_criteria_names):
                    st.markdown(f"<div class='pending-notice'>Evaluation is locked until <b>{emp_name}</b> completes their self-assessment.</div>", unsafe_allow_html=True)
                    continue
                elif manager_eval_count < len(all_criteria_names):
                    st.markdown(f"<div class='pending-notice'>Evaluation is locked until Manager <b>{manager_name}</b> completes their assessment for {emp_name}.</div>", unsafe_allow_html=True)
                    continue
                elif super_manager_eval_count >= len(all_criteria_names):
                    st.success(f"✅ You have already completed the evaluation for {emp_name} for Quarter {current_quarter}.")
                    continue

                # Fetch all ratings (self, manager, super_manager) for the view
                cursor.execute("SELECT id, rater, criteria, score, rating_type FROM user_ratings WHERE ratee = %s AND quarter = %s", (emp_email, current_quarter))
                all_ratings_data = cursor.fetchall()

                # Fetch all comments for these ratings
                rating_ids = [r['id'] for r in all_ratings_data if r['id']]
                comments = {}
                if rating_ids:
                    format_strings = ','.join(['%s'] * len(rating_ids))
                    cursor.execute(f"SELECT rating_id, comment_text FROM evaluation_comments WHERE rating_id IN ({format_strings}) AND commenter_email = %s", (*rating_ids, email))
                    comment_data = cursor.fetchall()
                    comments = {c['rating_id']: c['comment_text'] for c in comment_data}

                # Prepare data for easy access
                ratings = {
                    'self': {r['criteria']: {'score': r['score'], 'id': r['id']} for r in all_ratings_data if r['rating_type'] == 'self'},
                    'manager': {r['criteria']: {'score': r['score'], 'id': r['id']} for r in all_ratings_data if r['rating_type'] == 'manager'},
                    'super_manager': {r['criteria']: {'score': r['score'], 'id': r['id']} for r in all_ratings_data if r['rating_type'] == 'super_manager'}
                }

                # --- START THE FORM FOR THIS EMPLOYEE ---
                with st.form(key=f"form_eval_employee_{emp_email}"):
                    st.markdown(f"### Evaluating: {emp_name} for Quarter {current_quarter}")
                    st.write("---")

                    sm_ratings = {}
                    sm_comments = {}

                    # Loop through each criteria category
                    for category_name, criteria_list in {"Development (70%)": development_criteria, "Other Aspects (30%)": other_aspects_criteria, "Foundational Progress": foundational_criteria, "Futuristic Progress": futuristic_criteria}.items():
                        st.subheader(category_name)
                        for criterion_name, _ in criteria_list:
                            st.markdown(f"**{criterion_name}**")
                            col1, col2, col3 = st.columns(3)
                            # Column 1: Employee Self-Eval
                            with col1:
                                st.markdown("<div class='eval-column-sm'>", unsafe_allow_html=True)
                                st.write("**Employee Self-Eval**")
                                self_rating = ratings['self'].get(criterion_name, {'score': 'N/A', 'id': None})
                                st.metric("Score", value=self_rating['score'])
                                if self_rating['id']:
                                    existing_comment = comments.get(self_rating['id'], "")
                                    sm_comments[self_rating['id']] = st.text_area("Your Comment on Self-Rating", value=existing_comment, key=f"sm_comment_self_{emp_email}_{criterion_name}", height=100)
                                st.markdown("</div>", unsafe_allow_html=True)
                            # Column 2: Manager Eval
                            with col2:
                                st.markdown("<div class='eval-column-sm'>", unsafe_allow_html=True)
                                st.write(f"**Manager ({manager_name}) Eval**")
                                mgr_rating = ratings['manager'].get(criterion_name, {'score': 'N/A', 'id': None})
                                st.metric("Score", value=mgr_rating['score'])
                                if mgr_rating['id']:
                                    existing_comment = comments.get(mgr_rating['id'], "")
                                    sm_comments[mgr_rating['id']] = st.text_area("Your Comment on Manager Rating", value=existing_comment, key=f"sm_comment_mgr_{emp_email}_{criterion_name}", height=100)
                                st.markdown("</div>", unsafe_allow_html=True)
                            # Column 3: Super Manager Eval
                            with col3:
                                st.markdown("<div class='eval-column-sm'>", unsafe_allow_html=True)
                                st.write("**Your Evaluation**")
                                existing_rating = ratings['super_manager'].get(criterion_name, {'score': 0})['score']
                                sm_ratings[criterion_name] = st.number_input("Your Score", min_value=0, max_value=10, value=existing_rating, key=f"sm_rating_{emp_email}_{criterion_name}", label_visibility="collapsed")
                                st.markdown("</div>", unsafe_allow_html=True)
                            st.write("---")
                    
                    # Submit button, disabled if not the evaluation period
                    submit_button = st.form_submit_button(f"Submit Evaluation for {emp_name} (Q{current_quarter})", disabled=not is_evaluation_period, type="primary")

                    if submit_button:
                        current_year = now.year
                        for criterion, score in sm_ratings.items():
                            cursor.execute("""
                                INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type, quarter, year)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE score = VALUES(score)
                            """, (email, emp_email, 'super_manager', criterion, score, 'super_manager', current_quarter, current_year))
                        
                        for rating_id, comment_text in sm_comments.items():
                            if comment_text: # Only save if there's text
                                cursor.execute("""
                                    INSERT INTO evaluation_comments (rating_id, commenter_email, comment_text)
                                    VALUES (%s, %s, %s)
                                    ON DUPLICATE KEY UPDATE comment_text = VALUES(comment_text)
                                """, (rating_id, email, comment_text))
                        
                        db.commit()
                        st.success(f"Successfully submitted evaluation for {emp_name}.")
                        st.rerun()