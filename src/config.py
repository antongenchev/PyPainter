import json
import os
import sys

# WITHGUI - whehter to create the gui or avoid the gui logic for tests.
WITHGUI = os.getenv('WITHGUI', '1') == '1'

if getattr(sys, 'frozen', False):
    # If the application is bundled, use the path to the temporary folder
    config_path = os.path.join(sys._MEIPASS, 'config.json')
else:
    # If running in a normal Python environment, use the local path
    config_path = 'config.json'

with open(config_path, 'r') as config_file:
    config = json.load(config_file)