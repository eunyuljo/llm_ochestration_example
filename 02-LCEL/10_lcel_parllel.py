# API KEY를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
from langchain_teddynote import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
import asyncio

# API KEY 정보로드
load_dotenv()
logging.langsmith("CH01-Basic")


# ChatOpenAI 모델을 인스턴스화합니다.
model = ChatOpenAI()
# 주어진 토픽에 대한 농담을 요청하는 프롬프트 템플릿을 생성합니다.
prompt = PromptTemplate.from_template("{topic} 에 대하여 3문장으로 설명해줘.")


# 체인
chain = prompt | model | StrOutputParser()

# {country} 의 수도를 물어보는 체인을 생성합니다.
chain1 = (
    PromptTemplate.from_template("{country} 의 수도는 어디야?")
    | model
    | StrOutputParser()
)

# {country} 의 면적을 물어보는 체인을 생성합니다.
chain2 = (
    PromptTemplate.from_template("{country} 의 면적은 얼마야?")
    | model
    | StrOutputParser()
)

# 위의 2개 체인을 동시에 생성하는 병렬 실행 체인을 생성합니다.
combined = RunnableParallel(capital=chain1, area=chain2)

# chain1 를 실행합니다.
print(chain1.invoke({"country": "대한민국"}))
# chain2 를 실행합니다.
print(chain2.invoke({"country": "미국"}))
