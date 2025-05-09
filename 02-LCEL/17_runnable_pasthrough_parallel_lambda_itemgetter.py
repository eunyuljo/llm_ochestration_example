# .env 파일을 읽어서 환경변수로 설정
from dotenv import load_dotenv
from langchain_teddynote import logging
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableParallel
from langchain_core.runnables import RunnableLambda

from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter


# 토큰 정보로드
load_dotenv()
logging.langsmith("CH01-Basic")
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

prompt = ChatPromptTemplate.from_template("{a} + {b} 는 무엇인가요?")

# 문장의 길이를 반환하는 함수입니다.
def length_function(text):
    return len(text)

# 두 문장의 길이를 곱한 값을 반환하는 함수입니다.
def _multiple_length_function(text1, text2):
    return len(text1) * len(text2)

# _multiple_length_function 함수를 사용하여 두 문장의 길이를 곱한 값을 반환하는 함수입니다.
def multiple_length_function(_dict):
    return _multiple_length_function(_dict["text1"], _dict["text2"])

chain1 = prompt | llm

chain = (
    {
        "a": itemgetter("word1") | RunnableLambda(length_function),
        "b": {"text1": itemgetter("word1"), "text2": itemgetter("word2")}
        | RunnableLambda(multiple_length_function),
    }
    | prompt
    | llm
)


print(chain.invoke({"word1": "hello", "word2": "world"}))
