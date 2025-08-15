# Import python dependencies
import streamlit as st

# Import project dependencies
from streamlit_components.ui_components import (
    configure_page_config
)
from shared import Variables

from functions.ui_sections import (
    render_club_yardage_analysis
)
# Collect all project variables
variables = Variables()

# Set page config
configure_page_config(repository_name='golf-ui-streamlit',
                      page_icon=":golf:")

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If logged in, render page components
if st.user.is_logged_in:

    render_club_yardage_analysis()
