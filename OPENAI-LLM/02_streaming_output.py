# API KEY를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
load_dotenv()

# 수정된 임포트 경로
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_teddynote import logging
from langchain_teddynote.messages import stream_response

# LangSmith 추적을 설정
logging.langsmith("CH01-Basic")

# 객체 생성
llm = ChatOpenAI(
    temperature=0.1,  # 창의성 (0.0 ~ 2.0)
    model_name="gpt-4o",  # 모델명
)

answer = llm.stream("대한민국의 아름다운 관광지 10곳과 주소를 알려주세요!")
final_answer = stream_response(answer, return_output=True)