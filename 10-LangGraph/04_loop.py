"""04. 루프 — 같은 노드로 되돌아가며 state를 갱신한다.

START -> tick -> tick -> tick -> END
                (n < 3이면 다시 tick, n >= 3이면 끝)

분기(03)와 같은 add_conditional_edges 인데,
도착지가 "다른 노드"가 아니라 "방금 온 노드"다.
"""

from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END

from show_graph import show


class State(TypedDict, total=False):
    n: int


def tick(state: State) -> State:
    n = state.get("n", 0) + 1
    print(f"  [tick] n={n}")
    return {"n": n}


def should_stop(state: State) -> Literal["more", "stop"]:
    if state["n"] >= 3:
        return "stop"
    return "more"


graph = StateGraph(State)
graph.add_node("tick", tick)
graph.add_edge(START, "tick")
graph.add_conditional_edges(
    "tick",
    should_stop,
    {"more": "tick", "stop": END},  # more 면 자기 자신으로
)

app = graph.compile()


if __name__ == "__main__":
    show(app)
    result = app.invoke({"n": 0})
    print(f"\n최종 state: {result}")
