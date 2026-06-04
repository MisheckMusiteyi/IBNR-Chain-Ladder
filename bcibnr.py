# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import chainladder as cl
from io import BytesIO
from datetime import date
import re

st.set_page_config(page_title="Chain Ladder IBNR Calculator", layout="wide")

# ---------- CUSTOM CSS (same as before) ----------
st.markdown("""
<style>
    /* Global */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: 'Calisto MT', serif;
        font-size: 11pt;
    }
    
    body, p, h1, h2, h3, h4, h5, h6, div, span, label, .stMarkdown, 
    .stTextInput label, .stDateInput label, .stSelectbox label, .stMultiSelect label,
    .stButton button, .stDownloadButton button, .stFileUploader label,
    .stAlert, .stInfo, .stWarning, .stError, .stSuccess, .stSpinner, 
    .stProgress, .stToast, .stSidebar, .stMetric, .stExpander {
        font-family: 'Calisto MT', serif !important;
    }
    
    .header {
        background-color: #000000;
        padding: 1rem 2rem;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        border-bottom: 3px solid #D4AF37;
    }
    .nav-links a {
        color: #FFFFFF;
        margin-left: 2rem;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s;
        font-family: 'Calisto MT', serif;
    }
    .nav-links a:hover {
        color: #D4AF37;
    }
    
    .hero {
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        color: #FFFFFF;
        padding: 2rem 2rem;
        text-align: center;
        border-bottom: 3px solid #D4AF37;
    }
    .hero h1 {
        color: #D4AF37;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-family: 'Calisto MT', serif;
    }
    .hero p {
        font-size: 1.2rem;
        max-width: 800px;
        margin: 0 auto;
        font-family: 'Calisto MT', serif;
    }
    
    .main-container {
        max-width: 1400px;
        margin: 2rem auto;
        padding: 0 2rem;
    }
    
    .required-container {
        background-color: #F9F9F9;
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        min-height: 120px;
        height: auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        width: 100%;
        margin-bottom: 1rem;
    }
    .required-container h3 {
        color: #D4AF37;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .required-container p {
        color: #666666;
        font-size: 0.85rem;
        margin-bottom: 0;
        line-height: 1.3;
    }
    
    .grouping-container {
        background-color: #F9F9F9;
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .grouping-container h3 {
        color: #D4AF37;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .date-range-container {
        background-color: #F9F9F9;
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .date-range-container h3 {
        color: #D4AF37;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .grain-container {
        background-color: #F9F9F9;
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .grain-container h3 {
        color: #D4AF37;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .card {
        background-color: #F9F9F9;
        border: 1px solid #D4AF37;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .card h3 {
        color: #D4AF37;
        margin-top: 0;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 0.5rem;
        font-family: 'Calisto MT', serif;
    }
    
    .footer {
        background-color: #000000;
        color: #FFFFFF;
        text-align: center;
        padding: 1.5rem;
        border-top: 3px solid #D4AF37;
        margin-top: 3rem;
    }
    .footer a {
        color: #D4AF37;
        text-decoration: none;
        font-family: 'Calisto MT', serif;
    }
    
    .stButton > button, .stDownloadButton > button {
        background-color: #D4AF37;
        color: #000000;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
        font-family: 'Calisto MT', serif !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #B8960F;
        color: #FFFFFF;
    }
    
    .stFileUploader {
        border: 2px dashed #D4AF37;
        border-radius: 5px;
        padding: 1rem;
    }
    
    .stMultiSelect [data-baseweb="select"], 
    .stSelectbox [data-baseweb="select"] {
        border: 1px solid #D4AF37;
        border-radius: 4px;
    }
    
    .dataframe {
        border: 1px solid #D4AF37;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .data-check-container {
        background-color: #E3F2FD;
        border: 2px solid #2196F3;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .data-check-warning {
        background-color: #FFF3E0;
        border: 2px solid #FF9800;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .data-check-error {
        background-color: #FFEBEE;
        border: 2px solid #F44336;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="header">
    <div class="nav-links">
        <a href="#">Home</a>
        <a href="#">Services</a>
        <a href="#">Tools</a>
        <a href="#">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown("""
<div class="hero">
    <h1>Chain Ladder IBNR Calculator</h1>
    <p>Upload your claims data (CSV or Excel). Map your columns, select the IBNR period, choose grain, and select value columns.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Main Container ----------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --- User inputs ---
col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name (for file name)", value="Client").strip()
with col2:
    pass

# --- IBNR Period Selection ---
st.markdown("""
<div class="date-range-container">
    <h3>📅 IBNR Period</h3>
    <p>Select the date range for claims to be included (based on Loss Date)</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input("From Date", value=date(2020, 1, 1))
    st.caption("Claims with Loss Date on or after this date")
with col2:
    to_date = st.date_input("To Date", value=date(2024, 12, 31))
    st.caption("Claims with Loss Date on or before this date")

from_date = pd.to_datetime(from_date)
to_date = pd.to_datetime(to_date)

st.info(f"**Selected IBNR Period:** {from_date.date()} to {to_date.date()}")

# --- Grain Selection ---
st.markdown("""
<div class="grain-container">
    <h3>📊 Triangle Grain</h3>
    <p>Select the time unit for grouping origin and development periods</p>
</div>
""", unsafe_allow_html=True)

grain_options = {'Yearly': 'Y', 'Quarterly': 'Q', 'Monthly': 'M'}
selected_grain_label = st.selectbox("Select Grain:", options=list(grain_options.keys()), index=0)
selected_grain = grain_options[selected_grain_label]
st.caption(f"Selected grain: {selected_grain_label} ({selected_grain})")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        original_filename = uploaded_file.name
        base_filename = re.sub(r'\.[^.]*$', '', original_filename)

        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='cp1252')
                st.info("File read with Windows-1252 encoding.")
        else:
            df = pd.read_excel(uploaded_file)

        unnamed = [c for c in df.columns if c.startswith('Unnamed:')]
        if unnamed:
            df = df.drop(columns=unnamed)
            st.info(f"Dropped {len(unnamed)} unnamed column(s).")

        # Show available columns
        st.markdown("#### Preview of uploaded data")
        st.dataframe(df.head())
        
        # Show column names for debugging
        with st.expander("View available column names"):
            st.write(df.columns.tolist())
        
        st.markdown("---")

        # ============================================================
        # COLUMN MAPPING - ALL COLUMNS FROM USER SELECTION
        # ============================================================
        st.markdown("### Map Your Columns to Required Fields")
        
        all_columns = df.columns.tolist()
        
        # Loss Date and Report Date in two columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="required-container">
                <h3>Loss_Date</h3>
                <p>The date when the loss occurred (origin period)</p>
            </div>
            """, unsafe_allow_html=True)
            loss_date_col = st.selectbox("Select your Loss Date column", options=[""] + all_columns, key="loss_date")
            if loss_date_col == "": 
                loss_date_col = None
        
        with col2:
            st.markdown("""
            <div class="required-container">
                <h3>Report_Date</h3>
                <p>The date when the claim was reported (development period)</p>
            </div>
            """, unsafe_allow_html=True)
            report_date_col = st.selectbox("Select your Report Date column", options=[""] + all_columns, key="report_date")
            if report_date_col == "": 
                report_date_col = None

        st.markdown("---")
        
        # Index Columns Selection
        st.markdown("""
        <div class="grouping-container">
            <h3>📊 Index Columns (Grouping)</h3>
            <p>Select the columns you want to group by (e.g., Line_of_Business, Region).</p>
        </div>
        """, unsafe_allow_html=True)
        
        grouping_options = [col for col in all_columns if col not in [loss_date_col, report_date_col]]
        index_cols = st.multiselect(
            "Choose columns to group by (at least one required):",
            options=grouping_options,
            default=[]
        )
        
        if not index_cols:
            st.error("Please select at least one index (grouping) column.")
            st.stop()

        st.markdown("---")

        # Numeric columns selection
        st.markdown("### Select Numeric Columns (Claim Amounts)")
        
        numeric_options = [col for col in all_columns if col not in [loss_date_col, report_date_col] + index_cols]
        
        if not numeric_options:
            st.error("No numeric columns available. Please check your data.")
            st.stop()
        
        selected_value_cols = st.multiselect(
            "Choose the numeric columns (claim amounts) to analyze:",
            options=numeric_options,
            default=[]
        )

        if not selected_value_cols:
            st.warning("Please select at least one numeric column.")
            st.stop()

        # ============================================================
        # DATA QUALITY CHECKS
        # ============================================================
        st.markdown("### Data Quality Checks")
        
        all_selected_cols = [loss_date_col, report_date_col] + index_cols + selected_value_cols
        df_original_len = len(df)
        
        def clean_numeric(series):
            if series.dtype == 'object':
                cleaned = series.astype(str).str.replace(r'[$,€£]', '', regex=True)
                cleaned = cleaned.str.replace(r',', '', regex=False)
                cleaned = cleaned.str.replace(r'^\((.+)\)$', r'-\1', regex=True)
                cleaned = cleaned.str.strip()
                cleaned = cleaned.replace('', np.nan)
                return pd.to_numeric(cleaned, errors='coerce')
            else:
                return pd.to_numeric(series, errors='coerce')
        
        # 1. Missing Values Check
        st.markdown("#### 1. Missing Values Check")
        missing_in_selected = False
        for col in all_selected_cols:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    missing_in_selected = True
                    st.warning(f"Column '{col}' has {missing_count} missing value(s).")
        
        if missing_in_selected:
            st.error("❌ Missing values found. Please fix and re-upload.")
            st.stop()
        else:
            st.success("✅ No missing values found.")
        
        # 2. Duplicate Rows Check
        st.markdown("#### 2. Duplicate Rows Check")
        duplicate_count = len(df[df.duplicated()])
        if duplicate_count > 0:
            df = df.drop_duplicates()
            st.success(f"✅ Removed {duplicate_count} duplicate row(s).")
        else:
            st.success("✅ No duplicate rows found.")
        
        # 3. Date Reasonability Check
        st.markdown("#### 3. Date Reasonability Check")
        df['temp_loss'] = pd.to_datetime(df[loss_date_col], errors='coerce')
        df['temp_report'] = pd.to_datetime(df[report_date_col], errors='coerce')
        invalid_dates = df[df['temp_report'] < df['temp_loss']]
        
        if len(invalid_dates) > 0:
            st.error(f"❌ {len(invalid_dates)} rows have Report_Date before Loss_Date.")
            st.stop()
        else:
            st.success("✅ All dates valid (Report_Date >= Loss_Date).")
        
        # 4. Non-Numeric Values Check
        st.markdown("#### 4. Non-Numeric Values Check")
        for col in selected_value_cols:
            test_clean = clean_numeric(df[col])
            failed = test_clean.isna() & df[col].notna()
            if failed.sum() > 0:
                st.info(f"Converting {failed.sum()} non-numeric values in '{col}' to 0.")
                df[col] = clean_numeric(df[col]).fillna(0)
        
        st.success("✅ Data quality checks complete.")
        st.markdown("---")
        
        # ============================================================
        # PREPARE DATA FOR TRIANGLE - USING ONLY SELECTED COLUMNS
        # ============================================================
        
        # Build clean dataframe using only the selected column names
        df_clean = pd.DataFrame()
        df_clean['Loss_Date'] = pd.to_datetime(df[loss_date_col], errors='coerce')
        df_clean['Report_Date'] = pd.to_datetime(df[report_date_col], errors='coerce')
        
        for col in index_cols:
            df_clean[col] = df[col]
        
        for col in selected_value_cols:
            df_clean[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Filter by date range
        df_filtered = df_clean[
            (df_clean['Loss_Date'] >= from_date) & 
            (df_clean['Loss_Date'] <= to_date)
        ]
        
        if df_filtered.empty:
            st.error("No data found for selected period.")
            st.stop()
        
        st.success(f"**Filtered:** {len(df_filtered)} claims selected")
        
        # ============================================================
        # CREATE TRIANGLE - USING USER-SELECTED COLUMN NAMES
        # ============================================================
        try:
            triangle = cl.Triangle(
                data=df_filtered,
                origin='Loss_Date',
                development='Report_Date',
                columns=selected_value_cols,
                index=index_cols,
                cumulative=False,
                grain=selected_grain
            )
            st.success(f"Triangle created! Grain: {selected_grain_label}")
        except Exception as e:
            st.error(f"Triangle error: {str(e)}")
            st.stop()
        
        # ============================================================
        # FIT MODEL
        # ============================================================
        try:
            model = cl.Chainladder().fit(triangle)
            st.success("Model fitted successfully!")
        except Exception as e:
            st.error(f"Model error: {str(e)}")
            st.stop()
        
        # ============================================================
        # EXTRACT RESULTS
        # ============================================================
        ibnr = model.ibnr_
        ultimate = model.ultimate_
        ldfs = model.ldf_
        completed_triangle = model.full_triangle_
        
        # Convert to DataFrames
        ibnr_df = ibnr.to_frame().reset_index()
        ultimate_df = ultimate.to_frame().reset_index()
        ldfs_df = ldfs.to_frame()
        completed_df = completed_triangle.to_frame()
        
        # Aggregate by index columns
        ibnr_summary = ibnr_df.groupby(index_cols)[selected_value_cols].sum().reset_index()
        ultimate_summary = ultimate_df.groupby(index_cols)[selected_value_cols].sum().reset_index()
        
        # ============================================================
        # DISPLAY RESULTS
        # ============================================================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"IBNR Results: {from_date.date()} to {to_date.date()}")
        st.markdown(f"**Grain:** {selected_grain_label} | **Grouped by:** {', '.join(index_cols)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("IBNR Summary")
            display_ibnr = ibnr_summary.copy()
            for col in selected_value_cols:
                display_ibnr[col] = display_ibnr[col].apply(lambda x: f"{x:,.2f}")
            st.dataframe(display_ibnr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Ultimate Claims")
            display_ultimate = ultimate_summary.copy()
            for col in selected_value_cols:
                display_ultimate[col] = display_ultimate[col].apply(lambda x: f"{x:,.2f}")
            st.dataframe(display_ultimate, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Loss Development Factors (LDFs)")
        st.dataframe(ldfs_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ============================================================
        # EXPORT TO EXCEL
        # ============================================================
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            ibnr_summary.to_excel(writer, index=False, sheet_name='IBNR_Summary')
            ultimate_summary.to_excel(writer, index=False, sheet_name='Ultimate_Summary')
            ldfs_df.to_excel(writer, sheet_name='LDFs')
            completed_df.to_excel(writer, sheet_name='Completed_Triangle')
        
        output.seek(0)
        
        safe_client = re.sub(r'[\\/*?:"<>|]', "", client_name).strip() or "Client"
        safe_original = re.sub(r'[\\/*?:"<>|]', "", base_filename).strip() or "Data"
        file_name = f"{safe_client}_{safe_original}_IBNR_Results.xlsx"
        
        st.download_button(
            label="Download Excel Report",
            data=output,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check your file format and column selections.")

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("""
<div class="footer">
    <p>© 2026 African Actuarial Consultants. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
