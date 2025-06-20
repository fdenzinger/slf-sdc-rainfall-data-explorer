# SDC2: Rainfall Data Explorer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An interactive web application built with Streamlit for the analysis and visualization of a specific daily rainfall dataset. This tool allows users to explore rainfall patterns, estimate monsoon withdrawal dates, and analyze climatological anomalies.

---

## Features

The application is organized into three main tabs, each providing a distinct set of analytical tools:

### 1. General Rainfall Analysis
- **Flexible Timeframes:** View data for a specific year or select a custom date range.
- **Multiple Aggregation Levels:** Aggregate rainfall totals **Daily**, **Weekly**, **Monthly**, or **Yearly**.
- **Key Performance Indicators (KPIs):** Instantly see key stats for the selected period, including:
    - Total Rainfall
    - Average Daily Rainfall
    - Peak Rainfall Day and Amount
- **Data Export:** Download the aggregated data as a CSV file for offline analysis.
- **Interactive Charts:** Visualize data through interactive bar charts powered by Altair.

### 2. Monsoon End Date Estimator
- **Algorithmic Estimation:** Automatically estimates the monsoon withdrawal date based on a sustained dry period.
- **Customizable Parameters:** Fine-tune the algorithm by setting:
    - The **analysis start date** (to avoid pre-monsoon dry spells).
    - The **'dry day' threshold** (mm) to define what counts as a dry day.
    - The required number of **consecutive dry days** to confirm the withdrawal.
- **Visual Feedback:** The estimated monsoon end date is clearly marked with a vertical line on the year's rainfall chart.

### 3. Climatology & Anomaly
- **Long-Term Comparison:** Compare a selected year's daily rainfall against the long-term daily average (climatology) calculated from all other years in the dataset.
- **Dual Visualization:**
    1.  An overlay chart showing the selected year's daily rainfall bars and the long-term average as a line.
    2.  A rainfall anomaly chart, highlighting days that were wetter (blue) or drier (brown) than the historical average.
- **Identify Trends:** Easily spot significant deviations from the norm, such as prolonged droughts or exceptionally wet periods.

---

## Data Source

The application uses a specific rainfall dataset located in the Indian Himalayas.

-   **Coordinates:** 30.463° N, 79.525° E
-   **Data URL:** [rainfall_data_30.463_79.525.csv](https://raw.githubusercontent.com/fdenzinger/slf-sdc-rainfall-data-explorer/refs/heads/main/data/rainfall_data_30.463_79.525.csv)

The location of the dataset is also displayed on an interactive map at the bottom of the application.

---

## Installation & Usage

To run this application on your local machine, please follow these steps.

### Prerequisites
- [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.

### 1. Clone the Repository
```bash
git clone [https://github.com/fdenzinger/slf-sdc-rainfall-data-explorer.git](https://github.com/fdenzinger/slf-sdc-rainfall-data-explorer.git)
cd slf-sdc-rainfall-data-explorer
```

### 2. Create and Activate a Conda Environment

This command creates a new conda environment named rainfall-app with Python 3.12 and activates it.
```bash
conda create --name rainfall-app python=3.12
conda activate rainfall-app
```

### 3. Install Required Packages

Install the packages directly using conda. This is the recommended method for managing dependencies in a conda environment. We will specify the conda-forge channel as it provides a wide range of up-to-date packages.

```bash 
conda install -c conda-forge pandas streamlit altair
```

### 4. Run the Streamlit App

Once the packages are installed, run the following command in your terminal:
```bash
streamlit run slf-sdc-rainfall-app.py
```

Your web browser should automatically open a new tab with the running application.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
