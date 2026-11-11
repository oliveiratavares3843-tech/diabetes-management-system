# 🩸 Diabetes Management System
DME
A modern, full-stack medical telemetry dashboard and analytics web application designed to track blood glucose levels, insulin dosages, and carbohydrate intake. Built for high-volume data handling and clinical report generation.

## 🚀 Live Demo
* **Live System Link:** [https://diabetes-management-system.streamlit.app/]

## 🛠️ Architecture & Core Features

* **Data Entry Layer:** Segmented forms built with Streamlit utilizing custom data validation and state management (`clear_on_submit`).
* **Relational Database (SQLite):** Configured with explicit schema constraints and index optimization (`idx_glucose_date`) for hyper-fast querying over long timelines.
* **Analytics Engine (Pandas):** Processes internal relational records to calculate rolling mathematical glucose averages and estimate HbA1c percentages using standard medical DCCT metrics.
* **Clinical Report Exporter (WeasyPrint):** Renders responsive, printable PDF documents directly from optimized HTML templates with custom CSS pagination controls (`break-inside: avoid`).

## 💻 Tech Stack
* **Language:** Python
* **Frontend/Dashboard:** Streamlit
* **Data Processing:** Pandas
* **Database:** SQLite
* **PDF Engine:** WeasyPrint (GTK+ Framework)

## 📦 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com
   cd diabetes-management-system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

