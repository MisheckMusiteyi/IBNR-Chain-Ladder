import streamlit as st
import pandas as pd
import numpy as np
import chainladder as cl
from io import BytesIO
from datetime import date
import re

st.set_page_config(page_title="Chain Ladder IBNR Calculator", layout="wide")

# Simplified header (no complex CSS for now)
st.title("Chain Ladder IBNR Calculator")
st.markdown("Upload your claims data. Map your columns to the required fields.")

col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name (for file name)", value="Client").strip()
with col2:
    pass

# Date range filter
col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input("From Date (Loss Date)", value=date(2020, 1, 1))
with col2:
    to_date = st.date_input("To Date (Loss Date)", value=date(2024, 12, 31))

from_date = pd.to_datetime(from_date)
to_date = pd.to_datetime(to_date)

# Grain selection
grain_options = {'Yearly': 'Y', 'Quarterly': 'Q', 'Monthly': 'M'}
selected_grain_label = st.selectbox("Triangle Grain:", options=list(grain_options.keys()), index=0)
selected_grain = grain_options[selected_grain_label]

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        original_filename = uploaded_file.name
        base_filename = re.sub(r'\.[^.]*$', '', original_filename)

        # Read file
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == 'csv':
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='cp1252')
        else:
            df = pd.read_excel(uploaded_file)

        # Drop unnamed columns
        unnamed = [c for c in df.columns if c.startswith('Unnamed:')]
        if unnamed:
            df = df.drop(columns=unnamed)

        st.markdown("#### Preview of your data")
        st.dataframe(df.head())
        st.markdown("---")

        # ============================================================
        # COLUMN MAPPING - USER SELECTS EVERYTHING
        # ============================================================
        st.markdown("### Map Your Columns")
        st.markdown("Tell the app which column in your data represents each required field.")

        all_columns = df.columns.tolist()
        
        # Show available columns
        with st.expander("Available columns in your file"):
            st.write(all_columns)

        # Loss Date column
        loss_col = st.selectbox("Which column is your LOSS DATE?", options=[""] + all_columns)
        if not loss_col:
            st.error("Please select a Loss Date column.")
            st.stop()

        # Report Date column
        report_col = st.selectbox("Which column is your REPORT DATE?", options=[""] + all_columns)
        if not report_col:
            st.error("Please select a Report Date column.")
            st.stop()

        # Grouping columns
        grouping_options = [col for col in all_columns if col not in [loss_col, report_col]]
        index_cols = st.multiselect("Which columns do you want to GROUP BY? (e.g., Line of Business)", options=grouping_options)
        
        if not index_cols:
            st.error("Please select at least one grouping column.")
            st.stop()

        # Numeric columns
        numeric_options = [col for col in all_columns if col not in [loss_col, report_col] + index_cols]
        selected_value_cols = st.multiselect("Which columns contain the CLAIM AMOUNTS?", options=numeric_options)
        
        if not selected_value_cols:
            st.warning("Please select at least one numeric column.")
            st.stop()

        st.markdown("---")
        st.markdown("### Data Quality Checks")

        # ============================================================
        # DATA CLEANING
        # ============================================================
        # Convert dates using the user's selected column names
        df[loss_col] = pd.to_datetime(df[loss_col], errors='coerce')
        df[report_col] = pd.to_datetime(df[report_col], errors='coerce')

        # Check for missing values in selected columns
        missing_found = False
        for col in [loss_col, report_col] + index_cols + selected_value_cols:
            missing = df[col].isna().sum()
            if missing > 0:
                st.warning(f"Column '{col}' has {missing} missing value(s).")
                missing_found = True
        
        if missing_found:
            st.error("Please fix missing values and re-upload.")
            st.stop()

        # Check date reasonability
        invalid = df[df[report_col] < df[loss_col]]
        if len(invalid) > 0:
            st.error(f"Found {len(invalid)} rows where Report Date is before Loss Date.")
            st.stop()

        # Remove duplicates
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        if before != after:
            st.info(f"Removed {before - after} duplicate rows.")

        st.success("✅ All data quality checks passed!")

        # ============================================================
        # FILTER BY DATE RANGE
        # ============================================================
        df_filtered = df[(df[loss_col] >= from_date) & (df[loss_col] <= to_date)]
        
        if df_filtered.empty:
            st.error("No data found for selected date range.")
            st.stop()

        st.success(f"Selected {len(df_filtered)} claims for the period {from_date.date()} to {to_date.date()}")

        # ============================================================
        # CREATE TRIANGLE - USING USER'S COLUMN NAMES DIRECTLY
        # ============================================================
        try:
            triangle = cl.Triangle(
                data=df_filtered,
                origin=loss_col,           # User's loss date column name
                development=report_col,     # User's report date column name
                columns=selected_value_cols, # User's numeric column names
                index=index_cols,           # User's grouping column names
                cumulative=False,
                grain=selected_grain
            )
            st.success(f"Triangle created! Grain: {selected_grain_label}")
        except Exception as e:
            st.error(f"Triangle creation error: {str(e)}")
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
        # RESULTS
        # ============================================================
        ibnr = model.ibnr_.to_frame().reset_index()
        ultimate = model.ultimate_.to_frame().reset_index()
        ldfs = model.ldf_.to_frame()
        completed = model.full_triangle_.to_frame()

        # Summarize by index columns
        ibnr_summary = ibnr.groupby(index_cols)[selected_value_cols].sum().reset_index()
        ultimate_summary = ultimate.groupby(index_cols)[selected_value_cols].sum().reset_index()

        st.subheader("IBNR Summary")
        st.dataframe(ibnr_summary)

        st.subheader("Ultimate Claims Summary")
        st.dataframe(ultimate_summary)

        st.subheader("Loss Development Factors")
        st.dataframe(ldfs)

        # ============================================================
        # EXPORT
        # ============================================================
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            ibnr_summary.to_excel(writer, index=False, sheet_name='IBNR_Summary')
            ultimate_summary.to_excel(writer, index=False, sheet_name='Ultimate_Summary')
            ldfs.to_excel(writer, sheet_name='LDFs')
            completed.to_excel(writer, sheet_name='Completed_Triangle')
        
        output.seek(0)

        safe_client = re.sub(r'[\\/*?:"<>|]', "", client_name).strip() or "Client"
        safe_original = re.sub(r'[\\/*?:"<>|]', "", base_filename).strip() or "Data"
        file_name = f"{safe_client}_{safe_original}_IBNR_Results.xlsx"

        st.download_button("Download Excel Report", data=output, file_name=file_name)

    except Exception as e:
        st.error(f"Error: {str(e)}")
