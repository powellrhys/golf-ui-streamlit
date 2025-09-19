from unittest.mock import patch, MagicMock
from frontend import get_navigation

def test_get_navigation():

    # Make fake variables object
    fake_vars = MagicMock()
    fake_vars.golf_course_name = "pinehurst"

    # Execute patch on streamlit components
    with patch("frontend.functions.navigation.st.Page") as mock_page, \
         patch("frontend.functions.navigation.st.navigation") as mock_nav:

        # Mock side effect and returned value
        mock_page.side_effect = lambda *a, **kw: MagicMock()
        mock_nav.return_value = "fake_nav_object"

        # Execute function
        result = get_navigation(fake_vars)

        # Assert values
        assert result == "fake_nav_object"
        assert mock_page.call_count == 5

        # Assert expected values in mocked object
        mock_nav.assert_called_once()
        pages_arg = mock_nav.call_args[0][0]
        assert "Overview" in pages_arg
        assert "Trackman" in pages_arg
        assert "Pinehurst Golf Course Analysis" in pages_arg
