from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
import os
import sqlite3
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", google_api_key = GOOGLE_API_KEY) 

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState) -> dict:
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database='chatnot.db', check_same_thread=False)
# check pointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)
# # test
# CONFIG = {'configurable':{'thread_id':'thread-1'}}
# response = chatbot.invoke(
#     {'messages':[HumanMessage(content="what is my name?")]},
#     config=CONFIG
# )
# print(response)
