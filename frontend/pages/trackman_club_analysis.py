# Import dependencies
from streamlit_components.ui_components import configure_page_config
from frontend import render_trackman_club_analysis
from shared import Variables
import streamlit as st

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

    render_trackman_club_analysis(variables=variables)
