import pandas as pd
import streamlit as st

from .keygen import key_generator


def get_dataframe_from_json_entrypoint(
    loaded_json_data, data_type, current_selection_params, target_override, data_retrieval_config
):
    """
    Retrieves a specific DataFrame (df, dfh, dfhg) based on configuration.

    Args:
        loaded_json_data (dict): The fully loaded JSON data.
        data_type (str): Type of data to retrieve ('df', 'dfh', 'dfhg').
        current_selection_params (dict): Current user selections from sidebar.
        target_override (str or None): Specific target for 'df' or 'dfhg', or None.
                                       For 'dfh', target might be ignored or taken from key_params.
        data_retrieval_config (dict): The global data retrieval configuration.

    Returns:
        pd.DataFrame or None: The requested DataFrame or None if not found.
    """
    if data_type not in data_retrieval_config:
        st.error(f"Configuration for data type '{data_type}' not found.")
        return pd.DataFrame()  # Return empty DataFrame

    config_for_type = data_retrieval_config[data_type]
    source_dict_name = config_for_type["source_dict_key"]
    data_field_name = config_for_type["data_field_in_entry"]
    key_param_names = config_for_type["key_params"]
    fixed_params = config_for_type.get("fixed_params", {})

    # Build the parameters for key generation from current_selection_params
    key_gen_params = {p: current_selection_params[p] for p in key_param_names if p in current_selection_params}

    # Apply fixed parameters, potentially overriding selections
    key_gen_params.update(fixed_params)

    # Override target if provided (typically for 'df' and 'dfhg' when iterating targets)
    if target_override is not None and "target" in key_param_names:
        key_gen_params["target"] = target_override
    elif (
        "target" in key_param_names
        and "target" not in key_gen_params
        and "targets" in current_selection_params
        and current_selection_params["targets"]
    ):
        # For types like 'dfh' that might use a single target from the list if not fixed
        if data_type == "dfh":  # dfh usually uses the first target or a global one
            key_gen_params["target"] = current_selection_params["targets"][0]

    # Ensure all parameters required for the key are present
    for p_name in key_param_names:
        if p_name not in key_gen_params:
            # This could be an issue if a param is essential for the key and not provided.
            # For example, if 'column' is in key_params but somehow missing from selections.
            # key_generator might produce an incomplete key or error.
            # st.warning(f"Parameter '{p_name}' required for '{data_type}' key is missing from selections.")
            pass  # Allow key_generator to handle missing keys if it's designed to

    data_key = key_generator(key_gen_params, preserve_types=True)

    if source_dict_name not in loaded_json_data:
        st.error(f"Source dictionary '{source_dict_name}' not found in loaded data.")
        return pd.DataFrame()  # Return empty DataFrame

    source_dict = loaded_json_data[source_dict_name]

    if data_key not in source_dict:
        st.warning(
            f"Data key '{data_key}' not found in source dictionary '{source_dict_name}'. "
            f"Available keys: {list(source_dict.keys())}"
        )
        return pd.DataFrame()  # Return empty DataFrame to avoid downstream errors

    entry = source_dict[data_key]

    if data_field_name not in entry:
        # st.warning(
        # f"Data field '{data_field_name}' not found in entry for key '{data_key}'. Entry keys: {entry.keys()}")
        return pd.DataFrame()  # Return empty DataFrame

    # The data should already be a DataFrame due to processing in load_data_dict
    return entry[data_field_name]
