import asyncio
import os

from openai import AsyncOpenAI
from agents import Runner, Agent, set_default_openai_api, OpenAIChatCompletionsModel
from dotenv import load_dotenv

load_dotenv()

external_mode = AsyncOpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

set_default_openai_api(external_mode)

ds = OpenAIChatCompletionsModel(
    model=os.getenv("MODEL"),
    openai_client=external_mode
)

