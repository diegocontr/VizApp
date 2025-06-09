from pathlib import Path

import streamlit as st

from modelviz.config import (
    analysis_explanations,
    config_colors,
    config_labels,
    custom_xticks,
    data_retrieval_config,  # Import data_retrieval_config
    global_settings,  # Import global_settings
)
from modelviz.data_loader import load_data_dict
from modelviz.dataframe_display import display_dataframes
from modelviz.plotting import create_figure
from modelviz.sidebar_setup import select_config, setup_sidebar

# ===========================
# Configurable Paths
# ===========================
DATA_PATH = "./data"
IMAGE_PATH = "./images/log.jpeg"

# Entry point
if __name__ == "__main__":
    # Set page configuration
    st.set_page_config(page_title="Data Visualization Tool", layout="wide", page_icon="📊")

    selected_file = setup_sidebar(config_labels, IMAGE_PATH, DATA_PATH)

    if not selected_file:
        st.stop()

    full_data_path = Path(DATA_PATH) / selected_file
    loaded_json_data = load_data_dict(full_data_path)

    if loaded_json_data is None:
        st.error(f"Failed to load data from {full_data_path}. Please check the file and logs.")
        st.stop()

    # dictionary_aggregated_values is now obtained from global_settings
    # This specific variable might not be needed directly here if select_config and other functions
    # correctly use the global_settings passed to them.
    # For example, select_config uses global_settings to get dictionary_aggregated_values for y0.

    # The 'data_dict' previously used for populating dropdowns is now handled internally by
    # select_config using loaded_json_data and data_retrieval_config.

    # selected_params_dict now holds all selections including y0 and var_y_type
    selected_params_dict = select_config(
        loaded_json_data,
        config_labels,
        analysis_explanations,
        global_settings,  # Pass the imported global_settings
        data_retrieval_config,
    )

    # viz_configs bundles various configuration dictionaries for plotting
    viz_configs = {
        "config_labels": config_labels,
        "config_colors": config_colors,
        "custom_xticks": custom_xticks,
        "data_retrieval_config": data_retrieval_config,
        # global_settings could also be part of viz_configs if needed by plotting directly
    }

    fig_plotly, add_third_subplot = create_figure(
        loaded_json_data,
        selected_params_dict,
        viz_configs,
    )
    st.header(f"{selected_params_dict['column']}.")
    st.plotly_chart(fig_plotly, use_container_width=True)

    display_dataframes(
        loaded_json_data,
        selected_params_dict,
        config_labels,
        data_retrieval_config,
        add_third_subplot,
    )
