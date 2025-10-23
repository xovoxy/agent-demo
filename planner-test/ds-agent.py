from datetime import datetime
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
import os, uuid
load_dotenv()


class DsAgentState(TypedDict):
    user_input: str
    question_type: str
    answer: str
    messages: list
    

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
)

def receive_input(state: DsAgentState):
    print(f"用户输入：", state["user_input"])
    messages = state.get("messages", [])
    messages.append(HumanMessage(state["user_input"]))
    return {"user_input": state["user_input"], "messages": messages}


def classfy_question(state: DsAgentState):
    prompt = f"""你是一个分类助手， 根据用户输入的问题判断类型:
    问题：{state['user_input']}
    类型：weather, time, general
    要求仅返回类型字符串，并且是如上三个类型其中之一
    
    """
    
    result = llm.invoke(prompt)
    q_type = result.content.strip().lower()
    print(f"问题类型: {q_type}")
    return {"question_type": q_type}


def answer_weather(state: DsAgentState):
    return {"answer": "这是天气agent"}

    
def answer_time(state: DsAgentState):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"answer": f"现在时间{now}"}

def answer_general(state: DsAgentState):
    promp = f"回答用户的问题：\n {state['user_input']}"
    messages = state["messages"]
    resutl = llm.invoke(messages)
    return {"answer": resutl.content}

def show_output(state: DsAgentState):
    print(f"模型回答：{state['answer']}")
    messages = state.get("messages", [])
    messages.append(AIMessage(state["answer"]))
    return {"messages": messages}

grap = StateGraph(DsAgentState)

grap.add_node("input", receive_input)
grap.add_node("classify", classfy_question)
grap.add_node("weather", answer_weather)
grap.add_node("time", answer_time)
grap.add_node("general", answer_general)
grap.add_node("output", show_output)

grap.add_edge(START, "input")
grap.add_edge("input", "classify")
grap.add_conditional_edges(
    "classify",
    lambda state: state["question_type"],
    {
        "time", "time",
        "weather", "weather",
        "general", "general"
    },
)

grap.add_edge("time", "output")
grap.add_edge("weather", "output")
grap.add_edge("general", "output")
grap.add_edge("output", END)

memory = MemorySaver()
agent = grap.compile(checkpointer=memory)

if __name__=="__main__":
    while True:
        q = input("请输入你的问题，按q退出 \n")
        if q.lower() == "q":
            break
        
        rand = uuid.uuid4()
        print("随机数 ", rand)
        result = agent.invoke({"user_input": q}, config={"configurable": {"thread_id": rand}})
        print("\n")
        print("*"*40)
