# .env 파일을 읽어서 환경변수로 설정
from dotenv import load_dotenv
from langchain_teddynote import logging
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough

# 토큰 정보로드
load_dotenv()
logging.langsmith("CH01-Basic")


# prompt 와 llm 을 생성합니다.
prompt = PromptTemplate.from_template("{num} 의 10배는?")
llm = ChatOpenAI(temperature=0)

# runnable
runnable_chain = {"num": RunnablePassthrough()} | prompt | llm

print(runnable_chain.invoke(10))