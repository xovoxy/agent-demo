import asyncio
import os
from openai import AsyncOpenAI
from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent
from agents import Agent, Runner, RunConfig, set_default_openai_api, OpenAIChatCompletionsModel, TResponseInputItem, RawResponsesStreamEvent
from dotenv import load_dotenv

load_dotenv()

external = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

set_default_openai_api(external)

ds = OpenAIChatCompletionsModel(
    model=os.getenv("MODEL"),
    openai_client=external,
)

english_agent = Agent(
    name="eng-agent",
    instructions="只用英文进行回复",
    model=ds
)

chinese_agent = Agent(
    name="zh-agent",
    instructions="只用中文进行回复",
    model=ds
)

triage_agent = Agent(
    name="triage_agent",
    instructions="基于请求的语言是中文还是英文，分别使用对应的Agent来处理",
    handoffs=[english_agent, chinese_agent],
    model=ds
)


async def main():
    msg = input("Hi, i can speak chinese and english, can i help you? ")

    agent = triage_agent
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    config = RunConfig(tracing_disabled=True)
    while True:
        result = Runner.run_streamed(agent, inputs, run_config=config)

        async for event in result.stream_events():
            if not isinstance(event, RawResponsesStreamEvent):
                continue
            data = event.data
            if isinstance(data, ResponseTextDeltaEvent):
                print(data.delta, end="", flush=True)
            elif isinstance(data, ResponseContentPartDoneEvent):
                print("\n")
        inputs = result.to_input_list()
        print("\n")

        user_msg = input("请输入: ")
        inputs.append({"content": user_msg, "role": "user"})
        agent = result.current_agent


if __name__ == "__main__":
    asyncio.run(main())
