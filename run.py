import streamlit
import streamlit.web.cli as stcli
import os, sys


# This script is designed to launch your Streamlit data visualization application.
# It's configured to run `app/viz5.py`, ensuring a smooth user experience by disabling
# development mode for a cleaner final product.

'''
--- PyInstaller Packaging Notes ---

To make your Streamlit app easily shareable, you can package it into a single executable file
using **PyInstaller**. This bundles all necessary dependencies, so users don't need to install
anything extra.

1.  **Basic Packaging (no console window):**
    For the final version you distribute to users, it's usually best to hide the console window.
    This provides a cleaner and more professional experience.
    ```bash
    pyinstaller --onefile --noconsole run.py
    ```

2.  **Packaging for Debugging (with console window):**
    If you want to see `print()` statements or other console output for debugging purposes,
    use the `--console` (or `-c`) flag.
    ```bash
    pyinstaller --onefile --console run.py
    ```

3.  **Including Additional Data Files:**
    If your Streamlit application relies on external data files (like CSVs, images, or other assets),
    you'll need to include them in the executable. Use the `--add-data` flag to specify these files
    and where they should be placed within the bundled application.

    The format is: `--add-data "source_path;destination_folder_in_bundle"`

    Example: To include a CSV file located at `app/data/my_data.csv` and make it accessible
    in a `data` directory within your packaged app:
    ```bash
    pyinstaller --onefile --noconsole run.py --add-data "app/data/my_data.csv;data"
    ```
    Your Streamlit app can then access it using a path like `os.path.join(sys._MEIPASS, 'data', 'my_data.csv')`.
'''

if __name__ == "__main__":
    sys.argv = [
        "streamlit", 
        "run", 
        "app/viz5.py",
        "--global.developmentMode=false",
        ]
    sys.exit(stcli.main())