
from __future__ import print_function
import httplib2
import os
import datetime

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import base64
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import mimetypes
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

now = datetime.datetime.now()

class send_email:
    def __init__(self,service):
        self.service = service

    def create_message_with_attachment(self,form,file):
      
      email_send = form['recipient_email']
      subject = form['subject']
      body = 'Sent by ' + 'Chicken Friedrice' + '\n' + now.strftime("%Y-%m-%d %H:%M") + '\n' + form['body']

      message = MIMEMultipart()
      message['to'] = ", ".join(email_send)
      message['subject'] = subject

      msg = MIMEText(body)
      message.attach(msg)

      content_type, encoding = mimetypes.guess_type("bullshit.pdf")
      main_type, sub_type = content_type.split('/', 1)

      if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
      else:
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(file, 'utf-8')

      msg.add_header('Content-Disposition', 'attachment', filename='Document')
      message.attach(msg)

      return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_message(self, user_id, message):
      """Send an email message.

      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

      Returns:
        Sent Message.
      """
      try:
        message = (self.service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
      except errors.HttpError as error:
        print('An error occurred: %s' % error)