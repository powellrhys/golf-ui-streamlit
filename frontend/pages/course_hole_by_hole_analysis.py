# Import dependencies
from streamlit_components.ui_components import configure_page_config
from frontend import render_hole_metrics
from frontend.functions.plots import plot_fairways_hit
from shared import Variables
import streamlit as st

from frontend.functions.data_functions import aggregate_fairway_data

# Collect all project variables
variables = Variables(source="frontend")

# Set page config
configure_page_config(repository_name='golf-ui-streamlit',
                      page_icon=":golf:")

# Ensure user is authenticated to use application
if not st.user.is_logged_in:
    st.login('auth0')

# If logged in, render page components
if st.user.is_logged_in:

    # Define page title
    st.title(f"{variables.golf_course_name.capitalize()} GC Analysis")

    # Render hole metrics section
    data = render_hole_metrics(vars=Variables())

    if data[0]["Par"] != 3:

        with st.expander(label="Fairway Accuracy Overview", expanded=True):

            fairway_df = aggregate_fairway_data(data)

            fig = plot_fairways_hit(fairway_df)

            st.plotly_chart(fig)

    with st.expander(label="Stroke Performance Overview", expanded=True):

        import pandas as pd
        import plotly.express as px

        df = pd.DataFrame(data)

        df = df.sort_values("date", ascending=False)  # newest → oldest
        df["date_str"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        # Force date_str to be a string and categorical
        df["date_str"] = pd.Categorical(df["date_str"], categories=df["date_str"], ordered=True)

        plot_df = (
            df.groupby(["date_str", "result"], as_index=False)["Strokes"].sum()
        )

        color_map = {
            "Eagle": "#ffee00",
            "Birdie": "#2ca02c",             # green
            "Par": "#1f77b4",                # blue
            "Bogey": "#ff7f0e",              # orange
            "Double Bogey or worse": "#d62728"  # red
        }

        fig = px.bar(
            plot_df,
            x="date_str",   # categorical string labels
            y="Strokes",
            text="Strokes",
            color="result",   # differentiate by result
            title="Strokes Per Round Overview",
            barmode="stack",  # stacked bar chart
            category_orders={
                "date_str": plot_df["date_str"].unique(),
                "result": list(color_map.keys())  # enforce stacking order too
            },
            color_discrete_map=color_map
        )

        # Place values inside the bars
        fig.update_traces(textposition="inside")

        # Explicitly treat x-axis as categorical
        fig.update_xaxes(type="category", title="Date")
        fig.update_layout(
            yaxis_title="Strokes"
        )

        st.plotly_chart(fig)
