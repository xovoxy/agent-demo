#!/usr/bin/env python3
"""
完整的Python类型注解系统演示
展示所有可用的类型注解，不仅仅是集合类型
"""

from typing import (
    # 基础类型注解
    Any, Optional, Union, Literal,
    # 集合类型注解
    List, Dict, Set, Tuple,
    # 函数类型注解
    Callable, TypeVar,
    # 高级类型注解
    Generic, Protocol, Type, ClassVar,
    # 特殊类型注解
    Final, NoReturn, Never,
    # 新式类型注解 (Python 3.9+)
    Annotated
)
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum


# 1. 基础类型注解
def demo_basic_types():
    """演示基础类型注解"""
    print("=== 基础类型注解 ===")
    
    # Any - 任意类型
    def handle_any(data: Any) -> str:
        return f"处理了: {data}"
    
    # Optional - 可选类型（等价于 Union[T, None]）
    def find_user(user_id: int) -> Optional[str]:
        if user_id == 1:
            return "Alice"
        return None
    
    # Union - 联合类型
    def process_data(data: Union[str, int, list]) -> str:
        if isinstance(data, str):
            return data.upper()
        elif isinstance(data, int):
            return str(data * 2)
        else:
            return ", ".join(map(str, data))
    
    # Literal - 字面量类型
    def set_status(status: Literal["active", "inactive", "pending"]) -> None:
        print(f"状态设置为: {status}")
    
    print(handle_any(42))
    print(handle_any("Hello"))
    print(find_user(1))
    print(find_user(2))
    print(process_data("hello"))
    print(process_data(21))
    print(process_data([1, 2, 3]))
    set_status("active")


# 2. 集合类型注解
def demo_collection_types():
    """演示集合类型注解"""
    print("\n=== 集合类型注解 ===")
    
    # List - 列表类型
    def process_names(names: List[str]) -> List[int]:
        return [len(name) for name in names]
    
    # Dict - 字典类型
    def create_user_map(users: List[str]) -> Dict[str, int]:
        return {user: len(user) for user in users}
    
    # Set - 集合类型
    def get_unique_items(items: List[str]) -> Set[str]:
        return set(items)
    
    # Tuple - 元组类型
    def get_coordinates() -> Tuple[float, float]:
        return (10.5, 20.3)
    
    # 嵌套集合类型
    def process_matrix(matrix: List[List[int]]) -> Dict[str, List[int]]:
        return {
            "rows": [sum(row) for row in matrix],
            "columns": [sum(col) for col in zip(*matrix)]
        }
    
    names = ["Alice", "Bob", "Charlie"]
    print(f"姓名长度: {process_names(names)}")
    print(f"用户映射: {create_user_map(names)}")
    print(f"唯一项: {get_unique_items(['a', 'b', 'a', 'c'])}")
    print(f"坐标: {get_coordinates()}")
    print(f"矩阵处理: {process_matrix([[1, 2], [3, 4]])}")


# 3. 函数类型注解
def demo_function_types():
    """演示函数类型注解"""
    print("\n=== 函数类型注解 ===")
    
    # Callable - 可调用类型
    def apply_operation(func: Callable[[int, int], int], a: int, b: int) -> int:
        return func(a, b)
    
    def add(x: int, y: int) -> int:
        return x + y
    
    def multiply(x: int, y: int) -> int:
        return x * y
    
    # 高阶函数
    def create_multiplier(factor: int) -> Callable[[int], int]:
        def multiplier(x: int) -> int:
            return x * factor
        return multiplier
    
    print(f"加法: {apply_operation(add, 5, 3)}")
    print(f"乘法: {apply_operation(multiply, 5, 3)}")
    
    double = create_multiplier(2)
    print(f"双倍: {double(7)}")


# 4. 泛型类型注解
def demo_generic_types():
    """演示泛型类型注解"""
    print("\n=== 泛型类型注解 ===")
    
    # TypeVar - 类型变量
    T = TypeVar('T')
    
    class Container(Generic[T]):
        def __init__(self, item: T):
            self.item = item
        
        def get_item(self) -> T:
            return self.item
        
        def set_item(self, item: T) -> None:
            self.item = item
    
    # 使用泛型
    string_container = Container("Hello")
    int_container = Container(42)
    
    print(f"字符串容器: {string_container.get_item()}")
    print(f"整数容器: {int_container.get_item()}")


# 5. 协议类型注解
def demo_protocol_types():
    """演示协议类型注解"""
    print("\n=== 协议类型注解 ===")
    
    # Protocol - 协议类型
    class Drawable(Protocol):
        def draw(self) -> str:
            ...
    
    class Circle:
        def draw(self) -> str:
            return "画一个圆"
    
    class Rectangle:
        def draw(self) -> str:
            return "画一个矩形"
    
    def render_shape(shape: Drawable) -> str:
        return shape.draw()
    
    circle = Circle()
    rectangle = Rectangle()
    
    print(render_shape(circle))
    print(render_shape(rectangle))


# 6. 类类型注解
def demo_class_types():
    """演示类类型注解"""
    print("\n=== 类类型注解 ===")
    
    class Animal:
        def make_sound(self) -> str:
            return "Some sound"
    
    class Dog(Animal):
        def make_sound(self) -> str:
            return "Woof!"
    
    class Cat(Animal):
        def make_sound(self) -> str:
            return "Meow!"
    
    # Type - 类类型
    def create_animal(animal_class: Type[Animal]) -> Animal:
        return animal_class()
    
    # ClassVar - 类变量
    class Config:
        api_key: ClassVar[str] = "secret_key"
        max_connections: ClassVar[int] = 100
    
    dog = create_animal(Dog)
    cat = create_animal(Cat)
    
    print(f"狗叫: {dog.make_sound()}")
    print(f"猫叫: {cat.make_sound()}")
    print(f"配置: {Config.api_key}, {Config.max_connections}")


# 7. 特殊类型注解
def demo_special_types():
    """演示特殊类型注解"""
    print("\n=== 特殊类型注解 ===")
    
    # Final - 最终类型（不可重新赋值）
    API_VERSION: Final[str] = "v1.0"
    
    # NoReturn - 永不返回
    def raise_error() -> NoReturn:
        raise ValueError("这是一个错误")
    
    # Never - 永不存在的类型（Python 3.11+）
    def infinite_loop() -> Never:
        while True:
            pass
    
    print(f"API版本: {API_VERSION}")
    print("错误函数已定义（不会执行）")


# 8. 新式类型注解 (Python 3.9+)
def demo_modern_types():
    """演示新式类型注解"""
    print("\n=== 新式类型注解 ===")
    
    # 使用内置类型进行注解（Python 3.9+）
    def modern_list_function(items: list[str]) -> dict[str, int]:
        return {item: len(item) for item in items}
    
    # Annotated - 带元数据的注解
    def process_user_data(
        name: Annotated[str, "用户名"],
        age: Annotated[int, "年龄，必须大于0"]
    ) -> Annotated[dict, "用户信息字典"]:
        return {"name": name, "age": age}
    
    result = modern_list_function(["Alice", "Bob"])
    print(f"现代类型注解结果: {result}")
    
    user_info = process_user_data("Alice", 25)
    print(f"用户信息: {user_info}")


# 9. 复杂组合类型注解
def demo_complex_types():
    """演示复杂组合类型注解"""
    print("\n=== 复杂组合类型注解 ===")
    
    # 复杂的嵌套类型
    def process_api_response(
        response: Dict[str, Union[List[Dict[str, Any]], str, int]]
    ) -> Optional[List[Dict[str, str]]]:
        """处理API响应"""
        if "data" in response and isinstance(response["data"], list):
            return [
                {"id": str(item.get("id", "")), "name": str(item.get("name", ""))}
                for item in response["data"]
                if isinstance(item, dict)
            ]
        return None
    
    # 使用复杂类型
    api_response = {
        "success": True,
        "data": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "count": 2
    }
    
    result = process_api_response(api_response)
    print(f"API响应处理结果: {result}")


# 10. 实际应用场景
def demo_practical_scenarios():
    """演示实际应用场景"""
    print("\n=== 实际应用场景 ===")
    
    # 数据库操作
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """从数据库获取用户"""
        if user_id == 1:
            return {"id": 1, "name": "Alice", "email": "alice@example.com"}
        return None
    
    # 批量处理
    def process_users(users: List[Dict[str, Any]]) -> List[str]:
        """批量处理用户数据"""
        return [f"{user['name']} ({user['email']})" for user in users]
    
    # 配置管理
    def load_config(config_path: str) -> Dict[str, Union[str, int, bool]]:
        """加载配置文件"""
        return {
            "database_url": "postgresql://localhost:5432/mydb",
            "port": 8080,
            "debug": True
        }
    
    # 事件处理
    def handle_event(
        event_type: Literal["user_created", "user_updated", "user_deleted"],
        data: Dict[str, Any]
    ) -> bool:
        """处理用户事件"""
        print(f"处理事件: {event_type}, 数据: {data}")
        return True
    
    # 使用示例
    user = get_user_by_id(1)
    if user:
        print(f"找到用户: {user}")
    
    users = [{"name": "Alice", "email": "alice@example.com"}]
    processed = process_users(users)
    print(f"处理后的用户: {processed}")
    
    config = load_config("config.json")
    print(f"配置: {config}")
    
    handle_event("user_created", {"name": "Bob", "email": "bob@example.com"})


if __name__ == "__main__":
    print("Python完整类型注解系统演示")
    print("=" * 60)
    
    demo_basic_types()
    demo_collection_types()
    demo_function_types()
    demo_generic_types()
    demo_protocol_types()
    demo_class_types()
    demo_special_types()
    demo_modern_types()
    demo_complex_types()
    demo_practical_scenarios()
    
    print("\n" + "=" * 60)
    print("总结：Python类型注解系统包含：")
    print("1. 基础类型：Any, Optional, Union, Literal")
    print("2. 集合类型：List, Dict, Set, Tuple")
    print("3. 函数类型：Callable, TypeVar")
    print("4. 高级类型：Generic, Protocol, Type, ClassVar")
    print("5. 特殊类型：Final, NoReturn, Never")
    print("6. 新式类型：内置类型注解, Annotated")
    print("7. 复杂组合：嵌套类型、联合类型等")
    print("集合类型只是类型注解系统的一部分，不是全部！")
