"""10. 메시지 에이전트 — 09 의 대화 목록 + 07 의 도구 루프

칠판은 messages 하나뿐.
agent 는 마지막 메시지를 보고
  - 도구가 필요하면 tool_calls 가 있는 AI 메시지를 남기고
  - 충분하면 일반 AI 메시지로 끝낸다.
lookup 은 ToolMessage 를 목록에 붙인다.
"""

from typing import Annotated, TypedDict, Literal

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from show_graph import show


class State(TypedDict):
    messages: Annotated[list, add_messages]


def last_message(state: State):
    return state["messages"][-1]


def agent(state: State) -> State:
    last = last_message(state)
    print(f"  [agent] 마지막={type(last).__name__} {getattr(last, 'content', '')!r}")

    # 도구가 방금 답을 가져왔다 -> 문장으로 마무리
    if isinstance(last, ToolMessage):
        return {"messages": [AIMessage(content=f"서울 날씨: {last.content}")]}

    # 사용자 말에 "날씨"가 있다 -> 도구 호출을 메시지에 기록
    text = last.content
    if "날씨" in text:
        return {"messages": [AIMessage(
            content="",
            tool_calls=[{
                "name": "lookup",
                "args": {"city": "서울"},
                "id": "call_1",
                "type": "tool_call",
            }],
        )]}

    return {"messages": [AIMessage(content="날씨 질문이 아니라서 도구를 안 씁니다.")]}


def lookup(state: State) -> State:
    call = last_message(state).tool_calls[0]
    print(f"  [lookup] {call['args']}")
    return {"messages": [ToolMessage(content="맑음", tool_call_id=call["id"])]}


def should_lookup(state: State) -> Literal["lookup", "end"]:
    last = last_message(state)
    if isinstance(last, AIMessage) and last.tool_calls:
        return "lookup"
    return "end"


graph = StateGraph(State)
graph.add_node("agent", agent)
graph.add_node("lookup", lookup)
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_lookup,
    {"lookup": "lookup", "end": END},
)
graph.add_edge("lookup", "agent")

app = graph.compile()


def show_messages(result):
    for m in result["messages"]:
        extra = ""
        if isinstance(m, AIMessage) and m.tool_calls:
            extra = f"  tool_calls={m.tool_calls[0]['name']}"
        print(f"  {m.type:10} {m.content!r}{extra}")


if __name__ == "__main__":
    show(app)

    print("=== 날씨 ===")
    show_messages(app.invoke({"messages": [{"role": "user", "content": "오늘 날씨 어때?"}]}))

    print("\n=== 인사 ===")
    show_messages(app.invoke({"messages": [{"role": "user", "content": "안녕"}]}))
