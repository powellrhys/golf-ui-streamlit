# Import dependencies
from streamlit_components.ui_components import configure_page_config
from frontend import render_course_hole_by_hole_section
from shared import Variables
import streamlit as st

# Set page config
configure_page_config(repository_name='golf-ui-streamlit',
                      page_icon=":golf:")

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If logged in, render page components
if st.user.is_logged_in:

    # Render course hole by hole section
    render_course_hole_by_hole_section(variables=Variables(source="frontend"))
