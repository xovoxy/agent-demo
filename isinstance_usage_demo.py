#!/usr/bin/env python3
"""
isinstance() 使用演示
展示为什么必须使用内置类型（小写），不能使用注释类型（大写）
"""

from typing import List, Dict, Set, Tuple, Any, Optional, Union
import sys


def demo_correct_isinstance_usage():
    """演示正确的isinstance使用方式"""
    print("=== 正确的isinstance使用方式 ===")
    
    # 创建一些对象
    my_list = [1, 2, 3, 4, 5]
    my_dict = {'name': 'Alice', 'age': 25}
    my_set = {1, 2, 3, 4, 5}
    my_tuple = (1, 2, 3)
    my_string = "Hello World"
    my_int = 42
    my_float = 3.14
    my_bool = True
    
    # ✅ 正确：使用内置类型（小写）
    print(f"my_list是list类型: {isinstance(my_list, list)}")
    print(f"my_dict是dict类型: {isinstance(my_dict, dict)}")
    print(f"my_set是set类型: {isinstance(my_set, set)}")
    print(f"my_tuple是tuple类型: {isinstance(my_tuple, tuple)}")
    print(f"my_string是str类型: {isinstance(my_string, str)}")
    print(f"my_int是int类型: {isinstance(my_int, int)}")
    print(f"my_float是float类型: {isinstance(my_float, float)}")
    print(f"my_bool是bool类型: {isinstance(my_bool, bool)}")
    
    # ✅ 正确：检查多个类型
    print(f"my_list是list或tuple: {isinstance(my_list, (list, tuple))}")
    print(f"my_int是int或float: {isinstance(my_int, (int, float))}")


def demo_incorrect_isinstance_usage():
    """演示错误的isinstance使用方式"""
    print("\n=== 错误的isinstance使用方式 ===")
    
    my_list = [1, 2, 3, 4, 5]
    
    # ❌ 错误：使用注释类型（大写）
    try:
        result = isinstance(my_list, List)
        print(f"isinstance(my_list, List): {result}")
    except TypeError as e:
        print(f"❌ 错误：{e}")
    
    try:
        result = isinstance(my_list, List[int])
        print(f"isinstance(my_list, List[int]): {result}")
    except TypeError as e:
        print(f"❌ 错误：{e}")
    
    try:
        result = isinstance(my_list, Dict)
        print(f"isinstance(my_list, Dict): {result}")
    except TypeError as e:
        print(f"❌ 错误：{e}")


def demo_why_this_happens():
    """演示为什么会出现这种情况"""
    print("\n=== 为什么会出现这种情况 ===")
    
    from typing import List, Dict
    
    # 查看类型注解和内置类型的区别
    print("内置类型（运行时存在）:")
    print(f"  list: {list}")
    print(f"  dict: {dict}")
    print(f"  str: {str}")
    print(f"  int: {int}")
    
    print("\n注释类型（仅用于类型检查）:")
    print(f"  List: {List}")
    print(f"  Dict: {Dict}")
    print(f"  List[int]: {List[int]}")
    
    print("\n类型检查:")
    print(f"  isinstance(list, type): {isinstance(list, type)}")
    print(f"  isinstance(List, type): {isinstance(List, type)}")
    print(f"  isinstance(List[int], type): {isinstance(List[int], type)}")
    
    # 查看List[int]的实际类型
    print(f"\nList[int]的实际类型: {type(List[int])}")
    print(f"List[int]是GenericAlias: {type(List[int]).__name__}")


def demo_practical_examples():
    """演示实际应用中的正确用法"""
    print("\n=== 实际应用中的正确用法 ===")
    
    def process_data(data: Any) -> str:
        """处理任意类型的数据"""
        # ✅ 正确：使用内置类型进行运行时检查
        if isinstance(data, list):
            return f"处理列表: {len(data)}个元素"
        elif isinstance(data, dict):
            return f"处理字典: {len(data)}个键"
        elif isinstance(data, str):
            return f"处理字符串: {len(data)}个字符"
        elif isinstance(data, (int, float)):
            return f"处理数字: {data}"
        else:
            return f"处理其他类型: {type(data).__name__}"
    
    # 测试不同类型的数据
    test_data = [
        [1, 2, 3, 4, 5],
        {'name': 'Alice', 'age': 25},
        "Hello World",
        42,
        3.14,
        {1, 2, 3},
        (1, 2, 3)
    ]
    
    for data in test_data:
        result = process_data(data)
        print(f"  {data} -> {result}")


def demo_type_annotation_vs_runtime():
    """演示类型注解与运行时检查的区别"""
    print("\n=== 类型注解与运行时检查的区别 ===")
    
    def process_items(items: List[str]) -> List[int]:
        """处理字符串列表，返回长度列表"""
        # 类型注解：List[str] 告诉IDE和静态检查工具这是字符串列表
        # 但运行时检查仍然需要使用内置类型
        
        result = []
        for item in items:
            # ✅ 正确：运行时检查使用内置类型
            if isinstance(item, str):
                result.append(len(item))
            else:
                # 处理类型不匹配的情况
                result.append(0)
        
        return result
    
    # 测试
    test_items = ["Alice", "Bob", "Charlie"]
    result = process_items(test_items)
    print(f"处理结果: {result}")
    
    # 即使类型注解说应该是List[str]，运行时仍可能收到其他类型
    mixed_items = ["Alice", 123, "Bob", True]
    print(f"混合类型处理: {process_items(mixed_items)}")


def demo_advanced_usage():
    """演示高级用法"""
    print("\n=== 高级用法演示 ===")
    
    def smart_processor(data: Any) -> str:
        """智能处理器，根据数据类型进行不同处理"""
        
        # ✅ 正确：使用内置类型进行运行时检查
        if isinstance(data, list):
            if len(data) == 0:
                return "空列表"
            elif all(isinstance(item, str) for item in data):
                return f"字符串列表: {', '.join(data)}"
            elif all(isinstance(item, (int, float)) for item in data):
                return f"数字列表: 总和={sum(data)}"
            else:
                return f"混合列表: {len(data)}个元素"
        
        elif isinstance(data, dict):
            if all(isinstance(key, str) for key in data.keys()):
                return f"字符串键字典: {list(data.keys())}"
            else:
                return f"混合键字典: {len(data)}个键值对"
        
        elif isinstance(data, (int, float)):
            if isinstance(data, int):
                return f"整数: {data}"
            else:
                return f"浮点数: {data:.2f}"
        
        elif isinstance(data, str):
            if data.isdigit():
                return f"数字字符串: {int(data)}"
            else:
                return f"文本字符串: {data.upper()}"
        
        else:
            return f"未知类型: {type(data).__name__}"
    
    # 测试各种数据类型
    test_cases = [
        [],  # 空列表
        ["Alice", "Bob", "Charlie"],  # 字符串列表
        [1, 2, 3, 4, 5],  # 数字列表
        ["Alice", 123, "Bob"],  # 混合列表
        {"name": "Alice", "age": 25},  # 字符串键字典
        {1: "one", 2: "two"},  # 数字键字典
        42,  # 整数
        3.14159,  # 浮点数
        "123",  # 数字字符串
        "Hello",  # 文本字符串
        {1, 2, 3},  # 集合
        (1, 2, 3),  # 元组
    ]
    
    for test_case in test_cases:
        result = smart_processor(test_case)
        print(f"  {test_case} -> {result}")


def demo_best_practices():
    """演示最佳实践"""
    print("\n=== 最佳实践 ===")
    
    # 1. 类型注解用于静态检查
    def process_user_data(
        users: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """处理用户数据"""
        result = {"names": [], "emails": []}
        
        for user in users:
            # ✅ 正确：运行时检查使用内置类型
            if isinstance(user, dict):
                if "name" in user and isinstance(user["name"], str):
                    result["names"].append(user["name"])
                if "email" in user and isinstance(user["email"], str):
                    result["emails"].append(user["email"])
        
        return result
    
    # 2. 类型安全的函数
    def safe_get_value(data: Any, key: str, default: Any = None) -> Any:
        """安全获取字典值"""
        # ✅ 正确：运行时检查使用内置类型
        if isinstance(data, dict) and key in data:
            return data[key]
        return default
    
    # 3. 类型转换函数
    def convert_to_string(value: Any) -> str:
        """将任意值转换为字符串"""
        # ✅ 正确：运行时检查使用内置类型
        if isinstance(value, str):
            return value
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            return ", ".join(map(str, value))
        elif isinstance(value, dict):
            return str(value)
        else:
            return str(value)
    
    # 测试
    users = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
        {"name": "Charlie"}  # 缺少email
    ]
    
    result = process_user_data(users)
    print(f"用户数据处理结果: {result}")
    
    # 测试安全获取
    user = {"name": "Alice", "age": 25}
    name = safe_get_value(user, "name", "Unknown")
    email = safe_get_value(user, "email", "No email")
    print(f"安全获取: name={name}, email={email}")
    
    # 测试类型转换
    test_values = [42, "Hello", [1, 2, 3], {"key": "value"}]
    for value in test_values:
        converted = convert_to_string(value)
        print(f"转换: {value} -> {converted}")


if __name__ == "__main__":
    print("isinstance() 使用指南")
    print("=" * 50)
    
    demo_correct_isinstance_usage()
    demo_incorrect_isinstance_usage()
    demo_why_this_happens()
    demo_practical_examples()
    demo_type_annotation_vs_runtime()
    demo_advanced_usage()
    demo_best_practices()
    
    print("\n" + "=" * 50)
    print("总结:")
    print("✅ 正确：isinstance(obj, list)     - 使用内置类型（小写）")
    print("❌ 错误：isinstance(obj, List)    - 不能使用注释类型（大写）")
    print("❌ 错误：isinstance(obj, List[int]) - 不能使用泛型类型")
    print("\n关键点:")
    print("1. isinstance() 是运行时检查，需要实际的类型对象")
    print("2. 内置类型（list, dict, str等）是运行时存在的类型对象")
    print("3. 注释类型（List, Dict, Str等）仅用于静态类型检查")
    print("4. 类型注解和运行时检查是两个不同的概念")
