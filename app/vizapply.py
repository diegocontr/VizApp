import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from PIL import Image
import plotly.express as px

# ===========================
# Configuration Dictionaries
# ===========================

# Labels and Captions
config_labels = {
    "menus": {
        "database": "Select Database",
        "analysis_type": "Select Analysis Type",
        "column_to_analyse": "Select Column to Analyse",
        "agg_function": "Select Aggregation Function",
        "reference": "Select Reference",
        "groupping": "Select Groupping",
        "target": "Select Target"
    },
    "plot": {
        "x_label": "X-Axis",
        "y_label_line": "Y-Axis (Line Plot)",
        "y_label_var_y": "Y-Axis (Variable Y Plot)",
        "title_line": "Data Visualization Plot - Y vs X",
        "title_var_y": "Data Visualization Plot - Variable Y vs X",
        "fig_size": (1200, 800)  # Width, Height in pixels
    },
    "headers": {
        "main": "📊 Mock Database Visualization",
        "dataframes": "View Underlying Data"
    },
    "download_buttons": {
        "df_csv": "Download Line Plot Data as CSV",
        "dfh_csv": "Download Bar Plot Data as CSV"
    }
}

# Colors
config_colors = {
    "line_all": "#1f77b4",       # Blue
    "line_group": "#2ca02c",     # Green
    "bar_plot": "#ff7f0e",       # Orange
    "background": "#FFFFFF",     # White
    "plotly_palette": px.colors.qualitative.Plotly  # Plotly's qualitative palette
}

# ===========================
# Custom X-Ticks Dictionary
# ===========================

# This dictionary can be empty or contain custom x-ticks and labels for specific columns
custom_xticks = {
    'column1': {
        'xticks': [0, 5, 10, 15],
        'xticklabels': ['A', 'B', 'C', 'D']
    }
    # You can add more entries here for other columns if needed
}

# ===========================
# Utility Functions
# ===========================

@st.cache_data(show_spinner=False)
def load_data_dict(filename='./data/mock_database.json'):
    """
    Loads the nested data_dict from a JSON file, converting JSON strings back to DataFrames.

    Parameters:
        filename (str): The relative path to the JSON file to load.

    Returns:
        dict: The reconstructed nested dictionary with DataFrames.
    """
    try:
        # Ensure the file exists
        file_path = Path(filename)
        if not file_path.is_file():
            st.error(f"Data file not found at path: {filename}")
            return {}
        
        with open(filename, 'r') as f:
            data_dict_json = json.load(f)
        
        # Traverse the nested dictionary and convert JSON strings back to DataFrames
        for db in data_dict_json:
            for analysis in data_dict_json[db]:
                for column in data_dict_json[db][analysis]:
                    for agg in data_dict_json[db][analysis][column]:
                        for ref in data_dict_json[db][analysis][column][agg]:
                            for group in data_dict_json[db][analysis][column][agg][ref]:
                                for target in data_dict_json[db][analysis][column][agg][ref][group]:
                                    df_json = data_dict_json[db][analysis][column][agg][ref][group][target]['df']
                                    dfh_json = data_dict_json[db][analysis][column][agg][ref][group][target]['dfh']
                                    # Convert JSON strings back to DataFrames
                                    df = pd.read_json(df_json, orient='split')
                                    dfh = pd.read_json(dfh_json, orient='split')
                                    data_dict_json[db][analysis][column][agg][ref][group][target]['df'] = df
                                    data_dict_json[db][analysis][column][agg][ref][group][target]['dfh'] = dfh
        return data_dict_json
    
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return {}

def load_logo(image_path='../images/log.jpeg'):
    """
    Loads the logo image.

    Parameters:
        image_path (str): Relative path to the logo image.

    Returns:
        PIL.Image: The loaded image.
    """
    try:
        logo = Image.open(image_path)
        return logo
    except FileNotFoundError:
        st.warning(f"Logo file not found at path: {image_path}")
        return None

# ===========================
# Main Streamlit App
# ===========================

def main():
    # Set page configuration
    st.set_page_config(page_title="Data Visualization Tool", layout="wide", page_icon="📊")

    # Load the logo
    logo = load_logo('./images/log.jpeg')

    # Display the logo at the top of the sidebar
    if logo:
        st.sidebar.image(logo, use_column_width=True)

    # Display the main header in the sidebar
    st.sidebar.header(config_labels["headers"]["main"])

    # Load the data_dict
    data_dict = load_data_dict('./data/mock_database.json')

    if not data_dict:
        st.stop()

    # Configuration options
    databases = list(data_dict.keys())

    st.sidebar.header("Configuration")

    selected_db = st.sidebar.selectbox(config_labels["menus"]["database"], databases)
    analysis_types = list(data_dict[selected_db].keys())
    selected_analysis = st.sidebar.selectbox(config_labels["menus"]["analysis_type"], analysis_types)
    columns_to_analyse = list(data_dict[selected_db][selected_analysis].keys())
    selected_column = st.sidebar.selectbox(config_labels["menus"]["column_to_analyse"], columns_to_analyse)
    agg_functions = list(data_dict[selected_db][selected_analysis][selected_column].keys())
    selected_agg = st.sidebar.selectbox(config_labels["menus"]["agg_function"], agg_functions)
    references = list(data_dict[selected_db][selected_analysis][selected_column][selected_agg].keys())
    selected_ref = st.sidebar.selectbox(config_labels["menus"]["reference"], references)
    grouppings = list(data_dict[selected_db][selected_analysis][selected_column][selected_agg][selected_ref].keys())
    selected_group = st.sidebar.selectbox(config_labels["menus"]["groupping"], grouppings)
    targets = list(data_dict[selected_db][selected_analysis][selected_column][selected_agg][selected_ref][selected_group].keys())
    selected_target = st.sidebar.selectbox(config_labels["menus"]["target"], targets)

    # Get figure size from configuration
    fig_width, fig_height = config_labels["plot"]["fig_size"]

    # Retrieve the corresponding DataFrames
    try:
        selected_data = data_dict[selected_db][selected_analysis][selected_column][selected_agg][selected_ref][selected_group][selected_target]
        df = selected_data['df']
        dfh = selected_data['dfh']
    except KeyError as e:
        st.error(f"KeyError: {e}. Please check your selections.")
        st.stop()

    # Check if 'var_y' exists in the DataFrame
    if 'var_y' not in df.columns:
        st.error("The selected data does not contain the 'var_y' column.")
        st.write("**Available columns in `df`:**", df.columns.tolist())
        st.stop()

    # Check if data is available
    if df.empty:
        st.error("No line plot data available for the selected configuration.")
        return
    if dfh.empty:
        st.error("No bar plot data available for the selected configuration.")
        return

    # Plotting Section
    st.header(f"Visualization for: {selected_db} / {selected_analysis} / {selected_column} / {selected_agg} / {selected_ref} / {selected_group} / {selected_target}")

    # Set Plotly palette
    plotly_palette = config_colors["plotly_palette"]

    # Sort data to ensure proper plotting
    df_sorted = df.sort_values(by=['group', 'x'])
    df_sorted_var = df.sort_values(by=['group', 'x'])

    # Get unique groups
    unique_groups = df_sorted['group'].unique()
    unique_groups_var = df_sorted_var['group'].unique()

    # Initialize Plotly figure with two subplots
    fig_plotly = make_subplots(
        rows=2, cols=1,
        subplot_titles=(config_labels["plot"]["title_line"], config_labels["plot"]["title_var_y"]),
        shared_xaxes=False,
        vertical_spacing=0.15,
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": True}]
        ]
    )

    # ======================
    # Top Plot: Y vs X with Bar Plot
    # ======================

    # Line plots for Y vs X
    if len(unique_groups) == 1:
        group = unique_groups[0]
        fig_plotly.add_trace(
            go.Scatter(
                x=df_sorted['x'],
                y=df_sorted['y'],
                mode='lines+markers',
                name=group,
                line=dict(color=config_colors["line_all"]),
                marker=dict(color=config_colors["line_all"])
            ),
            row=1, col=1,
            secondary_y=False
        )
    else:
        for idx, group in enumerate(unique_groups):
            group_df = df_sorted[df_sorted['group'] == group]
            color = plotly_palette[idx % len(plotly_palette)]
            fig_plotly.add_trace(
                go.Scatter(
                    x=group_df['x'],
                    y=group_df['y'],
                    mode='lines+markers',
                    name=group,
                    line=dict(color=color),
                    marker=dict(color=color)
                ),
                row=1, col=1,
                secondary_y=False
            )

    # Bar plot on secondary y-axis
    fig_plotly.add_trace(
        go.Bar(
            x=dfh['x'],
            y=dfh['y'],
            name='Bar Plot',
            marker=dict(color=config_colors["bar_plot"]),
            opacity=0.3
        ),
        row=1, col=1,
        secondary_y=True
    )

    # ======================
    # Bottom Plot: var_y vs X with Bar Plot
    # ======================

    # Line plots for var_y vs X
    if len(unique_groups_var) == 1:
        group = unique_groups_var[0]
        fig_plotly.add_trace(
            go.Scatter(
                x=df_sorted_var['x'],
                y=df_sorted_var['var_y'],
                mode='lines+markers',
                name=group,
                line=dict(color=config_colors["line_all"]),
                marker=dict(color=config_colors["line_all"])
            ),
            row=2, col=1,
            secondary_y=False
        )
    else:
        for idx, group in enumerate(unique_groups_var):
            group_df_var = df_sorted_var[df_sorted_var['group'] == group]
            color = plotly_palette[idx % len(plotly_palette)]
            fig_plotly.add_trace(
                go.Scatter(
                    x=group_df_var['x'],
                    y=group_df_var['var_y'],
                    mode='lines+markers',
                    name=group,
                    line=dict(color=color),
                    marker=dict(color=color),
                    showlegend=False  # Avoid duplicate legends
                ),
                row=2, col=1,
                secondary_y=False
            )

    # Bar plot on secondary y-axis for var_y plot
    fig_plotly.add_trace(
        go.Bar(
            x=dfh['x'],
            y=dfh['y'],
            name='Bar Plot',
            marker=dict(color=config_colors["bar_plot"]),
            opacity=0.3,
            showlegend=False  # Avoid duplicate legends
        ),
        row=2, col=1,
        secondary_y=True
    )

    # ======================
    # Custom X-Ticks Handling
    # ======================

    if selected_column in custom_xticks:
        xticks = custom_xticks[selected_column]['xticks']
        xticklabels = custom_xticks[selected_column]['xticklabels']

        # Update x-axis for both subplots
        fig_plotly.update_xaxes(
            tickmode='array',
            tickvals=xticks,
            ticktext=xticklabels,
            row=1, col=1
        )
        fig_plotly.update_xaxes(
            tickmode='array',
            tickvals=xticks,
            ticktext=xticklabels,
            row=2, col=1
        )

    # Update axes titles
    fig_plotly.update_yaxes(title_text=config_labels["plot"]["y_label_line"], row=1, col=1, secondary_y=False)
    fig_plotly.update_yaxes(title_text="Bar Plot Y-Axis", row=1, col=1, secondary_y=True)
    fig_plotly.update_yaxes(title_text=config_labels["plot"]["y_label_var_y"], row=2, col=1, secondary_y=False)
    fig_plotly.update_yaxes(title_text="Bar Plot Y-Axis", row=2, col=1, secondary_y=True)
    fig_plotly.update_xaxes(title_text=config_labels["plot"]["x_label"], row=2, col=1)

    # Update layout for better aesthetics
    fig_plotly.update_layout(
        height=fig_height,
        width=fig_width,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor=config_colors["background"],
        paper_bgcolor=config_colors["background"],
        margin=dict(l=50, r=50, t=100, b=50)
    )

    # Update hover templates for better interactivity
    for trace in fig_plotly['data']:
        if trace['type'] == 'scatter':
            trace['hovertemplate'] = (
                f"{config_labels['plot']['x_label']}: %{{x}}<br>"
                f"{trace['name']}: %{{y}}<extra></extra>"
            )
        elif trace['type'] == 'bar':
            trace['hovertemplate'] = (
                f"{config_labels['plot']['x_label']}: %{{x}}<br>"
                f"Bar Plot: %{{y}}<extra></extra>"
            )

    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig_plotly, use_container_width=True)

    # ======================
    # DataFrames Section
    # ======================

    with st.expander(config_labels["headers"]["dataframes"]):
        st.subheader("Line Plot DataFrame (`df`)")
        st.dataframe(df)

        st.subheader("Bar Plot DataFrame (`dfh`)")
        st.dataframe(dfh)

    # ======================
    # Download Buttons
    # ======================

    # Download Line Plot DataFrame
    csv_df = df.to_csv(index=False)
    st.download_button(
        label=config_labels["download_buttons"]["df_csv"],
        data=csv_df,
        file_name='df.csv',
        mime='text/csv',
    )

    # Download Bar Plot DataFrame
    csv_dfh = dfh.to_csv(index=False)
    st.download_button(
        label=config_labels["download_buttons"]["dfh_csv"],
        data=csv_dfh,
        file_name='dfh.csv',
        mime='text/csv',
    )

# Entry point
if __name__ == "__main__":
    main()
