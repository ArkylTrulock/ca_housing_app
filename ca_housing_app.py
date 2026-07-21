
#-------------------------------------------------------------------------------------------------------------------------
# Imported libraries
#-------------------------------------------------------------------------------------------------------------------------
import os
import jinja2
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio                        
from streamlit_dynamic_filters import DynamicFilters
import warnings
warnings.filterwarnings('ignore')
#-------------------------------------------------------------------------------------------------------------------------
# Page config (must come before any st.* calls) - This is your html page name!
st.set_page_config(page_title="🏠📊 California Housing Market Dashboard App 😎👌", page_icon="🧊", layout="wide", initial_sidebar_state="auto", menu_items={'Get help':'mailto:tailback33@hotmail.com'})

# Set title
st.title("**🏠📊 :blue[California Housing Market Dashboard] 😎👌**", width="stretch", text_alignment="left")
# -------------------------------------------------------------------------------------------------------------------------
# Streamlit will not deploy the app with code below
# # Path to your CSV (adjust as needed)
# file_path = os.path.expanduser(
#     "~/Python-Documents/os/CSV Files/California_Housing_Market_Data_Analysis_modified_4.csv"
# )

# # Load data (cached)
# @st.cache_data
# def load_data(path):
#     df = pd.read_csv(path)
#     # strip whitespace from column names
#     df.columns = df.columns.str.strip()
#     return df

# df = load_data(file_path)
# -------------------------------------------------------------------------------------------------------------------------
# Streamlit will deploy the app with code below
# 1) Base dir of this script
BASE_DIR = Path(__file__).resolve().parent

# 2) Try relative path (CSV now in your repo)
REL_PATH = BASE_DIR / "California_Housing_Market_Data_Analysis_modified_4.csv"
# If you moved it into data/, do:
# REL_PATH = BASE_DIR / "data" / "California_Housing_Market_Data_Analysis_modified_4.csv"

# 3) Fallback to your local Windows path only if the relative one isn't there
if REL_PATH.exists():
    file_path = REL_PATH
else:
    #file_path = Path(r"C:\Users\tailb\Python-Documents\os\CSV Files\California_Housing_Market_Data_Analysis_modified_4.csv")
    file_path = os.path.expanduser("~/Python-Documents/os/CSV Files/California_Housing_Market_Data_Analysis_modified_4.csv")

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

df = load_data(file_path)
# -------------------------------------------------------------------------------------------------------------------------
# Streamlit will deploy the app with code below
# CSV_URL = (
#   "https://raw.githubusercontent.com/"
#   "ArkylTrulock/ca_housing_app/main/"
#   "California_Housing_Market_Data_Analysis_modified_4.csv"
# )

# @st.cache_data
# def load_data(url: str) -> pd.DataFrame:
#     df = pd.read_csv(url)
#     df.columns = df.columns.str.strip()
#     return df

# df = load_data(CSV_URL)
# -------------------------------------------------------------------------------------------------------------------------
# # (Optional) Debug: show columns so you can confirm exact names
# st.write("Columns in df:", df.columns.tolist())
# -------------------------------------------------------------------------------------------------------------------------
# Wrap all filters in a collapsible Expander
with st.sidebar.expander("**:red[🔍 Housing Features Filter]**", expanded=True, width="stretch"):
    locations   = df["location_name"].unique().tolist()
    oceans      = df["ocean_proximity"].unique().tolist()
    risks       = df["Risk"].unique().tolist()
    returns     = df["Return"].unique().tolist()
    strategies  = df["Best Strategy"].unique().tolist()
    clusters    = df["Cluster"].unique().tolist()
    
    # Filter order 1
    # selected_locations  = st.multiselect("**:orange[📍 Location Name Filter]**", options=locations, default=locations,)
    # selected_oceans     = st.multiselect("**:yellow[🌊 Ocean Proximity Filter]**", options=oceans, default=oceans,)
    # selected_risks      = st.multiselect("**:red[⚠️ Property Risk Profile Filter]**", options=risks, default=risks,)
    # selected_returns    = st.multiselect("**:green[💰 Investment Return Potential Filter]**", options=returns, default=returns,)
    # selected_strategies = st.multiselect("**:blue[🏡 Housing Strategy Filter]**", options=strategies, default=strategies,)
    # selected_clusters   = st.multiselect("**:violet[✨ Cluster Filter]**", options=clusters, default=clusters,)
    
    # Filter order 2
    selected_locations  = st.multiselect("**:orange[📍 Location Name Filter]**", options=locations, default=locations,)
    selected_oceans     = st.multiselect("**:yellow[🌊 Ocean Proximity Filter]**", options=oceans, default=oceans,)
    selected_strategies = st.multiselect("**:blue[🏡 Housing Strategy Filter]**", options=strategies, default=strategies,)
    selected_risks      = st.multiselect("**:red[⚠️ Property Risk Profile Filter]**", options=risks, default=risks,)
    selected_returns    = st.multiselect("**:green[💰 Investment Return Potential Filter]**", options=returns, default=returns,)
    selected_clusters   = st.multiselect("**:violet[✨ Cluster Filter]**", options=clusters, default=clusters,)

# Apply both filters in one go with pandas query
df = df.query("location_name in @selected_locations \
              and ocean_proximity in @selected_oceans \
              and Risk in @selected_risks \
              and Return in @selected_returns \
              and `Best Strategy` in @selected_strategies \
              and Cluster in @selected_clusters")
# df = df.query("ocean_proximity in @selected_oceans and `Best Strategy Short` in @selected_strategies and Cluster in @selected_clusters")
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Build dataframe summary for horizontal bar plot (1 & 2) & bar plot (3 & 4)
c_loc_op = (
    df
    .groupby(
        ['Cluster', 'location_name', 'ocean_proximity']
    )['median_house_value']
    .agg(['count', 'min', 'max', 'mean', 'median', 'sum'])
    .round(2)
    .reset_index()
    # compute proportion of total properties
    .assign(proportion=lambda x: x['count'] / x['count'].sum())
)

# Add rank columns for count, median & sum
c_loc_op['count_rank']  = c_loc_op['count'].rank(ascending=False)
c_loc_op['median_rank'] = c_loc_op['median'].rank(ascending=False)
c_loc_op['sum_rank']    = c_loc_op['sum'].rank(ascending=False)

# Sort dataFrame so the highest‐sum counties come first
c_loc_op = c_loc_op.sort_values('sum', ascending=False)
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Summary Table: Property Count & Value by Location & Ocean Proximity
# -------------------------------------------------------------------------------------------------------------------------
# # Set summary table expander
# with st.expander("**:blue[📌📶 Summary Table & Barplots (inc. Range Filters): Property Count & Value by Location & Ocean Proximity]**", width="stretch"):

# Set summary table header
st.header("**:red[Property Count & Value by Location & Ocean Proximity:]**", divider="", width="stretch", text_alignment="left")

# Set summary table subheader
st.subheader("**:violet[🔍 Property Count & Value Range Filter:]**", divider="violet", width="stretch", text_alignment="left")

# Count slider
counts = c_loc_op['count'].fillna(0)
min_count = int(counts.min())
max_count = int(counts.max())
count_low, count_high = st.slider("**:orange[Property Count Range]**", min_count, max_count, (min_count, max_count), format="%,.0f")

# Total value slider
# use step=1e6 if you have very large sums
sums = c_loc_op['sum'].fillna(0)
min_val = int(sums.min())
max_val = int(sums.max())
val_low, val_high = st.slider("**:green[Total Property Value Range ($)]**", min_val, max_val, (min_val, max_val), step=1_000_000, format="$%,.0f")

# Set summary table subheader
st.subheader("**:blue[📌 Summary Table: Property Count & Value by Location & Ocean Proximity]**", divider="violet", width="stretch", text_alignment="left")

# Filter summary table
filtered_summary_1 = c_loc_op[(c_loc_op['count'].between(count_low, count_high)) & (c_loc_op['sum'].between(val_low, val_high))]

# # Display summary table in streamlit
# st.write(filtered_summary_1)
#-------------------------------------------------------------------------------------------------------------------------
    # Define numeric values to be formatted
fmt = {
    "min"  :             "${:,.0f}",
    "count":              "{:,.0f}",
    "mean":               "${:,.0f}",
    "max":                "${:,.0f}",
    "mean":               "${:,.0f}",
    "median":             "${:,.0f}",
    "sum":                "${:,.0f}",
    "proportion":         "{:,.2%}",
    "count_rank":         "{:,.0f}",
    "median_rank":        "{:,.0f}",
    "sum_rank":           "{:,.0f}",
}
# List of columns to apply mix/max highlighting
subset_1 = ["min", "max", "count", "mean", "median", "sum", "proportion"]
subset_2 = ["count_rank", "median_rank", "sum_rank"]
min_props_1 = ("color:yellow; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:coral; ")
max_props_1 = ("color:darkgreen; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:yellow; ")
min_props_2 = ("color:darkgreen; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:yellow; ")
max_props_2 = ("color:yellow; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:coral; ")

# Apply formatting & styling
styled_filtered_summary_1 = filtered_summary_1.style.format(fmt)\
    .highlight_min(subset=subset_1, props=min_props_1, axis=0)\
        .highlight_max(subset=subset_1, props=max_props_1, axis=0)\
            .highlight_min(subset=subset_2, props=min_props_2, axis=0)\
                .highlight_max(subset=subset_2, props=max_props_2, axis=0)\
            
# Display styled summary table in streamlit
st.write(styled_filtered_summary_1)
#-------------------------------------------------------------------------------------------------------------------------
# Set horizontal bar plot 1 subheader
st.subheader("**:violet[📶 Horizontal Bar Plot 1: Property Count by Location & Ocean Proximity (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Display horizontal bar plot 1 in streamlit
st.bar_chart(filtered_summary_1, x="location_name", y="count", x_label='Location', y_label='Property Count', 
            color="ocean_proximity", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)

# Set horizontal bar plot 2 subheader
st.subheader("**:violet[📶 Horizontal Bar Plot 2: Property Value by Location & Ocean Proximity (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Display horizontal bar plot 2 in streamlit
st.bar_chart(filtered_summary_1, x="location_name", y="sum", x_label='Location', y_label='Property Value ($)', 
            color="ocean_proximity", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)
# -------------------------------------------------------------------------------------------------------------------------
# # OPTION 2: COUNT & VALUE FILTER IS SIDEBAR EXPANDER
# # Set filter sidebar expander
# with st.sidebar.expander("**:yellow[🔍 Location & Ocean Proximity: Property Count & Value Range Filter]**", width="stretch"):

#     # Count slider
#     counts = c_loc_op['count'].fillna(0)
#     min_count = int(counts.min())
#     max_count = int(counts.max())
#     count_low, count_high = st.slider("**:orange[Property Count Range]**", min_count, max_count, (min_count, max_count), format="%,.0f")

#     # Total value slider
#     # use step=1e6 if you have very large sums
#     sums = c_loc_op['sum'].fillna(0)
#     min_val = int(sums.min())
#     max_val = int(sums.max())
#     val_low, val_high = st.slider("**:green[Total Property Value Range ($)]**", min_val, max_val, (min_val, max_val), step=1_000_000, format="$%,.0f")

# # Set summary table expander
# with st.expander("**:yellow[📌📶 Summary Table & Barplot: Property Count & Value by Location & Ocean Proximity]**", width="stretch"):

#     # Set summary table subheader
#     st.subheader("**:violet[📌 Summary Table: Property Count & Value by Location & Ocean Proximity]**", divider="violet", width="stretch", text_alignment="left")

#     # Filter the summary table
#     filtered_summary_1 = c_loc_op[(c_loc_op['count'].between(count_low, count_high)) & (c_loc_op['sum'].between(val_low, val_high))]
# #-------------------------------------------------------------------------------------------------------------------------
#     # Define numeric values to be formatted
#     fmt = {
#         "min"  :             "${:,.0f}",
#         "count":              "{:,.0f}",
#         "mean":               "${:,.0f}",
#         "max":                "${:,.0f}",
#         "mean":               "${:,.0f}",
#         "median":             "${:,.0f}",
#         "sum":                "${:,.0f}",
#         "proportion":         "{:,.2%}",
#         "count_rank":         "{:,.0f}",
#         "median_rank":        "{:,.0f}",
#         "sum_rank":           "{:,.0f}",
#     }
#     # List of columns to apply mix/max highlighting
#     subset_1 = ["min", "max", "count", "mean", "median", "sum", "proportion"]
#     subset_2 = ["count_rank", "median_rank", "sum_rank"]
#     min_props_1 = ("color:yellow; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:coral; ")
#     max_props_1 = ("color:darkgreen; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:yellow; ")
#     min_props_2 = ("color:darkgreen; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:yellow; ")
#     max_props_2 = ("color:yellow; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:coral; ")

#     # Apply formatting & styling
#     styled_filtered_summary_1 = filtered_summary_1.style.format(fmt)\
#         .highlight_min(subset=subset_1, props=min_props_1, axis=0)\
#             .highlight_max(subset=subset_1, props=max_props_1, axis=0)\
#                 .highlight_min(subset=subset_2, props=min_props_2, axis=0)\
#                     .highlight_max(subset=subset_2, props=max_props_2, axis=0)\
                
#       # Display styled summary table in streamlit
#     st.write(styled_filtered_summary_1)
# #-------------------------------------------------------------------------------------------------------------------------
#     # Display summary table in streamlit
#     # st.write(filtered_summary_1)

#     # Set horizontal bar plot 1 subheader
#     st.subheader("**:violet[📶 Bar Chart 1: Property Count by Location & Ocean Proximity (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

#     # Display horizontal bar plot 1 in streamlit
#     st.bar_chart(filtered_summary_1, x="location_name", y="count", x_label='Location Name', y_label='Property Count', 
#                 color="ocean_proximity", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None) 

#     # Set horizontal bar plot 2 subheader
#     st.subheader("**:violet[📶 Bar Chart 2: Property Value by Location & Ocean Proximity (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

#     # Display horizontal bar plot 2 in streamlit
#     st.bar_chart(filtered_summary_1, x="location_name", y="sum", x_label='Location Name', y_label='Property Value ($)', 
#                 color="ocean_proximity", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)  

# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Bar Plot 1
# -------------------------------------------------------------------------------------------------------------------------
# # Set plot expander
# with st.expander("**:violet[📶 Bar Plot 1: Property Count by Location & Ocean Proximity]**", width="stretch"):

# Set plot subheader
st.subheader("**:violet[📶 Bar Plot 1: Property Count by Location & Ocean Proximity (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# # Build dataframe summary for fig 1 & fig 2
# c_loc_op = (
#     df
#     .groupby(
#         ['Cluster', 'location_name', 'ocean_proximity']
#     )['median_house_value']
#     .agg(['count', 'min', 'max', 'mean', 'median', 'sum'])
#     .round(2)
#     .reset_index()
#     # compute proportion of total properties
#     .assign(proportion=lambda x: x['count'] / x['count'].sum())
# )

# # Add rank columns for count, median & sum
# c_loc_op['count_rank']  = c_loc_op['count'].rank(ascending=False)
# c_loc_op['median_rank'] = c_loc_op['median'].rank(ascending=False)
# c_loc_op['sum_rank']    = c_loc_op['sum'].rank(ascending=False)

# # Sort dataFrame so the highest‐sum counties come first
# c_loc_op = c_loc_op.sort_values('sum', ascending=False)

# Build bar chart
fig1 = px.bar(
    filtered_summary_1,
    x="location_name",
    y="count", # sum
    color="ocean_proximity", 
    barmode="group",                   # "group or "stack" for stacked bars
    text="count",                      #  "count", "median", "sum", "proportion"
    # log_y=True,

    # Format hover_data values
    hover_data={
        "Cluster": True,               # no format change
        "count": ":,.0f",              # ✅ formatted as \1,234
        "mean": ":$,.0f",              # ✅ formatted as \$1,234
        "median": ":$,.0f",            # ✅ formatted as \$1,234
        "proportion": ":.2%",          # ✅ formatted as 15.00%
        "sum": ":$,.0f",               # ✅ formatted as \$1,234
        # "Risk": True,                # no format change
        # "Return":  True,             # no format change 
    },
    color_discrete_map={
        "<1H OCEAN": "turquoise",   
        "NEAR BAY": "orange",     
        "INLAND": "green",       
        "NEAR OCEAN": "lightblue",
    },
)

fig1.update_traces(
    texttemplate="%{text:,.0f}",       # ✅ Formats 1000 → 1,000
    # texttemplate="%{text:$,.0f}",    # ✅ Formats $1000 → $1,000
    # textposition="inside",           #  "inside", "top left", "top center", "top right", "middle left", "middle center", "middle right", "bottom left", "bottom center", "bottom right"
    insidetextanchor="end",            # 'end', 'middle', 'start'
    textangle=-90, #-90
    textfont=dict(family="Tahoma", size=14, color="black"),
    # selector=dict(mode="text"), # textposition="top centre"
)

fig1.update_layout(
    title={
        "text": "<b><u>Property Count by Location & Ocean Proximity</u></b>" # <b> bold, <i> italic, <u> underline, <br> start new line, <sup> open superscript, </>close, 
        "<br><sup>(Bar labels represent property count by location & ocean proximity)</sup>", 
        "x": 0.5,                     # centers the title
        "xanchor": "center", "font": {"family": "tahoma", "size": 16, "color": "red"},
    },
    xaxis_title="<b>Location</b>",    # bold x label
    xaxis=dict(
        color="blue",
        # tickformat="$,.0f",
        tickangle=-45,
        tickfont=dict(family="Tahoma", size=12, color="blue"),
        showgrid=True,                # ✅ Vertical gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    yaxis_title="<b>Property Count</b>", # <b>Total Median House Value ($)</b>
    yaxis=dict(
        color="green",
        tickformat=",.0f",
        # tickformat="$,.0f",
        tickangle=0,
        tickfont=dict(family="Tahoma", size=12, color="green"),
        showgrid=True,               # ✅ Horizontal gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    legend_title={
        "text": "<u><b>Ocean Proximity</b></u>",
        "font": {"family": "Tahoma", "size": 16, "color": "purple"},
    },
    legend=dict(
        bgcolor="white",
        bordercolor="black",
        borderwidth=2,
    ),
    plot_bgcolor="white",
    hoverlabel=dict(               # ✅ Styled hover box
        # bgcolor="white",
        font_size=12,
        font_family="Tahoma",
    )
)

# Display in streamlit
st.plotly_chart(fig1, width="stretch")
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Bar Plot 2
# -------------------------------------------------------------------------------------------------------------------------
# # Set plot expander
# with st.expander("**:violet[📶 Bar Plot 2: Property Value by Location & Ocean Proximity]**", width="stretch"):

# Set plot subheader
st.subheader("**:violet[📶 Bar Plot 2: Property Value by Location & Ocean Proximity (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Build bar chart
fig2 = px.bar(
    filtered_summary_1,
    x="location_name",
    y="sum",
    color="ocean_proximity", 
    barmode="group",                   # "group or "stack" for stacked bars
    text="sum",                        #  "count", "median", "sum", "proportion" 
    # log_y=True,

    # Format hover_data values
    hover_data={
        "Cluster": True,               # no format change
        "count": ":,.0f",              # ✅ formatted as \1,234
        "mean": ":$,.0f",              # ✅ formatted as \$1,234
        "median": ":$,.0f",            # ✅ formatted as \$1,234
        "proportion": ":.2%",          # ✅ formatted as 15.00%
        "sum": ":$,.0f",               # ✅ formatted as \$1,234
        # "Risk": True,                # no format change
        # "Return":  True,             # no format change 
    },
    color_discrete_map={
        "<1H OCEAN": "turquoise",   
        "NEAR BAY": "orange",     
        "INLAND": "green",       
        "NEAR OCEAN": "lightblue",
    },
)

fig2.update_traces(
    # texttemplate="%{text:,.0f}",     # ✅ Formats 1000 → 1,000
    texttemplate="%{text:$,.0f}",      # ✅ Formats $1000 → $1,000
    # textposition="inside",           #  "inside", "top left", "top center", "top right", "middle left", "middle center", "middle right", "bottom left", "bottom center", "bottom right"
    insidetextanchor="end",            # 'end', 'middle', 'start'
    textangle=0, #-90
    textfont=dict(family="Tahoma", size=14, color="black"),
    # selector=dict(mode="text"), # textposition="top centre"
)

fig2.update_layout(
    title={
        "text": "<b><u>Property Value by Location & Ocean Proximity</u></b>" # <b> bold, <i> italic, <u> underline, <br> start new line, <sup> open superscript, </>close, 
        "<br><sup>(Bar labels represent property value by location & ocean proximity)</sup>", 
        "x": 0.5,                     # centers the title
        "xanchor": "center", "font": {"family": "tahoma", "size": 16, "color": "red"},
    },
    xaxis_title="<b>Location</b>",    # bold x label
    xaxis=dict(
        color="blue",
        # tickformat="$,.0f",
        tickangle=-45,
        tickfont=dict(family="Tahoma", size=12, color="blue"),
        showgrid=True,                # ✅ Vertical gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    yaxis_title="<b>Total Median House Value ($)</b>",
    yaxis=dict(
        color="green",
        tickformat="$,.0f",
        tickangle=0,
        tickfont=dict(family="Tahoma", size=12, color="green"),
        showgrid=True,               # ✅ Horizontal gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    legend_title={
        "text": "<u><b>Ocean Proximity</b></u>",
        "font": {"family": "Tahoma", "size": 16, "color": "purple"},
    },
    legend=dict(
        bgcolor="white",
        bordercolor="black",
        borderwidth=2,
    ),
    plot_bgcolor="white",
    hoverlabel=dict(               # ✅ Styled hover box
        # bgcolor="white",
        font_size=12,
        font_family="Tahoma",
    )
)

# Display in streamlit
st.plotly_chart(fig2, width="stretch")
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Build dataframe summary for horizontal bar plot (1 & 2) & bar plot (3 & 4)
c_loc_hs = (
    df
    .groupby(
        ['Cluster', 'location_name', 'Risk', 'Return', 'Best Strategy Short']
    )['median_house_value']
    .agg(['count', 'min', 'max', 'mean', 'median', 'sum'])
    .round(2)
    .reset_index()
    # compute proportion of total properties
    .assign(proportion=lambda x: x['count'] / x['count'].sum())
)

# Add rank columns for count, median & sum
c_loc_hs['count_rank']  = c_loc_hs['count'].rank(ascending=False)
c_loc_hs['median_rank'] = c_loc_hs['median'].rank(ascending=False)
c_loc_hs['sum_rank']    = c_loc_hs['sum'].rank(ascending=False)

# Sort DataFrame so the highest‐sum counties come first
c_loc_hs = c_loc_hs.sort_values('sum', ascending=False)
# -------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------
# Summary Table: Property Count & Value by Location, Risk, Return & Housing Strategy
#-------------------------------------------------------------------------------------------------------------------------
# # Set summary table expander
# with st.expander("**:yellow[📌📶 Summary Table & Barplots (inc. Range Filters): Property Count & Value by Location, Risk, Return & Housing Strategy]**", width="stretch"):

# Set summary table header
st.header("**:red[Property Count & Value by Location, Risk, Return & Housing Strategy:]**", divider="", width="stretch", text_alignment="left")

# Set summary table subheader
st.subheader("**:violet[🔍 Property Count & Value Range Filter:]**", divider="violet", width="stretch", text_alignment="left")

# Count slider
counts = c_loc_hs['count'].fillna(0)
min_count = int(counts.min())
max_count = int(counts.max())
count_low, count_high = st.slider("**:orange[Property Count Range]**", min_count, max_count, (min_count, max_count), format="%,.0f")

# Total value slider
# use step=1e6 if you have very large sums
sums = c_loc_hs['sum'].fillna(0)
min_val = int(sums.min())
max_val = int(sums.max())
val_low, val_high = st.slider("**:green[Total Property Value Range ($)]**", min_val, max_val, (min_val, max_val), step=1_000_000, format="$%,.0f")

# Set summary table subheader
st.subheader("**:yellow[📌 Summary Table: Property Count & Value by Location, Risk, Return & Housing Strategy]**", divider="violet", width="stretch", text_alignment="left")

# Filter summary table
filtered_summary_2 = c_loc_hs[(c_loc_hs['count'].between(count_low, count_high)) & (c_loc_hs['sum'].between(val_low, val_high))]

# # Display summary table in streamlit
# st.write(filtered_summary_2)
#-------------------------------------------------------------------------------------------------------------------------
# Define numeric values to be formatted
fmt = {
    "min"  :             "${:,.0f}",
    "count":              "{:,.0f}",
    "mean":               "${:,.0f}",
    "max":                "${:,.0f}",
    "mean":               "${:,.0f}",
    "median":             "${:,.0f}",
    "sum":                "${:,.0f}",
    "proportion":         "{:,.2%}",
    "count_rank":         "{:,.0f}",
    "median_rank":        "{:,.0f}",
    "sum_rank":           "{:,.0f}",
}
# List of columns to apply mix/max highlighting
subset_1 = ["min", "max", "count", "mean", "median", "sum", "proportion"]
subset_2 = ["count_rank", "median_rank", "sum_rank"]
min_props_1 = ("color:yellow; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:coral; ")
max_props_1 = ("color:darkgreen; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:yellow; ")
min_props_2 = ("color:darkgreen; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:yellow; ")
max_props_2 = ("color:yellow; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:coral; ")

# Apply formatting & styling
styled_filtered_summary_2 = filtered_summary_2.style.format(fmt)\
    .highlight_min(subset=subset_1, props=min_props_1, axis=0)\
        .highlight_max(subset=subset_1, props=max_props_1, axis=0)\
            .highlight_min(subset=subset_2, props=min_props_2, axis=0)\
                .highlight_max(subset=subset_2, props=max_props_2, axis=0)\

# Display styled summary table in streamlit
st.write(styled_filtered_summary_2)
#-------------------------------------------------------------------------------------------------------------------------
# Set horizontal bar plot 1 subheader
st.subheader("**:violet[📶 Horizontal Bar Plot 1: Property Count by Location & Housing Strategy (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Display horizontal bar plot 1 in streamlit
st.bar_chart(filtered_summary_2, x="location_name", y="count", x_label='Location', y_label='Property Count', 
            color="Best Strategy Short", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)

# Set horizontal bar plot 2 subheader
st.subheader("**:violet[📶 Horizontal Bar Plot 2: Property Value by Location & Housing Strategy (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Display horizontal bar plot 2 in streamlit
st.bar_chart(filtered_summary_2, x="location_name", y="sum", x_label='Location', y_label='Property Value ($)', 
            color="Best Strategy Short", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)

# Set horizontal bar plot 3 subheader
st.subheader("**:violet[📶 Horizontal Bar Plot 3: Property Count by Location & Risk (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Display horizontal bar plot 3 in streamlit
st.bar_chart(filtered_summary_2, x="location_name", y="count", x_label='Location', y_label='Property Count', 
            color="Risk", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)

# Set horizontal bar plot 4 subheader
st.subheader("**:violet[📶 Horizontal Bar Plot 4: Property Value by Location & Risk (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Display horizontal bar plot 4 in streamlit
st.bar_chart(filtered_summary_2, x="location_name", y="sum", x_label='Location', y_label='Property Value ($)', 
            color="Risk", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)

# Set horizontal bar plot 5 subheader
st.subheader("**:violet[📶 Horizontal Bar Plot 5: Property Count by Location & Return (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Display horizontal bar plot 5 in streamlit
st.bar_chart(filtered_summary_2, x="location_name", y="count", x_label='Location', y_label='Property Count', 
            color="Return", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)

# Set horizontal bar plot 6 subheader
st.subheader("**:violet[📶 Horizontal Bar Plot 6: Property Value by Location & Return (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Display horizontal bar plot 6 in streamlit
st.bar_chart(filtered_summary_2, x="location_name", y="sum", x_label='Location', y_label='Property Value ($)', 
            color="Return", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)

#-------------------------------------------------------------------------------------------------------------------------
# # OPTION 2: COUNT & VALUE FILTER IS SIDEBAR EXPANDER
# # Set filter sidebar expander
# with st.sidebar.expander("**:orange[🔍 Location & Housing Strategy: Property Count & Value Range Filter]**", width="stretch"):

#     # Count slider
#     counts = c_loc_hs['count'].fillna(0)
#     min_count = int(counts.min())
#     max_count = int(counts.max())
#     count_low, count_high = st.slider("**:orange[Property Count Range]**", min_count, max_count, (min_count, max_count), format="%,.0f")

#     # Total value slider
#     # use step=1e6 if you have very large sums
#     sums = c_loc_hs['sum'].fillna(0)
#     min_val = int(sums.min())
#     max_val = int(sums.max())
#     val_low, val_high = st.slider("**:green[Total Property Value Range ($)]**", min_val, max_val, (min_val, max_val), step=1_000_000, format="$%,.0f")

# # Set summary table sidebar expander
# with st.expander("**:orange[📌📶 Summary Table & Barplots: Property Count & Value by Location & Housing Strategy]**", width="stretch"):

#     # Set summary table header
#     st.subheader("**🏡:violet[📌 Summary Table: Property Count & Value by Location & Housing Strategy]**", divider="violet", width="stretch", text_alignment="left")

#     # Filter summary table
#     filtered_summary_2 = c_loc_hs[(c_loc_hs['count'].between(count_low, count_high)) & (c_loc_hs['sum'].between(val_low, val_high))]

#     # Display summary table in streamlit
#     # st.write(filtered_summary_2)
# #-------------------------------------------------------------------------------------------------------------------------
#     # Define numeric values to be formatted
#     fmt = {
#         "min"  :             "${:,.0f}",
#         "count":              "{:,.0f}",
#         "mean":               "${:,.0f}",
#         "max":                "${:,.0f}",
#         "mean":               "${:,.0f}",
#         "median":             "${:,.0f}",
#         "sum":                "${:,.0f}",
#         "proportion":         "{:,.2%}",
#         "count_rank":         "{:,.0f}",
#         "median_rank":        "{:,.0f}",
#         "sum_rank":           "{:,.0f}",
#     }
#     # List of columns to apply mix/max highlighting
#     subset_1 = ["min", "max", "count", "mean", "median", "sum", "proportion"]
#     subset_2 = ["count_rank", "median_rank", "sum_rank"]
#     min_props_1 = ("color:yellow; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:coral; ")
#     max_props_1 = ("color:darkgreen; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:yellow; ")
#     min_props_2 = ("color:darkgreen; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:yellow; ")
#     max_props_2 = ("color:yellow; font-family:consolas; font-size:25px; font-weight:extra bold; background-color:coral; ")

#    # Apply formatting & styling
#     styled_filtered_summary_2 = filtered_summary_2.style.format(fmt)\
#         .highlight_min(subset=subset_1, props=min_props_1, axis=0)\
#             .highlight_max(subset=subset_1, props=max_props_1, axis=0)\
#                 .highlight_min(subset=subset_2, props=min_props_2, axis=0)\
#                     .highlight_max(subset=subset_2, props=max_props_2, axis=0)\

#     # Display styled summary table in streamlit
#     st.write(styled_filtered_summary_2)
#-------------------------------------------------------------------------------------------------------------------------
    # # Set horizontal bar plot 1 subheader
    # st.subheader("**:violet[📶 Horizontal Bar Plot 1: Property Count by Location & Housing Strategy (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

    # # Display horizontal bar plot 1 in streamlit
    # st.bar_chart(filtered_summary_2, x="location_name", y="count", x_label='Location', y_label='Property Count', 
    #             color="Best Strategy Short", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)

    # # Set horizontal bar plot 2 subheader
    # st.subheader("**:violet[📶 Horizontal Bar Plot 2: Property Value by Location & Housing Strategy (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

    # # Display horizontal bar plot 2 in streamlit
    # st.bar_chart(filtered_summary_2, x="location_name", y="sum", x_label='Location', y_label='Property Value ($)', 
    #             color="Best Strategy Short", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)
    
    # # Set horizontal bar plot 3 subheader
    # st.subheader("**:violet[📶 Horizontal Bar Plot 3: Property Count by Location & Risk (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

    # # Display horizontal bar plot 3 in streamlit
    # st.bar_chart(filtered_summary_2, x="location_name", y="count", x_label='Location', y_label='Property Count', 
    #             color="Risk", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)
    
    # # Set horizontal bar plot 4 subheader
    # st.subheader("**:violet[📶 Horizontal Bar Plot 4: Property Value by Location & Risk (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

    # # Display horizontal bar plot 4 in streamlit
    # st.bar_chart(filtered_summary_2, x="location_name", y="sum", x_label='Location', y_label='Property Value ($)', 
    #             color="Risk", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)
    
    # # Set horizontal bar plot 5 subheader
    # st.subheader("**:violet[📶 Horizontal Bar Plot 5: Property Count by Location & Return (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

    # # Display horizontal bar plot 5 in streamlit
    # st.bar_chart(filtered_summary_2, x="location_name", y="count", x_label='Location', y_label='Property Count', 
    #             color="Return", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)
    
    # # Set horizontal bar plot 6 subheader
    # st.subheader("**:violet[📶 Horizontal Bar Plot 6: Property Value by Location & Return (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

    # # Display horizontal bar plot 6 in streamlit
    # st.bar_chart(filtered_summary_2, x="location_name", y="sum", x_label='Location', y_label='Property Value ($)', 
    #             color="Return", horizontal=True, sort=True, stack='layered', width="stretch", height="stretch", use_container_width=None)

# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Bar Plot 3
# -------------------------------------------------------------------------------------------------------------------------
# # Set plot expander
# with st.expander("**:violet[📶 Bar Plot 1: Property Count by Location & Housing Strategy (Hover for insights)]**", width="stretch"):

# Set plot subheader
st.subheader("**:violet[📶 Bar Plot 1: Property Count by Location & Housing Strategy (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# # Build dataframe summary for fig 3 & fig 4
# c_loc_hs = (
#     df
#     .groupby(
#         ['Cluster', 'location_name', 'Risk', 'Return', 'Best Strategy Short']
#     )['median_house_value']
#     .agg(['count', 'min', 'max', 'mean', 'median', 'sum'])
#     .round(2)
#     .reset_index()
#     # compute proportion of total properties
#     .assign(proportion=lambda x: x['count'] / x['count'].sum())
# )

# # Add rank columns for count, median & sum
# c_loc_hs['count_rank']  = c_loc_hs['count'].rank(ascending=False)
# c_loc_hs['median_rank'] = c_loc_hs['median'].rank(ascending=False)
# c_loc_hs['sum_rank']    = c_loc_hs['sum'].rank(ascending=False)

# # Sort DataFrame so the highest‐sum counties come first
# c_loc_hs = c_loc_hs.sort_values('sum', ascending=False)

# Build bar chart 3
fig3 = px.bar(
    c_loc_hs,
    x="location_name",
    y="count", # sum
    color="Best Strategy Short",     # "Risk", "Return", "Best Strategy Short"
    barmode="group",                 # "group or "stack" for stacked bars
    text="count",                    #  "count", "median", "sum", "proportion"
    # log_y=True,  

    # Format hover_data values
    hover_data={
        "Cluster": True,             # no format change
        "count": ":,.0f",            # ✅ formatted as \1,234
        "mean": ":$,.0f",            # ✅ formatted as \$1,234
        "median": ":$,.0f",          # ✅ formatted as \$1,234
        "proportion": ":.2%",        # ✅ formatted as 15.00%
        "sum": ":$,.0f",             # ✅ formatted as \$1,234
        "Risk": True,                # no format change
        "Return":  True,             # no format change 
    },
    # title="Total Median House Value by Location & Best Housing Strategy",
    color_discrete_map={
        "PB&H": "#2ecc71",         # green — premium
        "F&F":  "#3498db",         # blue — mid
        "AFD":  "#e74c3c"          # red — affordable
    },

)

fig3.update_traces(
    texttemplate="%{text:,.0f}",       # ✅ Formats 1000 → 1,000
    # texttemplate="%{text:$,.0f}",    # ✅ Formats $1000 → $1,000
    textposition="outside",            # "inside", "top left", "top center", "top right", "middle left", "middle center", "middle right", "bottom left", "bottom center", "bottom right"
    #insidetextanchor="end",           # 'end', 'middle', 'start'
    textangle=0, #-90
    textfont=dict(family="Tahoma", size=11, color="black"),
    # selector=dict(mode="text"), # textposition="top centre"
)

fig3.update_layout(
    title={
        "text": "<b><u>Property Count By Location & Housing Strategy</u></b>" # <b> bold, <i> italic, <u> underline, <br> start new line, <sup> open superscript, </>close, 
        "<br><sup>(Bar labels represent property count by location & housing strategy)</sup>", 
        "x": 0.5,                     # centers the title
        "xanchor": "center", "font": {"family": "tahoma", "size": 16, "color": "red"},
    },
    xaxis_title="<b>Location</b>",    # bold x label
    xaxis=dict(
        color="blue",
        # tickformat="$,.0f",
        tickangle=-45,
        tickfont=dict(family="Tahoma", size=12, color="blue"),
        showgrid=True,               # ✅ Vertical gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    yaxis_title="<b>Property Count</b>",      # <b>Total Median House Value ($)</b>"
    yaxis=dict(
        color="green",
        tickformat=",.0f",
        # tickformat="$,.0f",
        tickangle=0,
        tickfont=dict(family="Tahoma", size=12, color="green"),
        showgrid=True,              # ✅ Horizontal gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    legend_title={
        "text": "<u><b>Housing Strategy</b></u>",
        "font": {"family": "Tahoma", "size": 16, "color": "purple"},
    },
    legend=dict(
        bgcolor="white",
        bordercolor="black",
        borderwidth=2,
    ),
    plot_bgcolor="white",
    hoverlabel=dict(              # ✅ Styled hover box
        # bgcolor="white",
        font_size=12,
        font_family="Tahoma",
    )
)

# Display in streamlit
st.plotly_chart(fig3, width="stretch")
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Bar Plot 4
# -------------------------------------------------------------------------------------------------------------------------
# # Set plot expander
# with st.expander("**:violet[📶 Bar Plot 2: Property Value by Location & Housing Strategy (Hover for insights)]**", width="stretch"):

# Set plot subheader
st.subheader("**:violet[📶 Bar Plot 2: Property Value by Location & Housing Strategy (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Build bar chart 4
fig4 = px.bar(
    c_loc_hs,
    x="location_name",
    y="sum",
    color="Best Strategy Short",     # "Risk", "Return", "Best Strategy Short"
    barmode="group",                 # "group or "stack" for stacked bars
    text="sum",                      #  "count", "median", "sum", "proportion"  
    # log_y=True,
    
    # Fomat hover_data values
    hover_data={
        "Cluster": True,             # no format change
        "count": ":,.0f",            # ✅ formatted as \1,234
        "mean": ":$,.0f",            # ✅ formatted as \$1,234
        "median": ":$,.0f",          # ✅ formatted as \$1,234
        "proportion": ":.2%",        # ✅ formatted as 15.00%
        "sum": ":$,.0f",             # ✅ formatted as \$1,234
        "Risk": True,                # no format change
        "Return":  True,             # no format change 
    },
    # title="Total Median House Value by Location & Best Housing Strategy",
    color_discrete_map={
        "PB&H": "#2ecc71",         # green — premium
        "F&F":  "#3498db",         # blue — mid
        "AFD":  "#e74c3c"          # red — affordable
    },

)

fig4.update_traces(
    # texttemplate="%{text:,.0f}",     # ✅ Formats 1000 → 1,000
    texttemplate="%{text:$,.0f}",      # ✅ Formats $1000 → $1,000
    textposition="outside",            # "inside", "top left", "top center", "top right", "middle left", "middle center", "middle right", "bottom left", "bottom center", "bottom right"
    #insidetextanchor="end",           # 'end', 'middle', 'start'
    textangle=0, #-90
    textfont=dict(family="Tahoma", size=11, color="black"),
    # selector=dict(mode="text"), # textposition="top centre"
)

fig4.update_layout(
    title={
        "text": "<b><u>Property Value By Location & Housing Strategy</u></b>" # <b> bold, <i> italic, <u> underline, <br> start new line, <sup> open superscript, </>close, 
        "<br><sup>(Bar labels represent property value by location & housing strategy)</sup>", 
        "x": 0.5,                     # centers the title
        "xanchor": "center", "font": {"family": "tahoma", "size": 16, "color": "red"},
    },
    xaxis_title="<b>Location</b>",    # bold x label
    xaxis=dict(
        color="blue",
        # tickformat="$,.0f",
        tickangle=-45,
        tickfont=dict(family="Tahoma", size=12, color="blue"),
        showgrid=True,               # ✅ Vertical gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    yaxis_title="<b>Total Median House Value ($)</b>",
    yaxis=dict(
        color="green",
        tickformat="$,.0f",
        tickangle=0,
        tickfont=dict(family="Tahoma", size=12, color="green"),
        showgrid=True,               # ✅ Horizontal gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    legend_title={
        "text": "<u><b>Housing Strategy</b></u>",
        "font": {"family": "Tahoma", "size": 16, "color": "purple"},
    },
    legend=dict(
        bgcolor="white",
        bordercolor="black",
        borderwidth=2,
    ),
    plot_bgcolor="white",
    hoverlabel=dict(                 # ✅ Styled hover box
        # bgcolor="white",
        font_size=12,
        font_family="Tahoma",
    )
)

# Display in streamlit
st.plotly_chart(fig4, width="stretch")
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Altair Pie Chart 1
# -------------------------------------------------------------------------------------------------------------------------
import altair as alt

# # Set plot expander
# with st.expander("**:violet[🍰 Pie Chart 1: Total Property Count & Value by Ocean Proximity (Hover for insights)]**", width="stretch"):

# Set plot subheader
st.subheader("**:violet[🍰 Pie Chart 1: Total Property Value & Count by Ocean Proximity (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Aggregate data by category
op_agg = (
    df
    .groupby("ocean_proximity", as_index=False)
    .agg(
        total_property_count     = ("ocean_proximity", "count"),
        total_property_value     = ("median_house_value", "sum"),
        median_income            = ("median_income", "median"),
        median_income_per_person = ("income_per_person", "median")
        )
)

# Add percetages columns
op_agg["total_property_count_percentage"] = op_agg["total_property_count"] / op_agg["total_property_count"].sum()
op_agg["total_property_value_percentage"] = op_agg["total_property_value"] / op_agg["total_property_value"].sum()

# Create a base chart on the aggregated data
base = alt.Chart(op_agg).encode(
    theta=alt.Theta(field="total_property_value", type="quantitative", stack=True, title="Total Property Value"),
    color=alt.Color(field="ocean_proximity", type="nominal", title="Ocean Proximity Clusters", legend=alt.Legend(orient="right")),
    
    # Display aggregates on hover
    tooltip=[
        alt.Tooltip("ocean_proximity", type="nominal", title="Cluster Name:"),
        alt.Tooltip("total_property_value", type="quantitative", title="Total Property Value:", format="$,.0f"),
        alt.Tooltip("total_property_value_percentage", type="quantitative", title="Total Property Value Percentage:", format=".0%"),
        alt.Tooltip("total_property_count", type="quantitative", title="Total Property Count:", format=",.0f"),
        alt.Tooltip("total_property_count_percentage", type="quantitative", title="Total Property Count Percentage:", format=".0%"),
        alt.Tooltip("median_income", type="quantitative", title="Median Income:", format="$,.0f"),
        alt.Tooltip("median_income_per_person", type="quantitative", title="Median Income per Person:",  format="$,.0f")
    ]
)

# Draw the pie
pie = base.mark_arc(innerRadius=15, outerRadius=100)

# Add one label per slice
#    Put cluster name just outside each slice
labels = base.mark_text(
    radius=180,         # push text outside the pie
    size=12,
    color="darkblue"
).encode(
    text=alt.Text(field="ocean_proximity", type="nominal")
)

    #  Add total property value label
prop_value_labels = base.mark_text(
    radius=160,
    size=10,
    color="white"
).encode(
    text=alt.Text("total_property_value", type="quantitative", format="$,.0f"),
    theta=alt.Theta("total_property_value", type="quantitative", stack=True)
)

    #  Add total property count label
prop_count_labels = base.mark_text(
    radius=130,
    size=10,
    color="white"
).encode(
    text=alt.Text("total_property_count", type="quantitative", format=",.0f"),
    theta=alt.Theta("total_property_value", type="quantitative", stack=True)
)

# Display in streamlit
st.altair_chart(pie + labels + prop_value_labels + prop_count_labels, width="stretch")
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Altair Pie Chart 2
# -------------------------------------------------------------------------------------------------------------------------
import altair as alt

# # Set plot expander
# with st.expander("**:violet[🍰 Pie Chart 2: Total Property Value & Count by Housing Strategy (Hover for insights)]**", width="stretch"):

# Set plot subheader
st.subheader("**:violet[🍰 Pie Chart 2: Total Property Value & Count by Housing Strategy (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Aggregate data by category
hs_agg = (
    df
    .groupby("Best Strategy", as_index=False)
    .agg(
        total_property_count     = ("Best Strategy", "count"),
        total_property_value     = ("median_house_value", "sum"),
        median_income            = ("median_income", "median"),
        median_income_per_person = ("income_per_person", "median")
        )
)

# Add percetages columns
hs_agg["total_property_count_percentage"] = hs_agg["total_property_count"] / hs_agg["total_property_count"].sum()
hs_agg["total_property_value_percentage"] = hs_agg["total_property_value"] / hs_agg["total_property_value"].sum()

# Create a base chart on the aggregated data
base = alt.Chart(hs_agg).encode(
    theta=alt.Theta(field="total_property_value", type="quantitative", stack=True, title="Total Property Value"),
    color=alt.Color(field="Best Strategy", type="nominal", title="Housing Strategy Clusters", legend=alt.Legend(orient="right")),
    
    # Display aggregates on hover
    tooltip=[
        alt.Tooltip("Best Strategy", type="nominal", title="Cluster Name:"),
        alt.Tooltip("total_property_value", type="quantitative", title="Total Property Value:", format="$,.0f"),
        alt.Tooltip("total_property_value_percentage", type="quantitative", title="Total Property Value Percentage:", format=".0%"),
        alt.Tooltip("total_property_count", type="quantitative", title="Total Property Count:", format=",.0f"),
        alt.Tooltip("total_property_count_percentage", type="quantitative", title="Total Property Count Percentage:", format=".0%"),
        alt.Tooltip("median_income", type="quantitative", title="Median Income:", format="$,.0f"),
        alt.Tooltip("median_income_per_person", type="quantitative", title="Median Income per Person:",  format="$,.0f")
    ]
)

# Draw the pie
pie = base.mark_arc(innerRadius=15, outerRadius=100)

# Add one label per slice
#    Put cluster name just outside each slice
labels = base.mark_text(
    radius=205,         # push text outside the pie
    size=12,
    color="darkblue"
).encode(
    text=alt.Text(field="Best Strategy", type="nominal")
)

#  Add total property value label
prop_value_labels = base.mark_text(
    radius=160,
    size=10,
    color="white"
).encode(
    text=alt.Text("total_property_value", type="quantitative", format="$,.0f"),
    theta=alt.Theta("total_property_value", type="quantitative", stack=True)
)

    #  Add total property count label
prop_count_labels = base.mark_text(
    radius=135,
    size=10,
    color="white"
).encode(
    text=alt.Text("total_property_count", type="quantitative", format=",.0f"),
    theta=alt.Theta("total_property_value", type="quantitative", stack=True)
)

# Display in streamlit
st.altair_chart(pie + labels + prop_value_labels + prop_count_labels, width="stretch")
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Boxplot
# -------------------------------------------------------------------------------------------------------------------------

# # Set plot expander
# with st.expander("**:violet[⏳ Boxplot: Property Value by Location & Return (Hover for insights)]**", width="stretch"):

# Set plot subheader
st.subheader("**:violet[⏳ Boxplot: Property Value by Location & Return (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Build boxplot 1
fig5 = px.box(
    df,
    x="location_name",
    y="median_house_value",
    color="Return",
    # log_y=True,

    # Fomat hover_data values
    hover_data={
        "Cluster": True,                   # no format change
        "MHV_cluster_name": True,          # no format change
        #"price_cluster_name": True,        # no format change
        #"wealth_cluster_name": True,       # no format change
        "geo_cluster_name": True,          # no format change
        "income_per_person": ":$,.0f",     # ✅ formatted as \$1,234
        "median_income": ":$,.0f",         # ✅ formatted as \$1,234
        #"Risk": True,                     # no format change
        "Return": True,                    # no format change
        #"Best Strategy": True,             # no format change
    },
    points="all",
    notched=True,                         # ✅ Shows 95% CI around the median
    color_discrete_map={
        "High": "#2ecc71",              # green — premium
        "Medium":  "#3498db",           # blue — mid
        "Low-Medium":  "#e74c3c"        # red — affordable
    },
)

fig5.update_traces(
    marker=dict(
        size=3,                           # ✅ Smaller points — less clutter
        opacity=0.3,                      # ✅ More transparent — less overlap
        line=dict(width=0.5, color="black")
    ),
    boxmean=True,                         # ✅ Dashed line showing mean inside box
    jitter=0.3,                           # ✅ Spreads points horizontally — less overlap
    pointpos=0,                           # ✅ Centers points within the box
)

fig5.update_layout(
    title={
        "text": "<b><u>Distribution of Property Values by Location & Return</u></b>"
                "<br><sup>Points represent individual property values by location name & return</sup>",
        "x": 0.5,
        "xanchor": "center",
        "font": {"family": "Tahoma", "size": 16, "color": "red"},
    },
    xaxis_title="<b>Location</b>",
    xaxis=dict(
        color="blue",
        # tickformat="$,.0f",
        tickangle=-45,
        tickfont=dict(family="Tahoma", size=12, color="blue"),
        showgrid=True,           # ✅ Vertical gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    yaxis_title="<b>House Value ($)</b>",
    yaxis=dict(
        color="green",
        tickformat="$,.0f",
        tickangle=0,
        tickfont=dict(family="Tahoma", size=12, color="green"),
        showgrid=True,           # ✅ Horizontal gridlines
        gridcolor="mistyrose",
        gridwidth=0.5,
    ),
    legend_title={
        "text": "<u><b>Return</b></u>",
        "font": {"family": "Tahoma", "size": 16, "color": "purple"},
    },
    legend=dict(
        bgcolor="white",
        bordercolor="black",
        borderwidth=2,
    ),
    plot_bgcolor="white",
    hoverlabel=dict(             # ✅ Styled hover box
        bgcolor="white",
        font_size=12,
        font_family="Tahoma",
    ),
    boxmode="group",             # ✅ Groups boxes side by side per location
)

# Display in streamlit
st.plotly_chart(fig5, width="stretch")
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Altair Scatterplot 1
# -------------------------------------------------------------------------------------------------------------------------
import altair as alt

# # Set plot expander
# with st.expander("**:violet[‧₊˚ ⋅ Scatterplot 1: Property Value vs Income by Property Value Cluster (Hover for insights)]**", width="stretch"):

# Set plot subheader
st.subheader("**:violet[‧₊˚ ⋅ Scatterplot 1: Property Value vs Income by Property Value Cluster (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Build Altair Chart
chart_1 = (
    alt.Chart(df)
    .mark_circle()
    .encode(x="median_house_value", y="median_income", size="MHV_cluster_name", color="MHV_cluster_name", 
            tooltip=["median_house_value", "median_income", "income_per_person"])
)

# Display in streamlit
st.altair_chart(chart_1)
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Altair Scatterplot 2
# -------------------------------------------------------------------------------------------------------------------------
import altair as alt

# # Set plot expander
# with st.expander("**:violet[‧₊˚ ⋅ Scatterplot 2: Property Value vs Income Person by Market Segment Cluster (Hover for insights)]**", width="stretch"):

# Set plot subheader
st.subheader("**:violet[‧₊˚ ⋅ Scatterplot 2: Property Value vs Income Person by Market Segment Cluster (Hover for insights)]**", divider="violet", width="stretch", text_alignment="left")

# Build Altair Chart
chart_2 = (
alt.Chart(df)
    .mark_circle()
    .encode(x="median_house_value", y="median_income", size="market_segment_cluster_name", color="market_segment_cluster_name", 
            tooltip=["median_house_value", "median_income", "income_per_person"])
)

# Display in streamlit
st.altair_chart(chart_2)
# -------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------
# Build summary table for display in streamlit
#-------------------------------------------------------------------------------------------------------------------------
# # Set plot expander
# with st.expander("**🌍✨📌:violet[Geo Cluster Summary Table - Property Hotspot Explorer🏡🔥]**", width="stretch"):

# Set page title
# st.set_page_config(page_title="**🏠📊 CA Housing Market: Property Hotspot Explorer Dashboard App🏡🔥**", page_icon="🧊", layout="wide", initial_sidebar_state="auto", menu_items={'Get help':'mailto:tailback33@hotmail.com'})

# # Set summary table title
# st.title("**🌍✨📌:Blue[Geo Cluster Summary Table - Property Hotspot Explorer🏡🔥]**", width="stretch", text_alignment="left")

# # Set summary table header
# st.header("**🌍✨📌:violet[Geo Cluster Summary Table - Property Hotspot Explorer🏡🔥]**", width="stretch", text_alignment="left")

# Set summary table subheader
st.subheader("**🌍✨📌:violet[Geo Cluster Summary Table - Property Hotspot Explorer🏡🔥]**", divider="violet", width="stretch", text_alignment="left")

# Build a cluster‐level summary table
summary = (
    df
    .groupby("Cluster", as_index=False)
    .agg(
        loc_name           = ("location_name", lambda x: x.mode().iloc[0]), # picks the single most frequent in each cluster.
        prop_cnt           =  ("Cluster", "count"),
        tot_rooms          = ("total_rooms", "sum"),
        tot_brooms         = ("total_bedrooms",  "sum"),
        med_prop_age       = ("housing_median_age", "median"),
        avg_rooms_per_prop = ("rooms_per_house",  "mean"),
        avg_ppl_per_prop   = ("people_per_house", "mean"),
        avg_rooms_per_pers = ("rooms_per_person",  "mean"),
        tot_prop_val       = ("median_house_value", "sum"),
        med_prop_val       = ("median_house_value", "median"),
        med_income         = ("median_income", "median"),
        med_income_pp      = ("income_per_person", "median"),
        top_ocn_prox       = ("ocean_proximity", lambda x: x.mode().iloc[0]), # picks the single most frequent in each cluster
        pct_top_ocn_prox   = ("ocean_proximity", lambda x: (x==x.mode().iloc[0]).sum() / x.size),
        top_strat          = ("Best Strategy", lambda x: x.mode().iloc[0]), # picks the single most frequent in each cluster
        pct_top_strat      = ("Best Strategy", lambda x: (x==x.mode().iloc[0]).sum() / x.size),
        longitude          = ("longitude", lambda x: x.mode().iloc[0]), # picks the single most frequent in each cluster
        latitude           = ("latitude", lambda x: x.mode().iloc[0]), # picks the single most frequent in each cluster
    )
)

# NB! - We can use .mode()[0]. The explicit .iloc[0] isn't required, it just makes the positional intent clearer but behaves the same.

# Define our numeric columns
numeric_columns = ["prop_cnt", "tot_prop_val", "med_prop_val", "med_income", "med_income_pp"]

# Compute descending “dense” ranks (1 = highest)
for col in numeric_columns:
    summary[f"{col}_rank"] = (
        summary[col]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

#-------------------------------------------------------------------------------------------------------------------------
# Summary table properties
#-------------------------------------------------------------------------------------------------------------------------
row_props = {"selector":"tr:hover","props":[("background-color","mistyrose"),("color","purple"),
("font-family","georgia"),("font-style","italic"),("font-weight","900"),("font-size","15px"),("text-align","center")]}

header_props = {"selector":"th:hover","props":[("background-color","grey"),("color","cyan"),
("font-family","tahoma"),("font-style","italic"),("font-weight","900"),("font-size","15px"),("text-align","center")]}

data_props = {"selector":"td:hover","props":[("background-color","orange"),("color","green"),
("font-family","consolas"),("font-style","italic"),("font-weight","900"),("font-size","15px"),("text-align","center")]}

cap_props = {"selector":"caption","props":[("caption-side","top"),("background-color","white"),("color","red"),
("font-family","Arial"),("font-style","normal"),("font-weight","900"),("font-size","15px"),("text-align","center")]}

props = {"border":"4px solid gray","width":"120px","text-align":"justify","height":"10px"}

warnings.filterwarnings("ignore", category=UserWarning)
#-------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------
# Define numeric values to be formatted
fmt = {
    "prop_cnt":              "{:,.0f}",
    "tot_rooms":             "{:,.0f}",
    "tot_brooms":            "{:,.1f}",
    "med_prop_age":          "{:,.1f}",
    "avg_rooms_per_prop":    "{:,.2f}",
    "avg_ppl_per_prop":      "{:,.2f}",
    "avg_rooms_per_pers":    "{:,.2f}",
    "tot_prop_val":          "${:,.0f}",
    "med_prop_val":          "${:,.0f}",
    "med_income":            "${:,.0f}",
    "med_income_pp":         "${:,.0f}",
    "pct_top_ocn_prox":      "{:,.2%}",
    "pct_top_strat":         "{:,.2%}"
}

# List of columns to apply mix/max highlighting
subset=["prop_cnt", "tot_rooms", "tot_brooms", "med_prop_age" ,
        "avg_rooms_per_prop", "avg_ppl_per_prop", "avg_rooms_per_pers", 
        "tot_prop_val", "med_prop_val", "med_income", "med_income_pp"      
]

# Apply formatting & styling
styled_summary = summary.style.format(fmt)\
    .highlight_min(subset=subset, color="coral", axis=0)\
        .highlight_max(subset=subset, color="yellow", axis=0)\
            .set_table_styles([row_props, header_props, data_props, cap_props])\
                .set_properties(**props)\
                    .set_caption("")

# Compute the set of row indices where each metric in subset hits its minimum
min_rows = set(summary[subset].idxmin().values)
# Compute the set of row indices where each metric in subset hits its maximum
max_rows = set(summary[subset].idxmax().values)

# List of columns to highlight
columns = ["Cluster", "loc_name"]

# Define function for highlighting columns of min and max values
def highlight_cluster_loc(col):
    # if this isn’t the category column, leave it alone
    # if col.name != "x":
    # if this isn’t the category columns, leave it alone
    if col.name not in columns:
        return [""] * len(col)
    # otherwise, produce one CSS rule per row
    out = []
    for idx in col.index:
        if idx in max_rows:
            out.append("background-color: yellow; font-weight: bold")
        elif idx in min_rows:
            out.append("background-color: coral; font-weight: bold")
        else:
            out.append("")
    return out

final_styled_summary = styled_summary.apply(highlight_cluster_loc, axis=0)

# Display in streamlit
# st.write(summary)
st.write(final_styled_summary.to_html(), unsafe_allow_html=True)
# st.write(styled_summary.to_html(), unsafe_allow_html=True)
#-------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------
# Geo Cluster Centers Map
#-------------------------------------------------------------------------------------------------------------------------
import streamlit as st
import folium
from streamlit_folium import st_folium

# # Set plot expander
# with st.expander("**🌍✨🗺️:violet[Geo Cluster Centers Map (with Labels) (Hover for insights)]🏷️**", width="stretch"):

# Set Geo Cluster Centers Map title
# st.title("**🌍✨🗺️:violet[Geo Cluster Centers Map (with Labels) (Hover for insights)]🏷️**", width="stretch", text_alignment="left")

# Set Geo Cluster Centers Map subheader
# st.subheader("🌍✨🗺️**:violet[Cluster Centers Map (with Labels) (Hover for insights)]🏷️**", divider="violet", width="stretch", text_alignment="left")

# Set Geo Cluster Centers Map subheader
st.subheader("**🌍✨🗺️:violet[Geo Cluster Centers Map (with Labels) (Hover for insights)]🏷️**", divider="violet", width="stretch", text_alignment="left")

# center map
m = folium.Map(location=[summary["latitude"].mean(), summary["longitude"].mean()], zoom_start=6,)

# add markers
for _, row in summary.iterrows():
    folium.CircleMarker(
        location=(row["latitude"], row["longitude"]),
        radius=8,
        color="red",
        fill=True,
        fill_opacity=0.6,
        popup=f"{row['loc_name']}\nMHV: ${row['med_prop_val']:,.0f}\nMI: ${row['med_income']:,.0f}\nMIPP: ${row['med_income_pp']:,.0f}",
        tooltip=f"{row['loc_name']}\nMHV: ${row['med_prop_val']:,.0f}\nMI: ${row['med_income']:,.0f}\nMIPP: ${row['med_income_pp']:,.0f}"
    ).add_to(m)

# render in Streamlit
st_folium(m, width=800, height=600)
#-------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------
# Filter Dataframe
# -------------------------------------------------------------------------------------------------------------------------
# dynamic_filters = DynamicFilters(df, filters=['location_name', 'ocean_proximity', 'Best Strategy', 'Risk', 'Return'])

# with st.sidebar:
#     dynamic_filters.display_filters(location='columns', num_columns=2, gap='large')

# dynamic_filters.display_df()
#-------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------
# Set created by text
#-------------------------------------------------------------------------------------------------------------------------
st.markdown(
    """
    <style>
      .footer {
        background-color, grey;
        color: magenta;
        font-family , Verdana;
        font-style, italic;
        font-weight, 900;
        font-size: 25px;
        text-align: right;
        margin-bottom: 3rem;
        border :4px solid cyan
      }
    </style>
    <div class="footer">
      🎂🎈 VAnalytics🥳🎉
    </div>
    """,
    unsafe_allow_html=True
)
#-------------------------------------------------------------------------------------------------------------------------