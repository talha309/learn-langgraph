import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import chatbot

CONFIG = {"configurable": {"thread_id": "thread_1"}}
# session_state = st.session_state -> dict when enter press the message no eeasries but when refresh the page the message history is lost
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []
# loading template messages
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Enter your message here")

if user_input:

    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)


    response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message = response["messages"][-1].content
    if isinstance(ai_message, list):
        ai_message = ai_message[0]['text']
    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)

