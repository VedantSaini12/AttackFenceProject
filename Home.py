import streamlit as st
import bcrypt
import mysql.connector as connector
import base64
from pathlib import Path
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Self-Evaluation Portal",
    page_icon="🔐",
    layout="wide"
)
signer = TimestampSigner("password123")
# --- HELPER FUNCTION TO ENCODE IMAGES ---
# This makes your app more portable by embedding the images directly in the code.
def image_to_base64(path_to_image):
    """Converts an image file to a base64 string."""
    try:
        with open(path_to_image, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        # Return a placeholder or None if the file is not found
        return None

# --- DATABASE CONNECTION (Your existing logic) ---
# It's good practice to wrap this in a function to handle potential errors
@st.cache_resource
def get_db_connection():
    try:
        db = connector.connect(
            host="localhost",
            user="root",
            password="sqladi@2710",
            database="auth"
        )
        return db
    except connector.Error as err:
        st.error(f"Error connecting to database: {err}")
        return None

db = get_db_connection()
if db:
    cursor = db.cursor()
else:
    st.stop()

# --- AUTO-LOGIN LOGIC (Corrected and Improved) ---
if not st.session_state.get("name"):
    token = st.experimental_get_query_params().get("auth_token", [None])[0] or st.experimental_get_cookie("auth_token")
    if token:
        try:
            decoded_email = signer.unsign(token, max_age=300).decode()
            cursor.execute("SELECT * FROM users WHERE Email = %s", (decoded_email,))
            user = cursor.fetchone()
            if user:
                username = user[5]
                user_role = user[3]
                st.session_state["name"] = username
                st.session_state["role"] = user_role
                if user_role == 'employee':
                    st.switch_page("pages/1_Employee_Dashboard.py")
                elif user_role == 'manager':
                    st.switch_page("pages/2_Manager_Dashboard.py")
                elif user_role == 'HR':
                    st.switch_page("pages/3_HR_Dashboard.py")
                elif user_role == 'admin':
                    st.switch_page("pages/4_Admin_Panel.py")
        except SignatureExpired:
            st.warning("Session expired. Please log in again.")
        except BadSignature:
            st.error("Invalid session. Please log in again.")

# --- LOAD ASSETS ---
# Paths to your logo parts
attack_logo_path = Path(__file__).parent / "atk.png"
fence_logo_path = Path(__file__).parent / "fnc.png"

# Encode images to Base64
attack_logo_b64 = image_to_base64(attack_logo_path)
fence_logo_b64 = image_to_base64(fence_logo_path)


# --- CSS STYLES ---
# This block combines ALL the CSS from your LogoIntro.module.css and LoginForm.module.css
# It also includes styles to mimic the layout and override default Streamlit styles.
def load_css():
    st.markdown(f"""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-LN+7fdVzj6u52u30Kp6M/trliBMCMKTyK833zpbD+pXdCLuTusPj697FH4R/5mcr" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js" integrity="sha384-ndDqU0Gzau9qJ1lfW4pNLlhNTkCfHzAVBReH9diLvGRem5+R9g2FzA8ZGN954O5Q" crossorigin="anonymous"></script>
    <style>
        /* --- Font Import --- */
        @import url('https://fonts.cdnfonts.com/css/sansation');

        /* --- Page Background & General Layout --- */
        /* This targets the main block of the Streamlit app */
        [data-testid="stAppViewContainer"] > .main {{
            background-image: radial-gradient(circle at 25% 60%, #1a2a45, #101828 45%);
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Hide Streamlit's default header and footer */
        header, footer {{
            visibility: hidden;
        }}
        
        /* Remove padding from the main block to allow full-width content */
        .block-container {{
            padding: 2rem 5rem !important;
        }}

        /* --- Logo & Tagline Styles (from LogoIntro.module.css) --- */
        .logo-intro-container {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
            height: 90vh; /* Make it take most of the viewport height */
        }}

        .logo-images {{
            display: flex;
            align-items: center;
            margin-bottom: 0px;
            margin-left: 200px;
        }}

        .logo-attack {{
            opacity: 0;
            animation: fadeInFromLeft 0.7s ease-out forwards;
        }}

        .logo-fence {{
            opacity: 0;
            animation: fadeInFromRight 0.7s ease-out forwards;
        }}

        .tagline {{
            opacity: 0;
            animation: fadeIn 0.3s ease-in forwards;
            animation-delay: 0.8s;
            font-family: 'Sansation', sans-serif;
            font-weight: bold;
            font-size: 35px;
            color: #FFFFFF;
            letter-spacing: 0.05em;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.2);
            line-height: 1.2;
            text-align: left;
            position: relative;
            left: 110px;
        }}

        @keyframes fadeInFromLeft {{
            from {{ opacity: 0; transform: translateX(60px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        @keyframes fadeInFromRight {{
            from {{ opacity: 0; transform: translateX(-60px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    """, unsafe_allow_html=True)

load_css()

# --- PAGE LAYOUT (2 Columns) ---
col1, col2 = st.columns([0.6, 0.4], gap="large")

# --- LEFT COLUMN: Logo and Tagline ---
with col1:
    # Use st.markdown to inject our custom animated HTML
    if attack_logo_b64 and fence_logo_b64:
        st.markdown(f"""
        <div class="logo-intro-container">
            <div class="logo-images">
                <img src="data:image/png;base64,{attack_logo_b64}" alt="Attack" class="logo-attack" width="200" />
                <img src="data:image/png;base64,{fence_logo_b64}" alt="Fence" class="logo-fence" width="170" />
            </div>
            <h1 class="tagline">
                SELF-EVALUATION PORTAL
            </h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback if images aren't found
        st.markdown('<div class="logo-intro-container"><h1 class="tagline">SELF-EVALUATION PORTAL</h1></div>', unsafe_allow_html=True)
        st.warning("Logo images not found. Please ensure atk.png and fnc.png are in the correct directory.")


# --- RIGHT COLUMN: Login Form ---
with col2:
    # We create a container div and place the form inside
    st.markdown('<div style="display: flex; align-items: center; height: 20vh;">', unsafe_allow_html=True)
    st.markdown('<div class="login-form-container">', unsafe_allow_html=True)

    # Use a form to group inputs and the button
    with st.form(key="login_form"):
        st.markdown('<h2 class="title">Login</h2>', unsafe_allow_html=True)
        
        
        email = st.text_input(
            "Email", 
            placeholder="Email", 
            label_visibility="collapsed",
            key="login_email"
        )
        password = st.text_input(
            "Password", 
            type="password", 
            placeholder="Password", 
            label_visibility="collapsed",
            key="login_password"
        )
        
        # This will hold our custom error message
        error_placeholder = st.empty()
        login_button = st.form_submit_button(label="Login")

    if login_button:
        if email and password:
            # Add these two lines
            cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
            user = cursor.fetchone()
            
            # New code for Home.py
            if user and bcrypt.checkpw(password.encode(), user[2].encode()):
                # user[5] is username, user[3] is role
                username = user[5]
                user_role = user[3] 

                st.session_state["name"] = username
                st.session_state["role"] = user_role

                # Redirect based on user role
                auth_token = signer.sign(email.encode()).decode()
                st.set_cookie("auth_token", auth_token, max_age=300)
                if user_role == 'employee':
                    st.switch_page("pages/1_Employee_Dashboard.py")
                elif user_role == 'manager':
                    st.switch_page("pages/2_Manager_Dashboard.py")
                elif user_role == 'HR':
                    st.switch_page("pages/3_HR_Dashboard.py")
                elif user_role == 'admin':
                    st.switch_page("pages/4_Admin_Panel.py")
                else:
                    st.error("Unknown user role. Please contact support.")
            else:
                error_placeholder.markdown('<p class="error-message alert alert-warning">⚠️Invalid Email or password</p>', unsafe_allow_html=True)
        else:
            error_placeholder.markdown('<p class="error-message alert alert-warning">⚠️Please enter both Email and password</p>', unsafe_allow_html=True)
            
    # Close the container divs
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
