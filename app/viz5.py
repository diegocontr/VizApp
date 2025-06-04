import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from PIL import Image
import plotly.express as px
from io import StringIO
from app.config import config_labels, config_colors, analysis_explanations, dictionary_aggregated_values
from modelviz.data_loader import load_data_dict, load_logo
from modelviz.sidebar_setup import setup_sidebar, select_config
from modelviz.plotting import create_figure, map_xticks
from modelviz.dataframe_display import display_dataframes

# ===========================
# Configurable Paths
# ===========================
DATA_PATH = './data'
IMAGE_PATH = './images/log.jpeg'

# ===========================
# Custom X-Ticks Dictionary
# ===========================


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
