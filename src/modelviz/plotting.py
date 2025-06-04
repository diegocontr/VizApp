# filepath: /home/diego/Dropbox/DropboxGit/VizApp/src/modelviz/plotting.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .keygen import key_generator

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

    params = {
        "db": selected_db,
        "analysis": selected_analysis,
        "column": selected_column,
        "agg": selected_agg,
        "ref": selected_ref,
        "group": selected_group,
        "target": first_target
    }
    first_data = get_data_entry(data_dict, params)
    dfh_first = first_data['dfh']

    if selected_column in custom_xticks:
        dfh_first['x'] = dfh_first['x'].map(map_xticks(custom_xticks[selected_column]))
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
            dfhg_first['x'] = dfhg_first['x'].map(map_xticks(custom_xticks[selected_column]))
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
                        x =group_dfhg['x'],
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
        params = {
            "db": selected_db,
            "analysis": selected_analysis,
            "column": selected_column,
            "agg": selected_agg,
            "ref": selected_ref,
            "group": selected_group,
            "target": target
        }
        selected_data = get_data_entry(data_dict, params)
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
            name=config_labels["labels"]["bar_plot"],  # Use the label from config
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
            name=config_labels["labels"]["bar_plot_var_y"],  # Use the label from config
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
                f"{config_labels['labels']['bar_plot']}: %{{y}}<extra>%{{fullData.name}}</extra>"  # Use the label from config
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
def map_xticks(d):
    return dict(zip(d['xticks'], d['xticklabels']))

def get_data_entry(data_dict, params):
    from .keygen import key_generator
    key = key_generator(params, preserve_types=True)
    return data_dict[key]