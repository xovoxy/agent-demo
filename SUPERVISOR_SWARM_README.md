# LangGraph 监督者模式和群体智能实现

这个项目展示了如何使用 LangGraph 实现高级的智能体模式：

## 🎯 核心功能

### 1. 监督者模式 (Supervisor Pattern)
- **智能任务路由**：根据用户请求自动选择最适合的专业智能体
- **集中协调**：主监督者智能体管理多个工作智能体
- **任务分配**：自动将任务分配给最合适的专业智能体

### 2. 群体智能 (Swarm Intelligence)
- **并行处理**：多个智能体同时工作
- **集体决策**：综合多个专业观点
- **共识构建**：通过协作产生更好的结果

## 📁 文件结构

```
├── langgraph-supervisor-swarm.py    # 主要实现文件
├── supervisor-swarm-demo.py        # 详细演示版本
├── supervisor-swarm-simple.py      # 简化版本
├── run-supervisor-swarm.py         # 运行脚本
└── SUPERVISOR_SWARM_README.md      # 说明文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install langgraph langchain langchain-deepseek langchain-tavily

# 设置环境变量
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export TAVILY_API_KEY="your_tavily_api_key"
```

### 2. 运行演示

```bash
# 运行主要演示
python langgraph-supervisor-swarm.py

# 或使用运行脚本
python run-supervisor-swarm.py
```

## 🏗️ 架构设计

### 监督者模式架构

```
用户输入 → 监督者智能体 → 任务分类 → 智能体分配 → 专业处理 → 返回结果
```

**核心组件**：
- `SupervisorState`: 监督者状态管理
- `supervisor_classify()`: 任务分类节点
- `supervisor_assign()`: 任务分配节点
- `supervisor_route()`: 路由决策函数

### 群体智能架构

```
用户输入 → 并行处理 → 多智能体协作 → 共识构建 → 综合结果
```

**核心组件**：
- `SwarmState`: 群体智能状态管理
- `swarm_parallel()`: 并行处理节点
- `swarm_consensus()`: 共识构建节点

## 🤖 智能体类型

### 专业工作智能体

1. **研究型智能体** (`research_worker`)
   - 专门处理信息搜索和资料收集
   - 使用 Tavily 搜索工具获取最新信息
   - 提供详细的研究报告

2. **分析型智能体** (`analysis_worker`)
   - 专门处理数据分析和比较
   - 提供深入的分析和评估
   - 给出建议和结论

3. **创意型智能体** (`creative_worker`)
   - 专门处理创作和创意任务
   - 提供创意构思和详细内容
   - 给出实施建议

4. **技术型智能体** (`technical_worker`)
   - 专门处理技术实现和编程
   - 提供技术方案和实现步骤
   - 给出技术建议

## 📊 使用示例

### 监督者模式示例

```python
# 用户输入
query = "请研究一下人工智能的最新发展趋势"

# 监督者会自动：
# 1. 分类任务为 "research"
# 2. 分配给研究型智能体
# 3. 返回详细的研究报告
```

### 群体智能示例

```python
# 用户输入
query = "如何提高团队的工作效率？"

# 群体智能会：
# 1. 并行调用所有4个专业智能体
# 2. 收集各智能体的观点
# 3. 构建综合共识
# 4. 返回平衡的最终答案
```

## 🔧 自定义和扩展

### 添加新的工作智能体

```python
def custom_worker(input_text: str) -> str:
    """自定义工作智能体"""
    prompt = f"""
    作为自定义专家，请处理以下请求：
    
    用户问题: {input_text}
    
    请提供专业的处理结果。
    """
    response = model.invoke([{"role": "user", "content": prompt}])
    return response.content

# 在监督者中添加
workers = {
    "research": research_worker,
    "analysis": analysis_worker,
    "creative": creative_worker,
    "technical": technical_worker,
    "custom": custom_worker  # 添加自定义智能体
}
```

### 修改任务分类逻辑

```python
def supervisor_classify(state: SupervisorState) -> SupervisorState:
    """自定义任务分类逻辑"""
    user_input = state.get("user_input", "")
    
    # 自定义分类逻辑
    if "编程" in user_input or "代码" in user_input:
        task_type = "technical"
    elif "分析" in user_input or "比较" in user_input:
        task_type = "analysis"
    # ... 更多自定义逻辑
    
    return {
        "task_type": task_type,
        "assigned_worker": task_type,
        "step": state.get("step", 0) + 1
    }
```

## 🎮 交互式演示

运行程序后，你可以选择：

1. **监督者模式**：智能路由到最合适的专业智能体
2. **群体智能**：并行协作，综合多个专业观点
3. **退出**：结束程序

## 🔍 技术特点

### LangGraph 核心功能

- **StateGraph**: 构建复杂的智能体工作流
- **MemorySaver**: 跨会话状态持久化
- **条件边**: 智能路由和决策
- **并行处理**: 高效的群体协作

### 高级特性

- **记忆管理**: 保持上下文连贯性
- **错误处理**: 优雅的异常处理
- **可扩展性**: 易于添加新的智能体
- **模块化**: 清晰的组件分离

## 🚨 注意事项

1. **API 密钥**: 确保设置了正确的 DeepSeek 和 Tavily API 密钥
2. **网络连接**: 需要网络连接来使用搜索功能
3. **资源消耗**: 群体智能模式会消耗更多计算资源
4. **错误处理**: 程序包含基本的错误处理，但建议在生产环境中加强

## 📈 性能优化

### 并行处理优化

```python
# 使用 asyncio 进行真正的并行处理
async def parallel_workers(user_input: str):
    tasks = [
        asyncio.create_task(research_worker(user_input)),
        asyncio.create_task(analysis_worker(user_input)),
        asyncio.create_task(creative_worker(user_input)),
        asyncio.create_task(technical_worker(user_input))
    ]
    results = await asyncio.gather(*tasks)
    return dict(zip(["research", "analysis", "creative", "technical"], results))
```

### 缓存机制

```python
# 添加结果缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_worker(input_text: str, worker_type: str) -> str:
    """带缓存的智能体处理"""
    # 处理逻辑
    pass
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

MIT License
