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
    },
    "plot": {
        "x_label": "X-Axis",
        "y_label_line": "Y-Axis (Line Plot)",
        "y_label_var_y": "Y-Axis (Var Y Plot)",
        "title_line": "Data Visualization Plot - Y vs X",
        "title_var_y": "Data Visualization Plot - Var Y vs X",
        "title_group_hist": "Grouped Histogram",
        "fig_size": (1200, 1000)
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
    },
    "labels": {
        "bar_plot": "Bar Plot",
        "bar_plot_var_y": "Bar Plot Var Y"
    }
}

config_colors = {
    "line_all": "#1f77b4",       # Default Blue
    "bar_plot": "#ff7f0e",       # Default Orange
    "background": "#FFFFFF",     # White
    "plotly_palette": px.colors.qualitative.Plotly  # Plotly's qualitative palette
}

analysis_explanations = {
    "analysis_type_1": "This is the analysis i",
    "analysis_type_2": "This is the analysis ii",
    # Add more as needed
}

dictionary_aggregated_values = {
    'mean': 100,
    'median': 1000
}


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