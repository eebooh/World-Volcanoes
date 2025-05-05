"""
Name: Ebrahim Alkhalifa
Course Section: CS-230-4
Date of File Creation: 4/29/2025
Data: volcanoes.csv
URL:
Program Purpose: The aim of this program is to make use of the streamlit package to create an interactive website about
volcanoes around the world. This aims to provide various ways to display the data in a fun and interactive way for the
audience.
"""
import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ----------------- [PY1] Function with default param & multiple calls -----------------
# [DA2] Sorting – used in get_top_volcanoes()
# [DA3] Top N – show tallest volcanoes
def get_top_volcanoes(df, n=5):
    return df.nlargest(n, 'Elevation (m)')[['Volcano Name', 'Country', 'Elevation (m)']]

# [PY2] Function returning multiple values
def get_summary_stats(df):
    count = len(df)
    avg = df['Elevation (m)'].mean()
    return count, avg

# [PY3] Error handling during CSV load
# [DA1] Data Cleaning – drop missing values, convert elevation to numeric
def load_data():
    try:
        df = pd.read_csv("volcanoes.csv", encoding="ISO-8859-1")
        df = df.dropna(subset=["Latitude", "Longitude", "Elevation (m)"])
        df["Elevation (m)"] = pd.to_numeric(df["Elevation (m)"], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

#Setting Up the Website
st.title("🌋 Volcanoes Worldwide! 🌋")
df = load_data()

# [PY4] List comprehension for filtering columns (used below)
columns_to_show = [col for col in ["Volcano Name", "Country", "Elevation (m)", "Primary Volcano Type"] if col in df.columns]

# Website Styling [ST4]
st.markdown("""
<style>
.block-container { background-color: #1a1a1a; color: #ffffff; }
section[data-testid="stSidebar"] { background-color: #2a2a2a; color: #ffffff; }
.block-container h1, h2, h3, h4, h5, h6 { color: #ff6f00 !important; }
button[kind="primary"] { background-color: #ff6f00; color: white; }
label, .stTextInput, .stSelectbox, .stSlider { color: white !important; }
.stDataFrame { background-color: #2e2e2e; color: white !important; }
thead tr th, tbody tr td { color: white !important; }
.css-1d391kg table td, .css-1d391kg table th { color: white !important; }
</style>
""", unsafe_allow_html=True)


# Sidebar Filters [ST1, ST2, ST3]
st.sidebar.header("Filter Options")
selected_country = st.sidebar.selectbox("Select Country", options=["All"] + sorted(df["Country"].dropna().unique().tolist()))
selected_type = st.sidebar.selectbox("Select Volcano Type", options=["All"] + sorted(df["Primary Volcano Type"].dropna().unique().tolist()))
elevation_slider = st.sidebar.slider("Minimum Elevation (m)", 0, int(df['Elevation (m)'].max()), 0)

# [DA4, DA5] Apply filters
filtered_df = df.copy()
if selected_country != "All":
    filtered_df = filtered_df[filtered_df["Country"] == selected_country]
if selected_type != "All":
    filtered_df = filtered_df[filtered_df["Primary Volcano Type"] == selected_type]
filtered_df = filtered_df[filtered_df["Elevation (m)"] >= elevation_slider]

# [DA1, DA7, DA9] Data cleaning, column selection, derived category
filtered_df = filtered_df.copy()

# Summary Stats [DA2, DA3]
st.subheader("Summary Stats")
count, avg = get_summary_stats(filtered_df)
st.write(f"Total volcanoes: {count}")
st.write(f"Average elevation: {avg:.2f} m")

st.subheader(f"Top Tallest Volcanoes in {selected_country if selected_country != 'All' else 'the Dataset'}")
#[PY1]
n = 5 if selected_country == "All" else 3
top_volcanoes = get_top_volcanoes(filtered_df, n=n)
st.dataframe(top_volcanoes)

# [CHART1] Seaborn Histogram
st.subheader("Elevation Distribution (Smoothed)")
elevations = filtered_df["Elevation (m)"].dropna()
fig, ax = plt.subplots(figsize=(8, 4))
fig, ax = plt.subplots(figsize=(10, 4))
bins = np.arange(0, elevations.max() + 500, 500)

# Orange bars, white edge
sns.histplot(
    elevations,
    bins=bins, #Makes sure the bins are divided as desired
    color="#ff6f00",          # Volcano orange
    edgecolor="white",        # White border
    linewidth=1.2,            # Border thickness
    ax=ax                     # Makes sure the axes are in the correct places for the chart
)
ax.set_xlabel("Elevation (meters)")
ax.set_ylabel("Number of Volcanoes")
ax.set_title("Elevation Histogram")
ax.set_xticks(bins)
plt.xticks(rotation=45) #Rotation 45 degrees for ticks
st.pyplot(fig)

# [Seaborn 2] Histogram of Elevation by Type
st.subheader("Elevation Distribution by Volcano Type")
top_types = filtered_df['Primary Volcano Type'].value_counts().head(5).index #Gets the top 5 most common types to compare
filtered_top = filtered_df[filtered_df['Primary Volcano Type'].isin(top_types)] #
fig3, ax3 = plt.subplots(figsize=(10, 4))
sns.boxplot(data=filtered_top, x='Primary Volcano Type', y='Elevation (m)', ax=ax3, palette="Oranges")
ax3.set_title("Elevation Distribution by Volcano Type")
ax3.set_ylabel("Elevation (m)")
ax3.set_xlabel("Volcano Type")
plt.xticks(rotation=30)
st.pyplot(fig3)

# [CHART 3] Volcano count by type
st.subheader("Volcano Count by Type")
type_counts = filtered_df['Primary Volcano Type'].value_counts().head(15)
fig2, ax2 = plt.subplots(figsize=(10, 6))
type_counts.plot(kind='barh', color='#ff6f00', ax=ax2) #horizontal bar chart, that's orange
ax2.set_title("Top Volcano Types")
ax2.set_xlabel("Number of Volcanoes")
ax2.set_ylabel("Volcano Type")
# Add clean tick marks every 10 (or 5 if values are low)
max_val = type_counts.max()
tick_interval = 30 if max_val >= 50 else 5
ax2.set_xticks(np.arange(0, max_val + tick_interval, tick_interval))
st.pyplot(fig2)

# [MAP] Pydeck volcano map
st.subheader("Estimated Eruption Impact Map")
filtered_df["Impact Radius"] = filtered_df["Elevation (m)"].clip(upper=3000) * 100
#Capped at 3000 for no extreme values, and * 100 to emulate real meters instead of virtual units
if not filtered_df.empty:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/satellite-streets-v12",
        initial_view_state=pdk.ViewState( #Centers the view around the mean of the latitude and longitude
            latitude=filtered_df["Latitude"].mean(),
            longitude=filtered_df["Longitude"].mean(),
            zoom=3.5,   # Slight zoom-in for better visibility
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=filtered_df,
                get_position='[Longitude, Latitude]',
                get_radius="Impact Radius",
                radius_scale=1,                  # Real-world scaling
                radius_min_pixels=5,             # Makes them visible no matter how small
                get_fill_color='[255, 69, 0, 140]',
                get_line_color='[255, 255, 255]',
                pickable=True #Allows hovering over each point
            )
        ],
        tooltip={"text": "🌋 {Volcano Name}\nEstimated Impact Radius: {Impact Radius} meters"} #Hovering over point info
    ))
else:
    st.info("No data to display on the map.")
st.caption("Note: Circle size reflects estimated affected radius based on elevation (approx. 10 meters per elevation meter).")