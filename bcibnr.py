# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import chainladder as cl
from io import BytesIO
from datetime import date

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
    .date-range-container p {
        color: #666666;
        font-size: 0.85rem;
        margin-bottom: 0;
    }
    
    /* Error Container */
    .error-container {
        background-color: #FFEBEE;
        border: 2px solid #F44336;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .error-container h3 {
        color: #F44336;
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
    <p>Upload your claims data (CSV or Excel). Map your columns, select the IBNR period (date range), and choose the currency columns. The app computes IBNR and Ultimate claims by product using the Chain Ladder method.</p>
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

# --- IBNR Period Selection with clear labels ---
st.markdown("""
<div class="date-range-container">
    <h3>📅 IBNR Period</h3>
    <p>Select the date range for claims to be included in the IBNR calculation</p>
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

# Display selected period summary
st.info(f"**Selected IBNR Period:** {from_date.date()} to {to_date.date()}")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
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
            # For Excel files, read dates as strings first to see raw values
            df = pd.read_excel(uploaded_file, dtype=str)

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

        # Get all column names for selection
        all_columns = df.columns.tolist()
        
        # Create three columns for the required mappings
        req_col1, req_col2, req_col3 = st.columns(3)
        
        with req_col1:
            st.markdown("""
            <div class="required-container">
                <h3>Loss_Date</h3>
                <p>The date when the loss occurred (origin period)</p>
            </div>
            """, unsafe_allow_html=True)
            loss_date_col = st.selectbox(
                "Select your Loss Date column",
                options=[""] + all_columns,
                key="loss_date",
                label_visibility="collapsed"
            )
            if loss_date_col == "":
                loss_date_col = None
        
        with req_col2:
            st.markdown("""
            <div class="required-container">
                <h3>Report_Date</h3>
                <p>The date when the claim was reported (development period)</p>
            </div>
            """, unsafe_allow_html=True)
            report_date_col = st.selectbox(
                "Select your Report Date column",
                options=[""] + all_columns,
                key="report_date",
                label_visibility="collapsed"
            )
            if report_date_col == "":
                report_date_col = None
        
        with req_col3:
            st.markdown("""
            <div class="required-container">
                <h3>Product</h3>
                <p>The category/segment for grouping results (e.g., Motor, Property, Agriculture)</p>
            </div>
            """, unsafe_allow_html=True)
            product_col = st.selectbox(
                "Select your Product column",
                options=[""] + all_columns,
                key="product",
                label_visibility="collapsed"
            )
            if product_col == "":
                product_col = None

        st.markdown("---")

        # Validate required mappings
        if not loss_date_col or not report_date_col or not product_col:
            st.error("Please map all required columns (Loss_Date, Report_Date, Product).")
            st.stop()

        # --- Rename columns for internal processing ---
        df_processed = df.rename(columns={
            loss_date_col: 'Loss_Date',
            report_date_col: 'Report_Date',
            product_col: 'Product'
        })

        # --- IMPROVED DATE CONVERSION FOR EXCEL ---
        # Store original values for error reporting
        original_loss_dates = df_processed['Loss_Date'].copy()
        original_report_dates = df_processed['Report_Date'].copy()
        
        # Get the data types of the original columns
        loss_date_dtype = df[loss_date_col].dtype
        report_date_dtype = df[report_date_col].dtype
        
        # Function to convert Excel serial numbers or text dates
        def convert_to_datetime(series, column_name):
            # First, try to convert using pandas (handles Excel serial numbers automatically)
            converted = pd.to_datetime(series, errors='coerce')
            
            # If all are NaN, try with explicit formats
            if converted.isna().all():
                date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y']
                for fmt in date_formats:
                    try:
                        converted = pd.to_datetime(series, format=fmt, errors='coerce')
                        if not converted.isna().all():
                            break
                    except:
                        continue
            
            return converted
        
        # Apply conversion
        df_processed['Loss_Date'] = convert_to_datetime(df_processed['Loss_Date'], 'Loss_Date')
        df_processed['Report_Date'] = convert_to_datetime(df_processed['Report_Date'], 'Report_Date')
        
        # Find problematic dates
        bad_loss_dates = original_loss_dates[df_processed['Loss_Date'].isna() & original_loss_dates.notna()]
        bad_report_dates = original_report_dates[df_processed['Report_Date'].isna() & original_report_dates.notna()]
        
        # Show detailed error if any dates couldn't be parsed
        if not bad_loss_dates.empty or not bad_report_dates.empty:
            st.markdown("""
            <div class="error-container">
                <h3>⚠️ Date Parsing Errors</h3>
                <p>The following date values could not be parsed. Please check these entries in your file.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if not bad_loss_dates.empty:
                st.write(f"**Loss_Date Column Issues:**")
                st.write(f"- Column name: `{loss_date_col}`")
                st.write(f"- Current data type: `{loss_date_dtype}`")
                st.write(f"- Expected data type: `datetime64`")
                st.write(f"- Number of invalid values: {len(bad_loss_dates)}")
                st.write("**Invalid values (first 10):**")
                bad_loss_list = bad_loss_dates.head(10).tolist()
                for i, val in enumerate(bad_loss_list, 1):
                    st.write(f"{i}. {repr(val)}")
                if len(bad_loss_dates) > 10:
                    st.write(f"... and {len(bad_loss_dates) - 10} more")
                st.write("")
            
            if not bad_report_dates.empty:
                st.write(f"**Report_Date Column Issues:**")
                st.write(f"- Column name: `{report_date_col}`")
                st.write(f"- Current data type: `{report_date_dtype}`")
                st.write(f"- Expected data type: `datetime64`")
                st.write(f"- Number of invalid values: {len(bad_report_dates)}")
                st.write("**Invalid values (first 10):**")
                bad_report_list = bad_report_dates.head(10).tolist()
                for i, val in enumerate(bad_report_list, 1):
                    st.write(f"{i}. {repr(val)}")
                if len(bad_report_dates) > 10:
                    st.write(f"... and {len(bad_report_dates) - 10} more")
            
            st.stop()

        # Show success message that dates were converted
        st.success(f"✅ Date columns successfully converted to datetime format!")
        st.caption(f"Loss_Date column '{loss_date_col}' converted from {loss_date_dtype} to datetime64")
        st.caption(f"Report_Date column '{report_date_col}' converted from {report_date_dtype} to datetime64")

        # --- Filter data by IBNR period (date range) ---
        df_filtered = df_processed[
            (df_processed['Loss_Date'] >= from_date) & 
            (df_processed['Loss_Date'] <= to_date)
        ]
        
        if df_filtered.empty:
            st.error(f"No data found for the selected IBNR period: {from_date.date()} to {to_date.date()}")
            st.stop()
        
        st.success(f"**IBNR Period Filter Applied:** {len(df_filtered)} claims selected (from {len(df_processed)} total)")

        # --- Identify numeric columns for selection ---
        numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove the mapped columns if they appear in numeric columns
        exclude_cols = ['Loss_Date', 'Report_Date', 'Product']
        for col in exclude_cols:
            if col in numeric_cols:
                numeric_cols.remove(col)

        if not numeric_cols:
            st.error("No numeric columns found in the data. Please ensure you have numeric columns for claim amounts.")
            st.stop()

        # Multi-select for currency columns
        st.markdown("### Select Currency Columns (Claim Amounts)")
        selected_columns = st.multiselect(
            "Choose the columns that contain claim amounts (these will be used as 'columns' in the triangle):",
            options=numeric_cols,
            default=numeric_cols[:min(3, len(numeric_cols))]
        )

        if not selected_columns:
            st.warning("Please select at least one currency column to proceed.")
            st.stop()

        # Show mapping summary button
        if st.button("View Column Mapping Summary"):
            mapping_data = {
                'Required Field': ['Loss_Date', 'Report_Date', 'Product'],
                'Your Column': [loss_date_col, report_date_col, product_col],
                'Description': [
                    'Loss occurrence date (origin period)',
                    'Claim report date (development period)',
                    'Category for grouping results'
                ]
            }
            mapping_df = pd.DataFrame(mapping_data)
            st.dataframe(mapping_df, use_container_width=True)
            
            st.markdown(f"**Selected IBNR Period:** {from_date.date()} to {to_date.date()}")
            st.markdown(f"**Selected numeric columns:** {', '.join(selected_columns)}")

        # --- Create Triangle ---
        try:
            triangle = cl.Triangle(
                data=df_filtered,
                origin='Loss_Date',
                development='Report_Date',
                columns=selected_columns,
                index='Product',
                cumulative=False
            )
        except Exception as e:
            st.error(f"Error creating triangle: {e}")
            st.stop()

        # --- Fit Chain Ladder model ---
        try:
            model = cl.Chainladder().fit(triangle)
        except Exception as e:
            st.error(f"Error fitting Chain Ladder model: {e}")
            st.stop()

        # Extract IBNR and Ultimate
        ibnr = model.ibnr_
        ultimate = model.ultimate_

        # Convert to DataFrame and group by Product
        ibnr_df = ibnr.to_frame()
        ultimate_df = ultimate.to_frame()

        ibnr_reset = ibnr_df.reset_index()
        ultimate_reset = ultimate_df.reset_index()

        ibnr_summary = ibnr_reset.groupby('Product')[selected_columns].sum().reset_index()
        ultimate_summary = ultimate_reset.groupby('Product')[selected_columns].sum().reset_index()

        # Display results with period label
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"IBNR Results for Period: {from_date.date()} to {to_date.date()}")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("IBNR by Product")
            st.dataframe(ibnr_summary, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Ultimate Claims by Product")
            st.dataframe(ultimate_summary, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Prepare Excel downloads
        output_ibnr = BytesIO()
        with pd.ExcelWriter(output_ibnr, engine='openpyxl') as writer:
            ibnr_summary.to_excel(writer, index=False, sheet_name='IBNR')
        output_ibnr.seek(0)

        output_ultimate = BytesIO()
        with pd.ExcelWriter(output_ultimate, engine='openpyxl') as writer:
            ultimate_summary.to_excel(writer, index=False, sheet_name='Ultimate')
        output_ultimate.seek(0)

        st.markdown("### Download Results")
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            safe_client = "".join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            ibnr_filename = f"{safe_client}_IBNR_Summary_{from_date.year}_{to_date.year}.xlsx" if safe_client else f"IBNR_Summary_{from_date.year}_{to_date.year}.xlsx"
            st.download_button(
                label="Download IBNR Summary (Excel)",
                data=output_ibnr,
                file_name=ibnr_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with dcol2:
            safe_client = "".join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            ultimate_filename = f"{safe_client}_Ultimate_Summary_{from_date.year}_{to_date.year}.xlsx" if safe_client else f"Ultimate_Summary_{from_date.year}_{to_date.year}.xlsx"
            st.download_button(
                label="Download Ultimate Summary (Excel)",
                data=output_ultimate,
                file_name=ultimate_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.write("Please check your file format and column selections.")

st.markdown('</div>', unsafe_allow_html=True)  # close main-container

# ---------- Footer ----------
st.markdown("""
<div class="footer">
    <p>© 2026 African Actuarial Consultants. All rights reserved. | <a href="#">Privacy</a> | <a href="#">Terms</a></p>
    <p style="margin-top: 0.5rem; font-size: 0.9rem;">Powered by Vanababa</p>
</div>
""", unsafe_allow_html=True)
