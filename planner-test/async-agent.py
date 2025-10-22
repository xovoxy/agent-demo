from dotenv import load_dotenv
from typing import TypedDict
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END
import os
import asyncio

load_dotenv()

class AgentState(TypedDict):
    user_input: str
    result: dict
    
llm = ChatDeepSeek(model="deepseek-chat", api_key=os.environ["DEEPSEEK_API_KEY"])



