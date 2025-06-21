import os
from pyparsing import html_comment
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_alert_email(sendgrid_key, email_to, Subject, html_content):
    try:
        message = Mail(
            from_email='alerts@yourdomain.com',
            to_emails=email_to,
            subject=Subject,
            html_content=html_content)
        sg = SendGridAPIClient(sendgrid_key)
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        return str(e)