import streamlit as st
import json
import plotly.express as px
import pandas as pd

from functions.ui_components import (
    configure_page_config
)

configure_page_config()

number_of_shots = st.sidebar.selectbox(
    label='Number of shot evaluate',
    options=[10, 20, 30, 40, 50, 100]
)

# Read the JSON file
with open(f'data/yardage_summary/latest_{number_of_shots}_shot_summary.json', 'r') as json_file:
    data = json.load(json_file)

df = pd.DataFrame([{"Club": list(d.keys())[0], **list(d.values())[0]} for d in data])

st.title('Trackman Yardages')
st.dataframe(data=df,
             hide_index=True)

df_long = df.melt(id_vars=["Club"], value_vars=["min_carry", "max_carry"],
                  var_name="Carry Type", value_name="Carry Distance")


df_long = df_long.sort_values(by="Carry Distance", ascending=True)

# Step 1: Get the average carry distances from the original df
club_order = df.sort_values(by="avg_carry", ascending=True)["Club"]

# Step 2: Apply this order to the long dataframe
df_long["Club"] = pd.Categorical(df_long["Club"], categories=club_order, ordered=True)

# Step 3: Sort df_long to ensure order is applied
df_long = df_long.sort_values(by="Club")


# Create the box plot
fig = px.line(df_long, x="Club", y="Carry Distance", color="Club", markers='o')

print(df_long)

# Display in Streamlit
st.plotly_chart(fig)