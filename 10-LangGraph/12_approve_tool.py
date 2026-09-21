"""12. 도구 실행 전 사람 승인 — 11 의 채팅 + 06 의 interrupt

agent 가 tool_calls 를 남기면 바로 lookup 하지 않고 approve 에서 멈춘다.
승인하면 lookup, 아니면 종료.
"""

from typing import Annotated, TypedDict, Literal

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

from show_graph import show


class State(TypedDict):
    messages: Annotated[list, add_messages]


def last_message(state: State):
    return state["messages"][-1]


def agent(state: State) -> State:
    last = last_message(state)
    print(f"  [agent] 마지막={type(last).__name__} {last.content!r}")

    if isinstance(last, ToolMessage):
        return {"messages": [AIMessage(content=f"서울 날씨: {last.content}")]}

    if "날씨" in last.content:
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


def approve(state: State) -> Command[Literal["lookup"]]:
    call = last_message(state).tool_calls[0]
    print("  [approve] interrupt 직전")
    answer = interrupt({"question": f"{call['name']}({call['args']}) 실행할까요?"})
    print(f"  [approve] 재개 답={answer!r}")
    if str(answer).lower() in ("y", "yes", "승인"):
        return Command(goto="lookup")
    return Command(
        goto=END,
        update={"messages": [AIMessage(content="조회를 취소했습니다.")]},
    )


def lookup(state: State) -> State:
    call = last_message(state).tool_calls[0]
    print(f"  [lookup] {call['args']}")
    return {"messages": [ToolMessage(content="맑음", tool_call_id=call["id"])]}


def route_after_agent(state: State) -> Literal["approve", "end"]:
    last = last_message(state)
    if isinstance(last, AIMessage) and last.tool_calls:
        return "approve"
    return "end"


graph = StateGraph(State)
graph.add_node("agent", agent)
graph.add_node("approve", approve)
graph.add_node("lookup", lookup)
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    route_after_agent,
    {"approve": "approve", "end": END},
)
graph.add_edge("lookup", "agent")
# approve -> lookup / END 는 Command 가 정한다.

app = graph.compile(checkpointer=InMemorySaver())


def show_messages(result):
    if "__interrupt__" in result:
        print(f"  (멈춤) {result['__interrupt__'][0].value}")
        return
    for m in result["messages"]:
        extra = ""
        if isinstance(m, AIMessage) and m.tool_calls:
            extra = f"  tool_calls={m.tool_calls[0]['name']}"
        print(f"  {m.type:10} {m.content!r}{extra}")


if __name__ == "__main__":
    show(app)

    print("=== 승인 ===")
    yes = {"configurable": {"thread_id": "yes-1"}}
    paused = app.invoke({"messages": [{"role": "user", "content": "오늘 날씨 어때?"}]}, yes)
    show_messages(paused)
    done = app.invoke(Command(resume="승인"), yes)
    show_messages(done)

    print("\n=== 거절 ===")
    no = {"configurable": {"thread_id": "no-1"}}
    paused = app.invoke({"messages": [{"role": "user", "content": "오늘 날씨 어때?"}]}, no)
    show_messages(paused)
    done = app.invoke(Command(resume="아니요"), no)
    show_messages(done)
