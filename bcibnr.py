# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import chainladder as cl
from io import BytesIO
from datetime import date
import re

st.set_page_config(page_title="Chain Ladder IBNR Calculator", layout="wide")

# ---------- CUSTOM CSS (minimal but functional) ----------
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: 'Calisto MT', serif;
        font-size: 11pt;
    }
    .stButton > button {
        background-color: #D4AF37;
        color: #000000;
        border: none;
        border-radius: 4px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #B8960F;
        color: #FFFFFF;
    }
    .stFileUploader {
        border: 2px dashed #D4AF37;
        border-radius: 5px;
        padding: 1rem;
    }
    .data-check-error {
        background-color: #FFEBEE;
        border: 2px solid #F44336;
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
    .data-check-success {
        background-color: #E8F5E9;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Chain Ladder IBNR Calculator")
st.markdown("Upload your claims data. Map your columns to the required fields.")

# --- User inputs ---
col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name (for file name)", value="Client").strip()
with col2:
    pass

# --- IBNR Period ---
st.subheader("IBNR Period")
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
st.subheader("Triangle Grain")
grain_map = {'Yearly': 'Y', 'Quarterly': 'Q', 'Monthly': 'M'}
grain_label = st.selectbox("Select Grain:", options=list(grain_map.keys()), index=0)
grain = grain_map[grain_label]

# --- File Upload ---
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
                st.info("File read with Windows-1252 encoding.")
        else:
            df = pd.read_excel(uploaded_file)

        # Drop unnamed columns
        df = df.drop(columns=[c for c in df.columns if c.startswith('Unnamed:')])

        st.write("### Preview of your data")
        st.dataframe(df.head())
        st.markdown("---")

        # --- COLUMN MAPPING ---
        st.write("### Map Your Columns")
        st.write("Tell the app which column in your data represents each required field.")

        all_cols = df.columns.tolist()
        
        with st.expander("Available columns in your file"):
            st.write(all_cols)

        loss_col = st.selectbox("Loss Date column (when the loss occurred)", options=[""] + all_cols)
        if not loss_col:
            st.error("Please select a Loss Date column.")
            st.stop()

        report_col = st.selectbox("Report Date column (when the claim was reported)", options=[""] + all_cols)
        if not report_col:
            st.error("Please select a Report Date column.")
            st.stop()

        # Grouping columns
        group_options = [c for c in all_cols if c not in [loss_col, report_col]]
        index_cols = st.multiselect("Grouping columns (e.g., Line of Business)", options=group_options)
        if not index_cols:
            st.error("Please select at least one grouping column.")
            st.stop()

        # Numeric columns
        num_options = [c for c in all_cols if c not in [loss_col, report_col] + index_cols]
        value_cols = st.multiselect("Numeric columns (claim amounts)", options=num_options)
        if not value_cols:
            st.error("Please select at least one numeric column.")
            st.stop()

        st.markdown("---")

        # ============================================================
        # STEP 1: CONVERT DATES AND FILTER BY DATE RANGE FIRST
        # ============================================================
        st.write("### Data Processing")
        
        # Convert dates using the selected column names
        df[loss_col] = pd.to_datetime(df[loss_col], errors='coerce')
        df[report_col] = pd.to_datetime(df[report_col], errors='coerce')
        
        # Filter by the selected IBNR period (based on Loss Date)
        df_filtered = df[
            (df[loss_col] >= from_date) & 
            (df[loss_col] <= to_date)
        ].copy()
        
        if df_filtered.empty:
            st.error(f"No data found for the selected IBNR period: {from_date.date()} to {to_date.date()}")
            st.stop()
        
        st.success(f"✅ Filtered to {len(df_filtered)} claims for the period {from_date.date()} to {to_date.date()}")
        
        # ============================================================
        # STEP 2: DATA QUALITY CHECKS ON FILTERED DATA
        # ============================================================
        st.write("### Data Quality Checks")
        
        errors_found = False
        warnings_found = False
        
        # Check 1: Missing values in selected columns
        st.write("**1. Missing Values Check**")
        missing_cols = []
        for col in [loss_col, report_col] + index_cols + value_cols:
            missing_count = df_filtered[col].isna().sum()
            if missing_count > 0:
                missing_cols.append(f"{col} ({missing_count} missing)")
                errors_found = True
        
        if missing_cols:
            st.markdown(f"""
            <div class="data-check-error">
                <b>❌ Missing values found in:</b> {', '.join(missing_cols)}<br>
                Please fix missing values and re-upload.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-check-success">✅ No missing values found.</div>', unsafe_allow_html=True)
        
        # Check 2: Date reasonability (Report Date >= Loss Date)
        st.write("**2. Date Reasonability Check**")
        invalid_dates = df_filtered[df_filtered[report_col] < df_filtered[loss_col]]
        if len(invalid_dates) > 0:
            errors_found = True
            st.markdown(f"""
            <div class="data-check-error">
                <b>❌ Found {len(invalid_dates)} rows where Report Date is before Loss Date.</b><br>
                Please fix these dates and re-upload.
            </div>
            """, unsafe_allow_html=True)
            with st.expander("View invalid rows (first 10)"):
                st.dataframe(invalid_dates[[loss_col, report_col]].head(10))
        else:
            st.markdown('<div class="data-check-success">✅ All dates valid (Report Date >= Loss Date).</div>', unsafe_allow_html=True)
        
        # Check 3: Duplicate rows (only warn, don't stop)
        st.write("**3. Duplicate Rows Check**")
        duplicate_count = df_filtered.duplicated().sum()
        if duplicate_count > 0:
            warnings_found = True
            st.markdown(f"""
            <div class="data-check-warning">
                <b>⚠️ Found {duplicate_count} duplicate rows.</b><br>
                These will be removed automatically.
            </div>
            """, unsafe_allow_html=True)
            df_filtered = df_filtered.drop_duplicates()
            st.info(f"✅ Removed {duplicate_count} duplicate rows. {len(df_filtered)} rows remaining.")
        else:
            st.markdown('<div class="data-check-success">✅ No duplicate rows found.</div>', unsafe_allow_html=True)
        
        # Check 4: Non-numeric values in numeric columns
        st.write("**4. Numeric Values Check**")
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
        
        numeric_issues = []
        for col in value_cols:
            test_clean = clean_numeric(df_filtered[col])
            failed = test_clean.isna() & df_filtered[col].notna()
            if failed.sum() > 0:
                numeric_issues.append(f"{col} ({failed.sum()} non-numeric values)")
                df_filtered[col] = clean_numeric(df_filtered[col]).fillna(0)
                warnings_found = True
        
        if numeric_issues:
            st.markdown(f"""
            <div class="data-check-warning">
                <b>⚠️ Non-numeric values found in:</b> {', '.join(numeric_issues)}<br>
                These have been converted to 0.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-check-success">✅ All numeric columns contain valid numbers.</div>', unsafe_allow_html=True)
        
        # Stop if critical errors found
        if errors_found:
            st.stop()
        
        # Summary
        st.markdown("---")
        if warnings_found:
            st.markdown('<div class="data-check-warning">⚠️ Data quality checks completed with warnings. Proceeding with calculation.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-check-success">✅ All data quality checks passed!</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ============================================================
        # STEP 3: CREATE TRIANGLE AND RUN CHAIN LADDER
        # ============================================================
        st.write("### Running Chain Ladder Calculation")
        
        # Prepare data for triangle (use filtered data with cleaned values)
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
                    grain=grain
                )
                st.success(f"✅ Triangle created successfully! Grain: {grain_label}")
            except Exception as e:
                st.error(f"Triangle creation error: {str(e)}")
                st.stop()
        
        # Fit Chain Ladder model
        with st.spinner("Fitting Chain Ladder model..."):
            try:
                model = cl.Chainladder().fit(triangle)
                st.success("✅ Chain Ladder model fitted successfully!")
            except Exception as e:
                st.error(f"Model fitting error: {str(e)}")
                st.stop()
        
        # Extract results
        ibnr = model.ibnr_.to_frame().reset_index()
        ultimate = model.ultimate_.to_frame().reset_index()
        ldfs = model.ldf_.to_frame()
        completed_triangle = model.full_triangle_.to_frame()
        
        # Aggregate by index columns
        ibnr_summary = ibnr.groupby(index_cols)[value_cols].sum().reset_index()
        ultimate_summary = ultimate.groupby(index_cols)[value_cols].sum().reset_index()
        
        # ============================================================
        # STEP 4: DISPLAY RESULTS
        # ============================================================
        st.write("### Results")
        st.markdown(f"**Period:** {from_date.date()} to {to_date.date()} | **Grain:** {grain_label} | **Grouped by:** {', '.join(index_cols)}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("IBNR Summary")
            display_ibnr = ibnr_summary.copy()
            for col in value_cols:
                display_ibnr[col] = display_ibnr[col].apply(lambda x: f"{x:,.2f}")
            st.dataframe(display_ibnr, use_container_width=True)
        
        with col2:
            st.subheader("Ultimate Claims")
            display_ultimate = ultimate_summary.copy()
            for col in value_cols:
                display_ultimate[col] = display_ultimate[col].apply(lambda x: f"{x:,.2f}")
            st.dataframe(display_ultimate, use_container_width=True)
        
        st.subheader("Loss Development Factors (LDFs)")
        st.dataframe(ldfs, use_container_width=True)
        
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
        
        st.download_button(
            label="📥 Download Excel Report",
            data=output,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

st.markdown("---")
st.markdown("© 2026 African Actuarial Consultants")
