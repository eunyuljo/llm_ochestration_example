# API KEY를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
from langchain_teddynote import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
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

async def process_stream():
    # 비동기 스트림을 사용하여 'YouTube' 토픽의 메시지를 처리합니다.
    async for token in chain.astream({"topic": "YouTube"}):
        # 메시지 내용을 출력합니다. 줄바꿈 없이 바로 출력하고 버퍼를 비웁니다.
        print(token, end="", flush=True)
    print()  # 마지막에 줄바꿈 추가

# 비동기 함수 실행
if __name__ == "__main__":
    asyncio.run(process_stream())