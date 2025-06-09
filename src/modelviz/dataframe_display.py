# filepath: /home/diego/Dropbox/DropboxGit/VizApp/src/modelviz/dataframe_display.py
import pandas as pd  # Import pandas for creating empty DataFrames
import streamlit as st

from .data_utils import get_dataframe_from_json_entrypoint  # Changed import source


def display_dataframes(
    loaded_json_data,
    selected_params,  # Combined dict of all selections
    config_labels,
    data_retrieval_config,
    add_third_subplot,  # This is determined in plotting, pass it here
):
    with st.expander(config_labels["headers"]["dataframes"]):
        selected_targets = selected_params.get("targets", [])
        if not selected_targets:
            st.write("No targets selected to display data for.")
            return

        for t in selected_targets:
            st.subheader(f"Target: {t}")

            # Fetch df
            t_df = get_dataframe_from_json_entrypoint(loaded_json_data, "df", selected_params, t, data_retrieval_config)
            if t_df is None:
                t_df = pd.DataFrame()  # Ensure it's a DataFrame

            st.write("Line Plot DataFrame (`df`):")
            st.dataframe(t_df)

            # Fetch dfh (usually uses the first target or a global configuration)
            # For display purposes, we might want to show the dfh relevant to the *current selections*
            # rather than a specific target, or the one used in the plot.
            # The current get_dataframe_from_json_entrypoint for 'dfh' might use selected_params.targets[0]
            # or a fixed target if defined in its key_params.
            # Let's assume it correctly fetches the relevant dfh based on selected_params.
            t_dfh = get_dataframe_from_json_entrypoint(
                loaded_json_data,
                "dfh",
                selected_params,
                t,
                data_retrieval_config,  # Pass target 't' for consistency if dfh can be target-specific
            )
            if t_dfh is None:
                t_dfh = pd.DataFrame()

            st.write("Bar Plot DataFrame (`dfh`):")
            st.dataframe(t_dfh)

            if add_third_subplot:
                t_dfhg = get_dataframe_from_json_entrypoint(
                    loaded_json_data, "dfhg", selected_params, t, data_retrieval_config
                )
                if t_dfhg is None:
                    t_dfhg = pd.DataFrame()
                st.write("Grouped Histogram DataFrame (`dfhg`):")
                st.dataframe(t_dfhg)

            # Download buttons for each target
            if not t_df.empty:
                csv_df = t_df.to_csv(index=False)
                st.download_button(
                    label=f"{config_labels['download_buttons']['df_csv']} - {t}",
                    data=csv_df,
                    file_name=f"df_{t}.csv",
                    mime="text/csv",
                    key=f"download_df_{t}",  # Add unique key
                )

            if not t_dfh.empty:
                csv_dfh = t_dfh.to_csv(index=False)
                st.download_button(
                    label=f"{config_labels['download_buttons']['dfh_csv']} - {t}",
                    data=csv_dfh,
                    file_name=f"dfh_{t}.csv",
                    mime="text/csv",
                    key=f"download_dfh_{t}",  # Add unique key
                )

            if add_third_subplot and "dfhg" in data_retrieval_config and t_dfhg is not None and not t_dfhg.empty:
                csv_dfhg = t_dfhg.to_csv(index=False)
                st.download_button(
                    label=f"Download dfhg Data as CSV - {t}",  # Consider adding to config_labels
                    data=csv_dfhg,
                    file_name=f"dfhg_{t}.csv",
                    mime="text/csv",
                    key=f"download_dfhg_{t}",  # Add unique key
                )
