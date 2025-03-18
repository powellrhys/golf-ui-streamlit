# Import python packages
from datetime import datetime
import streamlit as st
import os

# Import ui functions
from functions.ui_components import (
    configure_page_config
)

# Import logging functions
from functions.logging_functions import (
    log_page_change
)

# Import data functions
from functions.data_functions import (
    ProjectVariables
)

# Configure page config
logger = configure_page_config()

# Collect current page name
current_page = os.path.basename(__file__).split('_')[-1].replace('.py', '')

# Log page change
logger = log_page_change(logger=logger,
                         current_page=current_page)

# Collect all project variables
variables = ProjectVariables()

with open("data/logs/application_logs.log", "r") as file:
    lines = file.readlines()

logs = [line.strip() for line in lines]

logs_json = [{'timestamp': line.split(' - ')[0],
              'log_level': line.split(' - ')[1],
              'log_message': line.split(' - ')[2]
              } for line in logs if ' - ' in line]

logs_json = sorted(logs_json,
                   key=lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S,%f"),
                   reverse=True)


page_vists = [{'timestamp': line['timestamp'],
               'page_visited': line['log_message'].split("Time spent on the ")[1].split(" page:")[0],
               'browsing_time': datetime.strptime(line['log_message'].split(': ')[-1], "%H:%M:%S.%f").time()
               } for line in logs_json if 'Time spent on the' in line['log_message']]

st.title('Application Analytics')

with st.expander(label='Raw Logs',
                 expanded=True):
    log_container = st.container(height=400)
    log_container.json(logs_json)
