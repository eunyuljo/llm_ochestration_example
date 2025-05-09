# .env 파일을 읽어서 환경변수로 설정
from dotenv import load_dotenv
from langchain_teddynote import logging
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableParallel
from langchain_core.runnables import RunnableLambda
from datetime import datetime


# 토큰 정보로드
load_dotenv()
logging.langsmith("CH01-Basic")
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

prompt = PromptTemplate.from_template(
    "{today} 가 생일인 유명인 {n} 명을 나열하세요. 생년월일을 표기해 주세요."
)

def get_today(a):
    # 오늘 날짜를 가져오기
    return datetime.today().strftime("%b-%d")


# chain 을 생성합니다.
chain = (
    {"today": RunnableLambda(get_today), "n": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print(chain.invoke(3))