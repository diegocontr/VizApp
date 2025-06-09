# filepath: /home/diego/Dropbox/DropboxGit/VizApp/src/modelviz/plotting.py
import pandas as pd  # Ensure pandas is imported
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from .data_utils import get_dataframe_from_json_entrypoint  # Import from data_utils


# This is the refactored create_figure function.
# If you still get a TypeError about missing positional arguments,
# it means Python is NOT running this updated version of the code.
# Ensure this file is saved and your Python environment/Streamlit server is restarted.
def create_figure(
    loaded_json_data,
    selected_params,  # This is a dictionary of all user selections
    viz_configs,  # This is a dictionary containing other configurations
):
    """
    Creates a Plotly figure with line plots, bar plots, and a grouped histogram (optional).
    """
    # Unpack configurations from viz_configs
    config_labels = viz_configs["config_labels"]
    config_colors = viz_configs["config_colors"]
    custom_xticks = viz_configs["custom_xticks"]
    data_retrieval_config = viz_configs["data_retrieval_config"]

    # Extract individual selections from the selected_params dictionary
    # These names (e.g., "group", "column") must match the keys set in selected_params_dict in sidebar_setup.py
    selected_group = selected_params.get("group")
    selected_column = selected_params.get("column")
    selected_targets = selected_params.get("targets", [])  # Ensure 'targets' is the key used in selected_params
    var_y_type = selected_params.get("var_y_type")
    y0 = selected_params.get("y0")
    # Other parameters like selected_db, selected_analysis, etc., are implicitly passed
    # within the 'selected_params' dict to get_dataframe_from_json_entrypoint.

    # Determine if we have a third subplot
    add_third_subplot = selected_group != "all" and selected_group is not None  # Ensure group is not None

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
            config_labels["plot"]["title_group_hist"],
        )
        specs = [
            [{"secondary_y": True}],
            [{"secondary_y": True}],
            [{}],
        ]
    else:
        rows = 2
        subplot_titles = (
            config_labels["plot"]["title_line"],
            config_labels["plot"]["title_var_y"],
        )
        specs = [
            [{"secondary_y": True}],
            [{"secondary_y": True}],
        ]

    # Prepare the figure
    fig_plotly = make_subplots(
        rows=rows,
        cols=1,
        subplot_titles=subplot_titles,
        shared_xaxes=False,
        vertical_spacing=0.15,
        specs=specs,
    )

    plotly_palette = config_colors["plotly_palette"]

    # We'll handle the bar plot only once, using the first selected target (if targets exist)
    first_target_for_dfh = selected_targets[0] if selected_targets else None

    dfh_first = get_dataframe_from_json_entrypoint(
        loaded_json_data,
        "dfh",
        selected_params,
        first_target_for_dfh,
        data_retrieval_config,  # Pass the whole selected_params
    )

    if dfh_first is None or dfh_first.empty:
        st.error("No bar plot data (dfh) available for the selected configuration.")
        # Optionally, allow continuing if other plots might exist
        # st.stop()
        dfh_first = pd.DataFrame(columns=["x", "y"])  # Use empty df to prevent errors

    if selected_column in custom_xticks and not dfh_first.empty:
        dfh_first["x"] = dfh_first["x"].map(map_xticks(custom_xticks[selected_column]))
        dfh_first = dfh_first.sort_values("x")

    group_list = None

    # If we have a third subplot (grouped histogram per group), plot dfhg
    if add_third_subplot:
        # dfhg typically uses the first target as well, or iterates if structure supports multiple dfhg per target
        first_target_for_dfhg = selected_targets[0] if selected_targets else None
        dfhg_first = get_dataframe_from_json_entrypoint(
            loaded_json_data,
            "dfhg",
            selected_params,
            first_target_for_dfhg,
            data_retrieval_config,  # Pass selected_params
        )

        if dfhg_first is not None and not dfhg_first.empty:
            if selected_column in custom_xticks:
                dfhg_first["x"] = dfhg_first["x"].map(map_xticks(custom_xticks[selected_column]))
                # Ensure 'group' column exists before trying to use it
                if "group" in dfhg_first.columns:
                    group_list = dfhg_first["group"].unique().tolist()
                    dfhg_first["order"] = dfhg_first["group"].apply(lambda g: group_list.index(g))
                    dfhg_first = dfhg_first.sort_values(["order", "x"])
                else:
                    st.warning("Column 'group' not found in dfhg data for sorting.")

            if "group" in dfhg_first.columns:
                unique_groups_hg = dfhg_first["group"].unique()
                for idx, g_val in enumerate(unique_groups_hg):  # Renamed g to g_val to avoid conflict
                    group_dfhg = dfhg_first[dfhg_first["group"] == g_val]
                    color = plotly_palette[idx % len(plotly_palette)]
                    fig_plotly.add_trace(
                        go.Bar(
                            x=group_dfhg["x"],
                            y=group_dfhg["y"],
                            name=f"Group {g_val} Hist",
                            marker=dict(color=color),
                            opacity=0.7,
                        ),
                        row=3,
                        col=1,
                    )
                fig_plotly.update_layout(barmode="group")
            else:
                st.warning("Cannot create grouped histogram as 'group' column is missing in dfhg.")
        # else:
        #    st.warning("dfhg is empty or None for the selected configuration.")

    # A line index to differentiate line colors for each target-group combination
    line_index = 0

    # Loop over selected targets to plot line data
    for target in selected_targets:
        df = get_dataframe_from_json_entrypoint(
            loaded_json_data,
            "df",
            selected_params,
            target,
            data_retrieval_config,  # Pass selected_params
        )

        if df is None or df.empty:
            st.error(f"No line plot data (df) available for the target: {target}")
            continue

        # Ensure 'group' and 'x' columns exist
        if not all(col in df.columns for col in ["group", "x", "y"]):
            st.error(f"DataFrame for target {target} is missing required columns (group, x, or y).")
            continue

        df_sorted = df.sort_values(by=["group", "x"])

        y_min_val = df_sorted["y"].min()  # Renamed to avoid conflict
        y_max_val = df_sorted["y"].max()  # Renamed to avoid conflict

        if var_y_type == "min":
            var_y = 100 * (df_sorted["y"] - y_min_val) / y_min_val if y_min_val != 0 else 0
        elif var_y_type == "max":
            var_y = 100 * (df_sorted["y"] - y_max_val) / y_max_val if y_max_val != 0 else 0
        elif y0 is not None and y0 != 0:
            var_y = 100 * (df_sorted["y"] - y0) / y0
        else:  # y0 is None or zero
            var_y = pd.Series([0] * len(df_sorted["y"]), index=df_sorted.index)  # Default to zero variation
            if y0 == 0 and var_y_type not in ["min", "max"]:
                st.warning(f"y0 is zero for var_y calculation (type: {var_y_type}). Setting Var Y to 0.")

        unique_groups_data = df_sorted["group"].unique()

        for g_val in unique_groups_data:  # Renamed g to g_val
            group_df = df_sorted[df_sorted["group"] == g_val]
            color = plotly_palette[line_index % len(plotly_palette)]
            fig_plotly.add_trace(
                go.Scatter(
                    x=group_df["x"],
                    y=group_df["y"],
                    mode="lines+markers",
                    name=f"{target}-{g_val}",
                    line=dict(color=color),
                    marker=dict(color=color),
                ),
                row=1,
                col=1,
                secondary_y=False,
            )
            var_y_group = var_y[group_df.index]
            fig_plotly.add_trace(
                go.Scatter(
                    x=group_df["x"],
                    y=var_y_group,
                    mode="lines+markers",
                    name=f"{target}-{g_val} Var Y",
                    line=dict(color=color),
                    marker=dict(color=color),
                    showlegend=False,
                ),
                row=2,
                col=1,
                secondary_y=False,
            )
            line_index += 1
    # Add bar plot once to the first two subplots
    if not dfh_first.empty:
        fig_plotly.add_trace(
            go.Bar(
                x=dfh_first["x"],
                y=dfh_first["y"],
                name=config_labels["labels"]["bar_plot"]
                if "labels" in config_labels and "bar_plot" in config_labels["labels"]
                else "Bar Plot",
                marker=dict(color=config_colors["bar_plot"]),
                opacity=0.3,
            ),
            row=1,
            col=1,
            secondary_y=True,
        )
        fig_plotly.add_trace(
            go.Bar(
                x=dfh_first["x"],
                y=dfh_first["y"],
                name=config_labels["labels"]["bar_plot_var_y"]
                if "labels" in config_labels and "bar_plot_var_y" in config_labels["labels"]
                else "Bar Plot Var Y",
                marker=dict(color=config_colors["bar_plot"]),
                opacity=0.3,
                showlegend=False,
            ),
            row=2,
            col=1,
            secondary_y=True,
        )

    if len(fig_plotly.data) == 0:
        st.error("No data was plotted. Check your selections.")
        st.stop()

    fig_plotly.update_yaxes(title_text=config_labels["plot"]["y_label_line"], row=1, col=1, secondary_y=False)
    fig_plotly.update_yaxes(title_text="Bar Plot Y-Axis", row=1, col=1, secondary_y=True)
    fig_plotly.update_yaxes(title_text=config_labels["plot"]["y_label_var_y"], row=2, col=1, secondary_y=False)
    fig_plotly.update_yaxes(title_text="Bar Plot Y-Axis", row=2, col=1, secondary_y=True)
    if add_third_subplot:
        fig_plotly.update_yaxes(title_text="Grouped Histogram Y-Axis", row=3, col=1)

    fig_plotly.update_xaxes(title_text=config_labels["plot"]["x_label"], row=2, col=1)
    if add_third_subplot:
        fig_plotly.update_xaxes(title_text=config_labels["plot"]["x_label"], row=3, col=1)

    fig_plotly.update_layout(
        height=fig_height,
        width=fig_width,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        plot_bgcolor=config_colors["background"],
        paper_bgcolor=config_colors["background"],
        margin=dict(l=50, r=50, t=100, b=50),
    )

    for trace in fig_plotly["data"]:
        if trace["type"] == "scatter":
            trace["hovertemplate"] = (
                f"{config_labels['plot']['x_label']}: %{{x}}<br>%{{y}}<extra>%{{fullData.name}}</extra>"
            )
        elif trace["type"] == "bar":
            trace["hovertemplate"] = (
                f"{config_labels['plot']['x_label']}: %{{x}}<br>Bar Plot: %{{y}}<extra>%{{fullData.name}}</extra>"
            )

    return fig_plotly, add_third_subplot


def get_figure_size(config_labels, add_third_subplot):
    """
    Determines the figure width and height based on configuration and subplot presence.
    """
    fig_width, fig_height = config_labels["plot"]["fig_size"]
    if add_third_subplot:
        fig_height = int(fig_height * 1.5)
    return fig_width, fig_height


def get_subplot_specs(config_labels, add_third_subplot):
    """
    Defines subplot titles and specifications based on the presence of a third subplot.
    """
    if add_third_subplot:
        subplot_titles = (
            config_labels["plot"]["title_line"],
            config_labels["plot"]["title_var_y"],
            config_labels["plot"]["title_group_hist"],
        )
        specs = [[{"secondary_y": True}], [{"secondary_y": True}], [{}]]
    else:
        subplot_titles = (config_labels["plot"]["title_line"], config_labels["plot"]["title_var_y"])
        specs = [[{"secondary_y": True}], [{"secondary_y": True}]]
    return subplot_titles, specs


def map_xticks(d):
    return dict(zip(d["xticks"], d["xticklabels"]))
