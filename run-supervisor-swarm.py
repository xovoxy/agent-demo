#!/usr/bin/env python3
"""
运行监督者模式和群体智能演示

使用方法:
python run-supervisor-swarm.py
"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    """主运行函数"""
    print("🚀 启动 LangGraph 监督者模式和群体智能演示")
    print("=" * 60)
    
    try:
        # 导入并运行演示
        from langgraph_supervisor_swarm import main as demo_main
        await demo_main()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保 langgraph-supervisor-swarm.py 文件存在")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
