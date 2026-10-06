import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


model = ChatOpenAI(
    model="gpt-6-luna",
    api_key=os.getenv("AVALAI_API_KEY"),
    base_url="https://api.avalai.ir/v1",
    temperature=0,
)


prompt = ChatPromptTemplate.from_template(
    """
    این خبر ورزشی را به صورت کوتاه و دقیق خلاصه کن.
    فقط اطلاعات مهم خبر را نگه دار.

    خبر:
    {article_text}
    """
)


summary_chain = prompt | model