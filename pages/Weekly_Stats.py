import streamlit
from streamlit_app import displayText, strava_json_to_df

displayText()

df = strava_json_to_df()
streamlit.dataframe(df)
