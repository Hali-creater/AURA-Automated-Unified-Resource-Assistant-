import streamlit as st
import os
from aura_agent import AuraAgent

st.title("AURA - Your Virtual Assistant")

# Sidebar for API key configuration
st.sidebar.header("API Configuration")
groq_api_key = st.sidebar.text_input("Groq API Key", type="password")
email_address = st.sidebar.text_input("Email Address")
email_password = st.sidebar.text_input("Email Password", type="password")
smtp_server = st.sidebar.text_input("SMTP Server")
imap_server = st.sidebar.text_input("IMAP Server")

if st.sidebar.button("Save Keys"):
    os.environ["GROQ_API_KEY"] = groq_api_key
    os.environ["EMAIL_ADDRESS"] = email_address
    os.environ["EMAIL_PASSWORD"] = email_password
    os.environ["SMTP_SERVER"] = smtp_server
    os.environ["IMAP_SERVER"] = imap_server
    st.session_state.api_keys_set = True
    st.sidebar.success("API keys saved!")

# Calendar file uploader
st.sidebar.header("Calendar")
ics_file = st.sidebar.file_uploader("Upload .ics file", type=["ics"])
if ics_file:
    st.session_state.ics_file = ics_file

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
            if "BEGIN:VCALENDAR" in response:
                st.download_button(
                    label="Download Event File",
                    data=response,
                    file_name="event.ics",
                    mime="text/calendar",
                )
            else:
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("Please configure your API keys in the sidebar to begin.")
