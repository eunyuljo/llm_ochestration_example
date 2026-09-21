"""14. Send — 실행 중에 같은 노드를 N 번 복제한다.

05 는 left / right 를 도면에 미리 그렸다. 개수가 고정이다.
이번엔 cities 리스트 길이만큼 lookup 을 동시에 돌린다.

도면에는 lookup 이 하나다. Send 가 런타임에 도장을 여러 장 찍는다.
각 lookup 은 전체 칠판이 아니라 {city: ...} 만 받는다.
notes 는 05 와 같이 reducer 로 합친다.
"""

from typing import Annotated, TypedDict
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from show_graph import show


class State(TypedDict, total=False):
    cities: list[str]
    notes: Annotated[list[str], operator.add]


def plan(state: State) -> State:
    print(f"  [plan] cities={state['cities']}")
    return {}


def fanout(state: State):
    # 노드가 아니다. lookup 을 몇 번, 어떤 입력으로 돌릴지 목록으로 반환한다.
    return [Send("lookup", {"city": c}) for c in state["cities"]]


def lookup(state: State) -> State:
    print(f"  [lookup] 받은 것: {state}")
    return {"notes": [f"{state['city']} 맑음"]}


def join(state: State) -> State:
    print(f"  [join] notes={state.get('notes')}")
    return {}


graph = StateGraph(State)
graph.add_node("plan", plan)
graph.add_node("lookup", lookup)
graph.add_node("join", join)
graph.add_edge(START, "plan")
graph.add_conditional_edges("plan", fanout, ["lookup"])
graph.add_edge("lookup", "join")
graph.add_edge("join", END)

app = graph.compile()


if __name__ == "__main__":
    show(app)

    print("=== 도시 2개 ===")
    print("최종:", app.invoke({"cities": ["서울", "부산"], "notes": []}))

    print("\n=== 도시 1개 ===")
    print("최종:", app.invoke({"cities": ["대전"], "notes": []}))
