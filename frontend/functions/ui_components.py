import streamlit as st
import warnings


def configure_page_config(
    initial_sidebar_state: str = "expanded",
    layout: str = "wide"
) -> None:
    '''
    Configures the Streamlit page settings and suppresses warnings.

    This function sets the Streamlit page configuration, including the sidebar
    state (expanded or collapsed), layout (wide or centered), and page icon.
    It also disables all warnings during the page's runtime.

    Args:
        initial_sidebar_state (str, optional): Initial state of the sidebar.
        layout (str, optional): Layout of the page. Options are "wide" or "centered". Default is "wide".

    Returns:
        None

    Raises:
        None
    '''
    # Set page config
    st.set_page_config(
        initial_sidebar_state=initial_sidebar_state,
        layout=layout,
        page_icon=':golf:'
    )

    # Ignore all warnings
    warnings.filterwarnings("ignore")
