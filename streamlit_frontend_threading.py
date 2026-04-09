import streamlit as st
from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph_backend import chatbot
import uuid
# ---------------------------------- utility Functions ----------------------------------
def get_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = get_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
# ---------------------------------- session setup ----------------------------------
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = get_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']= []
add_thread(st.session_state['thread_id'])

def load_conversation(thread_id):
    return chatbot.get_state(config={"configurable": {"thread_id": st.session_state['thread_id']}}).values['messages']
# ---------------------------------- Sidebar UI ----------------------------------
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for message in messages:
            if isinstance(message, HumanMessage):
                role ='User'
            else:
                role = 'assistant'
            temp_messages.append({'role':role, 'content':message.content})

        st.session_state['message_history'] = temp_messages
# ---------------------------------- Main UI ----------------------------------
CONFIG = {"configurable": {"thread_id": st.session_state['thread_id']}}

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Enter your message here")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    def stream_text_only():
        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"
        ):
            if not isinstance(message_chunk, AIMessageChunk):
                continue

            for block in message_chunk.content:
                if not isinstance(block, dict):
                    continue

                if block.get("type") != "text":
                    continue

                text = block.get("text", "")

                # Skip empty / signature blocks
                if text and text.strip():
                    yield text

    # Display assistant response
    with st.chat_message("assistant"):
        full_response = st.write_stream(stream_text_only())

    # Save clean response
    st.session_state["message_history"].append({
        "role": "assistant",
        "content": full_response.strip() if full_response else ""
    })