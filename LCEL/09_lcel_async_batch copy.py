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

async def process_batch():
    # 주어진 토픽에 대해 비동기적으로 일괄 처리를 수행합니다.
    results = await chain.abatch(
        [{"topic": "YouTube"}, {"topic": "Instagram"}, {"topic": "Facebook"}]
    )
    
    # 결과 출력
    for i, result in enumerate(results):
        print(f"\n[결과 {i+1}]")
        print(result)
        print("-" * 50)
    
    return results

# 비동기 함수 실행
if __name__ == "__main__":
    results = asyncio.run(process_batch())
    print("\n처리 완료!")