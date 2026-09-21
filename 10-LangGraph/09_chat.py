"""09. 대화 칠판 — messages 리스트 + checkpointer

07 까지는 question / answer 칸이 하나씩이었다.
챗봇은 보통 칸이 아니라 "메시지 목록" 을 쌓는다.

add_messages 는 05 의 operator.add 와 같은 reducer 다.
리스트에 새 메시지를 이어 붙인다. (같은 id 면 수정)

checkpointer + thread_id 가 있으면
invoke 를 여러 번 해도 같은 대화가 이어진다.
"""

from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from show_graph import show


class State(TypedDict):
    messages: Annotated[list, add_messages]


def echo(state: State) -> State:
    last = state["messages"][-1]
    text = last.content
    print(f"  [echo] 마지막 말: {text!r}  (지금까지 {len(state['messages'])}개)")
    return {"messages": [{"role": "assistant", "content": f"메아리: {text}"}]}


graph = StateGraph(State)
graph.add_node("echo", echo)
graph.add_edge(START, "echo")
graph.add_edge("echo", END)

app = graph.compile(checkpointer=InMemorySaver())


def show_messages(label, result):
    print(f"\n{label}")
    for m in result["messages"]:
        print(f"  {m.type:10} {m.content}")


if __name__ == "__main__":
    show(app)
    cfg = {"configurable": {"thread_id": "chat-1"}}

    r1 = app.invoke({"messages": [{"role": "user", "content": "안녕"}]}, cfg)
    show_messages("1번째 턴", r1)

    r2 = app.invoke({"messages": [{"role": "user", "content": "난 eyjo"}]}, cfg)
    show_messages("2번째 턴 (같은 thread)", r2)

    other = app.invoke(
        {"messages": [{"role": "user", "content": "처음이야"}]},
        {"configurable": {"thread_id": "chat-2"}},
    )
    show_messages("다른 thread", other)
