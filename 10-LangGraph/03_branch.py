"""03. 조건 분기 — 칠판을 보고 다음 노드를 고른다.

START -> greet -> (shout | whisper) -> END

greet 까지는 같고,
style 값에 따라 shout 또는 whisper 로 갈린다.
"""

from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END

from show_graph import show


class State(TypedDict, total=False):
    name: str
    style: str
    greeting: str
    spoken: str


def greet(state: State) -> State:
    print(f"  [greet]   style={state.get('style')!r}")
    return {"greeting": f"안녕, {state['name']}"}


def shout(state: State) -> State:
    print("  [shout]")
    return {"spoken": state["greeting"].upper() + "!"}


def whisper(state: State) -> State:
    print("  [whisper]")
    return {"spoken": f"...{state['greeting'].lower()}..."}


# 노드가 아니다. state를 고치지 않고, "다음에 갈 노드 이름"만 반환한다.
def pick_style(state: State) -> Literal["shout", "whisper"]:
    if state.get("style") == "quiet":
        return "whisper"
    return "shout"


graph = StateGraph(State)
graph.add_node("greet", greet)
graph.add_node("shout", shout)
graph.add_node("whisper", whisper)

graph.add_edge(START, "greet")
graph.add_conditional_edges("greet", pick_style)
#                         출발 노드,  길 고르는 함수
# pick_style 이 "shout"를 주면 shout 노드로,
# "whisper"를 주면 whisper 노드로 간다.
graph.add_edge("shout", END)
graph.add_edge("whisper", END)

app = graph.compile()


if __name__ == "__main__":
    show(app)

    print("=== style=loud ===")
    print("최종:", app.invoke({"name": "eyjo", "style": "loud"}))

    print("\n=== style=quiet ===")
    print("최종:", app.invoke({"name": "eyjo", "style": "quiet"}))
