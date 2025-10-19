import os
import getpass
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter your DeepSeek API key: ")

from langchain.chat_models import init_chat_model
model = init_chat_model(model="deepseek-chat", model_provider="deepseek")

from langchain_core.messages import HumanMessage,SystemMessage

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is the capital of France?")
]

# response = model.invoke(messages)
# print(response)

for token in model.stream(messages):
    print(token.content, end="")
print()