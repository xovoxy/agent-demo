import asyncio
import os
import shutil

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agents import Agent, Runner, set_default_openai_client, OpenAIChatCompletionsModel, RunConfig
from agents.mcp import MCPServer, MCPServerStdio


load_dotenv()

async def run(mcp_server: MCPServer):
    external = AsyncOpenAI(
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

    set_default_openai_client(external)

    deepseek = OpenAIChatCompletionsModel(
        model=os.getenv("MODEL"),
        openai_client=external,
    )

    agent = Agent(
        name="Assistant",
        instructions="使用工具获取当前的天气，根据天气信息回答用户问题",
        mcp_servers=[mcp_server],
        model=deepseek
    )
    
    config = RunConfig(tracing_disabled=True)

    message = "获取北京的天气"
    print(f"Running: {message}")
    result = await Runner.run(agent, message, run_config=config)
    print(result.final_output)

    message = "推荐一下这个天气适合的穿搭"
    print(f"Running: {message}")
    result = await Runner.run(agent, message, run_config=config, previous_response_id=result.last_response_id)
    print(result.final_output)


async def main():
    async with MCPServerStdio(
        name="获取天气mcp，使用uv",
        params={
            "command": "uv",
            "args": ["run", "python", "/Users/xyt/pythonws/mcp-hello-world/ai-wardrobe/main.py"]
        }
    ) as server:
        await run(server)

if __name__ == "__main__":
    asyncio.run(main())
