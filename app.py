import streamlit as st
import os
from aura_agent import AuraAgent

st.title("AURA - Your Virtual Assistant")

# Sidebar for API key configuration
st.sidebar.header("API Configuration")
google_api_key = st.sidebar.text_input("Google API Key", type="password")
gcal_credentials_file = st.sidebar.text_input("Path to Google Calendar Credentials")
email_address = st.sidebar.text_input("Email Address")
email_password = st.sidebar.text_input("Email Password", type="password")
smtp_server = st.sidebar.text_input("SMTP Server")
imap_server = st.sidebar.text_input("IMAP Server")
timezone = st.sidebar.text_input("Timezone", "America/Los_Angeles")

if st.sidebar.button("Save Keys"):
    os.environ["GOOGLE_API_KEY"] = google_api_key
    os.environ["GCAL_CREDENTIALS_FILE"] = gcal_credentials_file
    os.environ["EMAIL_ADDRESS"] = email_address
    os.environ["EMAIL_PASSWORD"] = email_password
    os.environ["SMTP_SERVER"] = smtp_server
    os.environ["IMAP_SERVER"] = imap_server
    os.environ["TIMEZONE"] = timezone
    st.session_state.api_keys_set = True
    st.sidebar.success("API keys saved!")


# Initialize agent and chat if API keys are set
if 'api_keys_set' in st.session_state and st.session_state.api_keys_set:
    if 'agent' not in st.session_state:
        st.session_state.agent = AuraAgent()

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.session_state.agent.process_command(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("Please configure your API keys in the sidebar to begin.")
