from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any, Literal
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_tavily import TavilySearch
import os, json, uuid
import asyncio

load_dotenv()

class AgentState(TypedDict, total=False):
    user_input: str
    messages: List[Any]
    step: int
    done: bool
    model_action: Dict[str, Any]
    
SYSTEM_PROMPT = """
你是一个ReAct智能体：
- 按“思考 -> 调用工具（可选） -> 再思考 -> 最终回答”的流程工作。
- 严格输出 JSON（不要夹杂其他文本）:
  {"type": "tool", "tool": "tavily_search", "input": "<查询>"}
  或 {"type": "final", "answer": "<最终答案>"}
- 只有需要外部信息时才调用工具；否则直接输出最终答案。
- 工具名白名单：tavily_search
"""
    
llm = ChatDeepSeek(model="deepseek-chat", api_key=os.environ["DEEPSEEK_API_KEY"])
search = TavilySearch(max_results=3)
TOOL: Dict[str, Any] = {"tavily_search": search}

def node_input(state: AgentState) -> AgentState:
    messages = state.get("messages", [])[:]
    messages.append(HumanMessage(state.get("user_input", "")))
    return {
        "messages": messages,
        "step": 0,
        "done": False
    }


def node_think(state: AgentState) -> AgentState:
    if state.get("done"):
        return {}

    messages = state.get("messages", [])[:]

    full_msgs : List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        if isinstance(m, HumanMessage):
            full_msgs.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            full_msgs.append({"role": "assistant", "content": m.content})

        elif isinstance(m, ToolMessage):
            full_msgs.append({"role": "user", "content": f"[工具结果]\n{m.content}"})

    result = llm.invoke(full_msgs)
    content = (result.content or "").strip()
    
    try:
        action = json.loads(content)
    except Exception:
        action = {"type": "final", "answer": content}

    messages.append(AIMessage(content=content))
    return {"messages": messages, "model_action": action}

def router(state: AgentState) -> Literal["act", "finish"]:
    action = state.get("model_action", {})        
    if action.get("type") == "tool" and action.get("tool") in TOOL:
        return "act"
    return "finish"

def node_act(state: AgentState) -> AgentState :
    action = state["model_action"]
    tool_name = action["tool"]
    tool_input = action.get("input", "")
    tool = TOOL[tool_name]
    
    obs = tool.invoke(tool_input)
    messages = state.get("messages", [])[:]
    messages.append(ToolMessage(content=str(obs), name=tool_name, tool_call_id=str(uuid.uuid4())))
    return {
        "messages": messages,
        "step": state.get("step", 0) + 1
    }
    
def node_finish(state: AgentState) -> AgentState:
    messages = state.get("messages", [])[:]
    action = state.get("model_action", {})
    if action.get("type") == "final" and action.get("answer"):
        final_answer = action["answer"]
    else:
        final_answer = llm.invoke(
            [
                {"role": "system", "content": "基于现有上下文与工具结果，输出准确的最终答案。"}
            ] + [
                {"role": "user", "content": m.content}
                if isinstance(m, (HumanMessage, ToolMessage))
                else {"role": "assistant", "content": m.content}
                for m in messages
            ]
        ).content
        
    messages.append(AIMessage(final_answer))
    return {"messages": messages, "done": True}

grap = StateGraph(AgentState)
grap.add_node("input", node_input)
grap.add_node("think", node_think)
grap.add_node("act", node_act)
grap.add_node("finish", node_finish)

grap.add_edge(START, "input")
grap.add_edge("input", "think")
grap.add_conditional_edges("think", router, {"act": "act", "finish": "finish"})

grap.add_conditional_edges(
    "act",
    lambda state: "think" if state.get("step", 0) < 3 else "finish",
    {
        "think": "think",
        "finish": "finish"
    }
)

grap.add_edge("finish", END)


memory = MemorySaver()
agent = grap.compile(checkpointer=memory)


if __name__ == "__main__":
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    print("请输入你的问题，按q退出 \n")
    while True:
        user_input = input("用户:")
        if user_input.lower() == "q":
            break
        
        result = agent.invoke({"user_input": user_input}, config)
        print("AI: ", result["messages"][-1].content)
        print("*"*40)

