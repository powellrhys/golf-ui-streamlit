# Import python and project dependencies
from streamlit_components.ui_components import configure_page_config
import streamlit as st

# Set page config
configure_page_config(repository_name='golf-ui-streamlit',
                      page_icon=":golf:")

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If user logged in, render streamlit content
if st.user.is_logged_in:

    # Render page title
    st.title("Golf Analysis Home")

    # Render container
    with st.container(border=True):

        # Render application overview paragraph
        st.write(
            """
            This Streamlit application provides an interactive platform for analyzing golf performance through
            Scorecard Analysis and TrackMan Range data. The tool visualizes key performance metrics, helping players,
            coaches, and analysts gain insights into scoring trends, shot dispersion, club data, and more. Users can
            upload scorecards and TrackMan export files to generate customizable plots, performance summaries, and
            actionable insights for practice and game improvement.
            """
        )
