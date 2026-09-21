"""13. subgraph — 그래프를 노드처럼 넣는다.

안쪽 그래프: city 를 받아서 weather 를 채운다.
바깥 그래프: 질문을 보고 도시를 고른 뒤, 안쪽을 lookup 노드로 실행한다.

10 의 lookup 함수가 안쪽 그래프가 된 것과 같다.
큰 워크플로우를 파일/팀 단위로 나눌 때 쓴다.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from show_graph import show

class InnerState(TypedDict, total=False):
    city: str
    weather: str


def fetch(state: InnerState) -> InnerState:
    print(f"  [inner/fetch] city={state['city']}")
    return {"weather": "맑음"}


inner = StateGraph(InnerState)
inner.add_node("fetch", fetch)
inner.add_edge(START, "fetch")
inner.add_edge("fetch", END)
inner_app = inner.compile()


class OuterState(TypedDict, total=False):
    question: str
    city: str
    weather: str
    answer: str


def pick_city(state: OuterState) -> OuterState:
    print(f"  [outer/pick_city] {state['question']!r}")
    return {"city": "서울"}


def write_answer(state: OuterState) -> OuterState:
    print("  [outer/write_answer]")
    return {"answer": f"{state['city']} 날씨: {state['weather']}"}


outer = StateGraph(OuterState)
outer.add_node("pick_city", pick_city)
outer.add_node("lookup", inner_app)  # 함수 대신 컴파일된 그래프
outer.add_node("write_answer", write_answer)
outer.add_edge(START, "pick_city")
outer.add_edge("pick_city", "lookup")
outer.add_edge("lookup", "write_answer")
outer.add_edge("write_answer", END)

app = outer.compile()


if __name__ == "__main__":
    print("=== 바깥 + 안쪽을 한 장으로 (xray=True) ===")
    show(app, xray=True)

    print("최종:", app.invoke({"question": "오늘 날씨 어때?"}))
