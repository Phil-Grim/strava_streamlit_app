import streamlit
import requests
import pandas as pd
from datetime import datetime, timedelta

def displayText():
    streamlit.write("This is a test")

def strava_json_to_df()
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
    return activities

activities = strava_json_to_df()

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
activities['Date'] = pd.to_datetime(activities['Date'], format='%Y-%m-%d')
filtered_data = activities.loc[(activities['Date'] >= start_time[0]) & (activities['Date'] <= start_time[1])]

streamlit.header("Filtered Table")
# streamlit.dataframe(activities)
streamlit.dataframe(filtered_data)


#######################################
########### Cleaning Table
#######################################

# functions to format average speed to a minutes / seconds format
def frac(n):
    i = int(n)
    f = round((n - int(n)), 4)
    return (i, f)

def frmt(min):
    minutes, _sec = frac(min)
    seconds, _msecs = frac(_sec*60)
    if seconds > 9:
        return "%s:%s"%(minutes, seconds)
    else:
        return "%s:0%s"%(minutes, seconds)

filtered_data['Moving Time'] = filtered_data['Moving Time']/60 # moving time is now in mins
filtered_data['Average Speed'] = 1/(filtered_data['Average Speed']*(60/1000))
filtered_data['Max Speed'] = 1/(filtered_data['Max Speed']*(60/1000))
filtered_data['Distance (km)'] = filtered_data['Distance']

# Using above functions to format ave/max speed and moving time
formatted_speed = []
for index, row in filtered_data.iterrows():
    formatted_speed.append(frmt(row['Average Speed']))

formatted_max_speed = []
for index, row in filtered_data.iterrows():
    formatted_max_speed.append(frmt(row['Max Speed']))
    
formatted_moving_time = []
for index, row in filtered_data.iterrows():
    formatted_moving_time.append(frmt(row['Moving Time']))

filtered_data['Average Speed (min/km)'] = formatted_speed
filtered_data['Max Speed (min/km)'] = formatted_max_speed
filtered_data['Moving Time'] = formatted_moving_time

current_week_cleaned = filtered_data[['Name', 'Date', 'Distance', 'Moving Time', 'Elevation Gain', 'Average Speed (min/km)', 'Max Speed (min/km)', 'Average HR', 'Max HR']]
current_week_cleaned = current_week_cleaned.loc[(activities['Date'] >= start_time[0]) & (activities['Date'] <= start_time[1])]

streamlit.header("Cleaned Table!")
streamlit.text("Also filtered using the slider at the top")
streamlit.dataframe(current_week_cleaned)

#######################################
########### ADDING SOME HEADLINE NUMBERS
#######################################

week_distance = round(current_week_cleaned['Distance'].sum(), 1)

# Getting time moving was trickier

new_moving_times = []
for i in current_week_cleaned['Moving Time']:
    (m,s) = i.split(':')
    if int(m) >= 60:
        if (int(m) - 60) < 60:
            m = int(m) - 60
            if len(str(m)) == 1:
                m = '0' + str(m)
            time = '01' + ':' + str(m) + ':' + str(s)
            new_moving_times.append(time)
        elif (int(m) - 60) < 120:
            m = int(m) - 120
            if len(str(m)) == 1:
                m = '0' + str(m)
            time = '02' + ':' + str(m) + ':' + str(s)
            new_moving_times.append(time)
    else:
        time = '00:' + str(m) + ':' + str(s)
        new_moving_times.append(time)

current_week_cleaned['Cleaned Moving Time'] = new_moving_times

from datetime import timedelta
import datetime   

current_week_cleaned['Time'] = pd.to_datetime(current_week_cleaned['Cleaned Moving Time'], format='%H:%M:%S').dt.time

time_running = datetime.timedelta()
for i in current_week_cleaned['Cleaned Moving Time']: # has to be done for the string
    (h, m, s) = i.split(':')
    d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    time_running += d

# ave pace

try:
    ave_pace = time_running / week_distance
    ave_pace = str(ave_pace)[3:7]
except:
    ave_pace = 'N/A'

streamlit.header("Headline numbers from filtered date range!")
streamlit.write('Over the selected period, you ran for a total of:', str(time_running))
streamlit.write('You ran', week_distance, 'kms in the specified date range')
streamlit.write('Your average pace over this period was:', ave_pace, 'mins/km')
