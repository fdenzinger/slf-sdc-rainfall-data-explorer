#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# Filename: slf-sdc-rainfall-analysis.py
#
# Description:
#   Downloads 0.25 degree IMD gridded rainfall data and extracts a time series
#   for a specific coordinate.
#   Also processes 0.1 degree IPED gridded data to extract a time series for
#   the same coordinate and plots the result.
#
# Author:
#   Florian Denzinger (SLF Davos)
#
# Created:
#   09.09.2025
#
# Last Modified:
#   09.09.2025
#
# Version:
#   2.4
#
# License:
#   MIT
#
# Contact:
#   florian.denzinger@slf.ch
#
# Requirements:
#   - Python 3
#   - imdlib, netCDF4, pandas, numpy, matplotlib
#
# Usage:
#   python slf-sdc-rainfall-analysis.py
#
# ==============================================================================

# Import necessary libraries
import imdlib as imd
import netCDF4 as nc
import numpy as np
import pandas as pd
import os
from glob import glob
from datetime import date
import matplotlib.pyplot as plt


def download_and_process_imd_data():
    """Downloads and processes the 0.25 degree IMD gridded rainfall data.

    This function uses the 'imdlib' library to download daily rainfall data for
    a specified period and location, then saves the resulting time series to a
    CSV file.
    """
    print("--- Processing IMD 0.25 degree data ---")
    start_yr = 2010
    end_yr = 2025
    variable = 'rain'  # other options are ('tmin'/ 'tmax')
    # NOTE: Please update this path to a valid directory on your system.
    file_dir = './IMD_Download'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
        print(f"Created directory: {file_dir}")

    try:
        data = imd.get_data(variable, start_yr, end_yr, file_dir=file_dir, sub_dir=True)

        # Get data for a given coordinate and convert to csv file
        lat = 30.463
        lon = 79.525
        # NOTE: Please update this path to a valid directory on your system.
        out_dir = './IMD_Download'
        file_name = f'IMD_rainfall_{start_yr}_{end_yr}_{lat}_{lon}.csv'
        output_path = os.path.join(out_dir, file_name)

        data.to_csv(file_name, lat, lon, out_dir)
        print(f"IMD data successfully saved to {output_path}")
    except Exception as e:
        print(f"Could not download or process IMD data. Error: {e}")
        print("Please check your internet connection and if the 'imdlib' library is installed correctly.")


def plot_timeseries(csv_filepath):
    """Reads a CSV file containing a precipitation time series and plots it.

    Args:
        csv_filepath (str): The path to the input CSV file.
    """
    print(f"\nGenerating plot from '{os.path.basename(csv_filepath)}'...")
    try:
        # Read the data, ensuring the 'time' column is parsed correctly
        df_plot = pd.read_csv(csv_filepath, parse_dates=['time'], index_col='time')

        # Create the plot
        fig, ax = plt.subplots(figsize=(15, 7))
        ax.plot(df_plot.index, df_plot['rain (mm)'], label='Daily Precipitation', color='royalblue', linewidth=1)

        # Formatting the plot
        ax.set_title(
            f"Daily Precipitation Time Series\nLat: {df_plot['lat'].iloc[0]:.2f}, Lon: {df_plot['lon'].iloc[0]:.2f}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Precipitation (mm/day)")
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

        # Improve date formatting on the x-axis
        fig.autofmt_xdate()

        # Show the plot
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Could not generate plot. Error: {e}")


def extract_iped_timeseries(data_directory, target_lat, target_lon, output_csv):
    """Extracts a daily precipitation time series from IPED NetCDF files.

    This function iterates through a directory of yearly IPED .nc files,
    finds the grid point closest to the target coordinates, extracts the daily
    precipitation data, compiles it into a single CSV file, and plots the result.

    Args:
        data_directory (str):
            The path to the directory containing the .nc files.
        target_lat (float):
            The target latitude for the time series.
        target_lon (float):
            The target longitude for the time series.
        output_csv (str):
            The file path for the output CSV.
    """
    print("\n--- Processing IPED 0.1 degree data ---")
    search_path = os.path.join(data_directory, 'IPED_mean_*.nc')
    nc_files = sorted(glob(search_path))

    if not nc_files:
        print(f"Error: No NetCDF files found in '{data_directory}' matching the pattern 'IPED_mean_*.nc'")
        print("Please make sure the DATA_FOLDER variable is set correctly.")
        return

    print(f"Found {len(nc_files)} files to process.")

    # Initialize grid info variables
    lat_idx, lon_idx, actual_lat, actual_lon = None, None, None, None

    # --- Find the nearest grid point from the FIRST VALID file ---
    for file_path in nc_files:
        try:
            with nc.Dataset(file_path) as first_valid_file:
                if 'lat' in first_valid_file.variables:
                    lat_var_name = 'lat'
                    lon_var_name = 'lon'
                else:
                    lat_var_name = 'latitude'
                    lon_var_name = 'longitude'

                lats = first_valid_file.variables[lat_var_name][:]
                lons = first_valid_file.variables[lon_var_name][:]

                lat_idx = (np.abs(lats - target_lat)).argmin()
                lon_idx = (np.abs(lons - target_lon)).argmin()

                actual_lat = lats[lat_idx]
                actual_lon = lons[lon_idx]

                print(f"\nGrid information successfully read from: {os.path.basename(file_path)}")
                print(f"Target coordinates: (Lat: {target_lat}, Lon: {target_lon})")
                print(f"Closest grid point found: (Lat: {actual_lat:.2f}, Lon: {actual_lon:.2f})")

                break
        except Exception as e:
            print(
                f"Warning: Could not read grid info from {os.path.basename(file_path)}. It may be corrupt. Error: {e}. Trying next file.")
            continue

    if lat_idx is None or lon_idx is None:
        print("\nError: Could not read grid information from ANY of the NetCDF files. Aborting.")
        return

    all_dates = []
    all_precip = []
    processed_years = []

    for file_path in nc_files:
        print(f"Processing: {os.path.basename(file_path)}")
        try:
            with nc.Dataset(file_path, 'r') as ds:
                pcp_var = ds.variables['pcp']
                # The dimensions are (lat, lon, time), so the time dimension is the 3rd one (index 2)
                time_dim_name = pcp_var.dimensions[2]
                time_var = ds.variables[time_dim_name]
                main_time_var = ds.variables.get('time', time_var)

                datetime_objects = nc.num2date(time_var[:], units=main_time_var.units, calendar=main_time_var.calendar)
                dates_only = [date(dt.year, dt.month, dt.day) for dt in datetime_objects]

                # Correct slice for (lat, lon, time) dimension order
                precip_data = pcp_var[lat_idx, lon_idx, :]

                # --- VALIDATION CHECK ---
                # Ensure the number of dates matches the number of data points
                if len(dates_only) != len(precip_data):
                    print(f"  -> WARNING: Inconsistent data in {os.path.basename(file_path)}. "
                          f"Found {len(dates_only)} dates and {len(precip_data)} data points. Skipping this file.")
                    continue  # Skip to the next file

                filled_precip_data = np.ma.filled(precip_data, fill_value=0)

                all_dates.extend(dates_only)
                all_precip.extend(filled_precip_data)

                # Add year to processed list for diagnostics
                year = os.path.basename(file_path).split('_')[-1].split('.')[0]
                processed_years.append(year)

        except Exception as e:
            print(f"  -> Could not process file {file_path}. Error: {e}")

    if not all_dates:
        print("\nIPED extraction failed. No data was processed.")
        return

    # --- DIAGNOSTIC SUMMARY ---
    print(f"\nSuccessfully processed data for years: {sorted(list(set(processed_years)))}")

    # Create initial DataFrame
    df = pd.DataFrame({
        'date': all_dates,
        'precipitation_mm': all_precip
    })

    df['date'] = pd.to_datetime(df['date'])

    # Aggregate data in case of any duplicate dates
    df = df.groupby('date').sum()

    # Create a complete date range from the min to max date found
    full_date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')

    # Reindex to fill any missing days, and fill missing precipitation with 0
    df = df.reindex(full_date_range)
    df['precipitation_mm'] = df['precipitation_mm'].fillna(0)

    # Add coordinates and forward-fill them for the new empty rows
    df['latitude'] = actual_lat
    df['longitude'] = actual_lon

    # Use modern pandas methods to fill missing values and avoid FutureWarnings
    df[['latitude', 'longitude']] = df[['latitude', 'longitude']].ffill().bfill()

    # Reset index to make 'date' a column again
    df.reset_index(inplace=True)

    # --- RENAME AND REORDER ---
    df.rename(columns={
        'index': 'time',
        'precipitation_mm': 'rain (mm)',
        'latitude': 'lat',
        'longitude': 'lon'
    }, inplace=True)

    df = df[['time', 'rain (mm)', 'lat', 'lon']]

    # Write the CSV without the DataFrame index
    df.to_csv(output_csv, index=False)
    print(f"\nSuccess! IPED time series extracted and saved to '{output_csv}'")
    print(f"Total number of days in continuous series: {len(df)}")

    # --- QUICK PLOT OF THE RESULTS ---
    plot_timeseries(output_csv)


if __name__ == '__main__':

    # --- Part 1: IMD Data Processing ---
    # download_and_process_imd_data()

    # --- Part 2: IPED Data Processing ---
    DATA_FOLDER = r'/Users/denzinge/Documents/SLF/SDC_India/WP1/Patalganga_Data/MeteoData/03_IPED_RES_0P10/IPED_Mean'
    TARGET_LATITUDE = 30.463
    TARGET_LONGITUDE = 79.525
    OUTPUT_FILENAME = '/Users/denzinge/Documents/SLF/SDC_India/WP1/Patalganga_Data/MeteoData/03_IPED_RES_0P10/patalganga_IPED_rainfall_data_30.463_79.525_1991_2023.csv'

    extract_iped_timeseries(DATA_FOLDER, TARGET_LATITUDE, TARGET_LONGITUDE, OUTPUT_FILENAME)

