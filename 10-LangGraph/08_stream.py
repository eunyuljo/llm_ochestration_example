"""08. stream — invoke 대신 한 스텝씩 칠판을 본다.

새 그래프는 없다. 07 을 그대로 쓰면서
app.invoke (최종만) vs app.stream (중간중간) 만 비교한다.
"""

import importlib

mod = importlib.import_module("07_agent")
app = mod.app

from show_graph import show


if __name__ == "__main__":
    show(app)

    question = {"question": "오늘 날씨 어때?"}

    print("=== invoke: 끝까지 돈 뒤 한 번만 ===")
    print(app.invoke(question))

    print("\n=== stream: 칠판이 갱신될 때마다 ===")
    n = 0
    for state in app.stream(question, stream_mode="values"):
        n += 1
        print(f"  ({n}) {state}")
