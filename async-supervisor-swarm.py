"""
真正的异步监督者模式和群体智能实现

这个版本实现了真正的异步并行处理：
1. 异步工作智能体
2. 真正的并行执行
3. 异步图节点
4. 高效的并发处理
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

# ==================== 异步工作智能体 ====================

async def async_research_worker(input_text: str) -> str:
    """异步研究型工作智能体"""
    try:
        # 异步搜索
        search_results = await asyncio.to_thread(search.invoke, input_text)
        
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
        
        # 异步模型调用
        response = await asyncio.to_thread(model.invoke, [{"role": "user", "content": prompt}])
        return response.content
    except Exception as e:
        return f"研究过程中出现错误: {str(e)}"

async def async_analysis_worker(input_text: str) -> str:
    """异步分析型工作智能体"""
    try:
        prompt = f"""
        作为专业分析师，请对以下内容进行深入分析：
        
        用户问题: {input_text}
        
        请提供：
        1. 详细分析
        2. 优缺点比较
        3. 风险评估
        4. 建议和结论
        """
        
        response = await asyncio.to_thread(model.invoke, [{"role": "user", "content": prompt}])
        return response.content
    except Exception as e:
        return f"分析过程中出现错误: {str(e)}"

async def async_creative_worker(input_text: str) -> str:
    """异步创意型工作智能体"""
    try:
        prompt = f"""
        作为创意专家，请基于以下请求进行创作：
        
        用户问题: {input_text}
        
        请提供：
        1. 创意构思
        2. 详细内容
        3. 实施建议
        4. 创意亮点
        """
        
        response = await asyncio.to_thread(model.invoke, [{"role": "user", "content": prompt}])
        return response.content
    except Exception as e:
        return f"创作过程中出现错误: {str(e)}"

async def async_technical_worker(input_text: str) -> str:
    """异步技术型工作智能体"""
    try:
        prompt = f"""
        作为技术专家，请基于以下请求提供技术解决方案：
        
        用户问题: {input_text}
        
        请提供：
        1. 技术方案
        2. 实现步骤
        3. 代码示例（如适用）
        4. 技术建议
        """
        
        response = await asyncio.to_thread(model.invoke, [{"role": "user", "content": prompt}])
        return response.content
    except Exception as e:
        return f"技术处理过程中出现错误: {str(e)}"

# ==================== 异步监督者模式 ====================

async def async_supervisor_classify(state: SupervisorState) -> SupervisorState:
    """异步监督者：任务分类"""
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
    
    response = await asyncio.to_thread(model.invoke, [{"role": "user", "content": classification_prompt}])
    task_type = response.content.strip().lower()
    
    return {
        "task_type": task_type,
        "assigned_worker": task_type,
        "step": state.get("step", 0) + 1
    }

async def async_supervisor_assign(state: SupervisorState) -> SupervisorState:
    """异步监督者：分配任务"""
    task_type = state.get("assigned_worker", "analysis")
    user_input = state.get("user_input", "")
    
    # 异步工作智能体映射
    workers = {
        "research": async_research_worker,
        "analysis": async_analysis_worker,
        "creative": async_creative_worker,
        "technical": async_technical_worker
    }
    
    if task_type in workers:
        worker_func = workers[task_type]
        result = await worker_func(user_input)
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

# ==================== 异步群体智能 ====================

async def async_swarm_parallel(state: SwarmState) -> SwarmState:
    """异步群体智能：真正的并行处理"""
    user_input = state.get("user_input", "")
    
    # 异步工作智能体映射
    workers = {
        "research": async_research_worker,
        "analysis": async_analysis_worker,
        "creative": async_creative_worker,
        "technical": async_technical_worker
    }
    
    # 创建异步任务
    tasks = []
    worker_names = []
    
    for worker_name, worker_func in workers.items():
        task = asyncio.create_task(worker_func(user_input))
        tasks.append(task)
        worker_names.append(worker_name)
    
    # 等待所有任务完成
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理结果
    parallel_results = {}
    for worker_name, result in zip(worker_names, results):
        if isinstance(result, Exception):
            parallel_results[worker_name] = f"处理失败: {str(result)}"
        else:
            parallel_results[worker_name] = result
    
    return {
        "parallel_results": parallel_results,
        "step": state.get("step", 0) + 1
    }

async def async_swarm_consensus(state: SwarmState) -> SwarmState:
    """异步群体智能：构建共识"""
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
    
    response = await asyncio.to_thread(model.invoke, [{"role": "user", "content": consensus_prompt}])
    
    return {
        "consensus_result": response.content,
        "done": True
    }

# ==================== 异步图构建 ====================

def build_async_supervisor_graph():
    """构建异步监督者模式图"""
    graph = StateGraph(SupervisorState)
    
    # 添加异步节点
    graph.add_node("classify", async_supervisor_classify)
    graph.add_node("assign", async_supervisor_assign)
    
    # 添加边
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", supervisor_route, {
        "assign": "assign",
        "finish": END
    })
    graph.add_edge("assign", END)
    
    return graph.compile(checkpointer=MemorySaver())

def build_async_swarm_graph():
    """构建异步群体智能图"""
    graph = StateGraph(SwarmState)
    
    # 添加异步节点
    graph.add_node("parallel", async_swarm_parallel)
    graph.add_node("consensus", async_swarm_consensus)
    
    # 添加边
    graph.add_edge(START, "parallel")
    graph.add_edge("parallel", "consensus")
    graph.add_edge("consensus", END)
    
    return graph.compile(checkpointer=MemorySaver())

# ==================== 性能测试 ====================

async def performance_test():
    """性能测试：比较同步和异步版本"""
    print("🚀 性能测试：同步 vs 异步")
    print("=" * 60)
    
    test_input = "如何提高团队的工作效率？"
    
    # 同步版本测试
    print("📊 同步版本测试...")
    start_time = datetime.now()
    
    # 模拟同步执行
    sync_workers = {
        "research": lambda x: f"同步研究结果: {x}",
        "analysis": lambda x: f"同步分析结果: {x}",
        "creative": lambda x: f"同步创意结果: {x}",
        "technical": lambda x: f"同步技术结果: {x}"
    }
    
    sync_results = {}
    for name, worker in sync_workers.items():
        result = worker(test_input)
        sync_results[name] = result
    
    sync_time = (datetime.now() - start_time).total_seconds()
    print(f"⏱️ 同步执行时间: {sync_time:.2f} 秒")
    
    # 异步版本测试
    print("\n📊 异步版本测试...")
    start_time = datetime.now()
    
    # 真正的异步并行执行
    async_workers = {
        "research": async_research_worker,
        "analysis": async_analysis_worker,
        "creative": async_creative_worker,
        "technical": async_technical_worker
    }
    
    tasks = [worker(test_input) for worker in async_workers.values()]
    async_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    async_time = (datetime.now() - start_time).total_seconds()
    print(f"⏱️ 异步执行时间: {async_time:.2f} 秒")
    
    # 性能比较
    if sync_time > 0:
        speedup = sync_time / async_time
        print(f"\n🚀 性能提升: {speedup:.2f}x")
        print(f"💡 时间节省: {sync_time - async_time:.2f} 秒")

# ==================== 演示函数 ====================

async def demo_async_supervisor_mode():
    """演示异步监督者模式"""
    print("🤖 异步监督者模式演示")
    print("=" * 60)
    
    supervisor_graph = build_async_supervisor_graph()
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
        
        start_time = datetime.now()
        result = await supervisor_graph.ainvoke({
            "user_input": query,
            "step": 0,
            "done": False
        }, config)
        end_time = datetime.now()
        
        print(f"🎯 任务类型: {result.get('task_type', 'unknown')}")
        print(f"👤 分配智能体: {result.get('assigned_worker', 'unknown')}")
        print(f"⏱️ 处理时间: {(end_time - start_time).total_seconds():.2f} 秒")
        print(f"📋 处理结果:\n{result.get('worker_result', 'No result')}")
        print("=" * 40)

async def demo_async_swarm_intelligence():
    """演示异步群体智能"""
    print("\n🐝 异步群体智能演示")
    print("=" * 60)
    
    swarm_graph = build_async_swarm_graph()
    config = {"configurable": {"thread_id": f"swarm-{uuid.uuid4()}"}}
    
    test_cases = [
        "如何提高团队的工作效率？",
        "未来5年最有前景的技术领域是什么？"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}: {query}")
        print("-" * 40)
        
        start_time = datetime.now()
        result = await swarm_graph.ainvoke({
            "user_input": query,
            "step": 0,
            "done": False
        }, config)
        end_time = datetime.now()
        
        print(f"⏱️ 并行处理时间: {(end_time - start_time).total_seconds():.2f} 秒")
        print("🔍 各智能体观点:")
        parallel_results = result.get("parallel_results", {})
        for agent_name, agent_result in parallel_results.items():
            print(f"  {agent_name}: {agent_result[:100]}...")
        
        print(f"\n🤝 群体共识:\n{result.get('consensus_result', 'No consensus')}")
        print("=" * 40)

async def main():
    """主函数"""
    print("🚀 异步 LangGraph 监督者模式和群体智能演示")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 性能测试
        await performance_test()
        
        # 演示异步监督者模式
        await demo_async_supervisor_mode()
        
        # 演示异步群体智能
        await demo_async_swarm_intelligence()
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ 演示完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
