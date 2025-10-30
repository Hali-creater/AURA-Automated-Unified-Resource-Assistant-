import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import google.generativeai as genai
import datetime
import os

model = None

def get_model():
    global model
    if model is None:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            genai.configure(api_key=google_api_key)
            model = genai.GenerativeModel('gemini-pro')
    return model

def summarize_text(text):
    try:
        model = get_model()
        if not model:
            return "Model not initialized. Please check your API key."
        response = model.generate_content(f"Summarize the following text: {text}")
        return response.text
    except Exception as e:
        return f"Failed to summarize text: {e}"

def draft_email(prompt):
    try:
        model = get_model()
        if not model:
            return "Model not initialized. Please check your API key."
        response = model.generate_content(f"Draft an email based on the following prompt: {prompt}")
        return response.text
    except Exception as e:
        return f"Failed to draft email: {e}"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    gcal_credentials_file = os.getenv("GCAL_CREDENTIALS_FILE")
    if not gcal_credentials_file or not os.path.exists(gcal_credentials_file):
        return None

    try:
        creds = service_account.Credentials.from_service_account_file(
            gcal_credentials_file, scopes=SCOPES)
        return build('calendar', 'v3', credentials=creds)
    except Exception:
        return None

def get_calendar_events(max_events=10):
    service = get_calendar_service()
    if not service:
        return ["Google Calendar is not configured. Please check your credentials."]
    try:
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=max_events, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return ["No upcoming events found."]

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_list.append(f"{start} - {event['summary']}")

        return event_list
    except Exception as e:
        return [f"Failed to get calendar events: {e}"]


def create_calendar_event(summary, start_time, end_time):
    timezone = os.getenv("TIMEZONE", "America/Los_Angeles")
    service = get_calendar_service()
    if not service:
        return "Google Calendar is not configured. Please check your credentials."
    try:
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        return f"Failed to create calendar event: {e}"

def send_email(to, subject, body):
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_address or not email_password:
        return "Email credentials are not set. Please set the EMAIL_ADDRESS and EMAIL_PASSWORD environment variables."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = to

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not smtp_server:
        return "SMTP server details are not set. Please set the SMTP_SERVER and SMTP_PORT environment variables."

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"

def read_emails(max_emails=5):
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_address or not email_password:
        return ["Email credentials are not set. Please set the EMAIL_ADDRESS and EMAIL_PASSWORD environment variables."]

    imap_server = os.getenv("IMAP_SERVER")
    if not imap_server:
        return ["IMAP server details are not set. Please set the IMAP_SERVER environment variable."]

    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, email_password)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        emails = []
        for email_id in email_ids[-max_emails:]:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"]
                    sender = msg["from"]
                    emails.append(f"From: {sender}, Subject: {subject}")

        mail.logout()
        return emails
    except Exception as e:
        return [f"Failed to read emails: {e}"]
