#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# Filename: slf-sdc-rainfall-app.py
#
# Description:
#   A Streamlit application to visualize and analyze a specific rainfall dataset,
#   organized into tabs for different analysis tools.
#
# Author:
#   Florian Denzinger (SLF Davos)
#
# Created:
#   19.06.2025
#
# Last Modified:
#   20.06.2025
#
# Version:
#   7.3 (Enhanced map for comparison)
#
# License:
#   MIT
#
# Contact:
#   florian.denzinger@slf.ch
#
# Requirements:
#   - Python
#   - streamlit
#   - pandas
#   - altair
#   - datetime
#
#  Usage:
#    streamlit run slf-sdc-rainfall-app.py
#
# ==============================================================================

import streamlit as st
import pandas as pd
import altair as alt
import datetime

LOGO_IMG_PATH = "https://raw.githubusercontent.com/fdenzinger/slf-sdc-rainfall-data-explorer/main/docs/markdown/assets/logo.png"
DATA_URLS = {
    "IMD 0.25deg (2010-2024)": "https://raw.githubusercontent.com/fdenzinger/slf-sdc-rainfall-data-explorer/refs/heads/main/data/rainfall_data_30.463_79.525.csv",
    "IMD 0.1deg (1991-2023)": "https://raw.githubusercontent.com/fdenzinger/slf-sdc-rainfall-data-explorer/refs/heads/main/data/patalganga_IPED_rainfall_data_30.463_79.525_1991_2023.csv"
}


@st.cache_data(show_spinner="Loading data...")
def load_data(url: str) -> pd.DataFrame:
    """
    Loads raw data from the specified CSV file or URL.

    Args:
        url (str): The local path or URL to the CSV file.

    Returns:
        pd.DataFrame: The raw DataFrame loaded from the CSV.
    """
    return pd.read_csv(url)


# --- Streamlit App ---
st.set_page_config(layout="wide")


def main():
    """Defines the main execution of the Streamlit application."""

    # --- Data Loading and Processing ---
    
    dataset_options = list(DATA_URLS.keys()) + ["Compare Both datasets"]
    dataset_choice = st.radio(
        "Choose a dataset to analyze:",
        dataset_options,
        horizontal=True
    )

    # --- Header with Logo and Title ---
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        try:
            st.image(LOGO_IMG_PATH, width=80)
        except Exception as logo_error:
            st.error(f"Logo not found {logo_error}. Please ensure '{LOGO_IMG_PATH}' is in the same folder as the script.")
            st.caption("Logo")
    with col2:
        st.title("SDC2: Rainfall Data Explorer")
    
    st.subheader(dataset_choice)

    df_timeseries = pd.DataFrame()
    min_date_limit = None
    max_date_limit = None
    raw_df_for_map = None

    if dataset_choice == "Compare Both datasets":
        df_list = []
        map_data_list = []
        min_dates = []
        max_dates = []
        for name, url in DATA_URLS.items():
            try:
                raw_df = load_data(url)
                map_data_list.append(raw_df[['lat', 'lon']].iloc[:1])
                df = raw_df.copy()
                if name == "IMD 0.1deg (1991-2023)":
                    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d', errors='coerce')
                else:
                    df['time'] = pd.to_datetime(df['time'], format='%d-%m-%Y', errors='coerce')
                df.dropna(subset=['time'], inplace=True)
                df.set_index('time', inplace=True)
                
                if not df.empty:
                    min_dates.append(df.index.min())
                    max_dates.append(df.index.max())
                    df['source'] = name
                    df_list.append(df[['rain (mm)', 'source']])
            except Exception as e:
                st.error(f"Fatal Error: Could not load data for {name}. Error details: {e}")
        
        if df_list:
            df_timeseries = pd.concat(df_list)
            df_timeseries.sort_index(inplace=True)
            if min_dates and max_dates:
                min_date_limit = max(min_dates).date()
                max_date_limit = min(max_dates).date()
        if map_data_list:
            raw_df_for_map = pd.concat(map_data_list)

    else:
        try:
            raw_df = load_data(DATA_URLS[dataset_choice])
            raw_df_for_map = raw_df
            df = raw_df.copy()
            if dataset_choice == "IMD 0.1deg (1991-2023)":
                df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d', errors='coerce')
            else:
                df['time'] = pd.to_datetime(df['time'], format='%d-%m-%Y', errors='coerce')
            df.dropna(subset=['time'], inplace=True)
            df.set_index('time', inplace=True)
            df['source'] = dataset_choice
            df_timeseries = df[['rain (mm)', 'source']]
            df_timeseries.sort_index(inplace=True)
            if not df_timeseries.empty:
                min_date_limit = df_timeseries.index.min().date()
                max_date_limit = df_timeseries.index.max().date()
        except Exception as e:
            st.error(f"Fatal Error: Could not load data from the source URL. Error details: {e}")
            return

    if df_timeseries.empty:
        st.error("Data is empty after processing. Please check the source file.")
        return

    # --- Tab Layout ---
    tab1, tab2, tab3 = st.tabs(["General Rainfall Analysis", "Monsoon End Date Estimator", "Climatology & Anomaly"])

    # --- Tab 1: General Analysis ---
    with tab1:
        with st.container(border=True):
            st.subheader("Options")

            if min_date_limit and max_date_limit:
                years = range(max_date_limit.year, min_date_limit.year - 1, -1)
                years_with_custom = ["Custom Range"] + list(years)
            else:
                years_with_custom = ["Custom Range"] + sorted(df_timeseries.index.year.unique(), reverse=True)

            year_selection = st.selectbox("Select a Year (or a Custom Range)", years_with_custom)

            if year_selection == "Custom Range":
                r1_col1, r1_col2 = st.columns(2)
                with r1_col1:
                    start_date = st.date_input("Start Date", min_date_limit, min_value=min_date_limit,
                                               max_value=max_date_limit)
                with r1_col2:
                    end_date = st.date_input("End Date", max_date_limit, min_value=min_date_limit,
                                             max_value=max_date_limit)
            else:
                start_of_year = datetime.date(year_selection, 1, 1)
                end_of_year = datetime.date(year_selection, 12, 31)
                start_date = max(start_of_year, min_date_limit)
                end_date = min(end_of_year, max_date_limit)

            r2_col1, r2_col2 = st.columns(2)
            with r2_col1:
                agg_mode = st.selectbox("Aggregation Level", ["Daily", "Weekly", "Monthly", "Yearly"], key="agg_level")
            with r2_col2:
                st.write("")
                show_table = st.checkbox("Show Data Table", value=False)

        if start_date > end_date:
            st.error("Error: Start date must be before end date.")
        else:
            df_filtered = df_timeseries.loc[start_date:end_date]

            st.subheader(
                f"Total {agg_mode} Rainfall from {start_date.strftime('%d %b, %Y')} to {end_date.strftime('%d %b, %Y')}")

            plot_df = df_filtered.reset_index()
            plot_df.columns = ['Date', 'Rainfall (mm)', 'Source']

            time_unit_map = {"Daily": "yearmonthdate", "Weekly": "yearweek", "Monthly": "yearmonth", "Yearly": "year"}
            selected_time_unit = time_unit_map[agg_mode]

            selection = alt.selection_multi(fields=['Source'], bind='legend')

            if agg_mode == "Weekly":
                # Multi-line label: First line is the date, second is the week number.
                label_expression = "[timeFormat(datum.value, '%b %d'), 'Week ' + timeFormat(datum.value, '%W')]"
                x_axis = alt.X('Date:T', timeUnit=selected_time_unit, title=agg_mode, scale=alt.Scale(paddingInner=0.1),
                               axis=alt.Axis(labelExpr=label_expression))
                tooltip_date = alt.Tooltip('Date:T', format="%Y-%m-%d", title="Week Starting")
            else:
                x_axis = alt.X('Date:T', timeUnit=selected_time_unit, title=agg_mode, scale=alt.Scale(paddingInner=0.1))
                tooltip_date = alt.Tooltip('Date:T', timeUnit=selected_time_unit, title=agg_mode)

            chart = alt.Chart(plot_df).mark_bar(tooltip=True).encode(
                x=x_axis,
                y=alt.Y('sum(Rainfall (mm)):Q', title=f'{agg_mode} Rainfall (mm)'),
                color='Source:N',
                xOffset='Source:N',
                opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
                tooltip=[
                    tooltip_date,
                    alt.Tooltip('sum(Rainfall (mm)):Q', title='Total Rainfall (mm)', format='.2f'),
                    'Source:N'
                ]
            ).add_selection(
                selection
            ).properties(height=400).interactive()
            st.altair_chart(chart, use_container_width=True)

            st.subheader("Analysis & Export")
            with st.container(border=True):
                freq_map = {"Daily": "D", "Weekly": "W-MON", "Monthly": "MS", "Yearly": "AS"}
                freq = freq_map[agg_mode]
                
                # Pivot the table for a cleaner table view and export
                df_pivot = df_filtered.reset_index().pivot_table(
                    index='time',
                    columns='source',
                    values='rain (mm)'
                )
                table_df = df_pivot.resample(freq).sum()

                # Create a mapping for shorter column names
                column_rename_map = {
                    "IMD 0.25deg (2010-2024)": "Rainfall (mm) 0.25 deg",
                    "IMD 0.1deg (1991-2023)": "Rainfall (mm) 0.1 deg"
                }
                table_df.rename(columns=column_rename_map, inplace=True)

                total_rainfall = df_filtered['rain (mm)'].sum()
                avg_daily_rainfall = df_filtered['rain (mm)'].mean()
                
                peak_date, peak_value = None, 0
                if not df_filtered.empty and not df_filtered['rain (mm)'].empty:
                    peak_value = df_filtered['rain (mm)'].max()
                    peak_date = df_filtered['rain (mm)'].idxmax()

                kpi_cols = st.columns(4)
                kpi_cols[0].metric("Total Rainfall", f"{total_rainfall:.2f} mm")
                kpi_cols[1].metric("Avg. Daily Rainfall", f"{avg_daily_rainfall:.2f} mm")
                if peak_date:
                    kpi_cols[2].metric(f"Peak Day ({peak_date.strftime('%b %d, %Y')})", f"{peak_value:.2f} mm")
                else:
                    kpi_cols[2].metric("Peak Day", "N/A")

                with kpi_cols[3]:
                    st.write("")
                    st.download_button(
                        label="Export Aggregated Data",
                        data=table_df.to_csv().encode('utf-8'),
                        file_name=f"rainfall_data_{agg_mode.lower()}_{start_date}_to_{end_date}.csv",
                        mime='text/csv',
                    )

            if show_table:
                st.write("### Aggregated Data Table")
                st.dataframe(table_df)

    # --- Tab 2: Monsoon End Date Analysis ---
    with tab2:
        if dataset_choice == "Compare Both datasets":
            st.warning("This tool is not available when comparing both datasets.")
        else:
            st.subheader("About this Tool")
            st.info("""
            This tool estimates the **monsoon withdrawal date**. The withdrawal is defined as the *start* of the first sustained dry period after the main rainy season.
            The algorithm works by scanning the daily rainfall data from the "Analysis Start Date" that you select. It looks for the very first day that marks the beginning of a sequence of days meeting your "dry" criteria.
            """)

            with st.container(border=True):
                years_monsoon = sorted(df_timeseries.index.year.unique(), reverse=True)
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                with m_col1:
                    selected_year_monsoon = st.selectbox("Select Year to Analyze", years_monsoon, key="monsoon_year")
                with m_col2:
                    default_start_date = datetime.date(selected_year_monsoon, 7, 1)
                    analysis_start_date = st.date_input("Analysis Start Date", value=default_start_date,
                                                        min_value=datetime.date(selected_year_monsoon, 1, 1),
                                                        max_value=datetime.date(selected_year_monsoon, 12, 31),
                                                        help="The date from which to start searching for the end of the monsoon.")
                with m_col3:
                    dry_day_threshold = st.number_input("'Dry Day' Threshold (mm)", 0.0, 50.0, 5.0, 0.5,
                                                        help="Any day with rainfall below this value is considered a 'dry day'.")
                with m_col4:
                    consecutive_days = st.number_input("Consecutive Dry Days", 1, 30, 14, 1,
                                                       help="The number of 'dry days' that must occur in a row to confirm the end of the monsoon.")

            year_plot_df = df_timeseries[df_timeseries.index.year == selected_year_monsoon]
            year_analysis_df = year_plot_df[year_plot_df.index.date >= analysis_start_date]

            is_dry = year_analysis_df['rain (mm)'] <= dry_day_threshold
            dry_period_sum = is_dry.rolling(window=consecutive_days).sum()
            end_of_dry_spell_dates = dry_period_sum[dry_period_sum >= consecutive_days].index

            monsoon_end_date = None
            if not end_of_dry_spell_dates.empty:
                end_of_spell = end_of_dry_spell_dates[0]
                monsoon_end_date = end_of_spell - pd.Timedelta(days=consecutive_days - 1)
                st.success(
                    f"**Estimated Monsoon End Date for {selected_year_monsoon}: {monsoon_end_date.strftime('%B %d, %Y')}**")
            else:
                st.warning("No period matching the criteria found for this year. Try adjusting the thresholds.")

            year_chart_df = year_plot_df.reset_index()
            year_chart_df.columns = ['Date', 'Rainfall (mm)', 'Source']

            bar_chart = alt.Chart(year_chart_df).mark_bar().encode(x=alt.X('Date:T', title='Date'),
                                                                   y=alt.Y('Rainfall (mm):Q', title='Daily Rainfall (mm)'))
            start_rule = alt.Chart(pd.DataFrame({'date': [analysis_start_date]})).mark_rule(color='gray', strokeDash=[4, 4],
                                                                                            size=2).encode(x='date:T')

            if monsoon_end_date:
                end_rule = alt.Chart(pd.DataFrame({'date': [monsoon_end_date]})).mark_rule(color='red',
                                                                                           strokeWidth=2).encode(x='date:T')
                final_chart = (bar_chart + start_rule + end_rule).properties(
                    title=f"Daily Rainfall for {selected_year_monsoon}").interactive()
            else:
                final_chart = (bar_chart + start_rule).properties(
                    title=f"Daily Rainfall for {selected_year_monsoon}").interactive()

            st.altair_chart(final_chart, use_container_width=True)
            st.caption(
                "The dashed grey line indicates the start of the analysis period. The solid red line indicates the estimated monsoon end date.")

    # --- Tab 3: Climatology & Anomaly ---
    with tab3:
        if dataset_choice == "Compare Both datasets":
            st.warning("This tool is not available when comparing both datasets.")
        else:
            st.subheader("Climatology & Anomaly Analysis")
            st.info(
                "This tool compares a selected year's rainfall against the long-term daily average (climatology) to identify wetter or drier than normal periods.")

            with st.container(border=True):
                years_clim = sorted(df_timeseries.index.year.unique(), reverse=True)
                selected_year_clim = st.selectbox("Select Year for Climatology Analysis", years_clim, key="clim_year")

            year_df = df_timeseries[df_timeseries.index.year == selected_year_clim].copy()
            climatology_df = df_timeseries[df_timeseries.index.year != selected_year_clim]

            climatology = climatology_df.groupby([climatology_df.index.month, climatology_df.index.day])[
                'rain (mm)'].mean().rename("long_term_avg")

            year_df['month'] = year_df.index.month
            year_df['day'] = year_df.index.day

            year_df = pd.merge(
                year_df,
                climatology,
                left_on=['month', 'day'],
                right_index=True,  # Use the index from the climatology series
                how='left'
            )

            year_df['anomaly'] = year_df['rain (mm)'] - year_df['long_term_avg']

            plot_df_clim = year_df.reset_index()

            st.write(f"**Daily Rainfall for {selected_year_clim} vs. Long-Term Average**")
            st.caption(
                "Bars show daily rainfall for the selected year. The red line shows the historical average for each day of the year (calculated from all other years).")

            base = alt.Chart(plot_df_clim)
            bars = base.mark_bar(opacity=0.6).encode(
                x=alt.X('time:T', title='Date'),
                y=alt.Y('rain (mm):Q', title='Rainfall (mm)'),
                tooltip=[alt.Tooltip('time:T', title='Date'), alt.Tooltip('rain (mm):Q', format='.2f', title='Rainfall')]
            )
            line = base.mark_line(color='firebrick', strokeWidth=2).encode(
                x=alt.X('time:T'),
                y=alt.Y('long_term_avg:Q', title='Avg. Rainfall (mm)'),
                tooltip=[alt.Tooltip('time:T', title='Date'),
                         alt.Tooltip('long_term_avg:Q', format='.2f', title='Avg. Rainfall')]
            )
            st.altair_chart((bars + line).interactive(), use_container_width=True)

            st.write(f"**Rainfall Anomaly for {selected_year_clim}**")
            st.caption("Blue bars indicate wetter than average days. Brown bars indicate drier than average days.")

            anomaly_chart = alt.Chart(plot_df_clim).mark_bar().encode(
                x=alt.X('time:T', title='Date'),
                y=alt.Y('anomaly:Q', title='Rainfall Anomaly (mm)'),
                color=alt.condition(
                    alt.datum.anomaly > 0,
                    alt.value('steelblue'),
                    alt.value('saddlebrown')
                ),
                tooltip=['time:T', alt.Tooltip('anomaly:Q', format='.2f')]
            ).properties(height=250).interactive()
            st.altair_chart(anomaly_chart, use_container_width=True)

    # --- Common Elements Below Tabs ---
    st.subheader("Data Location")
    if raw_df_for_map is not None:
        if dataset_choice == "Compare Both datasets":
            st.map(raw_df_for_map, zoom=6)
        else:
            map_data = raw_df_for_map[['lat', 'lon']].iloc[:1]
            st.map(map_data, zoom=6)

    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: grey;'>"
        "© 2025 WSL Institute for Snow and Avalanche Research SLF<br>"
        "Developed by DF"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
