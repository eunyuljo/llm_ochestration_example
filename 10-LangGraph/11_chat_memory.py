"""11. 이어지는 채팅 — 10 그래프 + 09 의 thread 기억

invoke 를 여러 번 해도 같은 thread_id 면 messages 가 이어진다.
인사 다음에 날씨를 물으면, 그 턴에서 lookup 이 붙는다.
"""

import importlib

from langgraph.checkpoint.memory import InMemorySaver

from show_graph import show
from langchain_core.messages import AIMessage

mod = importlib.import_module("10_tool_chat")
app = mod.graph.compile(checkpointer=InMemorySaver())


def show_messages(label, result):
    print(f"\n{label}")
    for m in result["messages"]:
        extra = ""
        if isinstance(m, AIMessage) and m.tool_calls:
            extra = f"  tool_calls={m.tool_calls[0]['name']}"
        print(f"  {m.type:10} {m.content!r}{extra}")


if __name__ == "__main__":
    show(app)
    cfg = {"configurable": {"thread_id": "chat-1"}}

    r1 = app.invoke({"messages": [{"role": "user", "content": "안녕"}]}, cfg)
    show_messages("1턴: 안녕", r1)

    r2 = app.invoke({"messages": [{"role": "user", "content": "오늘 날씨 어때?"}]}, cfg)
    show_messages("2턴: 날씨 (같은 thread)", r2)
