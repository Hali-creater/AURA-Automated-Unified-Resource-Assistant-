import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from groq import Groq
import os
import datetime

client = None

def get_groq_client():
    global client
    if client is None:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            client = Groq(api_key=groq_api_key)
    return client

def summarize_text(text):
    try:
        client = get_groq_client()
        if not client:
            return "Groq client not initialized. Please check your API key."
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following text: {text}",
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Failed to summarize text: {e}"

def draft_email(prompt):
    try:
        client = get_groq_client()
        if not client:
            return "Groq client not initialized. Please check your API key."
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Draft an email based on the following prompt: {prompt}",
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Failed to draft email: {e}"

from ics import Calendar, Event

def get_calendar_events(ics_file):
    try:
        c = Calendar(ics_file.read().decode('utf-8'))
        events = sorted(c.events, key=lambda e: e.begin)
        event_list = []
        for event in events:
            event_list.append(f"{event.begin.humanize()} - {event.name}")
        return event_list
    except Exception as e:
        return [f"Failed to read calendar events: {e}"]

def create_calendar_event(summary, start_time, end_time):
    try:
        c = Calendar()
        e = Event()
        e.name = summary
        e.begin = start_time
        e.end = end_time
        c.events.add(e)
        return c.serialize()
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
