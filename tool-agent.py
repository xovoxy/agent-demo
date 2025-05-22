import asyncio
import os

from openai import AsyncOpenAI
from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent
from agents import Agent, Runner, set_default_openai_api, OpenAIChatCompletionsModel, TResponseInputItem, RunConfig, MessageOutputItem, ItemHelpers
from dotenv import load_dotenv

load_dotenv()

external_model = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

set_default_openai_api(external_model)

ds = OpenAIChatCompletionsModel(
    model=os.getenv("MODEL"),
    openai_client=external_model,
)

english_translate = Agent(
    name="eng_trans",
    instructions="将输入的内容翻译为英文",
    handoff_description="将文本翻译为英文的工具",
    model=ds
)

jap_translate = Agent(
    name="jap_trans",
    instructions="将输入的内容翻译为日文",
    handoff_description="将文本翻译为日文的工具",
    model=ds
)

orch_agent = Agent(
    name="orch_agent",
    instructions=(
        "你是一个翻译Agent，用给你的工具对内容进行翻译。"
        "当要求多语言翻译的时候，依次调用相关的工具进行处理。"
        "你不要自己翻译，用注册的工具进行处理。"
    ),
    tools=[
        english_translate.as_tool(
            tool_name="translate_to_eng",
            tool_description="翻译文本为英文"
        ),
        jap_translate.as_tool(
            tool_name="translate_to_jap",
            tool_description="翻译文本为日文"
        )
    ],
    model=ds
)

summary_agent = Agent(
    name="synthesizer_agent",
    instructions="你分析这些翻译后的文本，如果需要可以进行更正，并且将这些信息综合起来给一个最终答复",
    model=ds
)

async def main():
    msg = input("你想翻译什么，以及翻译成什么语言:  ")
    config = RunConfig(tracing_disabled=True)
    orch_result = await Runner.run(orch_agent, msg, run_config=config)

    for item in orch_result.new_items:
        if isinstance(item, MessageOutputItem):
            text = ItemHelpers.text_message_output(item)
            if text:
                print(f"  - Translation step: {text}\n")

    summary_result = await Runner.run(summary_agent, orch_result.to_input_list(), run_config=config)

    print(f"\n\n Final response:\n{summary_result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
    

    


