import asyncio
import os
import shutil

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agents import Agent, Runner, set_default_openai_client, OpenAIChatCompletionsModel, RunConfig, TResponseInputItem
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
        instructions="你是一个助手",
        mcp_servers=[mcp_server],
        model=deepseek
    )

    config = RunConfig(tracing_disabled=True)

    message: list[TResponseInputItem] = [
        {"content": "获取北京和天津的天气", "role": "user"}]

    result = await Runner.run(agent, message, run_config=config)
    print(result.final_output)

    message = result.to_input_list()

    message.append({"content": "根据天气推荐穿搭", "role": "user"})
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
