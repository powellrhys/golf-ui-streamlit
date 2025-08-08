# Import python dependencies
import streamlit as st

def get_navigation() -> st.navigation:
    """
    """
    # Construct pages dictionary
    pages = {
        "Overview": [st.Page("pages/home.py", title="Home")],
        "Trackman": [
            st.Page("pages/trackman_club_analysis.py", title="Club Analysis"),
            st.Page("pages/trackman_session_analysis.py", title="Session Analysis"),
            st.Page("pages/trackman_yardages.py", title="Yardages Analysis")
        ]
    }

    # Construct streamlit navigation object
    nav = st.navigation(pages)

    return nav
