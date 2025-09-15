#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# Filename: slf-sdc-rainfall-app.py
#
# Description:
#   A Streamlit application to visualize and analyze rainfall datasets,
#   with features for sensitivity analysis, custom data uploads, and
#   comparative monsoon end-date estimation.
#
# Author:
#   Florian Denzinger (SLF Davos)
#
# Created:
#   19.06.2025
#
# Last Modified:
#   11.09.2025
#
# Version:
#   14.0 (Altair syntax update and coordinate display)
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

    # --- Header with Logo and Title ---
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        try:
            st.image(LOGO_IMG_PATH, width=80)
        except Exception as logo_error:
            st.error(
                f"Logo not found {logo_error}. Please ensure '{LOGO_IMG_PATH}' is in the same folder as the script.")
            st.caption("Logo")
    with col2:
        st.title("SDC2: Landslide Monitoring Planner")

    # Sub-header on a new line below the columns
    st.subheader("A Data-Driven Forecast of Monsoon End Dates for ICEYE Acquisition")

    # --- How to Use Guide ---
    with st.expander("ℹ️ How to Use This App"):
        st.markdown("""
            This tool is designed to help you plan landslide monitoring campaigns by forecasting the end of the monsoon season. Here's a quick guide to the tabs:

            -   **🎯 Monsoon End Date Estimator:** **This is the main tool.** Use it to see the historical range of monsoon end dates and get a data-driven recommendation for when to start monitoring.
            -   **📊 General Rainfall Analysis:** Use this tab for a general exploration of the daily, weekly, or monthly rainfall data for any period.
            -   **☀️ Climatology & Anomaly:** This tab lets you compare a specific year against the long-term average to see if it was unusually wet or dry.
            """)
    st.divider()

    # --- Dataset Selection ---
    dataset_options = list(DATA_URLS.keys()) + ["Compare Both datasets", "Upload Your Own CSV"]
    dataset_choice = st.radio(
        "Choose a dataset to analyze:",
        dataset_options,
        horizontal=True
    )

    # --- Data Loading and Processing ---
    df_timeseries = pd.DataFrame()
    min_date_limit = None
    max_date_limit = None
    map_data_list = []

    if dataset_choice == "Compare Both datasets":
        st.subheader("Comparing Both IMD Datasets")
        df_list = []
        min_dates = []
        max_dates = []
        for name, url in DATA_URLS.items():
            try:
                raw_df = load_data(url)
                map_point_df = raw_df[['lat', 'lon']].iloc[:1].copy()
                map_point_df['source'] = name
                map_data_list.append(map_point_df)

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

    elif dataset_choice == "Upload Your Own CSV":
        st.subheader("Analyze Your Own Data")
        st.info(
            "Please upload a CSV file with 'time' and 'rain (mm)' columns. 'lat' and 'lon' columns are optional for map display.")
        uploaded_file = st.file_uploader("Upload your rainfall data", type=["csv"])

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)

                if 'time' not in df.columns or 'rain (mm)' not in df.columns:
                    st.error("Error: Your CSV must contain 'time' and 'rain (mm)' columns.")
                    st.stop()

                df['time'] = pd.to_datetime(df['time'], errors='coerce', infer_datetime_format=True)
                df.dropna(subset=['time'], inplace=True)

                if df.empty:
                    st.error("Error: Could not parse any valid dates from the 'time' column.")
                    st.stop()

                source_name = uploaded_file.name
                df.set_index('time', inplace=True)
                df['source'] = source_name
                df_timeseries = df[['rain (mm)', 'source']]
                df_timeseries.sort_index(inplace=True)

                min_date_limit = df_timeseries.index.min().date()
                max_date_limit = df_timeseries.index.max().date()

                if 'lat' in df.columns and 'lon' in df.columns:
                    map_point_df = df[['lat', 'lon']].iloc[:1].copy()
                    map_point_df['source'] = source_name
                    map_data_list.append(map_point_df)


            except Exception as e:
                st.error(f"An error occurred while processing the file: {e}")
                st.stop()
    else:
        st.subheader(dataset_choice)
        try:
            raw_df = load_data(DATA_URLS[dataset_choice])
            map_point_df = raw_df[['lat', 'lon']].iloc[:1].copy()
            map_point_df['source'] = dataset_choice
            map_data_list.append(map_point_df)

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

    # --- Data Source Information Expander ---
    if dataset_choice != "Upload Your Own CSV":
        with st.expander("About the Data Source(s)"):
            if dataset_choice == "IMD 0.25deg (2010-2024)" or dataset_choice == "Compare Both datasets":
                st.markdown("""
                **IMD 0.25deg: Official Gridded Daily Rainfall Data**
                - **Citation:** Pai, D.S., Sridhar, L., Rajeevan, M. *et al*. Development of a new high spatial resolution (0.25° X 0.25°) long period (1901-2010) daily gridded rainfall data set over India and its comparison with existing data sets over the region. *MAUSAM*, 65(1), pp.1-18 (2014).
                - **Data Access:** [India Meteorological Department (IMD), Pune](https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html)
                - **Derivation:** This official daily dataset from the IMD is created using Shepard's interpolation method, a form of inverse distance weighting, applied to measurements from a dense national network of rain gauge stations.
                - **Description:** It provides a long-term (1901-2024) deterministic, or "best-guess," estimate for daily rainfall at a 0.25° x 0.25° spatial resolution across the Indian subcontinent.
                """)
            if dataset_choice == "IMD 0.1deg (1991-2023)" or dataset_choice == "Compare Both datasets":
                st.markdown("""
                **IMD 0.1deg: Indian Precipitation Ensemble Dataset (IPED)**
                - **Source:** Peringiyil, A., Saharia, M., O. P., S. *et al.* A station-based 0.1-degree daily gridded ensemble precipitation dataset for India. *Sci Data* **12**, 333 (2025). [https://doi.org/10.1038/s41597-025-04474-2](https://doi.org/10.1038/s41597-025-04474-2)
                - **Data Access:** [Zenodo](https://zenodo.org/records/15618220)
                - **Derivation:** This dataset was developed by applying a locally weighted spatial regression method to data from thousands of IMD rain gauge stations. Unlike simpler interpolation, this approach also incorporates topographical features like elevation, slope, and aspect to produce more accurate estimates, especially in complex terrain.
                - **Description:** IPED is the first observation-based ensemble precipitation product for India. Instead of providing a single value for daily rainfall, it offers a 30-member ensemble. Each "member" represents a plausible rainfall scenario, and the spread between them provides a crucial estimate of the data's uncertainty, making it highly valuable for hydrological modeling and risk assessment.
                """)
    st.divider()

    if df_timeseries.empty:
        if dataset_choice == "Upload Your Own CSV":
            st.warning("Awaiting file upload to proceed...")
        else:
            st.error("Data is empty after processing. Please check the source file.")
        return

    # --- Tab Layout ---
    tab1, tab2, tab3 = st.tabs(
        ["🎯 Monsoon End Date Estimator", "📊 General Rainfall Analysis", "☀️ Climatology & Anomaly"])

    # --- Tab 1: Monsoon End Date Estimator ---
    with tab1:
        st.subheader("Monsoon End Date Estimator")
        st.info("""
            This tool estimates the **monsoon withdrawal date** to help forecast the optimal time to monitor post-monsoon landslide activity.
            It first calculates the likely range of monsoon end dates based on historical data and then helps you define a monitoring window for tasking satellite imagery like ICEYE. 🛰️
            """)

        with st.container(border=True):
            st.subheader("1. Define and Test Your Parameters (Sensitivity Analysis)")
            st.caption(
                "These settings control the definition of the monsoon's end. Adjust them to see how the statistics and recommendations change in real-time. This helps you understand the sensitivity of the results to your assumptions.")
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                analysis_start_month = st.selectbox("Analysis Start Month", list(range(1, 13)), index=6,
                                                    format_func=lambda x: datetime.date(2000, x, 1).strftime('%B'))
            with m_col2:
                dry_day_threshold = st.number_input("'Dry Day' Threshold (mm)", 0.0, 50.0, 5.0, 0.5,
                                                    help="Any day with rainfall below this value is considered a 'dry day'.")
            with m_col3:
                consecutive_days = st.number_input("Consecutive Dry Days", 1, 30, 14, 1,
                                                   help="The number of 'dry days' that must occur in a row to confirm the end of the monsoon.")

        def get_monsoon_end_date(year_df, start_date, threshold, days):
            analysis_df = year_df[year_df.index.date >= start_date]
            is_dry = analysis_df['rain (mm)'] <= threshold
            dry_period_sum = is_dry.rolling(window=days).sum()
            end_of_dry_spell_dates = dry_period_sum[dry_period_sum >= days].index
            if not end_of_dry_spell_dates.empty:
                end_of_spell = end_of_dry_spell_dates[0]
                return end_of_spell - pd.Timedelta(days=days - 1)
            return None

        sources = df_timeseries['source'].unique()
        results_by_source = {}
        stats_by_source = {}
        DISPLAY_YEAR = 2000

        for source in sources:
            source_df = df_timeseries[df_timeseries['source'] == source]
            all_years = sorted(source_df.index.year.unique())
            end_dates = []

            for year in all_years:
                year_data = source_df[source_df.index.year == year]
                start_date = datetime.date(year, analysis_start_month, 1)
                end_date = get_monsoon_end_date(year_data, start_date, dry_day_threshold, consecutive_days)
                if end_date:
                    display_date = end_date.replace(year=DISPLAY_YEAR)
                    end_dates.append({
                        'Year': year,
                        'EndDate': end_date,
                        'DayOfYear': end_date.dayofyear,
                        'DisplayDate': display_date,
                        'source': source
                    })

            if end_dates:
                results_df = pd.DataFrame(end_dates)
                results_by_source[source] = results_df

                median_doy = results_df['DayOfYear'].median()
                p025_doy = results_df['DayOfYear'].quantile(0.025)
                p975_doy = results_df['DayOfYear'].quantile(0.975)

                base_date = pd.to_datetime(f'{DISPLAY_YEAR}-01-01')
                stats_by_source[source] = {
                    'median_date': base_date + pd.to_timedelta(median_doy - 1, unit='D'),
                    'p025_date': base_date + pd.to_timedelta(p025_doy - 1, unit='D'),
                    'p975_date': base_date + pd.to_timedelta(p975_doy - 1, unit='D'),
                    'min_year': results_df['Year'].min(),
                    'max_year': results_df['Year'].max()
                }

        if not stats_by_source:
            st.warning("Could not calculate long-term statistics with the current parameters.")
        else:
            with st.container(border=True):
                st.subheader("2. Long-Term Analysis & Recommendation")
                left_col, right_col = st.columns([2, 1])

                with right_col:
                    with st.container(border=True):
                        st.info(
                            "Define the expected delay (lag time) between the monsoon's end and peak landslide movement.")
                        lag_time = st.number_input(
                            "Monitoring Lag Time (days)",
                            min_value=0,
                            max_value=90,
                            value=0,
                            help="How many days *after* the rain stops should monitoring begin?"
                        )

                        st.write("---")
                        st.write("##### Recommended Monitoring Dates")

                        for source in sources:
                            st.markdown(f"**Based on `{source}`**")
                            stats = stats_by_source[source]
                            monitoring_start_earliest = stats['p025_date'] + pd.Timedelta(days=lag_time)
                            monitoring_start_median = stats['median_date'] + pd.Timedelta(days=lag_time)
                            monitoring_start_latest = stats['p975_date'] + pd.Timedelta(days=lag_time)

                            m_col1, m_col2, m_col3 = st.columns(3)
                            m_col1.metric("Earliest", monitoring_start_earliest.strftime('%b %d'),
                                          help="Based on the 2.5th percentile of historical end dates (an unusually early end) plus the defined lag time.")
                            m_col2.metric("Likely", monitoring_start_median.strftime('%b %d'),
                                          help="Based on the historical median end date plus the defined lag time.")
                            m_col3.metric("Latest", monitoring_start_latest.strftime('%b %d'),
                                          help="Based on the 97.5th percentile of historical end dates (an unusually late end) plus the defined lag time.")

                with left_col:
                    full_results_df = pd.concat(results_by_source.values(), ignore_index=True)

                    min_date = full_results_df['DisplayDate'].min() - pd.Timedelta(days=15)
                    max_date = full_results_df['DisplayDate'].max() + pd.Timedelta(days=15)
                    y_domain = [min_date, max_date]

                    color_scheme = alt.Scale(domain=list(sources), range=['#1f77b4', '#ff7f0e'])

                    points = alt.Chart(full_results_df).mark_point(filled=True, size=60).encode(
                        x=alt.X('Year:O', title='Year'),
                        y=alt.Y(
                            'DisplayDate:T',
                            title='Date',
                            axis=alt.Axis(format='%b %d'),
                            scale=alt.Scale(domain=y_domain)
                        ),
                        color=alt.Color('source:N', scale=color_scheme, legend=alt.Legend(title="Dataset")),
                        tooltip=[
                            alt.Tooltip('Year:O'),
                            alt.Tooltip('EndDate:T', title='End Date', format='%B %d, %Y'),
                            alt.Tooltip('source:N', title='Source')
                        ]
                    )

                    stat_layers = []
                    for source, stats in stats_by_source.items():
                        color = color_scheme.range[list(sources).index(source)]

                        ci_band_df = pd.DataFrame({
                            'lower_bound': [stats['p025_date']],
                            'upper_bound': [stats['p975_date']],
                            'start_year': [stats['min_year']],
                            'end_year': [stats['max_year']]
                        })

                        ci_band = alt.Chart(ci_band_df).mark_rect(opacity=0.2, color=color).encode(
                            x='start_year:O',
                            x2='end_year:O',
                            y='lower_bound:T',
                            y2='upper_bound:T'
                        )

                        median_line = alt.Chart(pd.DataFrame({'median': [stats['median_date']]})) \
                            .mark_rule(strokeWidth=2, color=color).encode(y='median:T')

                        stat_layers.extend([ci_band, median_line])

                    final_chart = alt.layer(*stat_layers, points).properties(
                        title=f"Monsoon End Date | Thresholds: <= {dry_day_threshold}mm for {consecutive_days} days"
                    ).interactive()

                    st.altair_chart(final_chart, use_container_width=True)
                    st.caption(
                        "Shaded bands represent the 95% confidence interval for each dataset. Solid lines are the medians.")

            if dataset_choice != "Compare Both datasets":
                st.subheader("3. Detailed Single-Year Analysis")
                with st.container(border=True):
                    single_results_df = results_by_source[sources[0]]
                    years_monsoon = sorted(single_results_df['Year'].unique(), reverse=True)
                    selected_year_monsoon = st.selectbox("Select a Year to Analyze in Detail", years_monsoon,
                                                         key="monsoon_year")

                    year_plot_df = df_timeseries[df_timeseries.index.year == selected_year_monsoon]
                    analysis_start_date = datetime.date(selected_year_monsoon, analysis_start_month, 1)
                    monsoon_end_date = get_monsoon_end_date(year_plot_df, analysis_start_date, dry_day_threshold,
                                                            consecutive_days)

                    if monsoon_end_date:
                        st.success(
                            f"**Estimated Monsoon End Date for {selected_year_monsoon}: {monsoon_end_date.strftime('%B %d, %Y')}**")
                    else:
                        st.warning("No period matching the criteria found for this year. Try adjusting the thresholds.")

                    year_chart_df = year_plot_df.reset_index()
                    year_chart_df.columns = ['Date', 'Rainfall (mm)', 'Source']

                    bar_chart = alt.Chart(year_chart_df).mark_bar().encode(x=alt.X('Date:T', title='Date'),
                                                                           y=alt.Y('Rainfall (mm):Q',
                                                                                   title='Daily Rainfall (mm)'))
                    start_rule = alt.Chart(pd.DataFrame({'date': [analysis_start_date]})).mark_rule(color='gray',
                                                                                                    strokeDash=[4, 4],
                                                                                                    size=2).encode(
                        x='date:T')
                    if monsoon_end_date:
                        end_rule = alt.Chart(pd.DataFrame({'date': [monsoon_end_date]})).mark_rule(color='red',
                                                                                                   strokeWidth=2).encode(
                            x='date:T')
                        final_chart_single_year = (bar_chart + start_rule + end_rule).properties(
                            title=f"Daily Rainfall for {selected_year_monsoon}").interactive()
                    else:
                        final_chart_single_year = (bar_chart + start_rule).properties(
                            title=f"Daily Rainfall for {selected_year_monsoon}").interactive()

                    st.altair_chart(final_chart_single_year, use_container_width=True)
                    st.caption(
                        "The dashed grey line indicates the start of the analysis period. The solid red line indicates the estimated monsoon end date.")

    # --- Tab 2: General Rainfall Analysis ---
    with tab2:
        st.subheader("General Rainfall Analysis")
        st.info(
            "Use this tab to explore the rainfall data. Select a year or a custom date range, change the aggregation level (e.g., Daily, Weekly), and visualize the results in a chart and table.")
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
            freq_map = {"Daily": "D", "Weekly": "W-MON", "Monthly": "MS", "Yearly": "AS"}
            df_filtered = df_timeseries.loc[start_date:end_date]

            st.subheader(
                f"Total {agg_mode} Rainfall from {start_date.strftime('%d %b, %Y')} to {end_date.strftime('%d %b, %Y')}")

            plot_df = df_filtered.reset_index()
            plot_df.columns = ['Date', 'Rainfall (mm)', 'Source']

            time_unit_map = {"Daily": "yearmonthdate", "Weekly": "yearweek", "Monthly": "yearmonth", "Yearly": "year"}
            selected_time_unit = time_unit_map[agg_mode]

            legend_selection = alt.selection_point(fields=['Source'], bind='legend')
            zoom_selection = alt.selection_interval(bind='scales', encodings=['x'])

            if agg_mode == "Weekly":
                label_expression = "[timeFormat(datum.value, '%b %d'), 'Week ' + timeFormat(datum.value, '%W')]"
                x_axis = alt.X('Date:T', timeUnit=selected_time_unit, title=agg_mode, scale=alt.Scale(paddingInner=0.1),
                               axis=alt.Axis(labelExpr=label_expression))
                tooltip_date = alt.Tooltip('Date:T', format="%Y-%m-%d", title="Week Starting")
            else:
                x_axis = alt.X('Date:T', timeUnit=selected_time_unit, title=agg_mode, scale=alt.Scale(paddingInner=0.1))
                tooltip_date = alt.Tooltip('Date:T', timeUnit=selected_time_unit, title=agg_mode)

            if dataset_choice == "Compare Both datasets":
                st.subheader("Comparison of Datasets")

                freq = freq_map.get(agg_mode, "D")
                if not df_filtered.empty:
                    y_max = df_filtered.groupby([pd.Grouper(freq=freq), 'source'])['rain (mm)'].sum().max()
                else:
                    y_max = 0

                color_map = {
                    "IMD 0.1deg (1991-2023)": "#1f77b4",
                    "IMD 0.25deg (2010-2024)": "#ff7f0e"
                }

                source_charts = []
                for source in sorted(plot_df['Source'].unique()):
                    source_df = plot_df[plot_df['Source'] == source]
                    source_chart = alt.Chart(source_df).mark_bar(tooltip=True).encode(
                        x=x_axis,
                        y=alt.Y('sum(Rainfall (mm)):Q', title=f'{agg_mode} Rainfall (mm)',
                                scale=alt.Scale(domain=[0, y_max])),
                        color=alt.value(color_map.get(source, 'grey')),
                        tooltip=[
                            tooltip_date,
                            alt.Tooltip('sum(Rainfall (mm)):Q', title='Total Rainfall (mm)', format='.2f')
                        ]
                    ).properties(
                        height=200,
                        title=source
                    )
                    source_charts.append(source_chart)

                if source_charts:
                    final_chart = alt.vconcat(*source_charts)
                    final_chart_with_zoom = final_chart.add_params(zoom_selection)
                    st.altair_chart(final_chart_with_zoom, use_container_width=True)

            else:
                chart = alt.Chart(plot_df).mark_bar(tooltip=True).encode(
                    x=x_axis,
                    y=alt.Y('sum(Rainfall (mm)):Q', title=f'{agg_mode} Rainfall (mm)'),
                    color='Source:N',
                    xOffset='Source:N',
                    opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.2)),
                    tooltip=[
                        tooltip_date,
                        alt.Tooltip('sum(Rainfall (mm)):Q', title='Total Rainfall (mm)', format='.2f'),
                        'Source:N'
                    ]
                ).add_params(
                    legend_selection, zoom_selection
                ).properties(height=400)
                st.altair_chart(chart, use_container_width=True)

            st.subheader("Analysis & Export")
            with st.container(border=True):
                freq = freq_map.get(agg_mode, "D")

                df_pivot = df_filtered.reset_index().pivot_table(
                    index='time',
                    columns='source',
                    values='rain (mm)'
                )
                table_df = df_pivot.resample(freq).sum()

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
                kpi_cols[0].metric(
                    "Total Rainfall",
                    f"{total_rainfall:.2f} mm",
                    help="The sum of all rainfall (mm) within the selected date range."
                )
                kpi_cols[1].metric(
                    "Avg. Daily Rainfall",
                    f"{avg_daily_rainfall:.2f} mm",
                    help="The average rainfall (mm) per day over the selected period."
                )
                if peak_date:
                    kpi_cols[2].metric(
                        f"Peak Day ({peak_date.strftime('%b %d, %Y')})",
                        f"{peak_value:.2f} mm",
                        help="The day with the highest recorded rainfall in the selected period."
                    )
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

    # --- Tab 3: Climatology & Anomaly ---
    with tab3:
        if dataset_choice == "Compare Both datasets":
            st.warning("This tool is not available when comparing both datasets.")
        else:
            left_col, right_col = st.columns([1, 2])

            with left_col:
                st.subheader("Climatology & Anomaly")
                st.info(
                    "This tool compares a selected year's rainfall against the long-term daily average (climatology) to identify wetter or drier periods.")

                with st.container(border=True):
                    years_clim = sorted(df_timeseries.index.year.unique(), reverse=True)
                    selected_year_clim = st.selectbox("Select Year for Analysis", years_clim, key="clim_year")

            # --- Calculations ---
            year_df = df_timeseries[df_timeseries.index.year == selected_year_clim].copy()
            climatology_df = df_timeseries[df_timeseries.index.year != selected_year_clim]
            climatology = climatology_df.groupby([climatology_df.index.month, climatology_df.index.day])[
                'rain (mm)'].mean().rename("long_term_avg")
            year_df['month'] = year_df.index.month
            year_df['day'] = year_df.index.day
            year_df = pd.merge(year_df, climatology, left_on=['month', 'day'], right_index=True, how='left')
            year_df['anomaly'] = year_df['rain (mm)'] - year_df['long_term_avg']
            plot_df_clim = year_df.reset_index()

            with right_col:
                st.write(f"**Daily Rainfall for {selected_year_clim} vs. Long-Term Average**")
                st.caption("Bars show daily rainfall. The red line shows the historical average for that day.")

                base = alt.Chart(plot_df_clim)
                bars = base.mark_bar(opacity=0.6).encode(
                    x=alt.X('time:T', title='Date'),
                    y=alt.Y('rain (mm):Q', title='Rainfall (mm)'),
                    tooltip=[alt.Tooltip('time:T', title='Date'),
                             alt.Tooltip('rain (mm):Q', format='.2f', title='Rainfall')]
                )
                line = base.mark_line(color='firebrick', strokeWidth=2).encode(
                    x=alt.X('time:T'),
                    y=alt.Y('long_term_avg:Q', title='Avg. Rainfall (mm)'),
                    tooltip=[alt.Tooltip('time:T', title='Date'),
                             alt.Tooltip('long_term_avg:Q', format='.2f', title='Avg. Rainfall')]
                )
                st.altair_chart((bars + line).interactive(), use_container_width=True)

                st.write(f"**Rainfall Anomaly for {selected_year_clim}**")
                st.caption("Blue bars are wetter than average; brown bars are drier than average.")

                anomaly_chart = alt.Chart(plot_df_clim).mark_bar().encode(
                    x=alt.X('time:T', title='Date'),
                    y=alt.Y('anomaly:Q', title='Rainfall Anomaly (mm)'),
                    color=alt.condition(alt.datum.anomaly > 0, alt.value('steelblue'), alt.value('saddlebrown')),
                    tooltip=['time:T', alt.Tooltip('anomaly:Q', format='.2f')]
                ).properties(height=250).interactive()
                st.altair_chart(anomaly_chart, use_container_width=True)

    # --- Common Elements Below Tabs ---
    st.subheader("Data Location")
    if map_data_list:
        map_df = pd.concat(map_data_list)
        st.map(map_df, zoom=8, size=1000)

        st.write("Coordinates:")
        for index, row in map_df.iterrows():
            if 'source' in row and pd.notna(row['source']):
                st.markdown(f"- **{row['source']}**: Latitude `{row['lat']:.3f}`, Longitude `{row['lon']:.3f}`")
            else:
                st.markdown(f"- Latitude `{row['lat']:.3f}`, Longitude `{row['lon']:.3f}`")

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