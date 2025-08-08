# Import python dependencies
from dotenv import load_dotenv
import streamlit as st

from functions.data_functions import (
    Variables
)
from functions.navigation import (
    get_navigation
)

# Load environment variables
load_dotenv()
vars = Variables()

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# Render application if user is logged in
if st.user.is_logged_in:
    pg = get_navigation()
    pg.run()
