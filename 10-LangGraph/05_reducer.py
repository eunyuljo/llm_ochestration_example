"""05. reducer — 같은 키를 동시에 쓸 때 "어떻게 합칠지"

START -> (left, right) -> join -> END

left 와 right 가 둘 다 notes 에 쓴다.
  기본: 덮어쓰기 -> 한 스텝에 값이 둘이라 에러
  reducer: operator.add -> 리스트를 이어 붙임

    python 05_reducer.py broken
    python 05_reducer.py
"""

import sys
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, START, END

from show_graph import show

MODE = sys.argv[1] if len(sys.argv) > 1 else "fixed"


if MODE == "broken":
    class State(TypedDict, total=False):
        notes: list[str]
else:
    class State(TypedDict, total=False):
        notes: Annotated[list[str], operator.add]


def left(state: State) -> State:
    print("  [left]")
    return {"notes": ["왼쪽"]}


def right(state: State) -> State:
    print("  [right]")
    return {"notes": ["오른쪽"]}


def join(state: State) -> State:
    print(f"  [join] notes={state.get('notes')}")
    return {}


graph = StateGraph(State)
graph.add_node("left", left)
graph.add_node("right", right)
graph.add_node("join", join)

graph.add_edge(START, "left")
graph.add_edge(START, "right")   # START 에서 둘 다 출발 = 같은 스텝에서 병렬
graph.add_edge("left", "join")
graph.add_edge("right", "join")  # 둘 다 끝나야 join
graph.add_edge("join", END)

app = graph.compile()


if __name__ == "__main__":
    show(app)
    print(f"MODE={MODE}")
    try:
        result = app.invoke({"notes": []})
        print(f"최종 state: {result}")
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
