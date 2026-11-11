import streamlit as st
import sqlite3
import pandas as pd
import weasyprint
from datetime import datetime

# Configuração da página do Streamlit
st.set_page_config(page_title="Diabetes Management System", page_icon="🩸", layout="wide")

DB_NAME = "diabetes_management.db"

# Inicialização do banco de dados SQLite
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

# Título Principal
st.title("🩸 Diabetes Management System")
st.markdown("Track and monitor blood glucose levels, insulin doses, and carbohydrate intake.")

# Seção de Entrada de Dados
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
            measured_at = f"{date_input} {time_input}"
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO blood_glucose (glucose_level, measurement_type, measured_at, notes) VALUES (?, ?, ?, ?)", (glucose_level, measurement_type, measured_at, notes))
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
            applied_at = f"{date_input} {time_input}"
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO insulin_doses (dosage, insulin_type, applied_at) VALUES (?, ?, ?)", (dosage, insulin_type, applied_at))
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
            consumed_at = f"{date_input} {time_input}"
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO meals (meal_type, carbs_grams, consumed_at) VALUES (?, ?, ?)", (meal_type, carbs_grams, consumed_at))
            conn.commit()
            conn.close()
            st.success(f"Successfully recorded: {carbs_grams}g of carbs")

st.divider()

# Dashboard e Relatórios
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

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label="Average Glucose", value=f"{avg_glucose} mg/dL")
    c2.metric(label="Estimated HbA1c", value=f"{estimated_hba1c} %")
    c3.metric(label="Highest / Lowest", value=f"{max_glucose} / {min_glucose} mg/dL")
    c4.metric(label="Total Readings", value=len(df_glucose))

    st.markdown("#### 📈 Glucose Trends Over Time")
    st.line_chart(df_glucose.set_index('measured_at')['glucose_level'])

    # Função para gerar o relatório PDF corporativo
    def generate_pdf():
        rows_html = "".join([f"<tr><td>{r['measured_at']}</td><td>{r['glucose_level']} mg/dL</td><td>{r['measurement_type']}</td></tr>" for _, r in df_glucose.tail(10).iterrows()])
        html_content = f"""
        <html>
        <head>
            <style>
                @page {{ size: A4; margin: 20mm; }}
                body {{ font-family: Arial, sans-serif; color: #333; }}
                h1 {{ color: #0066cc; border-bottom: 2px solid #0066cc; }}
                .box {{ background: #f2f7fc; border-left: 4px solid #0066cc; padding: 15px; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; break-inside: avoid; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 10pt; }}
                th {{ background: #0066cc; color: white; }}
                .disclaimer {{ font-size: 8pt; color: #777; text-align: center; margin-top: 40px; border-top: 1px solid #ddd; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <h1>Diabetes Management Report</h1>
            <div class="box">
                <p><strong>Estimated HbA1c:</strong> {estimated_hba1c}%</p>
                <p><strong>Glucose Average:</strong> {avg_glucose} mg/dL</p>
                <p><strong>Generated At:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            <h2>Recent Telemetry Records</h2>
            <table>
                <thead><tr><th>Timestamp</th><th>Glucose Level</th><th>Context</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            <div class="disclaimer">This is for informational purposes only. For medical advice or diagnosis, consult a professional. AI responses may include mistakes.</div>
        </body>
        </html>
        """
        weasyprint.HTML(string=html_content).write_pdf("diabetes_report.pdf")

    st.divider()
    if st.button("📥 Generate Telemetry Report (PDF)"):
        generate_pdf()
        with open("diabetes_report.pdf", "rb") as file:
            st.download_button(label="Download Report PDF", data=file, file_name="diabetes_report.pdf", mime="application/pdf")
else:
    st.info("No glucose data logged yet. Fill out the form above to populate the analytics dashboard.")

