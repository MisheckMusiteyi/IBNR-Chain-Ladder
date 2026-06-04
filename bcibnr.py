# -*- coding: utf-8 -*-
"""
Chain Ladder IBNR Calculator
Version: 5.0 - Fixed Chainladder output handling
"""

import streamlit as st
import pandas as pd
import numpy as np
import chainladder as cl
from io import BytesIO
from datetime import date
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Chain Ladder IBNR Calculator", layout="wide")

# ---------- CUSTOM CSS (African Actuarial Consultants theme) ----------
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #000000; font-family: 'Calisto MT', serif; font-size: 11pt; }
    body, p, h1, h2, h3, h4, h5, h6, div, span, label, .stMarkdown, 
    .stTextInput label, .stDateInput label, .stSelectbox label, .stMultiSelect label,
    .stButton button, .stDownloadButton button, .stFileUploader label,
    .stAlert, .stInfo, .stWarning, .stError, .stSuccess, .stSpinner, 
    .stProgress, .stToast, .stSidebar, .stMetric {
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
    }
    .nav-links a:hover { color: #D4AF37; }
    .hero {
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        color: #FFFFFF;
        padding: 2rem 2rem;
        text-align: center;
        border-bottom: 3px solid #D4AF37;
    }
    .hero h1 { color: #D4AF37; font-size: 2.5rem; margin-bottom: 0.5rem; }
    .hero p { font-size: 1.2rem; max-width: 800px; margin: 0 auto; }
    .main-container { max-width: 1400px; margin: 2rem auto; padding: 0 2rem; }
    .required-container, .grouping-container, .date-range-container, .grain-container {
        background-color: #F9F9F9;
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .required-container h3, .grouping-container h3, .date-range-container h3, .grain-container h3 {
        color: #D4AF37;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
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
    .card h3 { color: #D4AF37; border-bottom: 2px solid #D4AF37; padding-bottom: 0.5rem; }
    .footer {
        background-color: #000000;
        color: #FFFFFF;
        text-align: center;
        padding: 1.5rem;
        border-top: 3px solid #D4AF37;
        margin-top: 3rem;
    }
    .footer a { color: #D4AF37; text-decoration: none; }
    .stButton > button, .stDownloadButton > button {
        background-color: #D4AF37;
        color: #000000;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #B8960F;
        color: #FFFFFF;
    }
    .stFileUploader { border: 2px dashed #D4AF37; border-radius: 5px; padding: 1rem; }
    .stMultiSelect [data-baseweb="select"], .stSelectbox [data-baseweb="select"] {
        border: 1px solid #D4AF37;
        border-radius: 4px;
    }
    .dataframe { border: 1px solid #D4AF37; border-radius: 8px; overflow: hidden; }
    .data-check-container { background-color: #E3F2FD; border: 2px solid #2196F3; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }
    .data-check-error { background-color: #FFEBEE; border: 2px solid #F44336; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }
    .stSelectbox div[data-baseweb="select"] { width: 100%; }
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
    <p>Upload your claims data. Map your columns, select period, grain, and value columns.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Main Container ----------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# User inputs
col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name (for file name)", value="Client").strip()
with col2:
    pass

# IBNR Period
st.markdown("""
<div class="date-range-container">
    <h3>📅 IBNR Period</h3>
    <p>Select date range based on Loss Date</p>
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

# Grain Selection
st.markdown("""
<div class="grain-container">
    <h3>📊 Triangle Grain</h3>
    <p>Select time unit for grouping periods</p>
</div>
""", unsafe_allow_html=True)

grain_map = {'Yearly': 'Y', 'Quarterly': 'Q', 'Monthly': 'M'}
grain_label = st.selectbox("Select Grain:", options=list(grain_map.keys()), index=0)
grain = grain_map[grain_label]

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        original_filename = uploaded_file.name
        base_filename = re.sub(r'\.[^.]*$', '', original_filename)

        # Read file
        ext = uploaded_file.name.split('.')[-1].lower()
        if ext == 'csv':
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='cp1252')
        else:
            df = pd.read_excel(uploaded_file)

        # Clean column names
        df.columns = df.columns.astype(str).str.strip()
        
        # Drop unnamed columns
        unnamed = [c for c in df.columns if c.lower().startswith('unnamed')]
        if unnamed:
            df = df.drop(columns=unnamed)
            st.info(f"Removed {len(unnamed)} unnamed column(s).")

        st.markdown("#### Preview of uploaded data")
        st.dataframe(df.head())
        st.markdown("---")

        # --- COLUMN MAPPING ---
        st.markdown("### Map Your Columns")
        all_cols = df.columns.tolist()

        st.markdown("""
        <div class="required-container">
            <h3>Loss_Date</h3>
            <p>Date when loss occurred</p>
        </div>
        """, unsafe_allow_html=True)
        loss_col = st.selectbox("Loss Date column", options=[""] + all_cols, label_visibility="collapsed")
        if not loss_col:
            st.stop()

        st.markdown("""
        <div class="required-container">
            <h3>Report_Date</h3>
            <p>Date when claim was reported</p>
        </div>
        """, unsafe_allow_html=True)
        report_col = st.selectbox("Report Date column", options=[""] + all_cols, label_visibility="collapsed")
        if not report_col:
            st.stop()

        st.markdown("---")

        st.markdown("""
        <div class="required-container">
            <h3>📊 Grouping Column</h3>
            <p>Select column to group by (e.g., Line_of_Business)</p>
        </div>
        """, unsafe_allow_html=True)
        
        group_options = [c for c in all_cols if c not in [loss_col, report_col]]
        group_col = st.selectbox("Group by column:", options=[""] + group_options, label_visibility="collapsed")
        if not group_col:
            st.error("Select a grouping column.")
            st.stop()

        st.markdown("---")
        st.markdown("### Select Numeric Columns (Claim Amounts)")
        num_options = [c for c in all_cols if c not in [loss_col, report_col, group_col]]
        
        value_cols = st.multiselect("Numeric columns:", options=num_options)
        
        if not value_cols:
            st.error("Select at least one numeric column.")
            st.stop()

        st.write(f"Selected numeric columns: {value_cols}")

        # --- PROCESS DATA ---
        df[loss_col] = pd.to_datetime(df[loss_col], errors='coerce')
        df[report_col] = pd.to_datetime(df[report_col], errors='coerce')
        
        # Filter by date range
        df_filtered = df[(df[loss_col] >= from_date) & (df[loss_col] <= to_date)].copy()
        
        if df_filtered.empty:
            st.error("No data for selected period.")
            st.stop()
        
        st.success(f"✅ Filtered: {len(df_filtered)} claims")

        # --- DATA QUALITY CHECKS ---
        st.markdown("### Data Quality Checks")
        
        # Check missing values
        missing = []
        for col in [loss_col, report_col, group_col] + value_cols:
            cnt = df_filtered[col].isna().sum()
            if cnt > 0:
                missing.append(f"{col} ({cnt})")
        
        if missing:
            st.markdown(f'<div class="data-check-error">❌ Missing values: {", ".join(missing)}</div>', unsafe_allow_html=True)
            st.stop()
        
        # Check date reasonability
        invalid = df_filtered[df_filtered[report_col] < df_filtered[loss_col]]
        if len(invalid) > 0:
            st.markdown(f'<div class="data-check-error">❌ {len(invalid)} rows with Report Date before Loss Date</div>', unsafe_allow_html=True)
            st.stop()
        
        # Remove duplicates
        dup_count = df_filtered.duplicated().sum()
        if dup_count > 0:
            df_filtered = df_filtered.drop_duplicates()
            st.markdown(f'<div class="data-check-warning">⚠️ Removed {dup_count} duplicate rows</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-check-container">✅ No duplicates found</div>', unsafe_allow_html=True)
        
        # Clean numeric values
        def clean_numeric_series(series):
            if series.dtype == 'object':
                cleaned = series.astype(str).str.replace(r'[$,€£]', '', regex=True)
                cleaned = cleaned.str.replace(r',', '', regex=False)
                cleaned = cleaned.str.replace(r'^\((.+)\)$', r'-\1', regex=True)
                cleaned = cleaned.str.strip().replace('', '0')
                return pd.to_numeric(cleaned, errors='coerce').fillna(0)
            return pd.to_numeric(series, errors='coerce').fillna(0)
        
        for col in value_cols:
            df_filtered[col] = clean_numeric_series(df_filtered[col])
        
        st.markdown('<div class="data-check-container">✅ Data quality checks passed</div>', unsafe_allow_html=True)
        st.markdown("---")

        # --- CREATE TRIANGLE AND CALCULATE IBNR ---
        all_ibnr_results = []
        
        for claim_col in value_cols:
            st.write(f"**Processing: {claim_col}**")
            
            with st.spinner(f"Calculating IBNR for {claim_col}..."):
                # Create triangle
                triangle = cl.Triangle(
                    data=df_filtered,
                    origin=loss_col,
                    development=report_col,
                    columns=claim_col,
                    index=group_col,
                    cumulative=False,
                    grain=grain
                )
                
                # Fit model
                model = cl.Chainladder().fit(triangle)
                
                # IBNR is directly available from model
                ibnr_result = model.ibnr_
                
                # Convert to DataFrame
                ibnr_df = ibnr_result.to_frame().reset_index()
                
                # The output has columns: [group_col, 'origin', 'values']
                # Sum by group_col to get total IBNR per line of business
                ibnr_summary = ibnr_df.groupby(group_col)['values'].sum().reset_index()
                ibnr_summary.columns = [group_col, claim_col]
                
                all_ibnr_results.append(ibnr_summary)
                
                # Store first model for LDFs and triangle display
                if claim_col == value_cols[0]:
                    first_model = model
                    first_ibnr_detail = ibnr_df
        
        # Combine results from all numeric columns
        if len(value_cols) > 1:
            final_results = all_ibnr_results[0]
            for res in all_ibnr_results[1:]:
                final_results = final_results.merge(res, on=group_col, how='outer')
        else:
            final_results = all_ibnr_results[0]
        
        # --- DISPLAY RESULTS ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"IBNR Results for Period: {from_date.date()} to {to_date.date()}")
        st.markdown(f"**Grain:** {grain_label} | **Grouped by:** {group_col}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display IBNR summary
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("IBNR Summary by Line of Business")
        
        # Format currency
        display_summary = final_results.copy()
        for col in display_summary.columns:
            if col != group_col:
                display_summary[col] = display_summary[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
        
        st.dataframe(display_summary, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display detailed IBNR by accident year
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Detailed IBNR by Accident Year")
        
        if 'first_ibnr_detail' in locals():
            detail_display = first_ibnr_detail.copy()
            detail_display['IBNR'] = detail_display['values'].apply(lambda x: f"{x:,.2f}")
            detail_display = detail_display.drop(columns=['values'])
            st.dataframe(detail_display, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display LDFs
        if 'first_model' in locals():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Loss Development Factors")
            ldfs_df = first_model.ldf_.to_frame()
            st.dataframe(ldfs_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # --- EXPORT TO EXCEL ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            final_results.to_excel(writer, index=False, sheet_name='IBNR_Summary')
            if 'first_ibnr_detail' in locals():
                first_ibnr_detail.to_excel(writer, index=False, sheet_name='IBNR_Detailed')
            if 'first_model' in locals():
                first_model.ldf_.to_frame().to_excel(writer, sheet_name='LDFs')
                first_model.full_triangle_.to_frame().to_excel(writer, sheet_name='Completed_Triangle')
        
        output.seek(0)
        
        safe_client = re.sub(r'[\\/*?:"<>|]', "", client_name).strip() or "Client"
        safe_original = re.sub(r'[\\/*?:"<>|]', "", base_filename).strip() or "Data"
        file_name = f"{safe_client}_{safe_original}_IBNR_Results_{from_date.year}_{to_date.year}.xlsx"
        
        st.markdown("### Download Results")
        st.download_button("📥 Download Excel Report", data=output, file_name=file_name)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write("Please check your file format and column selections.")
        logger.exception("Application error")

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("""
<div class="footer">
    <p>© 2026 African Actuarial Consultants. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
