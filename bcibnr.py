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
    }
    .hero p {
        font-size: 1.2rem;
        max-width: 800px;
        margin: 0 auto;
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
        min-height: 100px;
        height: auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        width: 100%;
        margin-bottom: 1rem;
    }
    .required-container h3 {
        color: #D4AF37;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
    .required-container p {
        color: #666666;
        font-size: 0.8rem;
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
        font-size: 1.1rem;
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
        font-size: 1.1rem;
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
    .card h3 {
        color: #D4AF37;
        margin-top: 0;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 0.5rem;
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
    }
    
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
    <p>Upload your claims data. Map your columns, select period, grain, and value columns.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Main Container ----------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name (for file name)", value="Client").strip()
with col2:
    pass

# --- IBNR Period ---
st.markdown("""
<div class="date-range-container">
    <h3>📅 IBNR Period</h3>
    <p>Select date range based on Loss Date</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input("From Date", value=date(2020, 1, 1))
with col2:
    to_date = st.date_input("To Date", value=date(2024, 12, 31))

from_date = pd.to_datetime(from_date)
to_date = pd.to_datetime(to_date)

st.info(f"**Selected IBNR Period:** {from_date.date()} to {to_date.date()}")

# --- Grain ---
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

        ext = uploaded_file.name.split('.')[-1].lower()
        if ext == 'csv':
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='cp1252')
        else:
            df = pd.read_excel(uploaded_file)

        df = df.drop(columns=[c for c in df.columns if c.startswith('Unnamed:')])

        st.markdown("#### Preview")
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
        <div class="grouping-container">
            <h3>📊 Grouping Columns</h3>
            <p>Select columns to group by (e.g., Line_of_Business)</p>
        </div>
        """, unsafe_allow_html=True)
        
        group_options = [c for c in all_cols if c not in [loss_col, report_col]]
        index_cols = st.multiselect("Group by:", options=group_options)
        if not index_cols:
            st.error("Select at least one grouping column.")
            st.stop()

        st.markdown("---")
        st.markdown("### Select Numeric Columns (Claim Amounts)")
        num_options = [c for c in all_cols if c not in [loss_col, report_col] + index_cols]
        value_cols = st.multiselect("Numeric columns:", options=num_options)
        if not value_cols:
            st.error("Select at least one numeric column.")
            st.stop()

        # --- PROCESS ---
        df[loss_col] = pd.to_datetime(df[loss_col], errors='coerce')
        df[report_col] = pd.to_datetime(df[report_col], errors='coerce')
        
        df_filtered = df[(df[loss_col] >= from_date) & (df[loss_col] <= to_date)].copy()
        
        if df_filtered.empty:
            st.error("No data for selected period.")
            st.stop()
        
        st.success(f"✅ Filtered: {len(df_filtered)} claims")

        # Data checks
        st.markdown("### Data Quality Checks")
        
        missing = [c for c in [loss_col, report_col] + index_cols + value_cols if df_filtered[c].isna().sum() > 0]
        if missing:
            st.markdown(f'<div class="data-check-error">❌ Missing values in: {", ".join(missing)}</div>', unsafe_allow_html=True)
            st.stop()
        
        invalid = df_filtered[df_filtered[report_col] < df_filtered[loss_col]]
        if len(invalid) > 0:
            st.markdown(f'<div class="data-check-error">❌ {len(invalid)} rows with Report Date before Loss Date</div>', unsafe_allow_html=True)
            st.stop()
        
        dup = df_filtered.duplicated().sum()
        if dup > 0:
            df_filtered = df_filtered.drop_duplicates()
            st.markdown(f'<div class="data-check-warning">⚠️ Removed {dup} duplicates</div>', unsafe_allow_html=True)
        
        def clean_numeric(series):
            if series.dtype == 'object':
                cleaned = series.astype(str).str.replace(r'[$,€£]', '', regex=True)
                cleaned = cleaned.str.replace(r',', '', regex=False)
                cleaned = cleaned.str.replace(r'^\((.+)\)$', r'-\1', regex=True)
                cleaned = cleaned.str.strip().replace('', np.nan)
                return pd.to_numeric(cleaned, errors='coerce')
            return pd.to_numeric(series, errors='coerce')
        
        for col in value_cols:
            df_filtered[col] = clean_numeric(df_filtered[col]).fillna(0)
        
        st.markdown('<div class="data-check-container">✅ Data quality checks passed</div>', unsafe_allow_html=True)
        st.markdown("---")

        # --- FIXED: PROPERLY EXTRACT CHAINLADDER RESULTS ---
        with st.spinner("Running Chain Ladder..."):
            triangle = cl.Triangle(
                data=df_filtered,
                origin=loss_col,
                development=report_col,
                columns=value_cols,
                index=index_cols,
                cumulative=False,
                grain=grain
            )
            model = cl.Chainladder().fit(triangle)
            st.success("✅ Model fitted successfully!")

        # --- FIXED RESULTS PROCESSING ---
        # Chainladder returns results with 'value' column, not original column names
        ibnr = model.ibnr_.to_frame().reset_index()
        ultimate = model.ultimate_.to_frame().reset_index()
        ldfs = model.ldf_.to_frame()
        completed = model.full_triangle_.to_frame()

        # Display column structure for debugging (optional, remove after testing)
        with st.expander("Debug: View IBNR column structure"):
            st.write("IBNR columns:", ibnr.columns.tolist())
            st.write("Ultimate columns:", ultimate.columns.tolist())

        # The value column contains the actual IBNR amounts
        # We need to pivot or group appropriately
        
        # For IBNR and Ultimate, the DataFrame has columns: index_cols + ['origin', 'development', 'value']
        # We want to sum by index_cols across all origins and developments
        
        if len(value_cols) == 1:
            # Single value column - simpler
            ibnr_summary = ibnr.groupby(index_cols)['value'].sum().reset_index()
            ibnr_summary.rename(columns={'value': value_cols[0]}, inplace=True)
            
            ultimate_summary = ultimate.groupby(index_cols)['value'].sum().reset_index()
            ultimate_summary.rename(columns={'value': value_cols[0]}, inplace=True)
        else:
            # Multiple value columns - need to handle the structure
            # The 'columns' dimension becomes a level in the index or separate column
            # Let's inspect and handle dynamically
            if 'columns' in ibnr.columns:
                # Pivot the data
                ibnr_summary = ibnr.pivot_table(
                    index=index_cols, 
                    columns='columns', 
                    values='value', 
                    aggfunc='sum'
                ).reset_index()
                ibnr_summary.columns.name = None
                
                ultimate_summary = ultimate.pivot_table(
                    index=index_cols, 
                    columns='columns', 
                    values='value', 
                    aggfunc='sum'
                ).reset_index()
                ultimate_summary.columns.name = None
            else:
                # Fallback: sum all values
                ibnr_summary = ibnr.groupby(index_cols)['value'].sum().reset_index()
                ibnr_summary.rename(columns={'value': 'Total_IBNR'}, inplace=True)
                
                ultimate_summary = ultimate.groupby(index_cols)['value'].sum().reset_index()
                ultimate_summary.rename(columns={'value': 'Total_Ultimate'}, inplace=True)

        # Display results
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"IBNR Results: {from_date.date()} to {to_date.date()}")
        st.markdown(f"**Grain:** {grain_label} | **Grouped by:** {', '.join(index_cols)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("IBNR Summary")
            st.dataframe(ibnr_summary, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Ultimate Claims")
            st.dataframe(ultimate_summary, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Loss Development Factors")
        st.dataframe(ldfs, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            ibnr_summary.to_excel(writer, index=False, sheet_name='IBNR_Summary')
            ultimate_summary.to_excel(writer, index=False, sheet_name='Ultimate_Summary')
            ldfs.to_excel(writer, sheet_name='LDFs')
            completed.to_excel(writer, sheet_name='Completed_Triangle')
        
        output.seek(0)
        
        safe_client = re.sub(r'[\\/*?:"<>|]', "", client_name).strip() or "Client"
        safe_original = re.sub(r'[\\/*?:"<>|]', "", base_filename).strip() or "Data"
        file_name = f"{safe_client}_{safe_original}_IBNR_Results_{from_date.year}_{to_date.year}.xlsx"
        
        st.download_button("📥 Download Excel Report", data=output, file_name=file_name)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("""
<div class="footer">
    <p>© 2026 African Actuarial Consultants. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
