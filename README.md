# AURA - Your Virtual Assistant

This is a Streamlit-based virtual assistant that can help you with various tasks, such as sending emails, managing your calendar, and creating content.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure your credentials:**
    -   Set the following environment variables:
        -   `EMAIL_ADDRESS`: Your email address.
        -   `EMAIL_PASSWORD`: Your email password.
        -   `SMTP_SERVER`: Your SMTP server address.
        -   `SMTP_PORT`: Your SMTP server port.
        -   `IMAP_SERVER`: Your IMAP server address.
        -   `GOOGLE_API_KEY`: Your Google Generative AI API key.
        -   `GCAL_CREDENTIALS_FILE`: The path to your Google Calendar credentials file (e.g., `credentials.json`).
        -   `TIMEZONE`: Your timezone (e.g., `America/Los_Angeles`).
    -   Set up a project in the Google Cloud Platform and enable the Google Calendar API. Create a service account and download the JSON key file. Place this file in a secure location and set the `GCAL_CREDENTIALS_FILE` environment variable to its path. You will also need to share your Google Calendar with the service account's email address.

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
