# filepath: /home/diego/Dropbox/DropboxGit/VizApp/src/modelviz/plotting.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .keygen import key_generator

def create_figure(data_dict, config_labels, config_colors, custom_xticks, selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets, var_y_type, y0):
    """
    Creates a Plotly figure with line plots, bar plots, and a grouped histogram (optional).
    """
    add_third_subplot = (selected_group != 'all')
    fig_width, fig_height = get_figure_size(config_labels, add_third_subplot)
    subplot_titles, specs = get_subplot_specs(config_labels, add_third_subplot)
    fig_plotly = make_subplots(
        rows=3 if add_third_subplot else 2, cols=1,
        subplot_titles=subplot_titles,
        shared_xaxes=False,
        vertical_spacing=0.15,
        specs=specs
    )

    dfh_first = prepare_bar_plot_data(data_dict, selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets, custom_xticks)
    if dfh_first.empty:
        st.error("No bar plot data available for the selected configuration.")
        st.stop()

    if add_third_subplot:
        add_grouped_histogram(fig_plotly, data_dict, config_labels, config_colors, custom_xticks, selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets)

    add_line_plots(fig_plotly, data_dict, config_labels, config_colors, selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets, var_y_type, y0)
    add_bar_plots(fig_plotly, config_labels, config_colors, dfh_first)
    update_layout(fig_plotly, config_labels, config_colors, fig_width, fig_height, add_third_subplot)
    update_hover_templates(fig_plotly, config_labels)
    apply_custom_xticks(fig_plotly, custom_xticks, selected_column, add_third_subplot)

    if len(fig_plotly.data) == 0:
        st.error("No data was plotted. Check your selections.")
        st.stop()

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
            config_labels["plot"]["title_group_hist"]
        )
        specs = [
            [{"secondary_y": True}],
            [{"secondary_y": True}],
            [{}]
        ]
    else:
        subplot_titles = (
            config_labels["plot"]["title_line"],
            config_labels["plot"]["title_var_y"]
        )
        specs = [
            [{"secondary_y": True}],
            [{"secondary_y": True}]
        ]
    return subplot_titles, specs

def prepare_bar_plot_data(data_dict, selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets, custom_xticks):
    """
    Prepares the data for the bar plot based on the selected configuration.
    """
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
    return dfh_first

def add_grouped_histogram(fig_plotly, data_dict, config_labels, config_colors, custom_xticks, selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets):
    """
    Adds a grouped histogram to the figure if a third subplot is enabled.
    """
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
    if 'dfhg' in first_data:
        dfhg_first = first_data['dfhg']
        if selected_column in custom_xticks:
            dfhg_first['x'] = dfhg_first['x'].map(map_xticks(custom_xticks[selected_column]))
            group_list = dfhg_first['group'].unique().tolist()
            dfhg_first['order'] = dfhg_first['group'].apply(lambda g: group_list.index(g))
            dfhg_first = dfhg_first.sort_values(['order','x'])

        if not dfhg_first.empty:
            unique_groups_hg = dfhg_first['group'].unique()
            for idx, g in enumerate(unique_groups_hg):
                group_dfhg = dfhg_first[dfhg_first['group'] == g]
                plotly_palette = config_colors["plotly_palette"]
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
            fig_plotly.update_layout(barmode='group')
        else:
            st.warning("dfhg is empty for the selected configuration.")

def add_line_plots(fig_plotly, data_dict, config_labels, config_colors, selected_db, selected_analysis, selected_column, selected_agg, selected_ref, selected_group, selected_targets, var_y_type, y0):
    """
    Adds line plots to the figure based on the selected targets and configuration.
    """
    plotly_palette = config_colors["plotly_palette"]
    line_index = 0
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
        y_min = df_sorted['y'].min()
        y_max = df_sorted['y'].max()

        if var_y_type == 'min':
            var_y = 100 * (df_sorted['y'] - y_min) / y_min
        elif var_y_type == 'max':
            var_y = 100 * (df_sorted['y'] - y_max) / y_max
        else:
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

def add_bar_plots(fig_plotly, config_labels, config_colors, dfh_first):
    """
    Adds bar plots to the first two subplots.
    """
    fig_plotly.add_trace(
        go.Bar(
            x=dfh_first['x'],
            y=dfh_first['y'],
            name=config_labels["labels"]["bar_plot"],
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
            name=config_labels["labels"]["bar_plot_var_y"],
            marker=dict(color=config_colors["bar_plot"]),
            opacity=0.3,
            showlegend=False
        ),
        row=2, col=1,
        secondary_y=True
    )

def update_layout(fig_plotly, config_labels, config_colors, fig_width, fig_height, add_third_subplot):
    """
    Updates the layout of the figure with titles, colors, and margins.
    """
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
            x=1
        ),
        plot_bgcolor=config_colors["background"],
        paper_bgcolor=config_colors["background"],
        margin=dict(l=50, r=50, t=100, b=50)
    )

def update_hover_templates(fig_plotly, config_labels):
    """
    Updates the hover templates for the traces in the figure.
    """
    for trace in fig_plotly['data']:
        if trace['type'] == 'scatter':
            trace['hovertemplate'] = (
                f"{config_labels['plot']['x_label']}: %{{x}}<br>"
                f"%{{y}}<extra>%{{fullData.name}}</extra>"
            )
        elif trace['type'] == 'bar':
            trace['hovertemplate'] = (
                f"{config_labels['plot']['x_label']}: %{{x}}<br>"
                f"{config_labels['labels']['bar_plot']}: %{{y}}<extra>%{{fullData.name}}</extra>"
            )

def apply_custom_xticks(fig_plotly, custom_xticks, selected_column, add_third_subplot):
    """
    Applies custom x-axis ticks to the figure if available for the selected column.
    """
    if selected_column in custom_xticks:
        xticks = custom_xticks[selected_column]['xticks']
        xticklabels = custom_xticks[selected_column]['xticklabels']

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
        if add_third_subplot:
            fig_plotly.update_xaxes(
                tickmode='array',
                tickvals=xticks,
                ticktext=xticklabels,
                row=3, col=1
            )

def map_xticks(d):
    return dict(zip(d['xticks'], d['xticklabels']))

def get_data_entry(data_dict, params):
    from .keygen import key_generator
    key = key_generator(params, preserve_types=True)
    return data_dict[key]