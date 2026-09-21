"""06. interrupt — 그래프를 멈추고, 같은 칠판으로 재개한다.

START -> ask -> finish -> END

ask 안에서 interrupt() 를 만나면 invoke 가 거기서 반환된다.
다음에 Command(resume=...) 로 같은 thread 를 이어서 돌린다.

checkpointer 가 칠판을 저장하고,
thread_id 가 "어느 칠판인지" 가리킨다. 둘 다 있어야 재개된다.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

from show_graph import show


class State(TypedDict, total=False):
    name: str
    answer: str
    done: str


def ask(state: State) -> State:
    print("  [ask] interrupt 직전")
    answer = interrupt({"question": f"{state['name']}님, 진행할까요?"})
    # 첫 invoke: 여기서 멈춘다. 아래 줄은 실행되지 않음.
    # 재개 후: interrupt() 가 resume 값을 반환하고 여기서부터 이어짐.
    print(f"  [ask] 재개됨, 답={answer!r}")
    return {"answer": str(answer)}


def finish(state: State) -> State:
    print("  [finish]")
    return {"done": f"{state['name']} -> {state['answer']}"}


graph = StateGraph(State)
graph.add_node("ask", ask)
graph.add_node("finish", finish)
graph.add_edge(START, "ask")
graph.add_edge("ask", "finish")
graph.add_edge("finish", END)

# compile 에 checkpointer 를 넣어야 interrupt 가 동작한다.
app = graph.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    show(app)

    cfg = {"configurable": {"thread_id": "demo-1"}}

    print("=== 1번째 invoke: 멈추기 ===")
    paused = app.invoke({"name": "eyjo"}, cfg)
    print(f"멈췄나? {'__interrupt__' in paused}")
    print(f"질문: {paused['__interrupt__'][0].value}")
    print(f"아직 answer 없음: {paused}")

    print("\n=== 2번째 invoke: 재개 ===")
    done = app.invoke(Command(resume="yes"), cfg)
    print(f"최종 state: {done}")
