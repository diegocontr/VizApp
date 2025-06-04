import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from PIL import Image
import plotly.express as px

# ===========================
# Configurable Paths
# ===========================
DATA_PATH = './data'
IMAGE_PATH = './images/log.jpeg'

# ===========================
# Configuration Dictionaries
# ===========================

# Labels and Captions
config_labels = {
    "menus": {
        "file": "Select Data File",
        "database": "Select Database",
        "analysis_type": "Select Analysis Type",
        "column_to_analyse": "Select Column to Analyse",
        "agg_function": "Select Aggregation Function",
        "reference": "Select Reference",
        "groupping": "Select Groupping",
        "target": "Select Target(s)",
        "reference": "Select Reference Type for Var Y Calculation"
    },
    "plot": {
        "x_label": "X-Axis",
        "y_label_line": "Y-Axis (Line Plot)",
        "y_label_var_y": "Y-Axis (Var Y Plot)",
        "title_line": "Data Visualization Plot - Y vs X",
        "title_var_y": "Data Visualization Plot - Var Y vs X",
        "title_group_hist": "Grouped Histogram",
        "fig_size": (1200, 1000)  # Width, Height in pixels
    },
    "headers": {
        "main": "📊 Mock Database Visualization",
        "dataframes": "View Underlying Data"
    },
    "download_buttons": {
        "df_csv": "Download Line Plot Data as CSV",
        "dfh_csv": "Download Bar Plot Data as CSV"
    },
    "help": {
        "database": "Choose the database to analyze.",
        "analysis_type": "Select the type of analysis to perform.",
        "column_to_analyse": "Pick the column for analysis.",
        "agg_function": "Select the aggregation function.",
        "groupping": "Choose how to group the data.",
        "target": "Select the target variable(s) for analysis.",
        "reference": "Select the reference type for Var Y calculation."
    }
}

# Colors
config_colors = {
    "line_all": "#1f77b4",       # Default Blue
    "bar_plot": "#ff7f0e",       # Default Orange
    "background": "#FFFFFF",     # White
    "plotly_palette": px.colors.qualitative.Plotly  # Plotly's qualitative palette
}

# Dictionary for explanations of each analysis type
analysis_explanations = {
    "analysis_type_1": "This is the analysis i",
    "analysis_type_2": "This is the analysis ii",
    # Add more as needed
}

# Dictionary for specific reference values
dictionary_aggregated_values = {
    'mean': 100,
    'median': 1000
}

# ===========================
# Custom X-Ticks Dictionary
# ===========================

def map_xticks(d):
    return dict(zip(d['xticks'], d['xticklabels']))

custom_xticks = {
#    'column1': {
#        'xticks': [0, 5, 10, 15],
#        'xticklabels': ['A', 'B', 'C', 'D']
#    }
   'column1': {
       'xticks': list(range(1,101)),
       'xticklabels': [str(i) for i in range(1, 101)]
   }
    # Add more entries if needed
}

# ===========================
# Utility Functions
# ===========================

@st.cache_data(show_spinner=False)
def load_data_dict(filename):
    """
    Loads the nested data_dict from a JSON file, converting JSON strings back to DataFrames.
    """
    try:
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
                                    entry = data_dict_json[db][analysis][column][agg][ref][group][target]
                                    df = pd.read_json(entry['df'], orient='split')
                                    dfh = pd.read_json(entry['dfh'], orient='split')
                                    data_dict_json[db][analysis][column][agg][ref][group][target]['df'] = df
                                    data_dict_json[db][analysis][column][agg][ref][group][target]['dfh'] = dfh
                                    # If dfhg exists, convert it too
                                    if 'dfhg' in entry:
                                        dfhg = pd.read_json(entry['dfhg'], orient='split')
                                        data_dict_json[db][analysis][column][agg][ref][group][target]['dfhg'] = dfhg
        return data_dict_json

    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return {}

def load_logo(image_path):
    """
    Loads the logo image.
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

def setup_sidebar(config_labels, IMAGE_PATH, DATA_PATH):
    # Load the logo
    logo = load_logo(IMAGE_PATH)
    if logo:
        st.sidebar.image(logo, use_container_width=True)
    st.sidebar.header(config_labels["headers"]["main"])

    # Let the user select a file from the data folder
    data_files = [f.name for f in Path(DATA_PATH).glob('*.json')]
    if not data_files:
        st.error("No data files found in the 'data' folder.")
        st.stop()
    selected_file = st.sidebar.selectbox(config_labels["menus"]["file"], data_files)
    return selected_file

def select_config(data_dict, config_labels, analysis_explanations, dictionary_aggregated_values):
    databases = list(data_dict.keys())
    st.sidebar.header("Configuration")
    selected_db = st.sidebar.selectbox(
        config_labels["menus"]["database"], databases,
        help=config_labels["help"]["database"]
    )
    analysis_types = list(data_dict[selected_db].keys())
    selected_analysis = st.sidebar.selectbox(
        config_labels["menus"]["analysis_type"], analysis_types,
        help=config_labels["help"]["analysis_type"]
    )
    if selected_analysis in analysis_explanations and analysis_explanations[selected_analysis]:
        st.sidebar.write(analysis_explanations[selected_analysis])
    columns_to_analyse = list(data_dict[selected_db][selected_analysis].keys())
    selected_column = st.sidebar.selectbox(
        config_labels["menus"]["column_to_analyse"], columns_to_analyse,
        help=config_labels["help"]["column_to_analyse"]
    )
    agg_functions = list(data_dict[selected_db][selected_analysis][selected_column].keys())
    selected_agg = st.sidebar.selectbox(
        config_labels["menus"]["agg_function"], agg_functions,
        help=config_labels["help"]["agg_function"]
    )
    selected_ref = 'ref1'
    grouppings = list(data_dict[selected_db][selected_analysis][selected_column][selected_agg][selected_ref].keys())
    selected_group = st.sidebar.selectbox(
        config_labels["menus"]["groupping"], grouppings,
        help=config_labels["help"]["groupping"]
    )
    targets = list(data_dict[selected_db][selected_analysis][selected_column][selected_agg][selected_ref][selected_group].keys())
    selected_targets = st.sidebar.multiselect(
        config_labels["menus"]["target"], targets, default=[targets[0]],
        help=config_labels["help"]["target"]
    )
    if not selected_targets:
        st.warning("Please select at least one target.")
        st.stop()
    var_y_options = ["min", "max"] + list(dictionary_aggregated_values.keys())
    var_y_type = st.sidebar.selectbox(
        config_labels["menus"]["reference"], var_y_options,
        help=config_labels["help"]["reference"]
    )
    y0 = dictionary_aggregated_values.get(var_y_type)
    return (selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets, var_y_type, y0)

def create_figure(data_dict, config_labels, config_colors, custom_xticks, selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets, var_y_type, y0):
    # Determine if we have a third subplot
    add_third_subplot = (selected_group != 'all')

    # Get figure size from configuration
    fig_width, fig_height = config_labels["plot"]["fig_size"]
    if add_third_subplot:
        fig_height = int(fig_height * 1.5)  # Increase height for three subplots

    # Determine subplot rows
    if add_third_subplot:
        rows = 3
        subplot_titles = (
            config_labels["plot"]["title_line"],
            config_labels["plot"]["title_var_y"],
            config_labels["plot"]["title_group_hist"]
        )
        specs = [
            [{"secondary_y": True}],
            [{"secondary_y": True}],
            [{}]
        ]
    else:
        rows = 2
        subplot_titles = (
            config_labels["plot"]["title_line"],
            config_labels["plot"]["title_var_y"]
        )
        specs = [
            [{"secondary_y": True}],
            [{"secondary_y": True}]
        ]

    # Prepare the figure
    fig_plotly = make_subplots(
        rows=rows, cols=1,
        subplot_titles=subplot_titles,
        shared_xaxes=False,
        vertical_spacing=0.15,
        specs=specs
    )

    plotly_palette = config_colors["plotly_palette"]

    # We'll handle the bar plot only once, using the first selected target
    first_target = selected_targets[0]
    first_data = data_dict[selected_db][selected_analysis][selected_column][selected_agg][selected_ref][selected_group][first_target]
    dfh_first = first_data['dfh']

    if selected_column in custom_xticks:
        dfh_first['x'] = dfh_first['x'].map( map_xticks( custom_xticks[selected_column]))
        dfh_first = dfh_first.sort_values('x')


    if dfh_first.empty:
        st.error("No bar plot data available for the selected configuration.")
        st.stop()

    group_list = None

    # ---------------------------------------------
    # If we have a third subplot (grouped histogram per group), plot dfhg
    if add_third_subplot and 'dfhg' in first_data:
        dfhg_first = first_data['dfhg']
        if selected_column in custom_xticks:
            dfhg_first['x'] = dfhg_first['x'].map( map_xticks( custom_xticks[selected_column]))
            group_list = dfhg_first['group'].unique().tolist()
            dfhg_first['order'] = dfhg_first['group'].apply(lambda g: group_list.index(g))
            dfhg_first = dfhg_first.sort_values(['order','x'])


        if not dfhg_first.empty:
            # group-based histogram: one bar trace per group
            unique_groups_hg = dfhg_first['group'].unique()
            for idx, g in enumerate(unique_groups_hg):
                group_dfhg = dfhg_first[dfhg_first['group'] == g]
                color = plotly_palette[idx % len(plotly_palette)]
                fig_plotly.add_trace(
                    go.Bar(
                        x=group_dfhg['x'],
                        y=group_dfhg['y'],
                        name=f"Group {g} Hist",
                        marker=dict(color=color),
                        opacity=0.7
                    ),
                    row=3, col=1
                )
            # Set barmode to group so bars appear side-by-side
            fig_plotly.update_layout(barmode='group')
        else:
            st.warning("dfhg is empty for the selected configuration.")

    # A line index to differentiate line colors for each target-group combination
    line_index = 0

    # Loop over selected targets to plot line data
    for target in selected_targets:
        selected_data = data_dict[selected_db][selected_analysis][selected_column][selected_agg][selected_ref][selected_group][target]
        df = selected_data['df']

        if df.empty:
            st.error(f"No line plot data available for the target: {target}")
            continue

        df_sorted = df.sort_values(by=['group', 'x'])

        # Compute var_y on the fly
        y_min = df_sorted['y'].min()
        y_max = df_sorted['y'].max()

        if var_y_type == 'min':
            var_y = 100 * (df_sorted['y'] - y_min) / y_min
        elif var_y_type == 'max':
            var_y = 100 * (df_sorted['y'] - y_max) / y_max
        else:
            # specific key from dictionary_aggregated_values
            var_y = 100 * (df_sorted['y'] - y0) / y0

        unique_groups_data = df_sorted['group'].unique()

        for g in unique_groups_data:
            group_df = df_sorted[df_sorted['group'] == g]
            color = plotly_palette[line_index % len(plotly_palette)]
            fig_plotly.add_trace(
                go.Scatter(
                    x=group_df['x'],
                    y=group_df['y'],
                    mode='lines+markers',
                    name=f"{target}-{g}",
                    line=dict(color=color),
                    marker=dict(color=color)
                ),
                row=1, col=1,
                secondary_y=False
            )
            # Plot lines for var_y vs X (bottom subplot)
            var_y_group = var_y[group_df.index]
            fig_plotly.add_trace(
                go.Scatter(
                    x=group_df['x'],
                    y=var_y_group,
                    mode='lines+markers',
                    name=f"{target}-{g} Var Y",
                    line=dict(color=color),
                    marker=dict(color=color),
                    showlegend=False
                ),
                row=2, col=1,
                secondary_y=False
            )

            line_index += 1
    # ---------------------------------------------
    # Add bar plot once to the first two subplots
    fig_plotly.add_trace(
        go.Bar(
            x=dfh_first['x'],
            y=dfh_first['y'],
            name='Bar Plot',
            marker=dict(color=config_colors["bar_plot"]),
            opacity=0.3
        ),
        row=1, col=1,
        secondary_y=True
    )
    fig_plotly.add_trace(
        go.Bar(
            x=dfh_first['x'],
            y=dfh_first['y'],
            name='Bar Plot Var Y',
            marker=dict(color=config_colors["bar_plot"]),
            opacity=0.3,
            showlegend=False
        ),
        row=2, col=1,
        secondary_y=True
    )
    # ---------------------------------------------

    # If after looping no data was plotted (e.g., all were empty), stop
    if len(fig_plotly.data) == 0:
        st.error("No data was plotted. Check your selections.")
        st.stop()
    # ---------------------------------------------
    # Update axes titles
    fig_plotly.update_yaxes(title_text=config_labels["plot"]["y_label_line"], row=1, col=1, secondary_y=False)
    fig_plotly.update_yaxes(title_text="Bar Plot Y-Axis", row=1, col=1, secondary_y=True)
    fig_plotly.update_yaxes(title_text=config_labels["plot"]["y_label_var_y"], row=2, col=1, secondary_y=False)
    fig_plotly.update_yaxes(title_text="Bar Plot Y-Axis", row=2, col=1, secondary_y=True)
    if add_third_subplot:
        fig_plotly.update_yaxes(title_text="Grouped Histogram Y-Axis", row=3, col=1)

    fig_plotly.update_xaxes(title_text=config_labels["plot"]["x_label"], row=2, col=1)
    if add_third_subplot:
        fig_plotly.update_xaxes(title_text=config_labels["plot"]["x_label"], row=3, col=1)

    # Update layout
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

    # Update hover templates
    for trace in fig_plotly['data']:
        if trace['type'] == 'scatter':
            trace['hovertemplate'] = (
                f"{config_labels['plot']['x_label']}: %{{x}}<br>"
                f"%{{y}}<extra>%{{fullData.name}}</extra>"
            )
        elif trace['type'] == 'bar':
            trace['hovertemplate'] = (
                f"{config_labels['plot']['x_label']}: %{{x}}<br>"
                f"Bar Plot: %{{y}}<extra>%{{fullData.name}}</extra>"
            )

    # If custom xticks available for selected_column, apply them
    # if selected_column in custom_xticks:
    #     xticks = custom_xticks[selected_column]['xticks']
    #     xticklabels = custom_xticks[selected_column]['xticklabels']

    #     # Update x-axis for first two subplots
    #     fig_plotly.update_xaxes(
    #         tickmode='array',
    #         tickvals=xticks,
    #         ticktext=xticklabels,
    #         row=1, col=1
    #     )
    #     fig_plotly.update_xaxes(
    #         tickmode='array',
    #         tickvals=xticks,
    #         ticktext=xticklabels,
    #         row=2, col=1
    #     )
    #     # Also update third if it exists
    #     if add_third_subplot:
    #         fig_plotly.update_xaxes(
    #             tickmode='array',
    #             tickvals=xticks,
    #             ticktext=xticklabels,
    #             row=3, col=1
    #         )



    return fig_plotly, add_third_subplot

def display_dataframes(data_dict, config_labels, selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets, add_third_subplot):
    with st.expander(config_labels["headers"]["dataframes"]):
        # Show each selected target's dataframes
        for t in selected_targets:
            t_data = data_dict[selected_db][selected_analysis][selected_column][selected_agg][selected_ref][selected_group][t]
            t_df = t_data['df']
            t_dfh = t_data['dfh']
            st.subheader(f"Target: {t}")
            st.write("Line Plot DataFrame (`df`):")
            st.dataframe(t_df)
            st.write("Bar Plot DataFrame (`dfh`):")
            st.dataframe(t_dfh)
            if add_third_subplot and 'dfhg' in t_data:
                st.write("Grouped Histogram DataFrame (`dfhg`):")
                st.dataframe(t_data['dfhg'])

            # Download buttons for each target
            csv_df = t_df.to_csv(index=False)
            st.download_button(
                label=f"{config_labels['download_buttons']['df_csv']} - {t}",
                data=csv_df,
                file_name=f'df_{t}.csv',
                mime='text/csv',
            )

            csv_dfh = t_dfh.to_csv(index=False)
            st.download_button(
                label=f"{config_labels['download_buttons']['dfh_csv']} - {t}",
                data=csv_dfh,
                file_name=f'dfh_{t}.csv',
                mime='text/csv',
            )
            if add_third_subplot and 'dfhg' in t_data:
                csv_dfhg = t_data['dfhg'].to_csv(index=False)
                st.download_button(
                    label=f"Download dfhg Data as CSV - {t}",
                    data=csv_dfhg,
                    file_name=f'dfhg_{t}.csv',
                    mime='text/csv',
                )


# Entry point
if __name__ == "__main__":
    # Set page configuration
    st.set_page_config(page_title="Data Visualization Tool", layout="wide", page_icon="📊")

    selected_file = setup_sidebar(config_labels, IMAGE_PATH, DATA_PATH)
    data_dict = load_data_dict(Path(DATA_PATH) / selected_file)

    if not data_dict:
        st.stop()

    (
        selected_db, selected_analysis, selected_column, selected_agg, selected_ref,
        selected_group, selected_targets, var_y_type, y0
    ) = select_config(data_dict, config_labels, analysis_explanations, dictionary_aggregated_values)

    fig_plotly, add_third_subplot = create_figure(
        data_dict, config_labels, config_colors, custom_xticks,
        selected_db, selected_analysis, selected_column, selected_agg, selected_ref,
        selected_group, selected_targets, var_y_type, y0
    )

    st.header(f"Variable impact for {selected_column} in {selected_db}.")
    st.plotly_chart(fig_plotly, use_container_width=True)

    display_dataframes(
        data_dict, config_labels, selected_db, selected_analysis, selected_column,
        selected_agg, selected_ref, selected_group, selected_targets, add_third_subplot
    )
