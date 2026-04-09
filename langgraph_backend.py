from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
import os
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", google_api_key = GOOGLE_API_KEY) 

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState) -> dict:
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


# CONFIG = {"configurable": {"thread_id":"thread-1"}}
# response = chatbot.invoke(
#     {"messages":[HumanMessage(content="hi i'm talha")]},
#     config=CONFIG
# )
# print(chatbot.get_state(config=CONFIG).values['messages'])
# for message_chunk, metadata in chatbot.stream(
#     {"messages": [HumanMessage(content="what is Gemini?")]},
#       config={"configurable": {"thread_id": "1"}},
#       streaam_mode = 'messages'
# ):
#     if message_chunk.content:
#         print(message_chunk.content, end=" ", flush=True)


# thread_id = "1"
# while True:
#     user_message = input("Type Here:")
#     if user_message.strip().lower() in ["exit", "quit", "bye"]:
#         break
#     print ("user:", user_message)
#     config = {"configurable": {"thread_id": thread_id}}
#     response = chatbot.invoke({"messages": [HumanMessage(content=user_message)]}, config=config)
#     ai_text = response["messages"][-1].content
#     if isinstance(ai_text, list):
#         ai_text = ai_text[0]['text']
        
#     print("AI:", ai_text)
