# Import python dependencies
import streamlit as st

# Import project dependencies
from streamlit_components.ui_components import (
    configure_page_config
)
from functions.data_functions import (
    Variables
)
from functions.ui_sections import (
    render_trackman_club_analysis
)

# Collect all project variables
variables = Variables()

# Set page config
configure_page_config(repository_name='play-cricket',
                      page_icon=":golf:")

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If logged in, render page components
if st.user.is_logged_in:

    render_trackman_club_analysis(variables=variables)
