import requests

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

data
