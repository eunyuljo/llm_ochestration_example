# .env 파일을 읽어서 환경변수로 설정
from dotenv import load_dotenv
from langchain_teddynote import logging
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableParallel

# 토큰 정보로드
load_dotenv()
logging.langsmith("CH01-Basic")

llm = ChatOpenAI(temperature=0)

chain1 = (
    {"country": RunnablePassthrough()}
    | PromptTemplate.from_template("{country} 의 수도는?")
    | ChatOpenAI()
)
chain2 = (
    {"country": RunnablePassthrough()}
    | PromptTemplate.from_template("{country} 의 면적은?")
    | ChatOpenAI()
)

combined_chain = RunnableParallel(capital=chain1, area=chain2)
print(combined_chain.invoke("대한민국"))

