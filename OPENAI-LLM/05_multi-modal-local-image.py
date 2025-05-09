# API KEY를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
load_dotenv()

# 수정된 임포트 경로
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_teddynote import logging
from langchain_teddynote.models import MultiModal
from langchain_teddynote.messages import stream_response


# 객체 생성
llm = ChatOpenAI(
    temperature=0.1,  # 창의성 (0.0 ~ 2.0)
    max_tokens=2048,  # 최대 토큰수
    model_name="gpt-4o",  # 모델명
)

# 멀티모달 객체 생성
multimodal_llm = MultiModal(llm)

# 샘플 이미지 주소(웹사이트로 부터 바로 인식)
IMAGE_PATH_FROM_FILE = "./sample-image.png"

# 이미지 파일로 부터 질의
answer = multimodal_llm.stream(IMAGE_PATH_FROM_FILE)
# 스트리밍 방식으로 각 토큰을 출력합니다. (실시간 출력)
stream_response(answer)