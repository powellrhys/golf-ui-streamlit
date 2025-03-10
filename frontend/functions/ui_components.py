import streamlit as st
import warnings


def configure_page_config(initial_sidebar_state: str = "expanded",
                          layout: str = "wide") -> None:
    '''
    Input: Page config parameters
    Output: None
    Function to define page config
    '''
    # Set page config
    st.set_page_config(
        initial_sidebar_state=initial_sidebar_state,
        layout=layout,
        page_icon=':golf:'
    )

    # Ignore all warnings
    warnings.filterwarnings("ignore")
