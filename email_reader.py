# import the required libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import re
import os.path
import base64
import time
from datetime import datetime, timedelta
import dateutil.parser as parser
from datetime import date
from exchangelib import Account, CalendarItem, Credentials, DELEGATE
from pytz import timezone
import pytz

# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar']

    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
creds = None
eastern = timezone('US/Eastern')
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

#connect to Outlook API
credentials = Credentials('manavbh@outlook.com', 'password')
account = Account('manavbh@outlook.com', credentials=credentials, autodiscover = True)

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
    for index in range(len(decoded_data)-1):
        if decoded_data[index]=='P' and decoded_data[index+1]=='M':
            valid=True
            isPM=True
        if decoded_data[index]=='A' and decoded_data[index+1]=='M':
            valid=True
            isPM=False
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
        loc=decoded_data[i:]
    return True,t,isPM,summary, loc


def getOutlook():
    for item in account.inbox.all().order_by('-datetime_received')[:1]:
        body = re.sub('<[^<]+?>', '', item.body)
        valid_email, start_time, isPM,description,loc = validEmail(body)
        print('in outlook')
        print(valid_email)
        print(created_events_set)
        if description in created_events_set:
            print('in set')
            getGmail()
            continue
        print('beyond set')
        created_events_set.add(description)
        if valid_email:
            date_time_str = getDate(item.body) + start_time
            date = parser.parse(date_time_str)
            start = date.isoformat()
            start = parser.isoparse(start)
            start_outlook = start
            if isPM:
                start+=timedelta(hours = 12)
                start_outlook+=timedelta(hours = 16)
            end = start
            end_outlook = start_outlook
            end += timedelta(hours=1)
            end_outlook +=timedelta(hours = 1)
            end = end.isoformat()
            start = start.isoformat()
            print(start)
            print(end)
            start_outlook = str(start_outlook)
            end_outlook = str(end_outlook)
            dt_start_time = datetime.fromisoformat(start_outlook)
            dt_end_time = datetime.fromisoformat(end_outlook)
            dt_start_time = pytz.utc.localize(dt_start_time).astimezone(eastern)
            dt_end_time = pytz.utc.localize(dt_end_time).astimezone(eastern)

            print(dt_start_time)
            print(loc)
            item = CalendarItem(folder=account.calendar, 
                        subject=item.subject, 
                        start = dt_start_time, 
                        end = dt_end_time,
                        location = loc,
                        body = description
                        )
            item.save()  
            service1.events().insert(calendarId='primary',
                body={
                    "summary": item.subject,
                    "description": description,
                    "location":loc,
                    "start": {"dateTime": start, "timeZone": 'America/New_York'},
                    "end": {"dateTime": end, "timeZone": 'America/New_York'},
                    "colorId": 3
                }
            ).execute()

def getGmail():
    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None
    print('in gmail line 163')
  
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
        # Get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        # Use try-except to avoid any Errors
        try:
            # Get value of 'payload' from dictionary 'txt'
            payload = txt['payload']
            headers = payload['headers']
            sender = [i['value'] for i in headers if i["name"]=="From"][0]
            subject = [i['value'] for i in headers if i["name"]=="Subject"][0]
            found=False
            for address in nameList:
                if address in sender:
                    found=True
                    break
            if not found:
                continue
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            parts = payload.get('parts')[0]
            data = parts['body']['data']
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data)
            decoded_data = str(decoded_data)[2:]
            valid_email, start_time, isPM,description,loc = validEmail(decoded_data)
            print('in gmail')
            print(valid_email)
            print(description)
            print(loc)
            service1.events().insert(calendarId='primary',
                body={
                    "summary": subject,
                    "description": description,
                    "location":loc,
                    "start": {"dateTime": start, "timeZone": 'America/New_York'},
                    "end": {"dateTime": end, "timeZone": 'America/New_York'},
                    "colorId": 7
                }
            ).execute()
            if valid_email:
                date_time_str = getDate(decoded_data) + start_time
                date = parser.parse(date_time_str)
                start = date.isoformat()
                start = parser.isoparse(start)
                start_outlook = start
                if isPM:
                    start+=timedelta(hours = 12)
                    start_outlook+=timedelta(hours = 16)
                end = start
                end_outlook = start_outlook
                start_outlook = str(start_outlook)
                end_outlook = str(end_outlook)
                dt_start_time = datetime.fromisoformat(start_outlook)
                dt_end_time = datetime.fromisoformat(end_outlook)
                dt_start_time = pytz.utc.localize(dt_start_time).astimezone(eastern)
                dt_end_time = pytz.utc.localize(dt_end_time).astimezone(eastern)
                print(start)
                print(end)

                print('after execution in gmail')
                dt_start_time = pytz.utc.localize(dt_start_time).astimezone(eastern)
                dt_end_time = pytz.utc.localize(dt_end_time).astimezone(eastern)
                item = CalendarItem(folder=account.calendar, 
                            subject=subject,
                            start = dt_start_time, 
                            end = dt_end_time,
                            location = loc,
                            body = description
                            )
                item.save() 

        except:
            pass

  
while(True):
    getGmail()
    getOutlook()
    time.sleep(5)
