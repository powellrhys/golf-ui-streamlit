# Import python dependencies
import streamlit as st

def get_navigation() -> st.navigation:
    """
    Build and return a Streamlit navigation object for the application.

    This method defines the navigation structure of the app by mapping
    page groups (e.g., "Overview", "Trackman") to their corresponding
    Streamlit pages. It then constructs a `st.navigation` object that
    can be used to render and manage page routing within the UI.

    Returns:
        st.navigation: A Streamlit navigation object containing the
        configured pages and navigation hierarchy.
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
