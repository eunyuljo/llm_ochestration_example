"""02. 선형 파이프라인 — 같은 state를 두 노드가 이어서 만진다.

START -> greet -> shout -> END

greet 가 greeting 을 쓰고,
shout 가 그걸 읽어서 loud 를 채운다.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from show_graph import show


class State(TypedDict, total=False):
    name: str
    greeting: str
    loud: str


def greet(state: State) -> State:
    print(f"  [greet] 받은 state: {state}")
    return {"greeting": f"안녕, {state['name']}"}


def shout(state: State) -> State:
    print(f"  [shout] 받은 state: {state}")
    # 앞 노드가 써 둔 greeting 을 읽는다.
    return {"loud": state["greeting"].upper() + "!"}


graph = StateGraph(State)
graph.add_node("greet", greet)
graph.add_node("shout", shout)
graph.add_edge(START, "greet")
graph.add_edge("greet", "shout")  # greet 다음이 END가 아니라 shout
graph.add_edge("shout", END)

app = graph.compile()


if __name__ == "__main__":
    show(app)
    result = app.invoke({"name": "eyjo"})
    print(f"\n최종 state: {result}")
