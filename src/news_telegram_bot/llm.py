import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


#Load environment variables from the .env file.
#The API key is kept outside the source code for security.
load_dotenv()


#Create the model from Aval Ai Website
model = ChatOpenAI(
    model="gpt-6-luna",
    api_key=os.getenv("AVALAI_API_KEY"),
    base_url="https://api.avalai.ir/v1",
    temperature=0,
)


#Define the prompt that will use for model usage
prompt = ChatPromptTemplate.from_template(
    """
    این خبر ورزشی را به صورت کوتاه و دقیق خلاصه کن.
    فقط اطلاعات مهم خبر را نگه دار.

    خبر:
    {article_text}
    """
)


#Combine the prompt and model into a LangChain chain
summary_chain = prompt | model