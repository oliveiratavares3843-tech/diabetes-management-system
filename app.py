import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Diabetes Management System", page_icon="🩸", layout="wide")

# 2. Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Demo credentials for recruiters + your original credentials
DEMO_USERS = {
    "recruiter": "diabetes2026",
    "admin": "Diabetes@2026"
}

# Safe custom blue style for Streamlit 1.67+
def apply_welcome_style():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #e6f2ff;
        }
        .stButton>button {
            background-color: #0066cc;
            color: white;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# --- SCREEN 1: HOME PAGE ---
def home_screen():
    apply_welcome_style()
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🩸 Diabetes Management System")
        st.subheader("Clinical Telemetry, Glycemic Analytics & Medical Reporting")
        st.markdown("---")
        st.write(
            "A full-stack clinical monitoring application built with Python, Streamlit, and SQLite. "
            "Track blood glucose levels, insulin administration, carbohydrate intake, and generate automated A4 medical reports."
        )
        st.write("")
        if st.button("Access Clinical System ➡️", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

# --- SCREEN 2: LOGIN PAGE ---
def login_screen():
    apply_welcome_style()
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🩸 Diabetes Management System")
        st.markdown("### Secure Clinical Access")
        
        # Visible demo credentials box for recruiters
        st.info("👋 **Recruiter / Visitor Demo Access:**\n\n* **Username:** `recruiter`\n* **Password:** `diabetes2026`")

        with st.form("login_form"):
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login", use_container_width=True)
            
            if submit_login:
                secrets_users = st.secrets.get("usuarios", {}) if hasattr(st, "secrets") else {}
                valid_users = {**DEMO_USERS, **secrets_users}

                u_clean = username_input.strip()
                p_clean = password_input.strip()

                if u_clean in valid_users and str(valid_users[u_clean]) == p_clean:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u_clean
                    st.session_state.page = "system"
                    st.rerun()
                else:
                    st.error("⚠️ Incorrect username or password.")
        
        if st.button("⬅️ Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

# --- SCREEN 3: MAIN CLINICAL SYSTEM ---
def system_screen():
    st.sidebar.title("👤 Active Session")
    st.sidebar.info(f"Logged in as: **{st.session_state.current_user}**")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.page = "home"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧪 Portfolio Demo Tools")
    st.sidebar.caption("Populate the database with sample readings to instantly test charts and PDF reports.")
    
    DB_NAME = "diabetes_management.db"

    # SQLite Database Initialization
    def init_db():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blood_glucose (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                glucose_level INTEGER NOT NULL,
                measurement_type TEXT NOT NULL,
                measured_at TEXT NOT NULL,
                notes TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insulin_doses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dosage REAL NOT NULL,
                insulin_type TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_type TEXT NOT NULL,
                carbs_grams INTEGER NOT NULL,
                consumed_at TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    init_db()

    # Button to seed demo data for recruiters
    if st.sidebar.button("📊 Load Sample Clinical Data"):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.now()
        samples = [
            (98, "Fasting", (now - timedelta(days=3)).strftime("%Y-%m-%d 07:30:00"), "Normal morning reading"),
            (142, "Post-meal", (now - timedelta(days=2)).strftime("%Y-%m-%d 13:45:00"), "After lunch"),
            (110, "Pre-meal", (now - timedelta(days=1)).strftime("%Y-%m-%d 19:00:00"), "Before dinner"),
            (104, "Fasting", now.strftime("%Y-%m-%d 08:00:00"), "Stable fasting level")
        ]
        cursor.executemany(
            "INSERT INTO blood_glucose (glucose_level, measurement_type, measured_at, notes) VALUES (?, ?, ?, ?)",
            samples
        )
        conn.commit()
        conn.close()
        st.sidebar.success("Sample data loaded!")
        st.rerun()

    # Main Title
    st.title("🩸 Diabetes Management System")
    st.markdown("Secure Telemetry Environment - Track and monitor clinical data.")

    # Data Entry Section
    st.subheader("📝 Data Entry")
    tab1, tab2, tab3 = st.tabs(["Blood Glucose", "Insulin Doses", "Meals & Carbs"])

    with tab1:
        with st.form("glucose_form", clear_on_submit=True):
            glucose_level = st.number_input("Glucose Level (mg/dL)", min_value=20, max_value=600, value=100, step=1)
            measurement_type = st.selectbox("Measurement Context", ["Fasting", "Pre-meal", "Post-meal", "Bedtime", "Other"])
            date_input = st.date_input("Date", datetime.now().date())
            time_input = st.time_input("Time", datetime.now().time())
            notes = st.text_area("Notes / Symptoms", placeholder="e.g., Felt a bit dizzy")
            if st.form_submit_button("Save Glucose Log"):
                measured_at = f"{date_input} {time_input.strftime('%H:%M:%S')}"
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO blood_glucose (glucose_level, measurement_type, measured_at, notes) VALUES (?, ?, ?, ?)",
                    (glucose_level, measurement_type, measured_at, notes)
                )
                conn.commit()
                conn.close()
                st.success(f"Successfully recorded: {glucose_level} mg/dL")

    with tab2:
        with st.form("insulin_form", clear_on_submit=True):
            dosage = st.number_input("Insulin Units", min_value=0.5, max_value=100.0, value=1.0, step=0.5)
            insulin_type = st.selectbox("Insulin Type", ["Rapid-acting", "Long-acting", "NPH", "Regular"])
            date_input = st.date_input("Date ", datetime.now().date())
            time_input = st.time_input("Time ", datetime.now().time())
            if st.form_submit_button("Save Insulin Log"):
                applied_at = f"{date_input} {time_input.strftime('%H:%M:%S')}"
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO insulin_doses (dosage, insulin_type, applied_at) VALUES (?, ?, ?)",
                    (dosage, insulin_type, applied_at)
                )
                conn.commit()
                conn.close()
                st.success(f"Successfully recorded: {dosage} units")

    with tab3:
        with st.form("meal_form", clear_on_submit=True):
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
            carbs_grams = st.number_input("Carbohydrates (grams)", min_value=0, max_value=300, value=30, step=1)
            date_input = st.date_input("Date ", datetime.now().date())
            time_input = st.time_input("Time ", datetime.now().time())
            if st.form_submit_button("Save Meal Log"):
                consumed_at = f"{date_input} {time_input.strftime('%H:%M:%S')}"
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO meals (meal_type, carbs_grams, consumed_at) VALUES (?, ?, ?)",
                    (meal_type, carbs_grams, consumed_at)
                )
                conn.commit()
                conn.close()
                st.success(f"Successfully recorded: {carbs_grams}g of carbs")

    st.divider()

    # Dashboard & Reports
    st.subheader("📊 Analytics Dashboard")
    conn = sqlite3.connect(DB_NAME)
    df_glucose = pd.read_sql_query("SELECT glucose_level, measurement_type, measured_at FROM blood_glucose ORDER BY measured_at ASC", conn)
    conn.close()

    if not df_glucose.empty:
        df_glucose['measured_at'] = pd.to_datetime(df_glucose['measured_at'])
        avg_glucose = int(df_glucose['glucose_level'].mean())
        max_glucose = int(df_glucose['glucose_level'].max())
        min_glucose = int(df_glucose['glucose_level'].min())
        estimated_hba1c = round((avg_glucose + 46.7) / 28.7, 1)


