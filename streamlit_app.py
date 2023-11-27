import streamlit
import requests
import pandas as pd
from datetime import datetime, timedelta

auth_url = "https://www.strava.com/oauth/token"


payload = {
    'client_id': "106698",
    'client_secret': 'a66bb23d9597d2b4027ff22a73720f226d021f68',
    'refresh_token': 'd9f95e45f5dc021ca00aef1151d694e9aa6c5c75', # should stay the same, allowing you to fetch access_token (which changes every few hours)
    'grant_type': "refresh_token",
    'f': 'json'
}

print("Requesting Token...\n")
res = requests.post(auth_url, data=payload, verify=False)

access_token = res.json()['access_token'] # retrieving access_token from above post request
print(f'Access Token = {access_token}\n')


activities_url = f'https://www.strava.com/api/v3/athlete/activities?access_token={access_token}'

header = {'Authorisation': 'Bearer ' + access_token} # works without this line - as I have the access token in the activities_url
param = {'per_page': 200, 'page': 1}

data = requests.get(activities_url, headers=header, params=param).json()

date_distance_list = []
count = 0
for i in data:
    if i['sport_type'] == 'Run':
        date_distance_list.append([i['id'], i['name'], i['start_date'][:10], i['distance'], i['moving_time'], i['total_elevation_gain'], i['end_latlng'], i['average_speed'], i['max_speed']])
        try:
            date_distance_list[count].append(i['average_heartrate'])
            date_distance_list[count].append(i['max_heartrate'])
        except:
            date_distance_list[count].append('None')
            date_distance_list[count].append('None')
        count += 1

activities = pd.DataFrame(date_distance_list, columns = ['ID', 'Name', 'Date', 'Distance', 'Moving Time', 'Elevation Gain', 'End Location', 'Average Speed', 'Max Speed', 'Average HR', 'Max HR'])
activities.sort_values(by='Date', inplace=True)
activities['Distance'] = pd.to_numeric(activities['Distance'])
activities['Distance'] = activities['Distance']/1000

min_date = datetime.strptime(activities['Date'].iloc[0],'%Y-%m-%d')
max_date = datetime.strptime(activities['Date'].iloc[-1],'%Y-%m-%d')

# min_date = datetime(2022,1,1)
# max_date = datetime(2023,7,1)

start_time = streamlit.slider(
    "Date picker",
    min_date,
    max_date,
    value=[min_date, max_date]
)

# filtered_data = activities.loc[((datetime.strptime(activities['Date'], '%Y-%m-%d') >= start_time[0]) and (datetime.strptime(activities['Date'], '%Y-%m-%d') <= start_time[1])]
filtered_data = activities.loc[(activities['Date'] >= start_time[0]) & (activities['Date'] <= start_time[1])]

streamlit.header("Filtered Table")
# streamlit.dataframe(activities)
streamlit.dataframe(filtered_data)
