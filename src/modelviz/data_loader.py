# filepath: /home/diego/Dropbox/DropboxGit/VizApp/src/modelviz/data_loader.py
import json
from io import StringIO
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image


@st.cache_data(show_spinner=False)
def load_data_dict(filename):
    """
    Loads the flat data_dict from a JSON file, converting JSON strings back to DataFrames.
    """
    try:
        file_path = Path(filename)
        if not file_path.is_file():
            st.error(f"Data file not found at path: {filename}")
            return {}

        with open(filename, "r") as f:
            data_dict_json = json.load(f)

        # Extract plot_data from the JSON
        if "plot_data" not in data_dict_json:
            st.error("The JSON file does not contain 'plot_data'.")
            return {}

        data_dict = data_dict_json["plot_data"]
        global_data = data_dict_json["global_data"] if "global_data" in data_dict_json else data_dict

        # Convert JSON strings to DataFrames for each entry
        for key, entry in data_dict.items():
            entry["df"] = pd.read_json(StringIO(entry["df"]), orient="split")
            entry["dfh"] = pd.read_json(StringIO(entry["dfh"]), orient="split")
            if "dfhg" in entry:
                entry["dfhg"] = pd.read_json(StringIO(entry["dfhg"]), orient="split")
        return data_dict, global_data

    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return {}


def load_logo(image_path):
    """
    Loads the logo image.
    """
    try:
        logo = Image.open(image_path)
        return logo
    except FileNotFoundError:
        st.warning(f"Logo file not found at path: {image_path}")
        return None
