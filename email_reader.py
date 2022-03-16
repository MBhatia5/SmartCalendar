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
from datetime import date
# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar']

created_events_set = set() 

nameList =[]
for line in open('names.txt', 'r').read().splitlines():
    nameList.append(line)
print(nameList)


def getDate(decoded_data):
    today = date.today()
    default = today.strftime("%d/%m/%y")+" "
    if 'tomorrow' in decoded_data:
        tomorrow=today+timedelta(days=1)
        return tomorrow.strftime("%d/%m/%y")+" "
    indexes = [x for x, v in enumerate(decoded_data) if v == '/']
    for index in indexes:
        if index>2 and index<(len(decoded_data)-2):
            if decoded_data[index-3]==' ' and decoded_data[index-2].isdigit() and decoded_data[index-1].isdigit() and decoded_data[index+1].isdigit() and decoded_data[index+2].isdigit() and (index==len(decoded_data)-3 or decoded_data[index+3]==' ' or decoded_data[index+3]==','or decoded_data[index+3]=='.'):
                return decoded_data[index+1:index+3]+"/"+decoded_data[index-2:index]+"/22 "
    return default

## return: valid_email, start_time, isPM, summary, location
def validEmail(decoded_data):
    valid=False
    isPM=False
    if (' AM ' or ' AM,' or ' AM.' in decoded_data) or ' AM'==decoded_data[-3:]:
        valid=True
    elif (' PM ' or ' PM,' or ' PM.' in decoded_data) or ' PM'==decoded_data[-3:]:
        valid=True
        isPM=True
    if not valid:
        return False,"",False,"", ""

    colon = decoded_data.index(':')
    t=""
    if decoded_data[colon-2].isdigit():
        t = decoded_data[colon-2:colon+3] +':19'
    else:
        t = '0' + decoded_data[colon-1:colon+3] +':19'
    summary= decoded_data[:colon-2]
    loc=""
    if 'http' in decoded_data:
        i=decoded_data.find('http')
        loc=decoded_data[i:decoded_data.find(' ',i)]
    return True,t,isPM,summary, loc

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
            sender = [i['value'] for i in headers if i["name"]=="From"][0]
            subject = [i['value'] for i in headers if i["name"]=="Subject"][0]
            print(sender)
            found=False
            for address in nameList:
                if address in sender:
                    found=True
                    break
            if not found:
                print('here')
                continue
            #print(headers)
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            parts = payload.get('parts')[0]
            data = parts['body']['data']
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data)
            decoded_data = str(decoded_data)[2:]
            valid_email, start_time, isPM,description,loc = valid_email(decoded_data)
            if valid_email:
                date_time_str = getDate(decoded_data) + start_time
                date = parser.parse(date_time_str)
                start = date.isoformat()
                start = parser.isoparse(start)
                if isPM:
                    start+=timedelta(hours = 12)
                end = start
                end += timedelta(hours=1)
                end = end.isoformat()
                start = start.isoformat()
                #first_index = decoded_data.index('Lets')
                event_result = service1.events().insert(calendarId='primary',
                    body={
                        "summary": subject,
                        "description": description,
                        "location":loc,
                        "start": {"dateTime": start, "timeZone": 'America/New_York'},
                        "end": {"dateTime": end, "timeZone": 'America/New_York'},
                    }
                ).execute()

        except:
            pass
  
while(True):
    getEmails()
    time.sleep(5)
