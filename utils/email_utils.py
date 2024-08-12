import logging
import smtplib
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from utils.celery_config import celery_app

load_dotenv()  # Load environment variables from .env file

smtp_server = os.getenv('SMTP_SERVER')
port = int(os.getenv('SMTP_PORT'))
smtp_sender_email = os.getenv('SENDER_EMAIL')
smtp_password = os.getenv('EMAIL_PASSWORD')

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
ses_sender_email = os.getenv('SES_SENDER_EMAIL')


@celery_app.task(bind=True, max_retries=5, default_retry_delay=60)
def send_email_task(self, to_email, company_name):
    subject = f"Information for {company_name}"
    body = f"Dear {company_name},\n\nThis is the body of the email."

    msg = MIMEMultipart()
    msg['From'] = smtp_sender_email if os.getenv('MAILER', 'smtp') == 'smtp' else ses_sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if os.getenv('MAILER') == 'aws':

        # Initialize a session using Amazon SES
        ses_client = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        try:
            response = ses_client.send_raw_email(
                Source=ses_sender_email,
                Destinations=[to_email],
                RawMessage={
                    'Data': msg.as_string(),
                }
            )
            logging.info(f"Email sent to {to_email}: {response['MessageId']}")

        except (BotoCoreError, ClientError) as e:
            logging.error(f"Failed to send email to {to_email}: {e}")
            raise self.retry(exc=e)

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise self.retry(exc=e)
    else:
        try:
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()
                server.login(smtp_sender_email, smtp_password)
                server.sendmail(smtp_sender_email, to_email, msg.as_string())
                logging.info(f"Email sent to {to_email}")

        except smtplib.SMTPException as e:
            logging.error(f"Failed to send email to {to_email}: {e}")
            raise self.retry(exc=e)

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise self.retry(exc=e)
