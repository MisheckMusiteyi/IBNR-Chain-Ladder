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
    <p>Upload the claims data (CSV or Excel). Map the columns, select the IBNR period, choose grain (Yearly/Quarterly/Monthly), and select value columns. The app computes IBNR, Ultimate claims, LDFs, and completed triangles.</p>
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
    <h3> Triangle Grain</h3>
    <p>Select the time unit for grouping origin and development periods</p>
</div>
""", unsafe_allow_html=True)

grain_options = {
    'Yearly': 'Y',
    'Quarterly': 'Q',
    'Monthly': 'M'
}
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
        
        # Row 1: Loss_Date, Report_Date
        req_col1, req_col2 = st.columns(2)
        
        with req_col1:
            st.markdown("""
            <div class="required-container">
                <h3>Loss_Date</h3>
                <p>The date when the loss occurred (origin period)</p>
            </div>
            """, unsafe_allow_html=True)
            loss_date_col = st.selectbox("Select your Loss Date column", options=[""] + all_columns, key="loss_date", label_visibility="collapsed")
            if loss_date_col == "": loss_date_col = None
        
        with req_col2:
            st.markdown("""
            <div class="required-container">
                <h3>Report_Date</h3>
                <p>The date when the claim was reported (development period)</p>
            </div>
            """, unsafe_allow_html=True)
            report_date_col = st.selectbox("Select your Report Date column", options=[""] + all_columns, key="report_date", label_visibility="collapsed")
            if report_date_col == "": report_date_col = None

        st.markdown("---")
        
        # --- Index Columns Selection (Multiple) ---
        st.markdown("""
        <div class="grouping-container">
            <h3>Index Columns (Grouping)</h3>
            <p>Select the columns you want to group by (e.g., Line_of_Business, Region). Results will be aggregated by these columns.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Exclude date columns from grouping options
        grouping_options = [col for col in all_columns if col not in [loss_date_col, report_date_col]]
        index_cols = st.multiselect(
            "Choose columns to group by (at least one required):",
            options=grouping_options,
            default=[grouping_options[0]] if grouping_options else [],
            help="Select one or more columns. The IBNR results will be aggregated by these columns."
        )
        
        if not index_cols:
            st.error("Please select at least one index (grouping) column.")
            st.stop()

        st.markdown("---")

        # --- Numeric columns selection ---
        st.markdown("### Select Numeric Columns (Claim Amounts)")
        st.markdown("Select which numeric columns contain claim amounts to run Chain Ladder on:")
        
        numeric_columns = []
        for col in df.columns:
            if col in [loss_date_col, report_date_col] + index_cols:
                continue
            try:
                pd.to_numeric(df[col])
                numeric_columns.append(col)
            except (ValueError, TypeError):
                pass
        
        numeric_columns = list(set(numeric_columns))
        
        if not numeric_columns:
            st.error("No numeric columns found in the data.")
            st.stop()
        
        selected_value_cols = st.multiselect(
            "Choose the numeric columns (claim amounts) to analyze:",
            options=numeric_columns,
            default=numeric_columns[:min(3, len(numeric_columns))]
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
        
        # Function to clean numeric values
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
        
        # -----------------------------------------------------------------
        # 1. MISSING VALUES CHECK (CRITICAL - STOPS)
        # -----------------------------------------------------------------
        st.markdown("#### 1. Missing Values Check")
        
        missing_summary = {}
        missing_in_selected = False
        
        for col in all_selected_cols:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                missing_summary[col] = missing_count
                if missing_count > 0:
                    missing_in_selected = True
        
        missing_df = pd.DataFrame(list(missing_summary.items()), columns=['Column', 'Missing Values'])
        st.dataframe(missing_df, use_container_width=True)
        
        if missing_in_selected:
            st.markdown("""
            <div class="data-check-error">
                <b>❌ CRITICAL ERROR: Missing values found in selected columns.</b><br>
                Please fix the missing values in your data and re-upload the file.<br>
                Calculation cannot proceed with missing values.
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("View rows with missing values (first 20)"):
                missing_rows = df[df[all_selected_cols].isna().any(axis=1)]
                st.dataframe(missing_rows.head(20))
            
            st.stop()
        else:
            st.success("✅ No missing values found in selected columns.")
        
        # -----------------------------------------------------------------
        # 2. DUPLICATE ROWS CHECK (REMOVE AUTOMATICALLY)
        # -----------------------------------------------------------------
        st.markdown("#### 2. Duplicate Rows Check")
        
        duplicate_rows = df[df.duplicated()]
        duplicate_count = len(duplicate_rows)
        
        if duplicate_count > 0:
            df = df.drop_duplicates()
            st.success(f"✅ Removed {duplicate_count} duplicate row(s). {len(df)} rows remaining.")
        else:
            st.success("✅ No duplicate rows found.")
        
        # -----------------------------------------------------------------
        # 3. DATE REASONABILITY CHECK (Report_Date >= Loss_Date)
        # -----------------------------------------------------------------
        st.markdown("#### 3. Date Reasonability Check")
        
        # Create temporary dataframe for date checking
        df_date_check = df.copy()
        df_date_check['temp_loss_date'] = pd.to_datetime(df_date_check[loss_date_col], errors='coerce')
        df_date_check['temp_report_date'] = pd.to_datetime(df_date_check[report_date_col], errors='coerce')
        
        # Report_Date must be >= Loss_Date (can be equal, but not before)
        invalid_dates = df_date_check[df_date_check['temp_report_date'] < df_date_check['temp_loss_date']]
        invalid_count = len(invalid_dates)
        
        if invalid_count > 0:
            st.markdown("""
            <div class="data-check-error">
                <b>❌ CRITICAL ERROR: Invalid dates found.</b><br>
                Report_Date cannot be before Loss_Date. Report_Date can be equal to or after Loss_Date.
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("View rows with invalid dates (first 20)"):
                st.dataframe(invalid_dates[[loss_date_col, report_date_col]].head(20))
            
            st.stop()
        else:
            st.success("✅ All dates are valid (Report_Date is on or after Loss_Date).")
        
        # -----------------------------------------------------------------
        # 4. NON-NUMERIC VALUES CHECK (CONVERT AUTOMATICALLY)
        # -----------------------------------------------------------------
        st.markdown("#### 4. Non-Numeric Values Check")
        
        conversion_issues = []
        for col in selected_value_cols:
            if col in df.columns:
                test_conversion = clean_numeric(df[col])
                failed_mask = test_conversion.isna() & df[col].notna()
                failed_count = failed_mask.sum()
                if failed_count > 0:
                    problematic_values = df[col][failed_mask].head(3).tolist()
                    conversion_issues.append(f"Column '{col}': {failed_count} non-numeric values (e.g., {problematic_values})")
        
        if conversion_issues:
            st.info(" Converting non-numeric values to numbers:")
            for issue in conversion_issues:
                st.write(f"  • {issue}")
            for col in selected_value_cols:
                df[col] = clean_numeric(df[col])
                df[col] = df[col].fillna(0)
            st.success("✅ Non-numeric values converted successfully.")
        else:
            st.success("✅ All selected numeric columns contain valid numbers.")
        
        # -----------------------------------------------------------------
        # SUMMARY
        # -----------------------------------------------------------------
        st.markdown("#### 📋 Data Quality Summary")
        
        rows_removed = df_original_len - len(df)
        if rows_removed > 0 or conversion_issues:
            st.markdown('<div class="data-check-warning">', unsafe_allow_html=True)
            st.markdown("** Data adjustments applied:**")
            if rows_removed > 0:
                st.write(f"• Removed {rows_removed} duplicate row(s)")
            if conversion_issues:
                st.write(f"• Converted non-numeric values in {len(conversion_issues)} column(s)")
            st.markdown('</div>')
        else:
            st.markdown('<div class="data-check-container">', unsafe_allow_html=True)
            st.markdown("**✅ All data quality checks passed!**")
            st.markdown('</div>')
        
        st.markdown("---")

        # ============================================================
        # PREPARE DATA FOR TRIANGLE
        # ============================================================
        
        # Build clean dataframe
        df_clean = pd.DataFrame()
        df_clean['Loss_Date'] = pd.to_datetime(df[loss_date_col], errors='coerce')
        df_clean['Report_Date'] = pd.to_datetime(df[report_date_col], errors='coerce')
        
        # Add index columns
        for col in index_cols:
            df_clean[col] = df[col]
        
        # Add numeric columns
        for col in selected_value_cols:
            df_clean[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Drop rows with missing critical data
        df_clean = df_clean.dropna(subset=['Loss_Date', 'Report_Date'])
        
        # Filter by date range
        df_filtered = df_clean[
            (df_clean['Loss_Date'] >= from_date) & 
            (df_clean['Loss_Date'] <= to_date)
        ]
        
        if df_filtered.empty:
            st.error(f"No data found for the selected IBNR period.")
            st.stop()
        
        st.success(f"**IBNR Period Filter Applied:** {len(df_filtered)} claims selected")
        
        # Show data summary
        with st.expander("View Data Summary Before Triangle Creation"):
            st.write(f"**Number of rows after filtering:** {len(df_filtered)}")
            st.write(f"**Unique index combinations:** {df_filtered.groupby(index_cols).ngroups}")
            st.write(f"**Selected numeric columns:** {selected_value_cols}")
            st.write(f"**Selected grain:** {selected_grain_label}")
            st.dataframe(df_filtered.head(10))

        # ============================================================
        # CREATE TRIANGLE
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
            st.success(f"Triangle created successfully with grain={selected_grain}!")
            
        except Exception as e:
            st.error(f"Error creating triangle: {str(e)}")
            st.stop()

        # ============================================================
        # FIT CHAIN LADDER MODEL
        # ============================================================
        try:
            model = cl.Chainladder().fit(triangle)
            st.success("Chain Ladder model fitted successfully!")
        except Exception as e:
            st.error(f"Error fitting Chain Ladder model: {e}")
            st.stop()

        # ============================================================
        # EXTRACT RESULTS
        # ============================================================
        
        # IBNR and Ultimate
        ibnr = model.ibnr_
        ultimate = model.ultimate_
        
        # Loss Development Factors
        ldfs = model.ldf_
        
        # Completed triangle (cumulative)
        completed_triangle = model.full_triangle_
        
        # Incremental triangle (convert cumulative to incremental)
        incremental_triangle = completed_triangle.copy()
        if hasattr(completed_triangle, 'incr_to_incremental'):
            incremental_triangle = completed_triangle.incr_to_incremental()
        
        # Convert to DataFrames and aggregate by index
        ibnr_df = ibnr.to_frame()
        ultimate_df = ultimate.to_frame()
        ldfs_df = ldfs.to_frame()
        completed_df = completed_triangle.to_frame()
        incremental_df = incremental_triangle.to_frame()
        
        # Reset index for grouping
        ibnr_reset = ibnr_df.reset_index()
        ultimate_reset = ultimate_df.reset_index()
        
        # Group by index columns and sum numeric columns
        ibnr_summary = ibnr_reset.groupby(index_cols)[selected_value_cols].sum().reset_index()
        ultimate_summary = ultimate_reset.groupby(index_cols)[selected_value_cols].sum().reset_index()
        
        # ============================================================
        # DISPLAY RESULTS
        # ============================================================
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"IBNR Results for Period: {from_date.date()} to {to_date.date()}")
        st.markdown(f"**Grain:** {selected_grain_label} | **Grouped by:** {', '.join(index_cols)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("IBNR by " + ", ".join(index_cols))
            display_ibnr = ibnr_summary.copy()
            for col in selected_value_cols:
                display_ibnr[col] = display_ibnr[col].apply(lambda x: f"{x:,.2f}")
            st.dataframe(display_ibnr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Ultimate Claims by " + ", ".join(index_cols))
            display_ultimate = ultimate_summary.copy()
            for col in selected_value_cols:
                display_ultimate[col] = display_ultimate[col].apply(lambda x: f"{x:,.2f}")
            st.dataframe(display_ultimate, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display LDFs
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Loss Development Factors (LDFs)")
        st.dataframe(ldfs_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ============================================================
        # PREPARE EXCEL DOWNLOAD WITH MULTIPLE SHEETS
        # ============================================================
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: IBNR Summary
            ibnr_summary.to_excel(writer, index=False, sheet_name='IBNR_Summary')
            
            # Sheet 2: Ultimate Summary
            ultimate_summary.to_excel(writer, index=False, sheet_name='Ultimate_Summary')
            
            # Sheet 3: LDFs
            ldfs_df.to_excel(writer, sheet_name='LDFs')
            
            # Sheet 4: Completed Triangle
            completed_df.to_excel(writer, sheet_name='Completed_Triangle')
            
            # Sheet 5: Incremental Triangle
            incremental_df.to_excel(writer, sheet_name='Incremental_Triangle')
        
        output.seek(0)
        
        # Build filename: ClientName_OriginalFileName_IBNR_Results.xlsx
        safe_client = re.sub(r'[\\/*?:"<>|]', "", client_name).strip()
        safe_client = safe_client if safe_client else "Client"
        safe_original = re.sub(r'[\\/*?:"<>|]', "", base_filename).strip()
        safe_original = safe_original if safe_original else "Data"
        
        file_name = f"{safe_client}_{safe_original}_IBNR_Results.xlsx"
        
        st.markdown("### Download Results")
        st.download_button(
            label="Download Excel Report (IBNR, Ultimate, LDFs, Triangles)",
            data=output,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.write("Please check your file format and column selections.")

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("""
<div class="footer">
    <p>© 2026 African Actuarial Consultants. All rights reserved. | <a href="#">Privacy</a> | <a href="#">Terms</a></p>
    <p style="margin-top: 0.5rem; font-size: 0.9rem;">Powered by Vanababa</p>
</div>
""", unsafe_allow_html=True)
