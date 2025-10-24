"""
基于 LangGraph StateGraph 的监督者模式和群体智能实现

这个实现展示了如何使用 LangGraph 的核心功能：
1. StateGraph 构建复杂的智能体工作流
2. 监督者模式：智能任务路由和分配
3. 群体智能：并行协作和共识构建
4. 记忆管理：跨会话状态持久化
"""

import asyncio
import os
import uuid
from typing import TypedDict, List, Dict, Any, Literal
from datetime import datetime

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# ==================== 状态定义 ====================

class SupervisorState(TypedDict, total=False):
    """监督者状态"""
    user_input: str
    task_type: str
    assigned_worker: str
    worker_result: str
    messages: List[Any]
    step: int
    done: bool

class SwarmState(TypedDict, total=False):
    """群体智能状态"""
    user_input: str
    parallel_results: Dict[str, str]
    consensus_result: str
    messages: List[Any]
    step: int
    done: bool

# ==================== 初始化 ====================

if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = input("Enter your DeepSeek API key: ")

model = init_chat_model("deepseek-chat", model_provider="deepseek")
search = TavilySearch(max_results=2)

# ==================== 监督者模式实现 ====================

def supervisor_classify(state: SupervisorState) -> SupervisorState:
    """监督者：任务分类"""
    user_input = state.get("user_input", "")
    
    classification_prompt = f"""
    作为智能任务分配器，请分析用户请求并确定最适合的处理方式：
    
    用户请求: {user_input}
    
    可选的工作智能体：
    - research: 需要搜索信息、查找资料、数据收集
    - analysis: 需要分析数据、比较、评估、总结  
    - creative: 需要创作内容、写作、设计、创意
    - technical: 需要技术实现、编程、系统设计
    
    请只返回一个关键词：research, analysis, creative, 或 technical
    """
    
    response = model.invoke([{"role": "user", "content": classification_prompt}])
    task_type = response.content.strip().lower()
    
    return {
        "task_type": task_type,
        "assigned_worker": task_type,
        "step": state.get("step", 0) + 1
    }

def supervisor_assign(state: SupervisorState) -> SupervisorState:
    """监督者：分配任务"""
    task_type = state.get("assigned_worker", "analysis")
    user_input = state.get("user_input", "")
    
    # 工作智能体映射
    workers = {
        "research": research_worker,
        "analysis": analysis_worker,
        "creative": creative_worker,
        "technical": technical_worker
    }
    
    if task_type in workers:
        worker_func = workers[task_type]
        result = worker_func(user_input)
        return {
            "worker_result": result,
            "done": True
        }
    else:
        return {
            "worker_result": "抱歉，我无法处理这种类型的任务。",
            "done": True
        }

def supervisor_route(state: SupervisorState) -> Literal["assign", "finish"]:
    """监督者：路由决策"""
    task_type = state.get("task_type", "")
    if task_type in ["research", "analysis", "creative", "technical"]:
        return "assign"
    return "finish"

# ==================== 工作智能体 ====================

def research_worker(input_text: str) -> str:
    """研究型工作智能体"""
    try:
        search_results = search.invoke(input_text)
        prompt = f"""
        作为专业研究助手，请基于搜索结果提供详细报告：
        
        用户问题: {input_text}
        搜索结果: {search_results}
        
        请提供：
        1. 关键信息摘要
        2. 详细分析
        3. 相关建议
        4. 信息来源
        """
        response = model.invoke([{"role": "user", "content": prompt}])
        return response.content
    except Exception as e:
        return f"研究过程中出现错误: {str(e)}"

def analysis_worker(input_text: str) -> str:
    """分析型工作智能体"""
    prompt = f"""
    作为专业分析师，请对以下内容进行深入分析：
    
    用户问题: {input_text}
    
    请提供：
    1. 详细分析
    2. 优缺点比较
    3. 风险评估
    4. 建议和结论
    """
    response = model.invoke([{"role": "user", "content": prompt}])
    return response.content

def creative_worker(input_text: str) -> str:
    """创意型工作智能体"""
    prompt = f"""
    作为创意专家，请基于以下请求进行创作：
    
    用户问题: {input_text}
    
    请提供：
    1. 创意构思
    2. 详细内容
    3. 实施建议
    4. 创意亮点
    """
    response = model.invoke([{"role": "user", "content": prompt}])
    return response.content

def technical_worker(input_text: str) -> str:
    """技术型工作智能体"""
    prompt = f"""
    作为技术专家，请基于以下请求提供技术解决方案：
    
    用户问题: {input_text}
    
    请提供：
    1. 技术方案
    2. 实现步骤
    3. 代码示例（如适用）
    4. 技术建议
    """
    response = model.invoke([{"role": "user", "content": prompt}])
    return response.content

# ==================== 群体智能实现 ====================

def swarm_parallel(state: SwarmState) -> SwarmState:
    """群体智能：并行处理"""
    user_input = state.get("user_input", "")
    
    # 并行调用所有工作智能体
    workers = {
        "research": research_worker,
        "analysis": analysis_worker,
        "creative": creative_worker,
        "technical": technical_worker
    }
    
    results = {}
    for worker_name, worker_func in workers.items():
        try:
            result = worker_func(user_input)
            results[worker_name] = result
        except Exception as e:
            results[worker_name] = f"处理失败: {str(e)}"
    
    return {
        "parallel_results": results,
        "step": state.get("step", 0) + 1
    }

def swarm_consensus(state: SwarmState) -> SwarmState:
    """群体智能：构建共识"""
    parallel_results = state.get("parallel_results", {})
    user_input = state.get("user_input", "")
    
    consensus_prompt = f"""
    作为群体智能协调者，请综合多个专业智能体的观点：
    
    用户问题: {user_input}
    
    研究专家观点: {parallel_results.get('research', '')}
    分析师观点: {parallel_results.get('analysis', '')}
    创意专家观点: {parallel_results.get('creative', '')}
    技术专家观点: {parallel_results.get('technical', '')}
    
    请综合这些观点，提供一个平衡、全面的最终答案，包括：
    1. 各观点的核心要点
    2. 共识和分歧
    3. 综合建议
    4. 实施路径
    """
    
    response = model.invoke([{"role": "user", "content": consensus_prompt}])
    
    return {
        "consensus_result": response.content,
        "done": True
    }

# ==================== 图构建 ====================

def build_supervisor_graph():
    """构建监督者模式图"""
    graph = StateGraph(SupervisorState)
    
    # 添加节点
    graph.add_node("classify", supervisor_classify)
    graph.add_node("assign", supervisor_assign)
    
    # 添加边
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", supervisor_route, {
        "assign": "assign",
        "finish": END
    })
    graph.add_edge("assign", END)
    
    return graph.compile(checkpointer=MemorySaver())

def build_swarm_graph():
    """构建群体智能图"""
    graph = StateGraph(SwarmState)
    
    # 添加节点
    graph.add_node("parallel", swarm_parallel)
    graph.add_node("consensus", swarm_consensus)
    
    # 添加边
    graph.add_edge(START, "parallel")
    graph.add_edge("parallel", "consensus")
    graph.add_edge("consensus", END)
    
    return graph.compile(checkpointer=MemorySaver())

# ==================== 演示函数 ====================

async def demo_supervisor_mode():
    """演示监督者模式"""
    print("🤖 监督者模式演示")
    print("=" * 60)
    
    supervisor_graph = build_supervisor_graph()
    config = {"configurable": {"thread_id": f"supervisor-{uuid.uuid4()}"}}
    
    test_cases = [
        "请研究一下人工智能的最新发展趋势",
        "分析一下Python和Java的优缺点",
        "帮我写一首关于春天的诗",
        "设计一个简单的用户登录系统"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}: {query}")
        print("-" * 40)
        
        result = supervisor_graph.invoke({
            "user_input": query,
            "step": 0,
            "done": False
        }, config)
        
        print(f"🎯 任务类型: {result.get('task_type', 'unknown')}")
        print(f"👤 分配智能体: {result.get('assigned_worker', 'unknown')}")
        print(f"📋 处理结果:\n{result.get('worker_result', 'No result')}")
        print("=" * 40)

async def demo_swarm_intelligence():
    """演示群体智能"""
    print("\n🐝 群体智能演示")
    print("=" * 60)
    
    swarm_graph = build_swarm_graph()
    config = {"configurable": {"thread_id": f"swarm-{uuid.uuid4()}"}}
    
    test_cases = [
        "如何提高团队的工作效率？",
        "未来5年最有前景的技术领域是什么？",
        "设计一个智能家居系统需要考虑哪些因素？"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}: {query}")
        print("-" * 40)
        
        result = swarm_graph.invoke({
            "user_input": query,
            "step": 0,
            "done": False
        }, config)
        
        print("🔍 各智能体观点:")
        parallel_results = result.get("parallel_results", {})
        for agent_name, agent_result in parallel_results.items():
            print(f"  {agent_name}: {agent_result[:100]}...")
        
        print(f"\n🤝 群体共识:\n{result.get('consensus_result', 'No consensus')}")
        print("=" * 40)

async def interactive_demo():
    """交互式演示"""
    print("\n🎮 交互式演示")
    print("=" * 60)
    print("选择模式:")
    print("1. 监督者模式 (智能路由)")
    print("2. 群体智能 (并行协作)")
    print("3. 退出")
    
    while True:
        choice = input("\n请选择 (1/2/3): ").strip()
        
        if choice == "1":
            query = input("请输入您的问题: ")
            supervisor_graph = build_supervisor_graph()
            config = {"configurable": {"thread_id": f"interactive-{uuid.uuid4()}"}}
            
            result = supervisor_graph.invoke({
                "user_input": query,
                "step": 0,
                "done": False
            }, config)
            
            print(f"\n🎯 任务类型: {result.get('task_type')}")
            print(f"👤 分配智能体: {result.get('assigned_worker')}")
            print(f"📋 处理结果:\n{result.get('worker_result')}")
            
        elif choice == "2":
            query = input("请输入您的问题: ")
            swarm_graph = build_swarm_graph()
            config = {"configurable": {"thread_id": f"interactive-{uuid.uuid4()}"}}
            
            result = swarm_graph.invoke({
                "user_input": query,
                "step": 0,
                "done": False
            }, config)
            
            print(f"\n🤝 群体共识:\n{result.get('consensus_result')}")
            
        elif choice == "3":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重试")

async def main():
    """主函数"""
    print("🚀 LangGraph 监督者模式和群体智能演示")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 演示监督者模式
        await demo_supervisor_mode()
        
        # 演示群体智能
        await demo_swarm_intelligence()
        
        # 交互式演示
        # await interactive_demo()
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ 演示完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
