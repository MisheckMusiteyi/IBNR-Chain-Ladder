# -*- coding: utf-8 -*-
"""
Chain Ladder IBNR Calculator
Version: 14.0 - Using your exact manual workflow
"""

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
    <h3>IBNR Period</h3>
    <p>Select date range based on Loss Date</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input("From Date", value=date(2021, 1, 1))
    st.caption("Claims with Loss Date on or after this date")
with col2:
    to_date = st.date_input("To Date", value=date(2025, 12, 31))
    st.caption("Claims with Loss Date on or before this date")

from_date = pd.to_datetime(from_date)
to_date = pd.to_datetime(to_date)

st.info(f"**Selected IBNR Period:** {from_date.date()} to {to_date.date()}")

# Grain Selection
st.markdown("""
<div class="grain-container">
    <h3>Triangle Grain</h3>
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

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="required-container">
                <h3>Loss_Date</h3>
                <p>Date when loss occurred</p>
            </div>
            """, unsafe_allow_html=True)
            loss_col = st.selectbox("Loss Date column", options=[""] + all_cols, label_visibility="collapsed")
        
        with col2:
            st.markdown("""
            <div class="required-container">
                <h3>Report_Date</h3>
                <p>Date when claim was reported</p>
            </div>
            """, unsafe_allow_html=True)
            report_col = st.selectbox("Report Date column", options=[""] + all_cols, label_visibility="collapsed")
        
        with col3:
            st.markdown("""
            <div class="required-container">
                <h3>Line_of_Business</h3>
                <p>Grouping column (e.g., Motor, Property, Health)</p>
            </div>
            """, unsafe_allow_html=True)
            lob_col = st.selectbox("Line of Business column", options=[""] + all_cols, label_visibility="collapsed")

        if not loss_col or not report_col or not lob_col:
            st.error("Please select all required columns.")
            st.stop()

        st.markdown("---")
        st.markdown("### Select Claim Amount Column")
        
        amount_options = [c for c in all_cols if c not in [loss_col, report_col, lob_col]]
        amount_col = st.selectbox("Claim amount column:", options=[""] + amount_options, label_visibility="collapsed")
        
        if not amount_col:
            st.error("Select a claim amount column.")
            st.stop()

        st.write(f"Selected claim amount column: **{amount_col}**")

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
        for col in [loss_col, report_col, lob_col, amount_col]:
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
        if df_filtered[amount_col].dtype == 'object':
            cleaned = df_filtered[amount_col].astype(str).str.replace(r'[$,€£]', '', regex=True)
            cleaned = cleaned.str.replace(r',', '', regex=False)
            cleaned = cleaned.str.replace(r'^\((.+)\)$', r'-\1', regex=True)
            cleaned = cleaned.str.strip().replace('', '0')
            df_filtered[amount_col] = pd.to_numeric(cleaned, errors='coerce').fillna(0)
        
        st.markdown('<div class="data-check-container">✅ Data quality checks passed</div>', unsafe_allow_html=True)
        st.markdown("---")

        # --- CREATE TRIANGLE AND RUN CHAIN LADDER (EXACTLY LIKE YOUR MANUAL WORKFLOW) ---
        with st.spinner("Creating triangle and running Chain Ladder..."):
            triangle = cl.Triangle(
                data=df_filtered,
                origin=loss_col,
                development=report_col,
                columns=amount_col,
                index=lob_col,
                cumulative=False,
                grain=grain
            )
            
            model = cl.Chainladder().fit(triangle)
            st.success("✅ Model fitted successfully!")

        # --- EXACTLY YOUR MANUAL WORKFLOW FOR IBNR ---
        # Step 1: Get IBNR (like your ibnr = cl_model.ibnr_)
        ibnr = model.ibnr_
        
        # Step 2: Display IBNR by accident year (like your display(ibnr.to_frame()))
        ibnr_df = ibnr.to_frame()
        
        # Step 3: Create summary by Line of Business (like your ibnr_df.sum(axis=1).to_frame(name=currency_columns[0]))
        # currency_columns[0] is the user's selected amount column
        ibnr_summary_df = ibnr_df.sum(axis=1).to_frame(name=amount_col)
        
        # Reset index to make Line_of_Business a column
        ibnr_summary_df = ibnr_summary_df.reset_index()
        ibnr_summary_df = ibnr_summary_df.rename(columns={'index': lob_col})


        # Also reset index for detailed view
        ibnr_detailed_df = ibnr_df.reset_index()
        # Rename 'values' to the user's amount column name, and 'origin' to 'AccidentYear'
        ibnr_detailed_df = ibnr_detailed_df.rename(columns={'values': amount_col, 'origin': 'AccidentYear', 'index': lob_col})
        
        # Also reset index for detailed view
        #ibnr_detailed_df = ibnr_df.reset_index()
        #ibnr_detailed_df = ibnr_detailed_df.rename(columns={'index': lob_col, 'values': amount_col, 'origin': 'AccidentYear'})

        # --- DISPLAY RESULTS ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"IBNR Results for Period: {from_date.date()} to {to_date.date()}")
        st.markdown(f"**Grain:** {grain_label}")
        st.markdown(f"**Grouped by:** {lob_col}")
        st.markdown(f"**Claim Amount Column:** {amount_col}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display IBNR Summary
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"IBNR Summary by {lob_col}")
        display_summary = ibnr_summary_df.copy()
        display_summary[amount_col] = display_summary[amount_col].apply(lambda x: f"{x:,.2f}")
        st.dataframe(display_summary, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display IBNR by Accident Year
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("IBNR by Accident Year")
        display_detailed = ibnr_detailed_df.copy()
        display_detailed[amount_col] = display_detailed[amount_col].apply(lambda x: f"{x:,.2f}")
        st.dataframe(display_detailed, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display ultimate triangle
        ultimate_df = model.ultimate_.to_frame()
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Ultimate Claims Triangle")
        st.dataframe(ultimate_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display LDFs
        ldfs_df = model.ldf_.to_frame()
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Loss Development Factors")
        st.dataframe(ldfs_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- EXPORT TO EXCEL ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            ibnr_summary_df.to_excel(writer, index=False, sheet_name='IBNR_Summary')
            ibnr_detailed_df.to_excel(writer, index=False, sheet_name='IBNR_Detailed')
            ultimate_df.reset_index().to_excel(writer, index=False, sheet_name='Ultimate_Triangle')
            ldfs_df.to_excel(writer, sheet_name='LDFs')
            model.full_triangle_.to_frame().to_excel(writer, sheet_name='Completed_Triangle')
        
        output.seek(0)
        
        safe_client = re.sub(r'[\\/*?:"<>|]', "", client_name).strip() or "Client"
        safe_original = re.sub(r'[\\/*?:"<>|]', "", base_filename).strip() or "Data"
        file_name = f"{safe_client}_{safe_original}_IBNR_Results_{from_date.year}_{to_date.year}.xlsx"
        
        st.markdown("### Download Results")
        st.download_button("📥 Download Excel Report", data=output, file_name=file_name)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write("Please check your file format and column selections.")
        import traceback
        st.write(traceback.format_exc())

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("""
<div class="footer">
    <p>© 2026 African Actuarial Consultants. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
