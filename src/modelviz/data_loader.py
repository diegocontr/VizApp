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
    Loads data from a JSON file, converting JSON strings back to DataFrames.
    Returns the entire loaded and processed JSON structure.
    """

    file_path = Path(filename)
    if not file_path.is_file():
        st.error(f"Data file not found at path: {filename}")
        return None  # Return None on error

    with open(filename, "r") as f:
        loaded_json_data = json.load(f)

    # Process DataFrames within the structure (assuming they are in 'plot_data')
    # This part might need to be more dynamic if DataFrames can be elsewhere.
    if "plot_data" in loaded_json_data:
        plot_data_dict = loaded_json_data["plot_data"]
        for _key, entry in plot_data_dict.items():
            if "df" in entry and isinstance(entry["df"], str):
                entry["df"] = pd.read_json(StringIO(entry["df"]), orient="split")
            if "dfh" in entry and isinstance(entry["dfh"], str):
                entry["dfh"] = pd.read_json(StringIO(entry["dfh"]), orient="split")
            if "dfhg" in entry and isinstance(entry["dfhg"], str):
                entry["dfhg"] = pd.read_json(StringIO(entry["dfhg"]), orient="split")

    # Potentially process other dictionaries if they also contain stringified DataFrames
    # based on a more complex config if needed in the future.

    return loaded_json_data


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
