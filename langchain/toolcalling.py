from typing import List, Optional
from pydantic import BaseModel, Field


class Person(BaseModel):
    """Information about a person"""
    
    name: Optional[str] = Field(default=None, description="The name of the person")
    hair_color: Optional[str] = Field(
        default=None, description="The color of the person hair if known, only color"
    )
    height_in_meters: Optional[str] = Field(
        default=None, description="Height measured in meters"
    )
    
class Data(BaseModel):
    """Extracted data about people."""
    
    people: List[Person]
    
    
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm,"
            "Only extract relevant information from the text. "
            "If you dont know the value of an attribute asked to extract, "
            "return null for the attributes value"
        ),
        ("human", "{text}"),
    ]
)

from dotenv import load_dotenv
import os
import getpass

load_dotenv()


if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter your DeepSeek API key: ")

from langchain.chat_models import init_chat_model
model = init_chat_model("deepseek-chat", model_provider="deepseek")

structured_llm = model.with_structured_output(Data)

prompt = prompt_template.invoke({"text": "My name is Jeff, my hair is black and i am 1.7 tall. Anna has the same color hair as me."})

response = structured_llm.invoke(prompt)
print(response.model_dump())
