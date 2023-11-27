import streamlit
import streamlit_app
import requests
import pandas as pd
# from streamlit_app import displayText
# from streamlit_app import strava_json_to_df

streamlit_app.displayText()

# try a second super simple function in streamlit_app
# try putting functions in same directory (i.e. pages)

streamlit_app.strava_json_to_df()
streamlit.dataframe(df)
