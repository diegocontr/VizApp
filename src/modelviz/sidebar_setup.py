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


def select_config(loaded_json_data, config_labels, analysis_explanations, global_settings, data_retrieval_config):
    selected_params_dict = {}

    # Determine all unique parameter names available for selection from data_retrieval_config
    all_configurable_params = set()
    for _data_type, conf in data_retrieval_config.items():
        all_configurable_params.update(conf["key_params"])
        # Remove fixed params as they are not user-selectable for those keys
        # for fixed_p in conf.get("fixed_params", {}).keys():
        #     if fixed_p in all_configurable_params:
        #         all_configurable_params.remove(fixed_p)

    # Parameters for sidebar dropdowns (excluding 'target' as it's handled separately and filtered)
    # The order can be predefined if necessary, e.g. ["db", "analysis", "column", "agg", "ref", "group"]
    # For now, use a default order or sort them.
    # Let's assume a preferred order for sidebar display
    sidebar_param_order = [
        "db",
        "analysis",
        "column",
        "agg",
        "ref",
        "group",
    ]  # These are the internal keys from data_retrieval_config

    # Mapping from internal param names to keys in config_labels
    param_to_config_key_map = {
        "db": "database",
        "analysis": "analysis_type",
        "column": "column_to_analyse",
        "agg": "agg_function",
        "ref": "reference",  # Assuming 'ref' in data maps to 'reference' for Var Y calc / dropdown label
        "group": "groupping",
        "target": "target",  # Though target is handled separately for multiselect
    }

    param_names_for_dropdowns = [p for p in sidebar_param_order if p in all_configurable_params]

    # Get all unique parameter values using keygen utility from the relevant source_dict
    # Assuming 'plot_data' is the primary source for now, or the first one in data_retrieval_config
    # This might need adjustment if distinct values should come from multiple source_dicts
    primary_source_key = data_retrieval_config.get("df", {}).get("source_dict_key", "plot_data")
    if primary_source_key not in loaded_json_data:
        st.error(f"Primary data source '{primary_source_key}' not found in loaded data for sidebar options.")
        st.stop()

    all_options = get_all_distinct_parameter_values(
        loaded_json_data[primary_source_key],
        list(all_configurable_params),  # Pass all, including 'target' for completeness if needed elsewhere
        preserved_types_in_keys=True,
    )

    st.sidebar.header("Configuration")

    # Create select boxes for each parameter
    for param_name in param_names_for_dropdowns:
        config_key = param_to_config_key_map.get(
            param_name, param_name
        )  # Use mapped key or param_name itself as fallback
        label = config_labels["menus"].get(config_key, param_name.capitalize())
        help_text = config_labels["help"].get(config_key, f"Select {param_name}")
        options = all_options.get(param_name, [])  # Options are fetched using the internal param_name
        if not options:
            st.sidebar.warning(f"No options available for {param_name}.")
            selected_value = None  # Or a default, or stop
        else:
            selected_value = st.sidebar.selectbox(label, options, help=help_text)
        selected_params_dict[param_name] = selected_value

        if (
            param_name == "analysis"
            and selected_value in analysis_explanations
            and analysis_explanations[selected_value]
        ):
            st.sidebar.write(analysis_explanations[selected_value])

    # Filter targets based on current selections
    # This uses the 'df' configuration to find relevant targets
    df_config = data_retrieval_config["df"]
    df_source_dict_name = df_config["source_dict_key"]
    df_key_params_for_target_filtering = df_config["key_params"]

    potential_targets = set()
    if df_source_dict_name in loaded_json_data:
        df_source_dict = loaded_json_data[df_source_dict_name]
        for key_str in df_source_dict.keys():
            try:
                params_from_key = reverse_key_generator(key_str, preserved_types=True)
            except ValueError:
                continue

            match = True
            for p_name in df_key_params_for_target_filtering:
                if p_name == "target":
                    continue
                # Check if param_name from key_params is in selected_params_dict (i.e., it was a dropdown)
                # and if its value matches the selection.
                if p_name in selected_params_dict:
                    if params_from_key.get(p_name) != selected_params_dict[p_name]:
                        match = False
                        break
                # If p_name is in key_params but not in selected_params_dict, it means it's not
                # part of the user-selectable dropdowns (e.g., if 'db' was optional and not selected).
                # This logic assumes that if a key_param is not in selected_params_dict,
                # it means we don't filter by it, or it's implicitly handled.
                # A stricter check might be needed if all non-target key_params must match.

            if match and "target" in params_from_key:
                potential_targets.add(params_from_key["target"])

    filtered_targets_list = sorted(list(potential_targets))

    # For target multiselect, use its specific config key if different
    target_config_key = param_to_config_key_map.get("target", "target")
    selected_targets = st.sidebar.multiselect(
        config_labels["menus"].get(target_config_key, "Target(s)"),
        filtered_targets_list,
        default=filtered_targets_list[:1] if filtered_targets_list else [],
        help=config_labels["help"].get(target_config_key, "Select the target variable(s) for analysis."),
    )
    selected_params_dict["targets"] = selected_targets

    if not selected_targets:
        st.warning("Please select at least one target.")
        st.stop()

    dictionary_aggregated_values = global_settings.get("dictionary_aggregated_values", {})
    var_y_options = ["min", "max"] + list(dictionary_aggregated_values.keys())
    # The 'reference' dropdown for var_y_type might need its own specific handling
    # if its label/help key in config_labels is different from what 'ref' maps to.
    # Current config_labels["menus"]["reference"] is "Select Reference"
    # Current config_labels["help"]["reference"] is "Select the reference type for Var Y calculation."
    # This seems appropriate for the var_y_type dropdown.
    var_y_type_label_key = "reference"  # Directly using the key from config_labels for this specific dropdown
    var_y_type = st.sidebar.selectbox(
        config_labels["menus"][var_y_type_label_key], var_y_options, help=config_labels["help"][var_y_type_label_key]
    )
    selected_params_dict["var_y_type"] = var_y_type
    selected_params_dict["y0"] = dictionary_aggregated_values.get(var_y_type)

    return selected_params_dict
