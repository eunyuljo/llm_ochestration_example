from dotenv import load_dotenv
from langchain_teddynote import logging
from langchain_teddynote.messages import stream_response  # 스트리밍 출력
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# API KEY 정보로드
load_dotenv()

# # 프로젝트 이름을 입력합니다.
logging.langsmith("CH01-Basic")

model = ChatOpenAI(
    model="gpt-3.5-turbo",
    max_tokens=2048,
    temperature=0.1,
)

template = """
당신은 영어를 가르치는 10년차 영어 선생님입니다. 주어진 상황에 맞는 영어 회화를 작성해 주세요.
양식은 [FORMAT]을 참고하여 작성해 주세요.

#상황:
{question}

#FORMAT:
- 영어 회화:
- 한글 해석:
"""

# 프롬프트 템플릿을 이용하여 프롬프트를 생성합니다.
prompt = PromptTemplate.from_template(template)

# ChatOpenAI 챗모델을 초기화합니다.
model = ChatOpenAI(model_name="gpt-4-turbo")

# 문자열 출력 파서를 초기화합니다.
output_parser = StrOutputParser()

# 완성된 Chain을 실행하여 답변을 얻습니다.
answer = chain.stream({"question": "저는 식당에 가서 음식을 주문하고 싶어요"})

# 파이프라인
chain = prompt | model | output_parser

# 스트리밍 출력
stream_response(answer)
