from __future__ import print_function
import pickle
import os.path

from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64


class gmailAPI:
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://mail.google.com/']
    creds = None
    service = None
    messages = None

    def __init__(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        self.refresh_token()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def refresh_token(self):
        if self.creds and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
            except RefreshError:
                os.unlink('token.pickle')
                return
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', self.SCOPES)
            self.creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(self.creds, token)

    def update_messages(self):
        results = self.service.users().messages().list(userId='me').execute()
        self.messages = results.get('messages', [])

    def get_message_bodies(self, unread_only=True, delete=True):
        message_text_list = []
        if not self.messages:
            print('No messages found.')
        else:
            for message in self.messages:
                email = self.service.users().messages().get(userId='me', id=message['id']).execute()
                if ('UNREAD' in email['labelIds']) or not unread_only:
                    try:
                        message_text_list.append(base64.urlsafe_b64decode(email['payload']['parts'][0]['body']['data']))
                    except(KeyError):
                        message_text_list.append(base64.urlsafe_b64decode(email['payload']['body']['data']))
                    self.service.users().messages().modify(userId='me', id=message['id'],
                                                           body={'removeLabelIds': ['UNREAD']}).execute()
                    if delete:
                        self.service.users().messages().trash(userId='me', id=message['id']).execute()
        return message_text_list


if __name__ == '__main__':
    dmMailAPI = gmailAPI()
    dmMailAPI.update_messages()
    print(dmMailAPI.get_message_bodies())
