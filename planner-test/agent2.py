from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
load_dotenv()

class AgentState(TypedDict):
    user_input: str
    question_type: str
    answer: str
    
    
def receive_input(state: AgentState):
    print(f"用户输入：{state['user_input']}")
    return {"user_input": state["user_input"]}

def classify_type(state: AgentState):
    text = state['user_input'].lower()
    if "时间" in text or "time" in text:
        q_type = "time"
    elif "天气" in text or "weather" in text:
        q_type = "weather"
    else:
        q_type = "general"
    
    print(f"问题类型：{q_type}")
    return {"question_type": q_type}

def answer_weather(state: AgentState):
    # 这里可以集成真实的天气API，现在返回模拟数据
    weather_info = "今天天气晴朗，温度25°C，适合外出"
    return {"answer": weather_info}

def answer_time(state: AgentState):
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"answer": f"现在时间是{now}"}
    
def answer_general(state: AgentState):
    return {"answer": f"关于'{state['user_input']}'这个问题，我需要更多信息才能给出准确的回答"}

def show_result(state: AgentState):
    print(f"agent回答{state['answer']}")
    return {}


grap = StateGraph(state_schema=AgentState)

grap.add_node("input", receive_input)
grap.add_node("classify", classify_type)
grap.add_node("weather", answer_weather)
grap.add_node("time", answer_time)
grap.add_node("general", answer_general)

grap.add_edge(START, "input")
grap.add_edge("input", "classify")
grap.add_conditional_edges(
    "classify",
    lambda state: state["question_type"],
    {
        "weather": "weather",
        "time": "time",
        "general": "general",
    },
)

agent = grap.compile()

if __name__ == "__main__":
    while True:
        question = input("请输入你的问题（输入q 退出）：")
        if question.lower() in ["q"]:
            break
        
        result = agent.invoke({"user_input": question})
        print("agent: ", result)
        print("-" * 40)