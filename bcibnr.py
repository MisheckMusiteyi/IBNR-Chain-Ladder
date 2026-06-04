# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import chainladder as cl
from io import BytesIO
from datetime import date
import re

st.set_page_config(page_title="Chain Ladder IBNR Calculator", layout="wide")

# ---------- CUSTOM CSS (African Actuarial Consultants theme) ----------
st.markdown("""
<style>
    /* Global */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: 'Calisto MT', serif;
        font-size: 11pt;
    }
    
    /* Apply Calisto MT to all text elements */
    body, p, h1, h2, h3, h4, h5, h6, div, span, label, .stMarkdown, 
    .stTextInput label, .stDateInput label, .stSelectbox label, .stMultiSelect label,
    .stButton button, .stDownloadButton button, .stFileUploader label,
    .stAlert, .stInfo, .stWarning, .stError, .stSuccess, .stSpinner, 
    .stProgress, .stToast, .stSidebar, .stMetric, .stExpander {
        font-family: 'Calisto MT', serif !important;
    }
    
    /* Header / Navigation */
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
    
    /* Hero Section */
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
    
    /* Main container */
    .main-container {
        max-width: 1400px;
        margin: 2rem auto;
        padding: 0 2rem;
    }
    
    /* Required Column Containers */
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
    
    /* Grouping Container */
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
    
    /* Date Range Container */
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
    
    /* Grain Container */
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
    
    /* Cards */
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
    
    /* Footer */
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
    
    /* Streamlit element overrides */
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
    
    /* Data Check Containers */
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
    
    /* Fix for select box container */
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
    <p>Upload your claims data (CSV or Excel). Map your columns, select the IBNR period, choose grain, and select value columns. The app computes IBNR, Ultimate claims, LDFs, and completed triangles.</p>
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
    <h3>IBNR Period</h3>
    <p>Select the date range for claims to be included in the IBNR calculation (based on Loss Date)</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input("From Date (Start of IBNR Period)", value=date(2020, 1, 1))
    st.caption("Claims with Loss Date on or after this date")
with col2:
    to_date = st.date_input("To Date (End of IBNR Period)", value=date(2024, 12, 31))
    st.caption("Claims with Loss Date on or before this date")

from_date = pd.to_datetime(from_date)
to_date = pd.to_datetime(to_date)

st.info(f"**Selected IBNR Period:** {from_date.date()} to {to_date.date()}")

# --- Grain Selection ---
st.markdown("""
<div class="grain-container">
    <h3>Triangle Grain</h3>
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

        # Read file based on extension
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

        # Drop unnamed columns
        unnamed = [c for c in df.columns if c.startswith('Unnamed:')]
        if unnamed:
            df = df.drop(columns=unnamed)
            st.info(f"Dropped {len(unnamed)} unnamed column(s).")

        # Preview
        st.markdown("#### Preview of uploaded data")
        st.dataframe(df.head())
        st.markdown("---")

        # --- Column Mapping Section ---
        st.markdown("### Map Your Columns to Required Fields")
        st.markdown("The calculator requires the following columns. For each required column, select the corresponding column from your uploaded data:")

        all_columns = df.columns.tolist()
        
        # Display available columns for debugging
        with st.expander("View available column names in your file"):
            st.write(all_columns)

        # Loss Date column
        st.markdown("""
        <div class="required-container">
            <h3>Loss_Date</h3>
            <p>The date when the loss occurred (origin period)</p>
        </div>
        """, unsafe_allow_html=True)
        loss_col = st.selectbox("Select your Loss Date column", options=[""] + all_columns, key="loss_date", label_visibility="collapsed")
        if not loss_col:
            st.error("Please select a Loss Date column.")
            st.stop()
        
        # Report Date column
        st.markdown("""
        <div class="required-container">
            <h3>Report_Date</h3>
            <p>The date when the claim was reported (development period)</p>
        </div>
        """, unsafe_allow_html=True)
        report_col = st.selectbox("Select your Report Date column", options=[""] + all_columns, key="report_date", label_visibility="collapsed")
        if not report_col:
            st.error("Please select a Report Date column.")
            st.stop()

        st.markdown("---")
        
        # Index Columns Selection
        st.markdown("""
        <div class="grouping-container">
            <h3>Index Columns (Grouping)</h3>
            <p>Select the columns you want to group by (e.g., Line_of_Business, Region). Results will be aggregated by these columns.</p>
        </div>
        """, unsafe_allow_html=True)
        
        grouping_options = [col for col in all_columns if col not in [loss_col, report_col]]
        index_cols = st.multiselect(
            "Choose columns to group by (at least one required):",
            options=grouping_options,
            default=[],
            help="Select one or more columns. The IBNR results will be aggregated by these columns."
        )
        
        if not index_cols:
            st.error("Please select at least one index (grouping) column.")
            st.stop()

        st.markdown("---")

        # Numeric columns selection
        st.markdown("### Select Numeric Columns (Claim Amounts)")
        st.markdown("Select which numeric columns contain claim amounts to run Chain Ladder on:")
        
        numeric_options = [col for col in all_columns if col not in [loss_col, report_col] + index_cols]
        
        if not numeric_options:
            st.error("No numeric columns available. Please check your data.")
            st.stop()
        
        value_cols = st.multiselect(
            "Choose the numeric columns (claim amounts) to analyze:",
            options=numeric_options,
            default=[]
        )

        if not value_cols:
            st.warning("Please select at least one numeric column.")
            st.stop()

        # ============================================================
        # STEP 1: FILTER BY DATE RANGE FIRST
        # ============================================================
        st.markdown("### Data Processing")
        
        # Convert dates using the selected column names
        df[loss_col] = pd.to_datetime(df[loss_col], errors='coerce')
        df[report_col] = pd.to_datetime(df[report_col], errors='coerce')
        
        # Filter by the selected IBNR period
        df_filtered = df[
            (df[loss_col] >= from_date) & 
            (df[loss_col] <= to_date)
        ].copy()
        
        if df_filtered.empty:
            st.error(f"No data found for the selected IBNR period: {from_date.date()} to {to_date.date()}")
            st.stop()
        
        st.success(f"Filtered to {len(df_filtered)} claims for the period {from_date.date()} to {to_date.date()}")
        
        # ============================================================
        # STEP 2: DATA QUALITY CHECKS ON FILTERED DATA
        # ============================================================
        st.markdown("### Data Quality Checks")
        
        errors_found = False
        
        # 1. Missing Values Check
        st.markdown("#### 1. Missing Values Check")
        missing_cols = []
        for col in [loss_col, report_col] + index_cols + value_cols:
            missing_count = df_filtered[col].isna().sum()
            if missing_count > 0:
                missing_cols.append(f"{col} ({missing_count} missing)")
                errors_found = True
        
        if missing_cols:
            st.markdown(f"""
            <div class="data-check-error">
                <b>Missing values found in:</b> {', '.join(missing_cols)}<br>
                Please fix missing values and re-upload.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-check-container">No missing values found.</div>', unsafe_allow_html=True)
        
        # 2. Date Reasonability Check
        st.markdown("#### 2. Date Reasonability Check")
        invalid_dates = df_filtered[df_filtered[report_col] < df_filtered[loss_col]]
        if len(invalid_dates) > 0:
            errors_found = True
            st.markdown(f"""
            <div class="data-check-error">
                <b>Found {len(invalid_dates)} rows where Report Date is before Loss Date.</b><br>
                Please fix these dates and re-upload.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-check-container">All dates valid (Report Date >= Loss Date).</div>', unsafe_allow_html=True)
        
        # 3. Duplicate Rows Check
        st.markdown("#### 3. Duplicate Rows Check")
        duplicate_count = df_filtered.duplicated().sum()
        if duplicate_count > 0:
            df_filtered = df_filtered.drop_duplicates()
            st.markdown(f"""
            <div class="data-check-warning">
                <b>Removed {duplicate_count} duplicate rows.</b><br>
                {len(df_filtered)} rows remaining.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-check-container">No duplicate rows found.</div>', unsafe_allow_html=True)
        
        # 4. Numeric Values Check
        st.markdown("#### 4. Numeric Values Check")
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
        
        for col in value_cols:
            df_filtered[col] = clean_numeric(df_filtered[col]).fillna(0)
        
        st.markdown('<div class="data-check-container">Numeric values cleaned and converted.</div>', unsafe_allow_html=True)
        
        # Stop if critical errors found
        if errors_found:
            st.stop()
        
        st.markdown("---")
        
        # ============================================================
        # STEP 3: CREATE TRIANGLE AND RUN CHAIN LADDER
        # ============================================================
        st.markdown("### Running Chain Ladder Calculation")
        
        # Prepare data for triangle
        triangle_df = df_filtered[[loss_col, report_col] + index_cols + value_cols].copy()
        
        # Create triangle
        with st.spinner("Creating triangle..."):
            try:
                triangle = cl.Triangle(
                    data=triangle_df,
                    origin=loss_col,
                    development=report_col,
                    columns=value_cols,
                    index=index_cols,
                    cumulative=False,
                    grain=selected_grain
                )
                st.success(f"Triangle created successfully! Grain: {selected_grain_label}")
            except Exception as e:
                st.error(f"Triangle creation error: {str(e)}")
                st.stop()
        
        # Fit Chain Ladder model
        with st.spinner("Fitting Chain Ladder model..."):
            try:
                model = cl.Chainladder().fit(triangle)
                st.success("Chain Ladder model fitted successfully!")
            except Exception as e:
                st.error(f"Model fitting error: {str(e)}")
                st.stop()
        
        # ============================================================
        # STEP 4: EXTRACT AND DISPLAY RESULTS
        # ============================================================
        
        # Extract results
        ibnr = model.ibnr_.to_frame().reset_index()
        ultimate = model.ultimate_.to_frame().reset_index()
        ldfs = model.ldf_.to_frame()
        completed_triangle = model.full_triangle_.to_frame()
        
        # Aggregate by index columns
        ibnr_summary = ibnr.groupby(index_cols)[value_cols].sum().reset_index()
        ultimate_summary = ultimate.groupby(index_cols)[value_cols].sum().reset_index()
        
        # Display results
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"IBNR Results for Period: {from_date.date()} to {to_date.date()}")
        st.markdown(f"**Grain:** {selected_grain_label} | **Grouped by:** {', '.join(index_cols)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("IBNR by " + ", ".join(index_cols))
            display_ibnr = ibnr_summary.copy()
            for col in value_cols:
                display_ibnr[col] = display_ibnr[col].apply(lambda x: f"{x:,.2f}")
            st.dataframe(display_ibnr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Ultimate Claims by " + ", ".join(index_cols))
            display_ultimate = ultimate_summary.copy()
            for col in value_cols:
                display_ultimate[col] = display_ultimate[col].apply(lambda x: f"{x:,.2f}")
            st.dataframe(display_ultimate, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display LDFs
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Loss Development Factors (LDFs)")
        st.dataframe(ldfs, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ============================================================
        # STEP 5: EXPORT TO EXCEL
        # ============================================================
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            ibnr_summary.to_excel(writer, index=False, sheet_name='IBNR_Summary')
            ultimate_summary.to_excel(writer, index=False, sheet_name='Ultimate_Summary')
            ldfs.to_excel(writer, sheet_name='LDFs')
            completed_triangle.to_excel(writer, sheet_name='Completed_Triangle')
        
        output.seek(0)
        
        safe_client = re.sub(r'[\\/*?:"<>|]', "", client_name).strip() or "Client"
        safe_original = re.sub(r'[\\/*?:"<>|]', "", base_filename).strip() or "Data"
        file_name = f"{safe_client}_{safe_original}_IBNR_Results_{from_date.year}_{to_date.year}.xlsx"
        
        st.markdown("### Download Results")
        st.download_button(
            label="📥 Download Excel Report (IBNR, Ultimate, LDFs, Triangles)",
            data=output,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.write("Please check your file format and column selections.")

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("""
<div class="footer">
    <p>© 2026 African Actuarial Consultants. All rights reserved. | <a href="#">Privacy</a> | <a href="#">Terms</a></p>
    <p style="margin-top: 0.5rem; font-size: 0.9rem;">Powered by Vanababa</p>
</div>
""", unsafe_allow_html=True)
