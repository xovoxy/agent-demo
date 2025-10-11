import getpass
import os
from dotenv import load_dotenv
from urllib3 import response

load_dotenv()

if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter your DeepSeek API key: ")

from langchain.chat_models import init_chat_model
model = init_chat_model("deepseek-chat", model_provider="deepseek")


from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import HumanMessage, AIMessage

workflow = StateGraph(state_schema=MessagesState)

def call_modal(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}

workflow.add_edge(START, "model")
workflow.add_node("model", call_modal)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "abc123"}}

# query = "Hi! i am bob"

# input_messages = [HumanMessage(query)]
# output = app.invoke({"messages": input_messages}, config)

# print(output["messages"][-1].pretty_print())

# config = {"configurable": {"thread_id": "abc234"}}
# query = "What is my name?"
# input_messages = [HumanMessage(query)]
# output = app.invoke({"messages": input_messages}, config)
# print(output["messages"][-1].pretty_print())

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是个海盗，所有的回答都基于你的认知和海盗生涯"
        ),
        MessagesPlaceholder(variable_name="messages")
    ]
)

def call_prompt_test(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": response}

workflowtest = StateGraph(state_schema=MessagesState)

workflowtest.add_edge(START, "prompt")
workflowtest.add_node("prompt", call_prompt_test)

memorytest = MemorySaver()
app_test = workflowtest.compile(checkpointer=memorytest)

configtest = {"configurable": {"thread_id": "abc123"}}

query = "你好，我是张三"

input_messages = [HumanMessage(query)]
for chunk, metadata in app_test.stream({"messages": input_messages}, configtest, stream_mode="messages"):
    if isinstance(chunk, AIMessage):
        print(chunk.content, end="", flush=True)