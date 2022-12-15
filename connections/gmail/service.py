from connections.gmail import create_service

CLIENT_FILE = 'connections/gmail/client.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

service = create_service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)