#!/usr/bin/env python3
"""
Python类型系统演示脚本
展示小写类型（内置类型）和大写类型（类型注解）的区别和使用场景
"""

from typing import List, Dict, Set, Tuple, Optional, Union, Any, Callable, Literal
from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    """状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class User:
    """用户数据类"""
    name: str
    age: int
    email: Optional[str] = None


def demo_builtin_types():
    """演示内置类型（小写）的使用"""
    print("=== 内置类型（小写）演示 ===")
    
    # 1. 创建实际对象
    my_list = list([1, 2, 3, 4, 5])
    my_dict = dict({'name': 'Alice', 'age': 25})
    my_set = set([1, 2, 3, 4, 5])
    my_tuple = tuple([1, 2, 3])
    
    print(f"列表: {my_list}, 类型: {type(my_list)}")
    print(f"字典: {my_dict}, 类型: {type(my_dict)}")
    print(f"集合: {my_set}, 类型: {type(my_set)}")
    print(f"元组: {my_tuple}, 类型: {type(my_tuple)}")
    
    # 2. 类型检查
    print(f"my_list是list类型: {isinstance(my_list, list)}")
    print(f"my_dict是dict类型: {isinstance(my_dict, dict)}")
    
    # 3. 直接使用（推荐方式）
    numbers = [1, 2, 3, 4, 5]  # 直接创建，不需要list()
    colors = {'red': '#FF0000', 'green': '#00FF00'}  # 直接创建字典
    print(f"直接创建的列表: {numbers}")
    print(f"直接创建的字典: {colors}")


def demo_type_annotations():
    """演示类型注解（大写）的使用"""
    print("\n=== 类型注解（大写）演示 ===")
    
    # 1. 函数参数和返回值类型注解
    def process_names(names: List[str]) -> Dict[str, int]:
        """处理姓名列表，返回姓名长度字典"""
        return {name: len(name) for name in names}
    
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户，可能返回None"""
        if user_id == 1:
            return User("Alice", 25, "alice@example.com")
        return None
    
    def process_data(data: Union[str, int, List[str]]) -> str:
        """处理不同类型的数据"""
        if isinstance(data, str):
            return data.upper()
        elif isinstance(data, int):
            return str(data * 2)
        else:
            return ", ".join(data)
    
    # 2. 变量类型注解
    user_names: List[str] = ["Alice", "Bob", "Charlie"]
    user_scores: Dict[str, int] = {"Alice": 95, "Bob": 87, "Charlie": 92}
    user_status: Optional[Status] = Status.ACTIVE
    
    # 3. 使用带类型注解的函数
    name_lengths = process_names(user_names)
    print(f"姓名长度字典: {name_lengths}")
    
    user = get_user_by_id(1)
    print(f"用户信息: {user}")
    
    # 4. 联合类型演示
    print(f"处理字符串: {process_data('hello')}")
    print(f"处理整数: {process_data(42)}")
    print(f"处理列表: {process_data(['a', 'b', 'c'])}")


def demo_advanced_types():
    """演示高级类型注解"""
    print("\n=== 高级类型注解演示 ===")
    
    # 1. 可调用类型
    def add_numbers(a: int, b: int) -> int:
        return a + b
    
    def multiply_numbers(a: int, b: int) -> int:
        return a * b
    
    def apply_operation(func: Callable[[int, int], int], a: int, b: int) -> int:
        """应用操作函数"""
        return func(a, b)
    
    print(f"加法结果: {apply_operation(add_numbers, 5, 3)}")
    print(f"乘法结果: {apply_operation(multiply_numbers, 5, 3)}")
    
    # 2. 字面量类型
    def set_user_status(status: Literal["active", "inactive", "pending"]) -> None:
        print(f"用户状态设置为: {status}")
    
    set_user_status("active")
    set_user_status("pending")
    
    # 3. 任意类型
    def handle_any_data(data: Any) -> str:
        """处理任意类型的数据"""
        return f"数据类型: {type(data)}, 值: {data}"
    
    print(handle_any_data(42))
    print(handle_any_data("Hello"))
    print(handle_any_data([1, 2, 3]))
    print(handle_any_data({"key": "value"}))


def demo_type_comparison():
    """演示类型比较"""
    print("\n=== 类型比较演示 ===")
    
    # 小写类型用于运行时
    my_list = [1, 2, 3]
    print(f"运行时类型检查: {isinstance(my_list, list)}")
    print(f"实际类型: {type(my_list)}")
    
    # 大写类型用于静态类型检查（IDE和mypy等工具）
    def typed_function(items: List[int]) -> List[str]:
        return [str(item) for item in items]
    
    # 这个函数有类型注解，IDE会提供更好的代码补全和错误检查
    result = typed_function([1, 2, 3, 4, 5])
    print(f"类型化函数结果: {result}")


def demo_practical_examples():
    """演示实际应用场景"""
    print("\n=== 实际应用场景演示 ===")
    
    # 1. API响应处理
    def parse_api_response(response: Dict[str, Any]) -> Optional[List[User]]:
        """解析API响应"""
        if response.get("success") and "data" in response:
            users = []
            for user_data in response["data"]:
                user = User(
                    name=user_data["name"],
                    age=user_data["age"],
                    email=user_data.get("email")
                )
                users.append(user)
            return users
        return None
    
    # 模拟API响应
    api_response = {
        "success": True,
        "data": [
            {"name": "Alice", "age": 25, "email": "alice@example.com"},
            {"name": "Bob", "age": 30, "email": None}
        ]
    }
    
    users = parse_api_response(api_response)
    if users:
        print("解析的用户:")
        for user in users:
            print(f"  - {user.name}, {user.age}岁, 邮箱: {user.email}")
    
    # 2. 数据处理管道
    def process_user_data(users: List[User]) -> Dict[str, List[User]]:
        """按年龄分组用户"""
        groups = {"young": [], "middle": [], "old": []}
        for user in users:
            if user.age < 30:
                groups["young"].append(user)
            elif user.age < 50:
                groups["middle"].append(user)
            else:
                groups["old"].append(user)
        return groups
    
    if users:
        age_groups = process_user_data(users)
        print("\n按年龄分组:")
        for group_name, group_users in age_groups.items():
            print(f"  {group_name}: {[user.name for user in group_users]}")


if __name__ == "__main__":
    print("Python类型系统完整演示")
    print("=" * 50)
    
    demo_builtin_types()
    demo_type_annotations()
    demo_advanced_types()
    demo_type_comparison()
    demo_practical_examples()
    
    print("\n" + "=" * 50)
    print("总结:")
    print("1. 小写类型（list, dict, set等）用于运行时创建对象和类型检查")
    print("2. 大写类型（List, Dict, Set等）用于静态类型注解，提供更好的IDE支持")
    print("3. 类型注解有助于代码可读性、IDE智能提示和静态类型检查")
    print("4. 在实际开发中，两者配合使用可以获得最佳效果")
