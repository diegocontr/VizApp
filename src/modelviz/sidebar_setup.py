# filepath: /home/diego/Dropbox/DropboxGit/VizApp/src/modelviz/sidebar_setup.py
from pathlib import Path

import streamlit as st

from .data_loader import load_logo
from .keygen import get_all_distinct_parameter_values, reverse_key_generator


def setup_sidebar(config_labels, IMAGE_PATH, DATA_PATH):
    # Load the logo
    logo = load_logo(IMAGE_PATH)
    if logo:
        st.sidebar.image(logo, use_container_width=True)
    st.sidebar.header(config_labels["headers"]["main"])

    # Let the user select a file from the data folder
    data_files = [f.name for f in Path(DATA_PATH).glob("*.json")]
    if not data_files:
        st.error("No data files found in the 'data' folder.")
        st.stop()
    selected_file = st.sidebar.selectbox(config_labels["menus"]["file"], data_files)
    return selected_file


def select_config(data_dict, config_labels, analysis_explanations, dictionary_aggregated_values):
    # Get all unique parameter values using keygen utility
    param_names = ["db", "analysis", "column", "agg", "ref", "group", "target"]
    all_options = get_all_distinct_parameter_values(data_dict, param_names, preserved_types_in_keys=True)

    st.sidebar.header("Configuration")
    selected_db = st.sidebar.selectbox(
        config_labels["menus"]["database"], all_options["db"], help=config_labels["help"]["database"]
    )
    selected_analysis = st.sidebar.selectbox(
        config_labels["menus"]["analysis_type"], all_options["analysis"], help=config_labels["help"]["analysis_type"]
    )
    if selected_analysis in analysis_explanations and analysis_explanations[selected_analysis]:
        st.sidebar.write(analysis_explanations[selected_analysis])
    selected_column = st.sidebar.selectbox(
        config_labels["menus"]["column_to_analyse"],
        all_options["column"],
        help=config_labels["help"]["column_to_analyse"],
    )
    selected_agg = st.sidebar.selectbox(
        config_labels["menus"]["agg_function"], all_options["agg"], help=config_labels["help"]["agg_function"]
    )
    selected_ref = st.sidebar.selectbox(
        config_labels["menus"]["reference"], all_options["ref"], help=config_labels["help"]["reference"]
    )
    selected_group = st.sidebar.selectbox(
        config_labels["menus"]["groupping"], all_options["group"], help=config_labels["help"]["groupping"]
    )
    # Filter targets for the current selection
    filtered_targets = [
        reverse_key_generator(k, preserved_types=True)["target"]
        for k in data_dict
        if reverse_key_generator(k, preserved_types=True).get("db") == selected_db
        and reverse_key_generator(k, preserved_types=True).get("analysis") == selected_analysis
        and reverse_key_generator(k, preserved_types=True).get("column") == selected_column
        and reverse_key_generator(k, preserved_types=True).get("agg") == selected_agg
        and reverse_key_generator(k, preserved_types=True).get("ref") == selected_ref
        and reverse_key_generator(k, preserved_types=True).get("group") == selected_group
    ]
    filtered_targets = sorted(set(filtered_targets))
    selected_targets = st.sidebar.multiselect(
        config_labels["menus"]["target"],
        filtered_targets,
        default=filtered_targets[:1],
        help=config_labels["help"]["target"],
    )
    if not selected_targets:
        st.warning("Please select at least one target.")
        st.stop()
    var_y_options = ["min", "max"] + list(dictionary_aggregated_values.keys())
    var_y_type = st.sidebar.selectbox(
        config_labels["menus"]["reference"], var_y_options, help=config_labels["help"]["reference"]
    )
    y0 = dictionary_aggregated_values.get(var_y_type)
    return (
        selected_db,
        selected_analysis,
        selected_column,
        selected_agg,
        selected_ref,
        selected_group,
        selected_targets,
        var_y_type,
        y0,
    )
