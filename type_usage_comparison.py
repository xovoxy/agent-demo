#!/usr/bin/env python3
"""
演示为什么在实际项目中会同时使用大写和小写类型
"""

from typing import List, Dict, Any, TypedDict
from dataclasses import dataclass


# 1. TypedDict 中的类型注解
class ReActState(TypedDict, total=False):
    messages: List[Any]        # 大写：需要指定列表元素类型
    step: int                  # 小写：简单类型
    done: bool                 # 小写：简单类型
    model_action: Dict[str, Any]  # 大写：需要指定字典键值类型
    last_tool_result: str      # 小写：简单类型


# 2. 为什么不能都用小写？
class BadReActState(TypedDict, total=False):
    messages: list             # ❌ 问题：不知道列表里放什么类型
    step: int                  # ✅ 简单类型用小写没问题
    done: bool                 # ✅ 简单类型用小写没问题
    model_action: dict         # ❌ 问题：不知道字典的键值类型
    last_tool_result: str      # ✅ 简单类型用小写没问题


# 3. 为什么不能都用大写？
class OverComplicatedState(TypedDict, total=False):
    messages: List[Any]        # ✅ 复杂类型用大写
    step: int                  # ❌ 过度复杂：简单类型不需要大写
    done: bool                 # ❌ 过度复杂：简单类型不需要大写
    model_action: Dict[str, Any]  # ✅ 复杂类型用大写
    last_tool_result: str      # ❌ 过度复杂：简单类型不需要大写


def demonstrate_usage():
    """演示实际使用中的区别"""
    print("=== 实际使用演示 ===")
    
    # 创建状态对象
    state: ReActState = {
        "messages": ["Hello", "World", 123],  # List[Any] 允许任何类型
        "step": 1,                            # int 类型
        "done": False,                        # bool 类型
        "model_action": {                     # Dict[str, Any] 允许任何值类型
            "action": "search",
            "query": "Python types",
            "confidence": 0.95
        },
        "last_tool_result": "Search completed"  # str 类型
    }
    
    print(f"状态: {state}")
    print(f"消息类型: {type(state['messages'])}")
    print(f"步骤类型: {type(state['step'])}")
    print(f"动作类型: {type(state['model_action'])}")
    
    # 类型检查
    print(f"messages是列表: {isinstance(state['messages'], list)}")
    print(f"step是整数: {isinstance(state['step'], int)}")
    print(f"model_action是字典: {isinstance(state['model_action'], dict)}")


def demonstrate_why_mixed_usage():
    """演示为什么需要混合使用"""
    print("\n=== 为什么需要混合使用 ===")
    
    # 1. 简单类型用小写更自然
    simple_types = {
        "name": "Alice",           # str - 简单字符串
        "age": 25,                 # int - 简单整数
        "is_active": True,         # bool - 简单布尔
        "score": 95.5              # float - 简单浮点数
    }
    
    # 2. 复杂类型用大写提供更多信息
    complex_types = {
        "users": ["Alice", "Bob", "Charlie"],           # List[str] - 知道是字符串列表
        "scores": {"Alice": 95, "Bob": 87},             # Dict[str, int] - 知道键是字符串，值是整数
        "mixed_data": [1, "hello", True, {"key": "value"}]  # List[Any] - 知道是任意类型列表
    }
    
    print("简单类型（小写）:")
    for key, value in simple_types.items():
        print(f"  {key}: {value} ({type(value).__name__})")
    
    print("\n复杂类型（大写注解）:")
    for key, value in complex_types.items():
        print(f"  {key}: {value} ({type(value).__name__})")


def demonstrate_ide_support():
    """演示IDE支持的区别"""
    print("\n=== IDE支持演示 ===")
    
    # 使用类型注解的函数
    def process_messages(messages: List[str]) -> Dict[str, int]:
        """处理消息列表，返回长度统计"""
        return {msg: len(msg) for msg in messages}
    
    def process_simple_data(value: int) -> str:
        """处理简单数据"""
        return f"Value: {value}"
    
    # 这些函数调用时，IDE会提供：
    # 1. 参数类型提示
    # 2. 返回值类型提示  
    # 3. 类型错误检查
    # 4. 自动补全支持
    
    messages = ["Hello", "World", "Python"]
    result = process_messages(messages)
    print(f"消息处理结果: {result}")
    
    simple_result = process_simple_data(42)
    print(f"简单数据处理: {simple_result}")


def demonstrate_practical_example():
    """演示实际项目中的使用"""
    print("\n=== 实际项目使用示例 ===")
    
    # 模拟 LangGraph 中的状态管理
    class AgentState(TypedDict, total=False):
        # 复杂类型用大写 - 提供更多信息
        messages: List[Any]           # 消息列表，元素可以是任何类型
        tools: List[Dict[str, Any]]    # 工具列表，每个工具是字典
        config: Dict[str, Any]         # 配置字典，键值都是任意类型
        
        # 简单类型用小写 - 简洁明了
        step: int                      # 当前步骤
        max_steps: int                 # 最大步骤数
        done: bool                     # 是否完成
        error: str                     # 错误信息
    
    # 创建状态
    state: AgentState = {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ],
        "tools": [
            {"name": "search", "description": "Search the web"},
            {"name": "calculate", "description": "Perform calculations"}
        ],
        "config": {
            "temperature": 0.7,
            "max_tokens": 1000,
            "model": "gpt-4"
        },
        "step": 1,
        "max_steps": 10,
        "done": False,
        "error": ""
    }
    
    print("Agent状态:")
    print(f"  消息数量: {len(state['messages'])}")
    print(f"  工具数量: {len(state['tools'])}")
    print(f"  当前步骤: {state['step']}/{state['max_steps']}")
    print(f"  是否完成: {state['done']}")


if __name__ == "__main__":
    print("Python类型使用最佳实践演示")
    print("=" * 50)
    
    demonstrate_usage()
    demonstrate_why_mixed_usage()
    demonstrate_ide_support()
    demonstrate_practical_example()
    
    print("\n" + "=" * 50)
    print("总结:")
    print("1. 简单类型（int, str, bool, float）用小写更自然")
    print("2. 复杂类型（List, Dict, Set, Tuple）用大写提供更多信息")
    print("3. 混合使用既保持了简洁性，又提供了类型安全")
    print("4. 这是Python社区的最佳实践，平衡了可读性和功能性")
