import smtplib, ssl
import os
from DotEnvHandler import set_environ

set_environ()

def send_email(_message):
  port = 465  # For SSL
  sender_email = os.environ['EmailAddress']
  receiver_email = 'pokecoveofficial@gmail.com'
  password = os.environ["EmailPassword"]
  message = _message

  # Create a secure SSL context
  context = ssl.create_default_context()

  with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
      server.login(sender_email, password)
      server.sendmail(sender_email, receiver_email, message)
