"""07. 에이전트 루프 — 판단 노드가 도구를 부를지, 끝낼지 고른다.

START -> agent -> lookup -> agent -> END
                └──────────────┘
                (날씨 도구가 필요하면)

나중에 agent 함수 안만 진짜 LLM 으로 바꾸면 챗봇이 된다.
지금은 if 문으로 "모델 흉내"만 낸다.
"""

from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END

from show_graph import show


class State(TypedDict, total=False):
    question: str
    city: str
    weather: str
    answer: str


def agent(state: State) -> State:
    print(f"  [agent] 지금 칠판: { {k: state[k] for k in state} }")

    # 날씨 질문인데 아직 조회 전이면 -> 도구
    if "날씨" in state["question"] and "weather" not in state:
        print("  [agent] 결정: lookup으로")
        return {}

    # 이미 조회했거나, 날씨 질문이 아니면 -> 답하고 끝
    if "weather" in state:
        answer = f"{state['city']} 날씨: {state['weather']}"
    else:
        answer = "날씨 질문이 아니라서 도구를 안 씁니다."
    print(f"  [agent] 결정: end ({answer})")
    return {"answer": answer}


def lookup(state: State) -> State:
    print("  [lookup] 가짜 날씨 API")
    return {"city": "서울", "weather": "맑음"}


def should_lookup(state: State) -> Literal["lookup", "end"]:
    if "answer" in state:
        return "end"
    return "lookup"


graph = StateGraph(State)
graph.add_node("agent", agent)
graph.add_node("lookup", lookup)
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_lookup,
    {"lookup": "lookup", "end": END},
)
graph.add_edge("lookup", "agent")  # 도구가 끝나면 다시 판단

app = graph.compile()


if __name__ == "__main__":
    show(app)

    print("=== 질문 1: 날씨 ===")
    print("최종:", app.invoke({"question": "오늘 날씨 어때?"}))

    print("\n=== 질문 2: 인사 ===")
    print("최종:", app.invoke({"question": "안녕"}))
