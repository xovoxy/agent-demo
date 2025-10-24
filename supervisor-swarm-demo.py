"""
LangGraph 监督者模式和群体智能演示

这个示例展示了如何使用 LangGraph 实现：
1. 监督者模式：主监督者智能体协调多个专业工作智能体
2. 群体智能：多个智能体并行协作，实现集体决策
3. 智能路由：根据任务类型自动选择合适的智能体
4. 记忆管理：跨会话的状态持久化
"""

import asyncio
import os
import json
import uuid
from typing import TypedDict, List, Dict, Any, Literal
from datetime import datetime

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

# ==================== 状态定义 ====================

class SupervisorState(TypedDict, total=False):
    """监督者状态"""
    user_input: str
    task_type: str
    assigned_agent: str
    worker_results: Dict[str, Any]
    final_result: str
    messages: List[Any]
    step: int
    done: bool

class SwarmState(TypedDict, total=False):
    """群体智能状态"""
    user_input: str
    worker_agents: List[str]
    parallel_results: Dict[str, Any]
    consensus_result: str
    messages: List[Any]
    step: int
    done: bool

# ==================== 模型和工具初始化 ====================

# 初始化模型
if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = input("Enter your DeepSeek API key: ")

model = init_chat_model("deepseek-chat", model_provider="deepseek")
search = TavilySearch(max_results=3)

# ==================== 监督者模式实现 ====================

class SupervisorAgent:
    """监督者智能体 - 负责任务分配和协调"""
    
    def __init__(self):
        self.workers = {
            "research": ResearchWorker(),
            "analysis": AnalysisWorker(), 
            "creative": CreativeWorker(),
            "technical": TechnicalWorker()
        }
    
    def classify_task(self, state: SupervisorState) -> SupervisorState:
        """任务分类 - 决定分配给哪个工作智能体"""
        user_input = state.get("user_input", "")
        
        classification_prompt = f"""
        分析以下用户请求，确定最适合的处理方式：
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
            "assigned_agent": task_type,
            "step": state.get("step", 0) + 1
        }
    
    def assign_task(self, state: SupervisorState) -> SupervisorState:
        """分配任务给相应的工作智能体"""
        task_type = state.get("assigned_agent", "analysis")
        user_input = state.get("user_input", "")
        
        if task_type in self.workers:
            worker = self.workers[task_type]
            result = worker.process(user_input)
            
            return {
                "worker_results": {task_type: result},
                "final_result": result,
                "done": True
            }
        else:
            return {
                "final_result": "抱歉，我无法处理这种类型的任务。",
                "done": True
            }

class ResearchWorker:
    """研究型工作智能体 - 专门处理信息搜索和资料收集"""
    
    def process(self, user_input: str) -> str:
        """处理研究类任务"""
        prompt = f"""
        你是一个专业的研究助手。请基于以下用户请求进行深入研究：
        
        用户请求: {user_input}
        
        请使用网络搜索工具获取最新信息，然后提供详细的研究报告。
        """
        
        # 使用搜索工具
        search_results = search.invoke(user_input)
        
        research_prompt = f"""
        基于以下搜索结果，为用户提供详细的研究报告：
        
        搜索结果: {search_results}
        用户请求: {user_input}
        
        请提供：
        1. 关键信息摘要
        2. 详细分析
        3. 相关建议
        4. 信息来源
        """
        
        response = model.invoke([{"role": "user", "content": research_prompt}])
        return response.content

class AnalysisWorker:
    """分析型工作智能体 - 专门处理数据分析和比较"""
    
    def process(self, user_input: str) -> str:
        """处理分析类任务"""
        prompt = f"""
        你是一个专业的分析师。请对以下内容进行深入分析：
        
        用户请求: {user_input}
        
        请提供：
        1. 详细分析
        2. 优缺点比较
        3. 风险评估
        4. 建议和结论
        """
        
        response = model.invoke([{"role": "user", "content": prompt}])
        return response.content

class CreativeWorker:
    """创意型工作智能体 - 专门处理创作和创意任务"""
    
    def process(self, user_input: str) -> str:
        """处理创意类任务"""
        prompt = f"""
        你是一个富有创意的内容创作者。请基于以下请求进行创作：
        
        用户请求: {user_input}
        
        请提供：
        1. 创意构思
        2. 详细内容
        3. 实施建议
        4. 创意亮点
        """
        
        response = model.invoke([{"role": "user", "content": prompt}])
        return response.content

class TechnicalWorker:
    """技术型工作智能体 - 专门处理技术实现和编程"""
    
    def process(self, user_input: str) -> str:
        """处理技术类任务"""
        prompt = f"""
        你是一个技术专家。请基于以下请求提供技术解决方案：
        
        用户请求: {user_input}
        
        请提供：
        1. 技术方案
        2. 实现步骤
        3. 代码示例（如适用）
        4. 技术建议
        """
        
        response = model.invoke([{"role": "user", "content": prompt}])
        return response.content

# ==================== 群体智能实现 ====================

class SwarmIntelligence:
    """群体智能 - 多个智能体并行协作"""
    
    def __init__(self):
        self.agents = {
            "researcher": ResearchWorker(),
            "analyst": AnalysisWorker(),
            "creator": CreativeWorker(),
            "technician": TechnicalWorker()
        }
    
    def parallel_processing(self, state: SwarmState) -> SwarmState:
        """并行处理 - 所有智能体同时工作"""
        user_input = state.get("user_input", "")
        
        # 并行调用所有智能体
        results = {}
        for agent_name, agent in self.agents.items():
            try:
                result = agent.process(user_input)
                results[agent_name] = result
            except Exception as e:
                results[agent_name] = f"处理失败: {str(e)}"
        
        return {
            "parallel_results": results,
            "step": state.get("step", 0) + 1
        }
    
    def consensus_building(self, state: SwarmState) -> SwarmState:
        """共识构建 - 综合所有智能体的结果"""
        parallel_results = state.get("parallel_results", {})
        user_input = state.get("user_input", "")
        
        consensus_prompt = f"""
        以下是多个专业智能体对同一问题的不同观点：
        
        用户问题: {user_input}
        
        研究专家观点: {parallel_results.get('researcher', '')}
        分析师观点: {parallel_results.get('analyst', '')}
        创意专家观点: {parallel_results.get('creator', '')}
        技术专家观点: {parallel_results.get('technician', '')}
        
        请综合这些观点，提供一个平衡、全面的最终答案。
        请包括：
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

# ==================== LangGraph 图构建 ====================

def build_supervisor_graph():
    """构建监督者模式的图"""
    supervisor = SupervisorAgent()
    
    def node_classify(state: SupervisorState) -> SupervisorState:
        return supervisor.classify_task(state)
    
    def node_assign(state: SupervisorState) -> SupervisorState:
        return supervisor.assign_task(state)
    
    def route_after_classify(state: SupervisorState) -> Literal["assign", "finish"]:
        task_type = state.get("task_type", "")
        if task_type in ["research", "analysis", "creative", "technical"]:
            return "assign"
        return "finish"
    
    # 构建图
    graph = StateGraph(SupervisorState)
    graph.add_node("classify", node_classify)
    graph.add_node("assign", node_assign)
    
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route_after_classify, {
        "assign": "assign",
        "finish": END
    })
    graph.add_edge("assign", END)
    
    return graph.compile(checkpointer=MemorySaver())

def build_swarm_graph():
    """构建群体智能的图"""
    swarm = SwarmIntelligence()
    
    def node_parallel(state: SwarmState) -> SwarmState:
        return swarm.parallel_processing(state)
    
    def node_consensus(state: SwarmState) -> SwarmState:
        return swarm.consensus_building(state)
    
    # 构建图
    graph = StateGraph(SwarmState)
    graph.add_node("parallel", node_parallel)
    graph.add_node("consensus", node_consensus)
    
    graph.add_edge(START, "parallel")
    graph.add_edge("parallel", "consensus")
    graph.add_edge("consensus", END)
    
    return graph.compile(checkpointer=MemorySaver())

# ==================== 演示和测试 ====================

async def demo_supervisor_mode():
    """演示监督者模式"""
    print("=" * 60)
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
        print(f"👤 分配智能体: {result.get('assigned_agent', 'unknown')}")
        print(f"📋 处理结果:\n{result.get('final_result', 'No result')}")
        print("=" * 40)

async def demo_swarm_intelligence():
    """演示群体智能"""
    print("\n" + "=" * 60)
    print("🐝 群体智能演示")
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
    print("\n" + "=" * 60)
    print("🎮 交互式演示")
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
            print(f"👤 分配智能体: {result.get('assigned_agent')}")
            print(f"📋 处理结果:\n{result.get('final_result')}")
            
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
        await interactive_demo()
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ 演示完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
