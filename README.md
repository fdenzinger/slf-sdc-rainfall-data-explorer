# SLF SDC2: Rainfall Data Explorer
## An Interactive Web Application for Rainfall Analysis

[![Built with Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/) [![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io) [![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Status:** Actively Developed (as of July 2025)

An interactive web application built with Streamlit for the analysis and visualization of a specific daily rainfall dataset. This tool allows users to explore rainfall patterns, estimate monsoon withdrawal dates, and analyze climatological anomalies.

---

The app is hosted on Streamlit Cloud and can be accessed [here](https://slf-sdc-rainfall-data-explorer.streamlit.app/).

![App Screenshot](docs/markdown/assets/SLF_SDC_Rainfall_DataExplorer.gif)

---

## Table of Contents

- [Features](#features)
- [Installation & Usage](#installation--usage)
- [License](#license)

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

This guide assumes you have a Mamba/Conda installation. For a new, minimal, open-source setup, we recommend installing Miniforge from the [official repository](https://github.com/conda-forge/miniforge?tab=readme-ov-file#install). Miniforge is pre-configured to use the `conda-forge` channel and includes the fast `mamba` package manager by default.

**Steps:**


1. Clone the repository & navigate into its directory
```bash
git clone "https://github.com/fdenzinger/slf-sdc-rainfall-data-explorer.git" slf-sdc-rainfall-data-explorer
cd slf-sdc-rainfall-data-explorer
```

2. Create and activate the environment with Mamba (this may take a few minutes).

Mamba is a fast, parallel replacement for Conda and comes with Miniforge.
```bash
mamba env create -f env/environment.yml
conda activate slf-sdc-rainfall-data-explorer
```

3. Run the Streamlit app

To run the Streamlit app locally, run the following command in your terminal:

```bash
streamlit run slf-sdc-rainfall-app.py
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/fdenzinger/slf-sdc-rainfall-data-explorer/tree/main?tab=MIT-1-ov-file) file for details.

---

## Collaborators

The project is developed by the following contributors:

<div align="left">
  <a href="https://github.com/fdenzinger">
    <img src="https://avatars.githubusercontent.com/fdenzinger" alt="fdenzinger" width="100" style="border-radius: 50%"><br>
    Florian Denzinger
  </a>
</div>

---
© 2025 WSL Institute for Snow and Avalanche Research SLF
