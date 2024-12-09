import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import gdown  # To download files from Google Drive

# Function to download dataset from Google Drive
@st.cache_data
def download_and_load_data(drive_url, filename):
    try:
        file_id = drive_url.split('/')[-2]  # Extract file ID from the link
        gdown.download(f"https://drive.google.com/uc?id={file_id}", filename, quiet=False)
        return pd.read_csv(filename)
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return pd.DataFrame()

# Google Drive links for datasets
drive_links = {
    "Benin-Malanville": "https://drive.google.com/file/d/1UUQLPW5uPlTBHn4ydYCVn59RfF5a0fOl/view?usp=drive_link",
    "Sierra Leone-Bumbuna": "https://drive.google.com/file/d/1LU2uzALN26Uj4b4Ez7FT9o2whMrkctW1/view?usp=sharing",
    "Togo-Dapaong_QC": "https://drive.google.com/file/d/1KJLvtnlPzv7Ov_Ve_zVeVhBmrNrFK9Fc/view?usp=sharing"
}

# Sidebar for dataset selection
st.sidebar.title("Dataset Selection")
dataset_name = st.sidebar.selectbox(
    "Select Dataset",
    ["Benin-Malanville", "Sierra Leone-Bumbuna", "Togo-Dapaong_QC"]
)

# Load selected dataset
data = download_and_load_data(drive_links.get(dataset_name), f"{dataset_name.replace(' ', '_')}.csv")

# Display title
st.title(f"Exploratory Data Analysis for {dataset_name}")

# Show Raw Data
if st.checkbox("Show Raw Data"):
    st.write(data)

# Summary Statistics
st.header("Summary Statistics")
if not data.empty:
    st.write(data.describe())
else:
    st.warning("Dataset is empty or could not be loaded.")

# Missing Values
st.header("Missing Values")
if not data.empty:
    missing_values = data.isnull().sum()
    st.write(missing_values)

# Correlation Heatmap
st.header("Correlation Heatmap")
if not data.empty:
    numeric_data = data.select_dtypes(include=["float64", "int64"])  # Select numeric columns
    if not numeric_data.empty:
        correlation = numeric_data.corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No numeric columns available for correlation analysis.")

# Time Series Analysis
if "Timestamp" in data.columns:
    st.header("Time Series Analysis")
    try:
        data["Timestamp"] = pd.to_datetime(data["Timestamp"])
        data.set_index("Timestamp", inplace=True)
        if "GHI" in data.columns:
            ghi_plot = data["GHI"].resample("D").mean()
            fig, ax = plt.subplots()
            ghi_plot.plot(ax=ax, title="Daily GHI Over Time", ylabel="GHI (W/m²)")
            st.pyplot(fig)
        else:
            st.warning("'GHI' column not found for time series analysis.")
    except Exception as e:
        st.error(f"Error processing time series: {e}")

# Distribution Plots
st.header("Distribution of Key Variables")
numeric_columns = data.select_dtypes(include=["float64", "int64"]).columns
if not numeric_columns.empty:
    key_variable = st.selectbox("Select Variable", numeric_columns)
    fig = px.histogram(data, x=key_variable, nbins=30, title=f"Distribution of {key_variable}")
    st.plotly_chart(fig)
else:
    st.warning("No numeric columns available for distribution plots.")

# Wind Analysis (Radial Plot)
if "WD" in data.columns and "WS" in data.columns:
    st.header("Wind Analysis")
    wind_rose = px.scatter_polar(
        data, r="WS", theta="WD", title="Wind Speed and Direction",
        color="WS", color_continuous_scale=px.colors.sequential.Plasma
    )
    st.plotly_chart(wind_rose)

# Cleaning Impact
if "Cleaning" in data.columns:
    st.header("Impact of Cleaning on Sensor Measurements")
    cleaning_group = data.groupby("Cleaning")[["ModA", "ModB"]].mean()
    st.write(cleaning_group)

# Bubble Chart Analysis
st.header("Bubble Chart Analysis")
bubble_x = st.selectbox("X-Axis Variable", data.select_dtypes(include=['float64', 'int64']).columns)
bubble_y = st.selectbox("Y-Axis Variable", data.select_dtypes(include=['float64', 'int64']).columns)
bubble_size = st.selectbox("Bubble Size Variable", data.select_dtypes(include=['float64', 'int64']).columns)

# Handle negative or invalid values in the size column
data[bubble_size] = data[bubble_size].clip(lower=0)  # Clip negative values to 0

fig = px.scatter(
    data,
    x=bubble_x,
    y=bubble_y,
    size=bubble_size,
    title=f"Bubble Chart: {bubble_x} vs {bubble_y} (Size: {bubble_size})",
    size_max=60  # Optional: Control maximum bubble size
)
st.plotly_chart(fig)
