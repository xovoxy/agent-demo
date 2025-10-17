from dotenv import load_dotenv
import os
import getpass
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter your DeepSeek API key: ")

model = init_chat_model("deepseek-chat", model_provider="deepseek")

search = TavilySearch(max_results=2)
tools = [search]

memory = MemorySaver()

agent_executor = create_react_agent(model, tools, checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}}

query = "推荐一部评分9.0以上的电影"
input_messages = {"messages": [{"role": "user", "content": query}]}

for step in agent_executor.stream(input_messages, config, stream_mode="values"):
    step["messages"][-1].pretty_print()
    
    
query = "基于推荐的电影，写一篇300字左右的影评"
input_messages = {"messages": [{"role": "user", "content": query}]}

for step in agent_executor.stream(input_messages, config, stream_mode="values"):
    step["messages"][-1].pretty_print()
