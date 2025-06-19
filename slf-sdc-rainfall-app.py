#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# Filename: slf-sdc-rainfall-app.py
#
# Description:
#   
#
# Author:
#   Florian Denzinger (SLF Davos)
#
# Created:
#   19.06.2025        
#
# Last Modified:
#   19.06.2025
#
# Version:
#   1.0
# 
# License:
#   MIT
#
# Contact:
#   florian.denzinger@slf.ch
#
# Requirements:
#   - Python
#   - See environments.yml
#   - Key libraries
# 
#  Usage:
#    python slf-sdc-rainfall-app.py
#
#  Notes:
#    -
#    -
#
# ==============================================================================


import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=False)
def load_data(url: str) -> pd.DataFrame:
    """
    Load rainfall data from a CSV URL and prepare it for analysis.

    This function reads a CSV file from the provided URL, renames the first column to 'Date',
    parses it as datetime, and sets it as the DataFrame index.

    Args:
        url (str): URL to the CSV file containing daily rainfall data.

    Returns:
        pd.DataFrame: DataFrame with a DatetimeIndex and a single rainfall column.
    """
    df = pd.read_csv(url, parse_dates=[0])
    # Rename the first column to 'Date' and set as index
    df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
    df.set_index('Date', inplace=True)
    return df

# --- Streamlit App ---
st.title("Rainfall Data Explorer")

# Sidebar: CSV URL input
def main():
    csv_url = st.sidebar.text_input(
        "CSV URL",
        "https://raw.githubusercontent.com/your_user/your_repo/main/rainfall_data_30.463_79.525.csv"
    )

    # Load data
    try:
        df = load_data(csv_url)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return

    # Sidebar: Date range selection
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    start_date, end_date = st.sidebar.date_input(
        "Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    if start_date > end_date:
        st.sidebar.error("Start date must be before end date.")
        return
    # Filter data by date range
    df = df.loc[start_date:end_date]

    # Sidebar: Aggregation mode
    agg_mode = st.sidebar.selectbox(
        "Aggregation Level",
        ["Daily", "Weekly", "Monthly"]
    )
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M"}
    freq = freq_map[agg_mode]

    # Aggregate rainfall
    rainfall_series = df.iloc[:, 0].resample(freq).sum()

    # Display
    st.subheader(f"{agg_mode} Rainfall Summary")
    # Chart: line for daily, bar for weekly/monthly
    if agg_mode == "Daily":
        st.line_chart(rainfall_series)
    else:
        st.bar_chart(rainfall_series)

    # Show raw aggregated data
    if st.sidebar.checkbox("Show Data Table", value=False):
        st.dataframe(rainfall_series)

if __name__ == "__main__":
    main()
