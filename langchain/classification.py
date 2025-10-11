import getpass
import os
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter your DeepSeek API key: ")

from langchain.chat_models import init_chat_model
model = init_chat_model(model="deepseek-chat", model_provider="deepseek")


from langchain_core.prompts import ChatPromptTemplate, prompt
from pydantic import BaseModel, Field

tagging_prompt = ChatPromptTemplate.from_template(
    """
    Extract the desired information from the following passage.
    
    Only extract the properties mentioned in the 'Classification' function.
    
    Passage:
    {input}
    """
)

class Classification(BaseModel):
    sentiment: str = Field(description="The sentiment of the input text", enum=["开心", "生气", "伤心", "惊讶", "平静"])
    aggressiveness: int = Field(description="How aggressive the text is, the higher the number, the more aggressive", enum=[1, 2, 3, 4, 5])
    language: str = Field(description="The language of the input text", enum=["中文", "英文"])
    
    
structured_llm = model.with_structured_output(Classification)


inp = "你太棒了，做的真好"
prompt = tagging_prompt.invoke({"input": inp})
response = structured_llm.invoke(prompt)
print(response.model_dump())
