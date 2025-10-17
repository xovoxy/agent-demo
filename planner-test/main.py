from typing import List, TypedDict
from langgraph.graph import StateGraph, END, START
import sys

class TaskState(TypedDict, total=False):
    user_goal: str
    sub_tasks: List[str]
    plan: List[str]

def task_analyzer(state: TaskState) -> TaskState:
    goal = state.get("user_goal", "未知任务")
    subtasks = [
        f"了解 {goal} 的基本概念",
        f"查阅 {goal} 相关资料",
        f"实践一个 {goal} 的简单实例"
    ]
    return {"sub_tasks": subtasks}

def planner(state: TaskState) -> TaskState:
    subtasks = state.get("sub_tasks", [])
    plan = [f"Day {i+1}: {task}" for i, task in enumerate(subtasks)]
    return {"plan": plan}


def build_graph() -> StateGraph:
    builder = StateGraph(TaskState)

    builder.add_node("analyzer", task_analyzer)
    builder.add_node("planner", planner)

    builder.add_edge(START, "analyzer")
    builder.add_edge("analyzer", "planner")
    builder.add_edge("planner", END)

    return builder

if __name__ == "__main__":
    user_goal = input("请输入你要学习的目标： ").strip()
    if not user_goal:
        print("目标不能为空")
        sys.exit(1)
    
    init_goal: TaskState = {"user_goal": user_goal}
    
    graph = build_graph().compile()
    
    result = graph.invoke(init_goal)
    
    print("\n 最终输出结果：")
    print(result)
    print("生成的子任务：", result.get("sub_tasks"))
    print("生成的计划：", result.get("plan"))


