import os
# from sendgrid import SendGridAPIClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# message = Mail(
#     from_email='pranjali.munfan@gmail.com',
#     to_emails='pranjali@cybersponse.com',
#     subject='Sending with Twilio SendGrid is Fun',
#     html_content='<strong>and easy to do anywhere, even with Python</strong>')
# try:
#     sg = SendGridAPIClient(api_key='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')
#     response = sg.send(message)
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)
# except Exception as e:
#     print(str(e))


import os
import base64

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)


message = Mail(
    from_email='pranjali.munfan@gmail.com',
    to_emails='pranjali@cybersponse.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content=None,
    plain_text_content = "bfbew"
)

with open('certificate.pdf', 'rb') as f:
    data = f.read()
    f.close()
encoded_file = base64.b64encode(data).decode()

attachedFile = Attachment(
    FileContent(encoded_file),
    FileName('certificate.pdf'),
    FileType('application/pdf'),
    Disposition('attachment')
)
message.attachment = attachedFile

sg = SendGridAPIClient('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')

response = sg.send(message)
# response = sg.client.alerts.get()
# params = {'limit': 1}
# response = sg.client.api_keys.get(query_params=params)
print(response.status_code, response.body, response.headers)