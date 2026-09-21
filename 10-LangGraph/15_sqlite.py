"""15. SqliteSaver — 프로세스가 끝나도 칠판이 남는다.

09 / 11 의 InMemorySaver 는 파이썬이 꺼지면 대화가 사라진다.
이번엔 같은 그래프를 SQLite 파일에 저장한다.

이 파일 안에서 compile 을 두 번 한다 = 프로그램이 죽었다가 다시 켜진 것과 같다.
thread_id 만 같으면 2번째 프로세스가 1번째 대화를 이어받는다.
"""

import importlib
from pathlib import Path

from langchain_core.messages import AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from show_graph import show

mod = importlib.import_module("10_tool_chat")
DB = Path(__file__).with_name("checkpoints.db")
CFG = {"configurable": {"thread_id": "chat-1"}}


def show_messages(label, result):
    print(f"\n{label}")
    for m in result["messages"]:
        extra = ""
        if isinstance(m, AIMessage) and m.tool_calls:
            extra = f"  tool_calls={m.tool_calls[0]['name']}"
        print(f"  {m.type:10} {m.content!r}{extra}")


if __name__ == "__main__":
    DB.unlink(missing_ok=True)

    # --- 1번째 프로세스 ---
    with SqliteSaver.from_conn_string(str(DB)) as saver:
        app = mod.graph.compile(checkpointer=saver)
        show(app)
        r1 = app.invoke({"messages": [{"role": "user", "content": "안녕"}]}, CFG)
        show_messages("1번째 프로세스: 안녕", r1)

    print(f"\n프로세스 종료. 파일만 남음: {DB.name} ({DB.stat().st_size} bytes)")

    # --- 2번째 프로세스 (새 compile, 같은 DB + 같은 thread_id) ---
    with SqliteSaver.from_conn_string(str(DB)) as saver:
        app = mod.graph.compile(checkpointer=saver)
        r2 = app.invoke(
            {"messages": [{"role": "user", "content": "오늘 날씨 어때?"}]},
            CFG,
        )
        show_messages("2번째 프로세스: 날씨", r2)
