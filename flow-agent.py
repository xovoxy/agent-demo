import asyncio
from pydantic import BaseModel
from agents import Agent, Runner, set_default_openai_api, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
import json

load_dotenv()

external_model = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

set_default_openai_api(external_model)

deepseek = OpenAIChatCompletionsModel(
    model=os.getenv("MODEL"),
    openai_client=external_model,
)

outline_agent = Agent(
    name="story_outline_agent",
    instructions="基于用户的输入，写一篇简短的故事大纲",
    model=deepseek
)


class OutlineCheckerOutput(BaseModel):
    good_quality: bool
    is_martial_arts: bool


outline_checker_agent = Agent(
    name="outline_checker_agent",
    instructions="""评估给出的故事大纲，并且判断是否是武侠风格, 输出结果为json
    例如，故事大纲是高质量的且是武侠风格的则输出:
    {
        "good_quality":true,
        "is_martial_arts":true
    }
    """,
    model=deepseek
)

story_agent = Agent(
    name="story_agent",
    instructions="基于故事大纲写一篇简短的小说",
    model=deepseek
)


async def main():
    input_prompt = str(input("请描述一下你想生成的故事: "))
    config = RunConfig(tracing_disabled=True)
    outline_result = await Runner.run(outline_agent, input=input_prompt, run_config=config)
    print(f"OutLine generate: {outline_result.final_output}")

    outline_checker_result = await Runner.run(outline_checker_agent, outline_result.final_output, run_config=config)
    print(f"{outline_checker_result.final_output=}")
    s = outline_checker_result.final_output.strip().removeprefix("```json").removesuffix("```").strip()
    print(f"{s=}")
    checker_obj = OutlineCheckerOutput.parse_raw(s)
    print(f"{checker_obj=}")

    if not checker_obj.good_quality:
        print("outline is not good quality, so we stop here")
        exit(0)

    if not checker_obj.is_martial_arts:
        print("outline is not a martial arts, so we stop here")
        exit(0)

    print("outline is good quality and a martial arts, so we continue to write the story")

    final_result = await Runner.run(story_agent, outline_result.final_output, run_config=config)

    print(f"Story: {final_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
