"""
app.py — InsightCloud Streamlit Main Application.
Cloud-native GenAI CSV Analytics Platform on AWS.
Pages: Login, Signup, Dashboard, Upload, Ask AI.
Triple AI Mode: Gemini (free) + Groq (free) + Bedrock (AWS production).
"""

import streamlit as st
import pandas as pd
import warnings
warnings.filterwarnings("ignore", message=".*Arrow.*")
from database import init_db, SessionLocal
from auth import signup_user, login_user
from upload import ensure_upload_dir, validate_csv, save_file, list_files, load_file_as_df
from processing import get_summary
from genai import ask_question, build_context
from Report import generate_insight_pdf
from config import APP_NAME, APP_VERSION, is_aws_mode, is_bedrock_mode, is_groq_mode, STORAGE_MODE, AI_MODE

# ─── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="InsightCloud",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Initialize Database & Upload Directory ────────────────
init_db()
ensure_upload_dir()

# ─── Custom CSS — Polished Warm Gold Theme (#B88E23) ──────
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700;800&display=swap');

    /* ─── Global Reset ─── */
    .stApp {
        background: #FDFAF3;
    }

    /* ─── Typography ─── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #2C2418;
    }

    h1 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #2C2418 !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    h2, h3 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #2C2418 !important;
        font-weight: 700 !important;
    }

    p, span, li, label, .stMarkdown {
        font-family: 'DM Sans', sans-serif !important;
        color: #2C2418;
    }

    /* ─── Sidebar ─── */
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E8DFC9;
        box-shadow: 2px 0 12px rgba(44,36,24,0.04);
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: #2C2418 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #2C2418 !important;
    }

    /* Sidebar radio buttons */
    section[data-testid="stSidebar"] .stRadio label {
        color: #2C2418 !important;
        font-weight: 500;
        padding: 8px 12px;
        border-radius: 8px;
        transition: background 0.2s;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: #F5ECD7;
    }

    /* ─── Primary Buttons — Warm Gold ─── */
    .stButton > button {
        background: linear-gradient(135deg, #B88E23 0%, #D4A832 100%);
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 12px 28px;
        font-weight: 600;
        font-family: 'DM Sans', sans-serif;
        font-size: 15px;
        letter-spacing: 0.3px;
        transition: all 0.25s ease;
        box-shadow: 0 2px 8px rgba(184,142,35,0.25);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #9A7620 0%, #B88E23 100%);
        color: white !important;
        border: none;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(184,142,35,0.35);
    }

    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 1px 4px rgba(184,142,35,0.2);
    }

    .stButton > button:focus,
    .stButton > button:visited {
        color: white !important;
    }

    /* ─── Text Inputs ─── */
    .stTextInput > div > div > input {
        background: #FFFFFF !important;
        border: 1.5px solid #E8DFC9 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 15px !important;
        color: #2C2418 !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    .stTextInput > div > div > input:focus {
        border-color: #B88E23 !important;
        box-shadow: 0 0 0 2px rgba(184,142,35,0.15) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #A89B85 !important;
    }

    /* ─── Select Box ─── */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border: 1.5px solid #E8DFC9 !important;
        border-radius: 10px !important;
    }

    /* ─── File Uploader ─── */
    .stFileUploader > div {
        border: 2px dashed #D4C9A8 !important;
        border-radius: 12px !important;
        background: #FEFDFB !important;
        transition: border-color 0.2s;
    }

    .stFileUploader > div:hover {
        border-color: #B88E23 !important;
    }

    /* ─── Metrics ─── */
    div[data-testid="stMetricLabel"] {
        color: #6B5D4A !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div[data-testid="stMetricValue"] {
        color: #B88E23 !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 700;
        font-size: 28px !important;
    }

    div[data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #E8DFC9;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(44,36,24,0.04);
    }

    /* ─── DataFrames ─── */
    .stDataFrame {
        border-radius: 12px !important;
        border: 1px solid #E8DFC9 !important;
        overflow: hidden;
    }

    /* ─── Expander ─── */
    .streamlit-expanderHeader {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        color: #2C2418 !important;
        font-size: 15px;
        background: #FEFDFB;
        border-radius: 8px;
    }

    details {
        border: 1px solid #E8DFC9 !important;
        border-radius: 12px !important;
        background: #FFFFFF !important;
    }

    /* ─── Divider ─── */
    hr {
        border-color: #E8DFC9 !important;
        margin: 24px 0 !important;
    }

    /* ─── Spinner ─── */
    .stSpinner > div {
        border-top-color: #B88E23 !important;
    }

    /* ─── Alerts & Info Boxes ─── */
    .stAlert {
        border-radius: 10px !important;
    }

    /* ─── Custom Classes ─── */
    .success-box {
        background: linear-gradient(135deg, #F5ECD7 0%, #FDF6E3 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #B88E23;
        margin: 12px 0;
        color: #2C2418;
        font-family: 'DM Sans', sans-serif;
        box-shadow: 0 2px 8px rgba(184,142,35,0.08);
    }

    .info-badge {
        display: inline-block;
        background: linear-gradient(135deg, #F5ECD7 0%, #FDF6E3 100%);
        color: #8B6914;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        font-family: 'DM Sans', sans-serif;
        border: 1px solid #E8DFC9;
        letter-spacing: 0.2px;
    }

    .page-header {
        background: linear-gradient(135deg, #FFFFFF 0%, #FDF6E3 100%);
        padding: 24px 28px;
        border-radius: 16px;
        border: 1px solid #E8DFC9;
        margin-bottom: 24px;
        box-shadow: 0 2px 12px rgba(44,36,24,0.04);
    }

    /* ─── Card Style for content sections ─── */
    .stMarkdown h3 {
        padding-top: 8px;
    }

    /* ─── Warning & Error ─── */
    .stWarning {
        background: #FFF8E7 !important;
        border: 1px solid #E8DFC9 !important;
        border-radius: 10px !important;
    }

    .stError {
        border-radius: 10px !important;
    }

    .stSuccess {
        border-radius: 10px !important;
    }

    .stInfo {
        background: #F5F0E4 !important;
        border: 1px solid #E8DFC9 !important;
        border-radius: 10px !important;
        color: #2C2418 !important;
    }

    /* ─── Tab styling ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-family: 'DM Sans', sans-serif;
    }

    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #F5ECD7;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: #D4C9A8;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #B88E23;
    }

    /* ─── Hide Streamlit Branding ─── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: #FDFAF3;
        border-bottom: 1px solid #E8DFC9;
        height: 0px !important;
        visibility: hidden;
    }

    /* ─── Reduce top padding ─── */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem !important;
    }

    /* ─── Fix password field overlap ─── */
    .stTextInput > div > div > span {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helper: Get AI Label ─────────────────────────────────
def get_ai_label() -> str:
    """Return the display label for the current AI mode."""
    if is_bedrock_mode():
        return "AWS Bedrock (Mistral 8B)"
    elif is_groq_mode():
        return "Groq LLaMA 70B"
    else:
        return "Gemini Flash"


def get_ai_badge() -> str:
    """Return the badge HTML for the current AI mode."""
    if is_bedrock_mode():
        return '<span class="info-badge">🧠 AI: AWS Bedrock (Mistral 8B)</span>'
    elif is_groq_mode():
        return '<span class="info-badge">🧠 AI: Groq LLaMA 70B (Free)</span>'
    else:
        return '<span class="info-badge">🧠 AI: Gemini Flash (Free)</span>'


# ─── Role-Based Access Control ────────────────────────────
def get_user_role() -> str:
    """Get the current user's role (lowercase)."""
    user = st.session_state.get("user")
    if user:
        return user.get("role", "viewer").lower()
    return "viewer"


def can_upload() -> bool:
    """Check if current user can upload files. Analysts and Admins only."""
    return get_user_role() in ["analyst", "admin"]


def can_ask_ai() -> bool:
    """Check if current user can use AI queries. All roles can ask AI."""
    return True


def can_view_dashboard() -> bool:
    """All roles can view the dashboard."""
    return True


def is_admin() -> bool:
    """Check if current user is an Admin."""
    return get_user_role() == "admin"


# ─── Session State Initialization ──────────────────────────
def init_session_state():
    """Initialize all session state variables with defaults."""
    defaults = {
        "authenticated": False,
        "token": None,
        "user": None,
        "auth_page": "login",
        "active_dataset": None,
        "active_df": None,
        "nav_page": "📊 Dashboard",
        "ai_question": "",
        "chat_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ─── Helper: Get DB Session ───────────────────────────────
def get_db_session():
    """Create and return a database session."""
    return SessionLocal()


# ═══════════════════════════════════════════════════════════
# AUTH PAGES
# ═══════════════════════════════════════════════════════════

def render_login_page():
    """Render the login page with centered layout."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("")
        st.markdown("")
        st.markdown(
            "<h1 style='text-align: center; font-size: 2.8rem;'>☁️ InsightCloud</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align: center; color: #6B5D4A; font-size: 1.1rem;'>"
            "Welcome back — sign in to continue</p>",
            unsafe_allow_html=True
        )
        st.markdown("")

        # Login form
        email = st.text_input("Email", value="demo@insightcloud.io", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        st.markdown("")

        if st.button("Sign In", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    db = get_db_session()
                    result = login_user(email, password, db)
                    db.close()

                    # Store auth info in session state
                    st.session_state["authenticated"] = True
                    st.session_state["token"] = result["token"]
                    st.session_state["user"] = result["user"]
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

        st.markdown("")
        st.markdown(
            "<p style='text-align: center; color: #6B5D4A;'>Don't have an account?</p>",
            unsafe_allow_html=True
        )
        if st.button("Sign Up", use_container_width=True):
            st.session_state["auth_page"] = "signup"
            st.rerun()


def render_signup_page():
    """Render the signup page with centered layout."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("")
        st.markdown("")
        st.markdown(
            "<h1 style='text-align: center; font-size: 2.8rem;'>☁️ InsightCloud</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align: center; color: #6B5D4A; font-size: 1.1rem;'>"
            "Create your account</p>",
            unsafe_allow_html=True
        )
        st.markdown("")

        # Signup form
        full_name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        role = st.selectbox("Role", ["Analyst", "Admin", "Viewer"], key="signup_role")

        # Role descriptions
        role_info = {
            "Analyst": "📊 **Analyst** — Upload datasets, ask AI questions, view dashboard. Best for data analysis.",
            "Admin": "🛡️ **Admin** — Full access including upload, AI queries, and user management.",
            "Viewer": "👁️ **Viewer** — View dashboard and ask AI questions on existing datasets. Cannot upload new files.",
        }
        st.markdown(
            f'<div style="background:#F5ECD7; padding:12px 16px; border-radius:10px; '
            f'font-size:13px; color:#2C2418; margin-top:4px;">'
            f'{role_info[role]}</div>',
            unsafe_allow_html=True
        )
        st.markdown("")

        if st.button("Create Account", use_container_width=True, type="primary"):
            if not full_name or not email or not password:
                st.error("Please fill in all fields.")
            else:
                try:
                    db = get_db_session()
                    result = signup_user(email, full_name, password, role, db)
                    db.close()

                    # Store auth info in session state
                    st.session_state["authenticated"] = True
                    st.session_state["token"] = result["token"]
                    st.session_state["user"] = result["user"]
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Signup failed: {str(e)}")

        st.markdown("")
        st.markdown(
            "<p style='text-align: center; color: #6B5D4A;'>Already have an account?</p>",
            unsafe_allow_html=True
        )
        if st.button("Back to Sign In", use_container_width=True):
            st.session_state["auth_page"] = "login"
            st.rerun()


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════

def render_sidebar():
    """Render the sidebar with navigation, user info, and mode badges."""
    with st.sidebar:
        st.title("☁️ InsightCloud")

        user = st.session_state["user"]
        st.markdown(f"Welcome, **{user['full_name']}**")

        # Role badge with color
        role = get_user_role()
        role_colors = {"admin": "#D4432F", "analyst": "#B88E23", "viewer": "#6B5D4A"}
        role_color = role_colors.get(role, "#6B5D4A")
        st.markdown(
            f'<span style="background:{role_color}; color:white; padding:3px 10px; '
            f'border-radius:12px; font-size:12px; font-weight:600; text-transform:uppercase;">'
            f'{role}</span>',
            unsafe_allow_html=True
        )
        st.divider()

        # Role-aware navigation
        nav_options = ["📊 Dashboard"]
        if can_upload():
            nav_options.append("📁 Upload Data")
        if can_ask_ai():
            nav_options.append("🤖 Ask AI")
        if is_admin():
            nav_options.append("👥 Users")

        # Make sure current page is valid for this role
        current_page = st.session_state.get("nav_page", "📊 Dashboard")
        if current_page not in nav_options:
            current_page = "📊 Dashboard"
            st.session_state["nav_page"] = current_page

        page = st.radio(
            "Navigate",
            nav_options,
            index=nav_options.index(current_page),
            key="sidebar_nav"
        )
        st.session_state["nav_page"] = page

        st.divider()

        # Storage mode badge
        if is_aws_mode():
            st.markdown(
                '<span class="info-badge">☁️ Storage: AWS S3</span>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<span class="info-badge">🔒 Storage: Local</span>',
                unsafe_allow_html=True
            )

        # AI mode badge — dynamically shows current mode
        st.markdown(get_ai_badge(), unsafe_allow_html=True)

        st.markdown("")
        st.markdown(
            f"<small style='color: #6B5D4A;'>v{APP_VERSION}</small>",
            unsafe_allow_html=True
        )

        # Logout button
        st.markdown("")
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ═══════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════

def render_dashboard():
    """Render the dashboard with stats overview and active dataset info."""
    st.title("📊 Dashboard")

    # Get file list for stats
    files = list_files()
    active_ds = st.session_state.get("active_dataset")
    active_df = st.session_state.get("active_df")

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Datasets", len(files))
    with col2:
        st.metric("Active Dataset", active_ds if active_ds else "None")
    with col3:
        st.metric("Columns", active_df.shape[1] if active_df is not None else "-")
    with col4:
        st.metric("Rows", f"{active_df.shape[0]:,}" if active_df is not None else "-")

    st.divider()

    # Active dataset details
    if active_df is not None and active_ds:
        st.subheader(f"Active Dataset: {active_ds}")
        st.dataframe(active_df.head(10), use_container_width=True)

        with st.expander("📈 Summary Statistics"):
            st.dataframe(active_df.describe(include="all"), use_container_width=True)

        with st.expander("🏷️ Column Types"):
            for col in active_df.columns:
                st.markdown(f"- **{col}**: `{active_df[col].dtype}`")

        with st.expander("❓ Null Values"):
            null_counts = active_df.isnull().sum()
            null_df = pd.DataFrame({
                "Column": null_counts.index,
                "Missing Values": null_counts.values,
                "% Missing": (null_counts.values / len(active_df) * 100).round(2)
            })
            st.dataframe(null_df, use_container_width=True, hide_index=True)
    else:
        st.info("📂 No active dataset. Select a dataset below to get started.")

    # ─── Available Datasets Section (visible to ALL roles including Viewer) ───
    st.divider()
    st.subheader("📁 Available Datasets")

    if files:
        for f in files:
            col1, col2 = st.columns([3, 1])
            with col1:
                size_info = f"{f['size_kb']} KB"
                if "last_modified" in f:
                    size_info += f" · {f['last_modified']}"
                st.markdown(f"📄 **{f['filename']}** ({size_info})")
            with col2:
                if st.button("Load", key=f"dash_load_{f['filename']}"):
                    with st.spinner(f"Loading {f['filename']}..."):
                        df = load_file_as_df(f["filename"])
                    if df is not None:
                        st.session_state["active_dataset"] = f["filename"]
                        st.session_state["active_df"] = df
                        st.rerun()
                    else:
                        st.error("Failed to load file.")
    else:
        if can_upload():
            st.info("No datasets yet. Go to **Upload Data** to add your first CSV.")
            if st.button("📁 Upload Data"):
                st.session_state["nav_page"] = "📁 Upload Data"
                st.rerun()
        else:
            st.info("No datasets available yet. Ask an Analyst or Admin to upload a CSV.")


# ═══════════════════════════════════════════════════════════
# UPLOAD PAGE
# ═══════════════════════════════════════════════════════════

def render_upload_page():
    """Render the upload page with drag-and-drop, preview, and file list."""
    st.title("📁 Upload Dataset")

    # Role check — Viewers cannot upload
    if not can_upload():
        st.warning("🔒 **Access Restricted** — Your role (`Viewer`) does not have permission to upload datasets. Contact an Admin to get Analyst or Admin access.")
        return

    # Storage mode badge
    if is_aws_mode():
        st.markdown(
            '<span class="info-badge">☁️ Uploading to AWS S3</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="info-badge">🔒 Saving to Local Storage</span>',
            unsafe_allow_html=True
        )
    st.markdown("")

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Maximum file size: 50MB. Accepted format: CSV (.csv)"
    )

    if uploaded_file is not None:
        # Validate the CSV
        valid, msg = validate_csv(uploaded_file)

        if not valid:
            st.error(f"❌ {msg}")
        else:
            with st.spinner("📤 Uploading and processing..."):
                result = save_file(uploaded_file)

            if result["success"]:
                st.markdown(
                    f'<div class="success-box">✅ <strong>Uploaded {result["filename"]}</strong>'
                    f' — {result["rows"]:,} rows, {result["columns"]} columns'
                    f' — Stored in <strong>{result["storage"]}</strong></div>',
                    unsafe_allow_html=True
                )

                # Load and set as active dataset
                df = load_file_as_df(result["filename"])
                st.session_state["active_dataset"] = result["filename"]
                st.session_state["active_df"] = df

                # Data preview
                st.subheader("Data Preview")
                st.dataframe(df.head(10), use_container_width=True)

                # Quick metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", f"{result['rows']:,}")
                with col2:
                    st.metric("Columns", result["columns"])
                with col3:
                    st.metric("Size", f"{result['size_kb']:.1f} KB")

                # Navigate to Ask AI
                st.markdown("")
                if st.button("🤖 Go to Ask AI →", type="primary"):
                    st.session_state["nav_page"] = "🤖 Ask AI"
                    st.rerun()
            else:
                st.error(f"❌ Upload failed: {result.get('error', 'Unknown error')}")

    st.divider()

    # Previously uploaded files
    st.subheader("Previously Uploaded Files")
    files = list_files()

    if files:
        for f in files:
            col1, col2 = st.columns([3, 1])
            with col1:
                size_info = f"{f['size_kb']} KB"
                if "last_modified" in f:
                    size_info += f" · {f['last_modified']}"
                st.markdown(f"📄 **{f['filename']}** ({size_info})")
            with col2:
                if st.button("Load", key=f"load_{f['filename']}"):
                    with st.spinner(f"Loading {f['filename']}..."):
                        df = load_file_as_df(f["filename"])
                    if df is not None:
                        st.session_state["active_dataset"] = f["filename"]
                        st.session_state["active_df"] = df
                        st.rerun()
                    else:
                        st.error("Failed to load file.")
    else:
        st.info("📂 No files uploaded yet. Use the uploader above to get started.")


# ═══════════════════════════════════════════════════════════
# ASK AI PAGE
# ═══════════════════════════════════════════════════════════

def render_ask_ai_page():
    """Render the Ask AI page with question input, suggestions, and chat history."""
    st.title("🤖 Ask AI")

    # AI mode badge — dynamically shows current mode
    st.markdown(
        f'<span class="info-badge">🧠 Powered by {get_ai_label()}</span>',
        unsafe_allow_html=True
    )
    st.markdown("")

    # Check for active dataset
    if st.session_state.get("active_df") is None or st.session_state.get("active_dataset") is None:
        st.warning("⚠️ Please upload a dataset first. Go to **Upload Data** to get started.")
        if st.button("📁 Go to Upload"):
            st.session_state["nav_page"] = "📁 Upload Data"
            st.rerun()
        return

    filename = st.session_state["active_dataset"]
    df = st.session_state["active_df"]

    # Dataset info badge
    st.markdown(
        f'<span class="info-badge">📊 {filename} — {df.shape[0]:,} rows × {df.shape[1]} columns</span>',
        unsafe_allow_html=True
    )
    st.divider()

    # Track if a suggestion was clicked this run
    pending_question = None

    # Question input
    question = st.text_input(
        "Ask a question about your data",
        placeholder="e.g., Which product had the highest sales?",
        key="question_input"
    )

    # Suggestion chips
    st.markdown("**Try these:**")
    suggestions = [
        "What are the key trends?",
        "Which category is highest?",
        "Any outliers or anomalies?",
        "Summarize this dataset",
        "Any missing values?",
    ]
    suggestion_cols = st.columns(len(suggestions))
    for i, s in enumerate(suggestions):
        with suggestion_cols[i]:
            if st.button(s, key=f"sug_{i}", use_container_width=True):
                pending_question = s

    # Use suggestion if clicked, otherwise use text input
    final_question = pending_question if pending_question else question

    st.markdown("")

    # Auto-ask if suggestion was clicked, or manual ask via button
    should_ask = pending_question is not None

    if st.button("🔍 Ask InsightCloud AI", type="primary", use_container_width=True):
        should_ask = True

    if should_ask:
        if not final_question or not final_question.strip():
            st.error("Please enter a question.")
        else:
            with st.spinner(f"🧠 Analyzing your data with {get_ai_label()}..."):
                answer = ask_question(final_question, df)

            st.markdown("---")
            st.markdown("### 💡 AI Insight")
            st.markdown(answer)

            # Download AI report as PDF
            user = st.session_state.get("user", {})
            pdf_bytes = generate_insight_pdf(
                filename=filename,
                rows=df.shape[0],
                columns=df.shape[1],
                question=final_question,
                answer=answer,
                user_name=user.get("full_name", "User"),
                user_role=user.get("role", "Analyst"),
            )
            st.download_button(
                label="📄 Download Report as PDF",
                data=pdf_bytes,
                file_name=f"InsightCloud_Report_{filename.replace('.csv', '')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            # Transparency: show dataset context sent to AI
            with st.expander("🔍 Dataset context sent to AI"):
                st.code(build_context(df), language="text")

            # Store in chat history
            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []
            st.session_state["chat_history"].append({"q": final_question, "a": answer})

    # Show chat history (previous questions)
    chat_history = st.session_state.get("chat_history", [])
    if len(chat_history) > 0:
        st.divider()
        st.subheader("Previous Questions")
        # Show all except the most recent (which is already displayed above)
        history_to_show = chat_history[:-1] if len(chat_history) > 1 else chat_history
        for i, chat in enumerate(reversed(history_to_show)):
            with st.expander(f"Q: {chat['q']}"):
                st.markdown(chat["a"])


# ═══════════════════════════════════════════════════════════
# ADMIN — USERS PAGE
# ═══════════════════════════════════════════════════════════

def render_users_page():
    """Render the Admin users page — shows all registered users."""
    st.title("👥 User Management")

    if not is_admin():
        st.warning("🔒 **Access Restricted** — Only Admins can view this page.")
        return

    st.markdown(
        '<span class="info-badge">🛡️ Admin Panel</span>',
        unsafe_allow_html=True
    )
    st.markdown("")

    try:
        from models import User
        db = get_db_session()
        users = db.query(User).all()
        db.close()

        if users:
            st.metric("Total Users", len(users))
            st.divider()

            # Build user table
            user_data = []
            for u in users:
                user_data.append({
                    "ID": u.id,
                    "Name": u.full_name,
                    "Email": u.email,
                    "Role": u.role.upper(),
                    "Created": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "N/A"
                })

            user_df = pd.DataFrame(user_data)
            st.dataframe(user_df, use_container_width=True, hide_index=True)

            # Role summary
            st.divider()
            st.subheader("Role Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                admin_count = sum(1 for u in users if u.role.lower() == "admin")
                st.metric("Admins", admin_count)
            with col2:
                analyst_count = sum(1 for u in users if u.role.lower() == "analyst")
                st.metric("Analysts", analyst_count)
            with col3:
                viewer_count = sum(1 for u in users if u.role.lower() == "viewer")
                st.metric("Viewers", viewer_count)
        else:
            st.info("No users registered yet.")

    except Exception as e:
        st.error(f"Error loading users: {str(e)}")


# ═══════════════════════════════════════════════════════════
# MAIN APP ROUTING
# ═══════════════════════════════════════════════════════════

def main():
    """Main application entry point — handles routing between auth and app pages."""
    if not st.session_state.get("authenticated"):
        # Show auth pages
        if st.session_state.get("auth_page") == "signup":
            render_signup_page()
        else:
            render_login_page()
    else:
        # Show sidebar and routed page
        render_sidebar()

        page = st.session_state.get("nav_page", "📊 Dashboard")

        if page == "📊 Dashboard":
            render_dashboard()
        elif page == "📁 Upload Data":
            render_upload_page()
        elif page == "🤖 Ask AI":
            render_ask_ai_page()
        elif page == "👥 Users":
            render_users_page()


if __name__ == "__main__":
    main()