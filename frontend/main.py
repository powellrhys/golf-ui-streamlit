# Import dependencies
from pathlib import Path
import sys

# Add project root to sys.path before any other imports
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import further dependencies following parent system path change
from functions import get_navigation # noqa
import streamlit as st # noqa

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# Render application if user is logged in
if st.user.is_logged_in:
    pg = get_navigation()
    pg.run()
