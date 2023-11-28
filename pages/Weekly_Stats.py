import streamlit
import streamlit_app
import requests
import pandas as pd
from matplotlib import pyplot as plt

streamlit_app.displayText()



df = streamlit_app.strava_json_to_df()

##############
## WEEK ACTIVITIES - GRAPH OF DAILY KMs COVERED
##############

# define start (Monday) and end (Sunday) date of week based on today's date
date = pd.to_datetime('today').floor('D').date()
start_week = date - timedelta(date.weekday())
end_week = start_week + timedelta(6)

# create data frame with data from current week only and set dates with no activity to distance = 0
r = pd.date_range(start=start_week, end=end_week).date


current_week = df[df['Date'].dt.date >= start_week]
current_week['Date'] = current_week['Date'].dt.date

current_week_summed = current_week.groupby(pd.Grouper(key='Date')).sum().reindex(r).fillna(0.0).rename_axis('Date').reset_index()

csfont = {'fontname':'Avenir'}
plt.bar(current_week_summed['Date'],current_week_summed['Distance'], color= '#49494f')
plt.xticks(current_week_summed['Date'], ('M', 'T', 'W', 'T', 'F', 'S', 'S'), **csfont)
plt.yticks(**csfont)
plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=True, labelbottom=True, labelsize=15)
plt.box(False)



