import asyncio
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, Agent, Runner, set_default_openai_client
from agents.model_settings import ModelSettings
from dotenv import load_dotenv
import os


load_dotenv()

async def main():
    external_client = AsyncOpenAI(
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

    set_default_openai_client(external_client)

    deepseek_model = OpenAIChatCompletionsModel(
        model=os.getenv("MODEL"),
        openai_client=external_client
    )

    agent = Agent(name="demo",
                  instructions="你是一个助人为乐的助手",
                  model=deepseek_model)

    result = await Runner.run(agent, "请写一首关于编程中递归的俳句")

    print(result)

if __name__ == "__main__":
    asyncio.run(main())
