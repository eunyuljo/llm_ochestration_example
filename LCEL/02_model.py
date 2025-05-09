from dotenv import load_dotenv
from langchain_teddynote import logging
from langchain_teddynote.messages import stream_response  # 스트리밍 출력
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# API KEY 정보로드
load_dotenv()

# # 프로젝트 이름을 입력합니다.
logging.langsmith("CH01-Basic")

prompt = PromptTemplate.from_template("{topic} 에 대해 쉽게 설명해주세요.")

model = ChatOpenAI(
    model="gpt-3.5-turbo",
    max_tokens=2048,
    temperature=0.1,
)

chain = prompt | model

print(chain)