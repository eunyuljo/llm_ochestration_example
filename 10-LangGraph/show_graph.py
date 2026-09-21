"""컴파일된 그래프를 Mermaid 로 보여 준다."""


def show(app, xray: bool = False) -> None:
    text = app.get_graph(xray=xray).draw_mermaid(with_styles=False)
    # xray 가 노드 이름을 lookup:fetch 로 만들면 Mermaid 가 깨진다.
    text = text.replace("\\3a", "_")
    print("\n[graph]")
    print(text)
