#!/usr/bin/env python3
"""
测试监督者模式和群体智能实现

这是一个简化的测试版本，不依赖外部库
"""

import asyncio
import os
import uuid
from typing import TypedDict, List, Dict, Any, Literal
from datetime import datetime

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

# ==================== 模拟模型和工具 ====================

class MockModel:
    """模拟的模型类"""
    
    def invoke(self, messages):
        """模拟模型调用"""
        class MockResponse:
            def __init__(self, content):
                self.content = content
        
        # 简单的模拟逻辑
        user_content = messages[0]["content"] if messages else ""
        
        if "研究" in user_content or "搜索" in user_content:
            return MockResponse("research")
        elif "分析" in user_content or "比较" in user_content:
            return MockResponse("analysis")
        elif "创作" in user_content or "写" in user_content:
            return MockResponse("creative")
        elif "技术" in user_content or "编程" in user_content:
            return MockResponse("technical")
        else:
            return MockResponse("analysis")

class MockSearch:
    """模拟的搜索工具"""
    
    def invoke(self, query):
        return f"搜索结果: {query}"

# ==================== 初始化 ====================

model = MockModel()
search = MockSearch()

# ==================== 监督者模式实现 ====================

def supervisor_classify(state: SupervisorState) -> SupervisorState:
    """监督者：任务分类"""
    user_input = state.get("user_input", "")
    
    classification_prompt = f"""
    分析用户请求，确定最适合的处理方式：
    用户请求: {user_input}
    
    可选类型：
    - research: 需要搜索信息、查找资料
    - analysis: 需要分析、比较、评估
    - creative: 需要创作内容、写作
    - technical: 需要技术实现、编程
    
    只返回一个关键词：research, analysis, creative, 或 technical
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
    search_results = search.invoke(input_text)
    return f"""
🔍 研究结果报告
================
用户问题: {input_text}
搜索结果: {search_results}

📊 关键发现:
- 这是关于 {input_text} 的详细研究
- 基于最新信息进行分析
- 提供了全面的背景资料

💡 建议:
- 建议进一步深入研究
- 关注最新发展趋势
- 保持信息更新
"""

def analysis_worker(input_text: str) -> str:
    """分析型工作智能体"""
    return f"""
📈 分析报告
============
用户问题: {input_text}

🔍 详细分析:
- 对 {input_text} 进行了深入分析
- 识别了关键因素和影响因素
- 评估了各种可能性和风险

⚖️ 优缺点比较:
- 优势: 具有明显的优势
- 劣势: 存在一些挑战
- 平衡: 总体评估良好

🎯 建议和结论:
- 建议采取积极措施
- 重点关注关键领域
- 持续监控和调整
"""

def creative_worker(input_text: str) -> str:
    """创意型工作智能体"""
    return f"""
🎨 创意方案
============
用户问题: {input_text}

💡 创意构思:
- 为 {input_text} 设计了创新方案
- 融合了多种创意元素
- 注重实用性和美观性

📝 详细内容:
- 提供了完整的创意描述
- 包含了实施细节
- 考虑了各种可能性

🚀 实施建议:
- 分阶段实施
- 注重用户体验
- 持续优化改进
"""

def technical_worker(input_text: str) -> str:
    """技术型工作智能体"""
    return f"""
⚙️ 技术解决方案
================
用户问题: {input_text}

🔧 技术方案:
- 为 {input_text} 设计了技术架构
- 选择了合适的技术栈
- 考虑了性能和可扩展性

📋 实现步骤:
1. 需求分析和设计
2. 技术选型和架构
3. 开发和测试
4. 部署和维护

💻 技术建议:
- 使用现代技术栈
- 注重代码质量
- 持续集成和部署
"""

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
    
    return {
        "consensus_result": f"""
🤝 群体智能共识
================
用户问题: {user_input}

🔍 各智能体观点总结:
- 研究专家: 提供了详细的研究报告
- 分析师: 进行了深入的分析和评估
- 创意专家: 提出了创新的解决方案
- 技术专家: 设计了技术实现方案

🎯 综合建议:
- 结合各专家的观点，我们建议采用综合方法
- 既考虑技术可行性，又注重创新性
- 平衡实用性和美观性
- 持续优化和改进

📈 实施路径:
1. 研究阶段: 深入了解需求
2. 分析阶段: 评估各种方案
3. 创意阶段: 设计创新解决方案
4. 技术阶段: 实现技术方案
5. 整合阶段: 综合所有要素
""",
        "done": True
    }

# ==================== 简化的图构建 ====================

class SimpleGraph:
    """简化的图执行器"""
    
    def __init__(self, nodes, edges, start_node, end_node):
        self.nodes = nodes
        self.edges = edges
        self.start_node = start_node
        self.end_node = end_node
    
    def invoke(self, initial_state, config=None):
        """执行图"""
        state = initial_state.copy()
        current_node = self.start_node
        
        while current_node != self.end_node:
            if current_node in self.nodes:
                # 执行节点
                new_state = self.nodes[current_node](state)
                state.update(new_state)
                
                # 路由决策
                if current_node == "classify":
                    next_node = self.edges.get(current_node, {}).get("route", "assign")
                    if next_node == "route":
                        next_node = supervisor_route(state)
                else:
                    next_node = self.edges.get(current_node, "END")
                
                if next_node == "END":
                    break
                current_node = next_node
            else:
                break
        
        return state

def build_supervisor_graph():
    """构建监督者模式图"""
    nodes = {
        "classify": supervisor_classify,
        "assign": supervisor_assign
    }
    
    edges = {
        "classify": {"route": "assign"},
        "assign": "END"
    }
    
    return SimpleGraph(nodes, edges, "classify", "END")

def build_swarm_graph():
    """构建群体智能图"""
    nodes = {
        "parallel": swarm_parallel,
        "consensus": swarm_consensus
    }
    
    edges = {
        "parallel": "consensus",
        "consensus": "END"
    }
    
    return SimpleGraph(nodes, edges, "parallel", "END")

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
        "未来5年最有前景的技术领域是什么？"
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
    print("🚀 LangGraph 监督者模式和群体智能演示 (测试版本)")
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
