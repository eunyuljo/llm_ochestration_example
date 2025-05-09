# 필요한 패키지 가져오기
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 환경변수 불러오기
load_dotenv()  # .env 파일의 변수들을 환경변수로 설정

# LangSmith 설정 (추적 기능)
os.environ["LANGCHAIN_TRACING_V2"] = "true"  # LangSmith 추적 활성화
os.environ["LANGCHAIN_PROJECT"] = "CH01-Basic"  # 프로젝트 이름 설정

# LangSmith 트레이서 설정
try:
    # 방법 1: LangSmith 콜백 핸들러 임포트 시도
    from langchain.callbacks.tracers import LangChainTracer
    tracer = LangChainTracer(project_name="CH01-Basic")
    print("LangSmith 추적이 활성화되었습니다.")
except ImportError:
    try:
        # 방법 2: langchain_core에서 임포트 시도
        from langchain_core.callbacks import LangSmithCallbackHandler
        tracer = LangSmithCallbackHandler(project_name="CH01-Basic")
        print("LangSmith 추적이 활성화되었습니다.")
    except ImportError:
        # 추적 실패 시 빈 콜백 리스트 사용
        tracer = None
        print("LangSmith 패키지를 찾을 수 없습니다. 추적 없이 진행합니다.")

# API 키 확인 메시지
if "OPENAI_API_KEY" not in os.environ:
    print("경고: OPENAI_API_KEY가 설정되지 않았습니다.")
if "LANGCHAIN_API_KEY" not in os.environ:
    print("경고: LANGCHAIN_API_KEY가 설정되지 않았습니다. LangSmith 추적이 작동하지 않을 수 있습니다.")

# 프롬프트 설정
system_prompt = """당신은 표(재무제표)를 해석하는 금융 AI 어시스턴트입니다. 
당신의 임무는 주어진 테이블 형식의 재무제표를 바탕으로 흥미로운 사실을 정리하여 친절하게 답변하는 것입니다."""

user_prompt = """당신에게 주어진 표는 회사의 재무제표입니다. 흥미로운 사실을 정리하여 답변하세요."""

# 이미지 URL
image_url = "https://storage.googleapis.com/static.fastcampus.co.kr/prod/uploads/202212/080345-661/kwon-01.png"

# 콜백 설정
callbacks = []
if tracer:
    callbacks.append(tracer)  # 추적 기능 추가

# AI 모델 설정
chat = ChatOpenAI(
    model="gpt-4o",     # 사용할 모델
    temperature=0.1,    # 창의성 조절 (0: 정확한 답변, 1: 다양한 답변)
    streaming=True,     # 답변을 스트리밍 방식으로 받기
    callbacks=callbacks  # LangSmith 추적 콜백 추가
)

# 메시지 구성
messages = [
    SystemMessage(content=system_prompt),  # 시스템 메시지 (AI의 역할 설정)
    HumanMessage(content=[                 # 사용자 메시지 (텍스트와 이미지)
        {"type": "text", "text": user_prompt},
        {"type": "image_url", "image_url": {"url": image_url}}
    ])
]

# 실행
print("\n=== 재무제표 분석 시작 ===\n")

# 모델에 메시지 전송하고 응답 받기
try:
    for chunk in chat.stream(messages):
        if chunk.content:
            print(chunk.content, end="", flush=True)  # 응답을 실시간으로 출력
    
    print("\n\n=== 분석 완료 ===")
    
    if tracer:
        print("LangSmith 추적이 완료되었습니다.")
        print("LangSmith 대시보드에서 결과를 확인할 수 있습니다: https://smith.langchain.com")
except Exception as e:
    print(f"\n오류 발생: {e}")
    print("LangSmith 추적 없이 다시 시도합니다...")
    
    # 추적 기능 없이 다시 시도
    chat_without_tracing = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        streaming=True
    )
    
    for chunk in chat_without_tracing.stream(messages):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    
    print("\n\n=== 분석 완료 (추적 없음) ===")