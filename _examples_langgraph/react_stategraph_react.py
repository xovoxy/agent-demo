from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, List, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langchain_tavily import TavilySearch


load_dotenv()


class ReActState(TypedDict, total=False):
    messages: List[Any]
    step: int
    done: bool
    model_action: Dict[str, Any]
    last_tool_result: str


SYSTEM_PROMPT = """
你是一个ReAct智能体：
- 按“思考→调用工具(可选)→再思考→最终回答”的流程工作。
- 严格输出 JSON（不要夹杂其它文本）：
  {"type": "tool", "tool": "tavily_search", "input": "<查询>"}
  或
  {"type": "final", "answer": "<最终答案>"}
- 只有需要外部信息时才调用工具；否则直接输出最终答案。
- 工具名白名单：tavily_search。
""".strip()


# 初始化 LLM 与工具
llm = ChatDeepSeek(model="deepseek-chat", api_key=os.environ["DEEPSEEK_API_KEY"])
search = TavilySearch(max_results=3)
TOOLS: Dict[str, Any] = {"tavily_search": search}


def node_input(state: ReActState) -> ReActState:
    # 输入节点：透传当前 messages
    return {
        "messages": state.get("messages", []),
        "step": 0,  # 重置步数
        "done": False,  # 重置完成状态
    }


def node_think(state: ReActState) -> ReActState:
    if state.get("done"):
        return {}

    messages = state.get("messages", [])[:]
    last_obs = state.get("last_tool_result")
    if last_obs:
        messages.append(AIMessage(content=f"(工具观察)\n{last_obs}"))

    full_msgs: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        if isinstance(m, HumanMessage):
            full_msgs.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            full_msgs.append({"role": "assistant", "content": m.content})
        elif isinstance(m, ToolMessage):
            # 作为用户提供的观察注入
            full_msgs.append({"role": "user", "content": f"[工具结果]\n{m.content}"})

    result = llm.invoke(full_msgs)
    content = (result.content or "").strip()

    try:
        action = json.loads(content)
    except Exception:
        action = {"type": "final", "answer": content}

    messages.append(AIMessage(content=content))
    return {"messages": messages, "model_action": action}


def route(state: ReActState) -> Literal["act", "finish"]:
    action = state.get("model_action", {})
    if action.get("type") == "tool" and action.get("tool") in TOOLS:
        return "act"
    return "finish"


def node_act(state: ReActState) -> ReActState:
    action = state["model_action"]
    tool_name = action["tool"]
    tool_input = action.get("input", "")
    tool = TOOLS[tool_name]
    obs = tool.invoke(tool_input)
    messages = state.get("messages", [])[:]
    messages.append(ToolMessage(content=str(obs), name=tool_name, tool_call_id=str(uuid.uuid4())))
    return {
        "messages": messages,
        "last_tool_result": str(obs),
        "step": state.get("step", 0) + 1,
    }


def node_finish(state: ReActState) -> ReActState:
    messages = state.get("messages", [])[:]
    action = state.get("model_action", {})
    if action.get("type") == "final" and action.get("answer"):
        final_answer = action["answer"]
    else:
        final_answer = llm.invoke(
            [
                {"role": "system", "content": "基于现有上下文与工具观察，输出简洁准确的最终答案。"}
            ]
            + [
                {"role": "user", "content": m.content}
                if isinstance(m, (HumanMessage, ToolMessage))
                else {"role": "assistant", "content": m.content}
                for m in messages
            ]
        ).content

    messages.append(AIMessage(content=final_answer))
    return {"messages": messages, "done": True}


# 构建图（含 ReAct 循环与步数上限）
g = StateGraph(ReActState)
g.add_node("input", node_input)
g.add_node("think", node_think)
g.add_node("act", node_act)
g.add_node("finish", node_finish)

g.add_edge(START, "input")
g.add_edge("input", "think")
g.add_conditional_edges("think", route, {"act": "act", "finish": "finish"})


def continue_or_finish(state: ReActState) -> Literal["think", "finish"]:
    return "think" if state.get("step", 0) < 3 else "finish"


g.add_conditional_edges("act", continue_or_finish, {"think": "think", "finish": "finish"})
g.add_edge("finish", END)

agent = g.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "react-demo-1"}}

    print("[回合1] 用户：请用网络找一部评分大于9.0的电影并推荐。")
    out = agent.invoke({"messages": [HumanMessage(content="请用网络找一部评分大于9.0的电影并推荐。")]}, config=config)
    print("助手：", out["messages"][-1].content)

    print("\n[回合2] 用户：基于刚刚的推荐，写一段200字影评。")
    out = agent.invoke({"messages": [HumanMessage(content="基于刚刚的推荐，写一段200字影评。")]}, config=config)
    print("助手：", out["messages"][-1].content)


