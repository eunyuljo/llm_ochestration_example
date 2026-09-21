"""01. LangGraph 최소 단위

LangGraph는 LLM이 아니라 "상태 기계를 그래프로 그리는 라이브러리"다.

필요한 것은 세 가지뿐:
  1. State  — 그래프가 들고 다니는 dict
  2. Node   — state를 받아서 "바꿀 부분만" dict로 반환하는 함수
  3. Edge   — 다음에 어느 노드로 갈지

이 파일은 START -> greet -> END 한 줄짜리 그래프.
LLM, 분기, 루프는 아직 없다.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from show_graph import show


# ---- 1. State -----------------------------------------------------------
# 그래프 전체가 공유하는 데이터 모양.
# total=False : 노드가 일부 키만 반환해도 되게 한다.
class State(TypedDict, total=False):
    name: str
    greeting: str


# ---- 2. Node ------------------------------------------------------------
# 인자는 항상 현재 state.
# 반환값은 "전체 state"가 아니라 "이번에 갱신할 키"만.
def greet(state: State) -> State:
    print(f"  [greet] 받은 state: {state}")
    return {"greeting": f"안녕, {state['name']}"}


# ---- 3. Graph -----------------------------------------------------------
graph = StateGraph(State)
graph.add_node("greet", greet)
graph.add_edge(START, "greet")   # 시작점 -> greet
graph.add_edge("greet", END)     # greet -> 끝

# compile() 해야 실행 가능한 객체가 된다.
app = graph.compile()


# ---- 4. 실행 ------------------------------------------------------------
if __name__ == "__main__":
    show(app)
    result = app.invoke({"name": "eyjo"})
    print(f"\n최종 state: {result}")
    print(f"greeting  = {result['greeting']}")
