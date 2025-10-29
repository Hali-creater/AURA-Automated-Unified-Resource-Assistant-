import streamlit as st
from aura_agent import AuraAgent

st.title("AURA - Your Virtual Assistant")

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
