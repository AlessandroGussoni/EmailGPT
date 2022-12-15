import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from connections.gmail.service import service


def draft_email(google_service,
                to,
                cc,
                subject,
                body):
    message = MIMEMultipart()
    message['to'] = to
    message['cc'] = cc
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    raw_string = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_response = google_service.users().drafts().create(userId='me',
                                                            body={'message': {'raw': raw_string}}).execute()
    return draft_response


def get_connected_user(self,
                       google_service):

    try:
        address = google_service.users().getProfile(userId='me').execute()['emailAddress']
        setattr(self, 'gmail_service', service)

    except Exception as e:
        print(e)
        address = 'not connected'

    return address
