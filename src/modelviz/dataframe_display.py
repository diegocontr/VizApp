# filepath: /home/diego/Dropbox/DropboxGit/VizApp/src/modelviz/dataframe_display.py
import streamlit as st

from .keygen import key_generator


def display_dataframes(
    data_dict,
    config_labels,
    selected_db,
    selected_analysis,
    selected_column,
    selected_agg,
    selected_ref,
    selected_group,
    selected_targets,
    add_third_subplot,
):
    with st.expander(config_labels["headers"]["dataframes"]):
        # Show each selected target's dataframes
        for t in selected_targets:
            params = {
                "db": selected_db,
                "analysis": selected_analysis,
                "column": selected_column,
                "agg": selected_agg,
                "ref": selected_ref,
                "group": selected_group,
                "target": t,
            }
            t_data = get_data_entry(data_dict, params)
            t_df = t_data["df"]
            t_dfh = t_data["dfh"]

            st.subheader(f"Target: {t}")
            st.write("Line Plot DataFrame (`df`):")
            st.dataframe(t_df)
            st.write("Bar Plot DataFrame (`dfh`):")
            st.dataframe(t_dfh)
            if add_third_subplot and "dfhg" in t_data:
                st.write("Grouped Histogram DataFrame (`dfhg`):")
                st.dataframe(t_data["dfhg"])

            # Download buttons for each target
            csv_df = t_df.to_csv(index=False)
            st.download_button(
                label=f"{config_labels['download_buttons']['df_csv']} - {t}",
                data=csv_df,
                file_name=f"df_{t}.csv",
                mime="text/csv",
            )

            csv_dfh = t_dfh.to_csv(index=False)
            st.download_button(
                label=f"{config_labels['download_buttons']['dfh_csv']} - {t}",
                data=csv_dfh,
                file_name=f"dfh_{t}.csv",
                mime="text/csv",
            )
            if add_third_subplot and "dfhg" in t_data:
                csv_dfhg = t_data["dfhg"].to_csv(index=False)
                st.download_button(
                    label=f"Download dfhg Data as CSV - {t}",
                    data=csv_dfhg,
                    file_name=f"dfhg_{t}.csv",
                    mime="text/csv",
                )


def get_data_entry(data_dict, params):
    key = key_generator(params, preserve_types=True)
    return data_dict[key]
