# import the required libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import os.path
import pickle
import os.path
import base64
import email
import time
from httplib2 import Http
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import dateutil.parser as parser
  
# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar']

created_events_set = set() 
def getEmails():
    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None
  
    # The file token.pickle contains the user access token.
    # Check if it exists
    if os.path.exists('token.pickle'):
  
        # Read the token from the file and store it in the variable creds
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
  
    # If credentials are not available or are invalid, ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
  
        # Save the access token in token.pickle file for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
  
    # Connect to the Gmail API
    service = build('gmail', 'v1', credentials=creds)
    service1 = build('calendar', 'v3', credentials=creds)
    # request a list of all the messages
    result = service.users().messages().list(userId='me').execute()
  
    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')
    # messages is a list of dictionaries where each dictionary contains a message id.
  
    # iterate through all the messages
    i = 0
    for msg in messages:
        if i == 5:
            break
        i = i + 1
        if msg['id'] in created_events_set:
            continue
        created_events_set.add(msg['id'])
        # print(created_events_set)
        # print(msg)
        # Get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        # Use try-except to avoid any Errors
        try:
            # Get value of 'payload' from dictionary 'txt'
            payload = txt['payload']
            headers = payload['headers']
            # Look for Subject and Sender Email in the headers
            subject = ''
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']
            #print(headers)
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            parts = payload.get('parts')[0]
            data = parts['body']['data']
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data)
            decoded_data = str(decoded_data)[2:]
            if 'AM' or 'PM' in decoded_data:
                colon = decoded_data.index(':')
                t = '0' + decoded_data[colon-1:colon+3] +':19'
                date_time_str = '14/03/22 ' + t
                date = parser.parse(date_time_str)
                start = date.isoformat()
                start = parser.isoparse(start)
                if 'PM' in decoded_data:
                    start+=timedelta(hours = 12)
                    #print(start)
                end = start
                end += timedelta(hours=1)
                end = end.isoformat()
                start = start.isoformat()
                event_result = service1.events().insert(calendarId='primary',
                    body={
                        "summary": decoded_data[:colon-2],
                        "description": 'New Event',
                        "start": {"dateTime": start, "timeZone": 'America/New_York'},
                        "end": {"dateTime": end, "timeZone": 'America/New_York'},
                    }
                ).execute()

        except:
            pass
  
while(True):
    getEmails()
    time.sleep(10)
