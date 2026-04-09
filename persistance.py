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

class JokeState(TypedDict):
    topic: str
    joke: str
    explanation: str

def generate_joke(state: JokeState) -> dict:
    topic = state["topic"]
    joke_prompt = f"Generate a joke about topic:{topic}."
    response = llm.invoke(joke_prompt).content
    return{
        'joke': response
    }
def explain_joke(state: JokeState) -> dict:
    joke = state["joke"]
    explanation_prompt = f"write an explanation for the joke: {joke}"
    response = llm.invoke(explanation_prompt).content
    return {
        'explanation': response
    }

graph = StateGraph(JokeState)
graph.add_node("generate_joke", generate_joke)
graph.add_node("explain_joke", explain_joke)

graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "explain_joke")
graph.add_edge("explain_joke", END)

checkpointer = InMemorySaver()
joke_generator = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}
result = joke_generator.invoke({"topic": "student"}, config=config)
if isinstance(result["joke"], list):
    result["joke"] = result["joke"][0]['text']
print("Joke:", result["joke"])
if isinstance(result["explanation"], list):
    result["explanation"] = result["explanation"][0]['text']
print("Explanation:", result["explanation"])

print ("the joke get state",joke_generator.get_state(config=config))
print(joke_generator.get_state_history(config=config))