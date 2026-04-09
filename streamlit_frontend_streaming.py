import streamlit as st
from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph_backend import chatbot

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

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
            config={"configurable": {"thread_id": "thread_1"}},
            stream_mode='messages'
        ):
            # message_chunk.content is a list of content blocks
            if isinstance(message_chunk, AIMessageChunk):
                for block in message_chunk.content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text", "")
                        if text:  # skip empty text blocks (the final signature block)
                            yield text

    with st.chat_message("assistant"):
        ai_message = st.write_stream(stream_text_only())

    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})