# LangGraph 기초

LangGraph는 LLM 라이브러리가 아니다. **하나의 상태(state)를 여러 함수가 돌아가며 갱신하는 흐름**을 그래프로 그리는 도구다.

평범한 파이썬 함수 호출과 뭐가 다른가:

| 그냥 파이썬 | LangGraph |
|---|---|
| `c(b(a(x)))` 로 직접 이어 붙임 | 도면(엣지)을 먼저 그리고 그래프가 호출함 |
| 중간에 멈추면 처음부터 다시 | 멈춘 지점의 상태를 저장했다가 재개 |
| 병렬은 직접 스레드/asyncio | 엣지만 갈라 놓으면 병렬 실행 |
| 흐름이 코드에 흩어짐 | 흐름이 한 곳에 도면으로 남음 |

그래서 "LLM이 도구를 부를지 말지 결정하고, 실패하면 재시도하고, 위험한 조치는 사람에게 묻는" 류의 워크플로우에 쓴다.

이 폴더는 **API 키 없이** 그 뼈대만 익히는 실습이다. 모델 호출은 없고, 판단은 `if`로 흉내 낸다. 그래프가 익숙해진 뒤 `agent` 함수 안만 실제 LLM으로 바꾸면 된다.

---

## 환경

Python 3.13. 패키지 버전은 `requirements.txt`에 고정되어 있다.

```bash
cd 10-LangGraph
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

**폴더를 옮겼다면 venv를 복사하지 말고 지우고 다시 만든다.** `.venv/bin/activate` 안에 만들 당시의 절대 경로가 박혀 있어서, 옮기면 활성화가 깨진다.

```bash
rm -rf .venv && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
```

각 파일은 실행하면 그래프를 Mermaid로 먼저 출력한다.

```bash
python 01_hello.py
```

---

## 핵심 개념 3가지

### 1. State — 공유 칠판

그래프 전체가 들고 다니는 dict 하나. 노드들은 이 칠판을 돌아가며 채운다.

```python
class State(TypedDict, total=False):
    name: str
    greeting: str
```

`TypedDict`라서 `state.name`이 아니라 `state["name"]`으로 읽는다.
`total=False`는 "키가 다 없어도 된다"는 뜻이다. 노드가 일부만 반환할 수 있게 해 준다.

### 2. Node — 칠판을 고치는 함수

인자는 항상 현재 state. 반환은 **전체가 아니라 바꿀 키만** 담은 dict.

```python
def greet(state: State) -> State:
    return {"greeting": f"안녕, {state['name']}"}   # name은 안 건드림
```

`{"greeting": ...}`만 돌려줘도 기존 `name`은 그대로 남는다. 그래프가 합쳐 준다.

### 3. Edge — 다음에 갈 곳

```python
graph.add_node("greet", greet)      # "이름"과 함수를 등록
graph.add_edge(START, "greet")      # 시작하면 greet로
graph.add_edge("greet", END)        # greet 끝나면 종료
app = graph.compile()               # 도면을 실행 가능한 객체로
app.invoke({"name": "eyjo"})        # 한 번 돌리기
```

`add_node`까지는 **도면만 그린 상태**다. 실제 실행은 `invoke`부터.

---

## 어떤 상황에 무엇을 쓰는가

문제를 만났을 때 찾아보는 표.

| 하고 싶은 것 | 쓰는 것 | 예제 |
|---|---|---|
| 순서대로 처리 | `add_edge` | `02` |
| 조건에 따라 다른 처리 | `add_conditional_edges` | `03` |
| 될 때까지 재시도 | 조건 분기의 목적지를 이전 노드로 | `04` |
| 여러 조사를 동시에 (개수 고정) | 엣지를 여러 개 | `05` |
| 여러 작업을 동시에 (개수 가변) | `Send` | `14` |
| 중간에 사람에게 묻기 | `interrupt` + checkpointer | `06`, `12` |
| 도구를 쓸지 모델이 판단 | 판단 노드 + 도구 노드 루프 | `07`, `10` |
| 진행 상황을 실시간으로 | `stream` | `08` |
| 대화를 이어 가기 | `add_messages` + `thread_id` | `09`, `11` |
| 프로세스 재시작 후에도 유지 | `SqliteSaver` | `15` |
| 복잡한 단계를 따로 떼기 | 그래프를 노드로 | `13` |

---

## 파일별 정리

번호 순서대로 실행한다. 각 항목은 **무엇을 배우는지 / 실무에서 언제 쓰는지 / 주의점** 순서다.

### 01_hello.py — 최소 그래프

`START → greet → END`. State, Node, Edge 세 가지만.

노드가 "바꿀 키만 반환한다"는 규칙을 여기서 확인한다. 나머지 전부가 이 규칙 위에 쌓인다.

### 02_pipeline.py — 선형 파이프라인

`greet`가 쓴 값을 `shout`가 읽는다.

```python
graph.add_edge("greet", "shout")   # END 대신 다음 노드로
```

**쓰는 곳**: 전처리 → 처리 → 후처리처럼 순서가 정해진 작업. 단계마다 칠판에 중간 결과가 남으니 어디서 틀어졌는지 추적하기 쉽다.

### 03_branch.py — 조건 분기

```python
def pick_style(state) -> Literal["shout", "whisper"]:
    return "whisper" if state.get("style") == "quiet" else "shout"

graph.add_conditional_edges("greet", pick_style)
```

`pick_style`은 **노드가 아니다.** 칠판을 고치지 않고 다음 노드 이름(문자열)만 반환한다.

**쓰는 곳**: 심각도에 따라 자동 조치 / 사람 호출을 가르는 경우, 입력 종류에 따라 다른 처리기로 보내는 경우.

**주의**: 반환 타입 힌트 `Literal[...]`을 써야 그래프가 목적지 후보를 알고 도면에 그린다.

### 04_loop.py — 루프

분기의 목적지를 **자기 자신**으로 준다.

```python
graph.add_conditional_edges("tick", should_stop, {"more": "tick", "stop": END})
```

**쓰는 곳**: 조치 → 검증 → 안 나으면 재시도. 리트라이 로직을 그래프에 드러내 놓는 방식.

**주의**: 정지 조건이 반드시 있어야 한다. 없으면 기본 재귀 한계(25)에서 `GraphRecursionError`로 죽는다. `attempts >= 3` 같은 상한을 칠판에 두는 게 안전하다.

### 05_reducer.py — 병렬과 reducer

`START`에서 `left`, `right`가 **같은 스텝에** 출발한다. 둘 다 `notes`에 쓴다.

```python
notes: Annotated[list[str], operator.add]
```

`Annotated`는 타입 옆에 규칙을 붙이는 문법이고, `operator.add`가 "리스트를 이어 붙여라"는 reducer다.

```bash
python 05_reducer.py broken   # reducer 없음 → InvalidUpdateError
python 05_reducer.py          # reducer 있음 → ['왼쪽', '오른쪽']
```

**쓰는 곳**: 메트릭·로그·배포 이력을 동시에 조회해 한 목록에 모으는 경우.

**주의**: 기본 규칙은 "한 스텝에 값 하나, 덮어쓰기"다. 순차 실행이면 나중 값이 이기지만, 동시 실행이면 뭘 택할지 몰라 에러가 난다. 순서는 실행 타이밍에 따라 달라질 수 있으니 순서에 의존하지 말 것.

`join`은 `notes`를 기다리는 게 아니라 **들어오는 엣지가 전부 끝나야** 시작한다(fan-in).

### 06_interrupt.py — 멈추고 재개

```python
answer = interrupt({"question": "진행할까요?"})
```

첫 `invoke`는 이 줄에서 반환된다. 결과에 `__interrupt__`가 들어 있다.

```python
app = graph.compile(checkpointer=InMemorySaver())
cfg = {"configurable": {"thread_id": "demo-1"}}

paused = app.invoke({"name": "eyjo"}, cfg)     # 멈춤
done   = app.invoke(Command(resume="yes"), cfg) # 재개
```

**쓰는 곳**: 승인 대기, 추가 정보 요청, 외부 웹훅 대기.

**주의**:
- `checkpointer`와 `thread_id`는 세트다. 하나라도 없으면 재개가 안 된다.
- 재개하면 그 노드를 **처음부터 다시 실행**한다. `interrupt()` 위에 있는 코드가 한 번 더 돈다. 그래서 `interrupt` 앞에 부작용(결제, 삭제)을 두면 안 된다.

### 07_agent.py — 에이전트 루프

`03`의 분기와 `04`의 루프를 합친 형태. 에이전트의 기본 골격이다.

```text
agent → (도구 필요?) → lookup → agent → END
```

`agent`는 칠판만 보고 결정한다. 도구가 필요하면 아직 답을 안 쓰고, 충분하면 답을 쓴다. 실제 분기는 `should_lookup`이 한다.

**쓰는 곳**: 모든 tool-calling 에이전트. 나중에 `agent` 안의 `if`만 LLM 호출로 바꾸면 그대로 동작한다.

### 08_stream.py — 중간 과정 보기

같은 그래프를 `invoke` 대신 `stream`으로 돌린다.

```python
for state in app.stream(question, stream_mode="values"):
    print(state)     # 칠판이 갱신될 때마다
```

- `values`: 매 스텝의 **칠판 전체**
- `updates`: 그 스텝에 **바뀐 부분만**

**쓰는 곳**: 채팅 UI의 진행 표시, 오래 걸리는 워크플로우의 로그, 디버깅.

### 09_chat.py — 대화 상태

챗봇은 칸 하나가 아니라 **메시지 목록**을 쌓는다.

```python
messages: Annotated[list, add_messages]
```

`add_messages`는 `05`의 `operator.add`와 같은 자리에 들어가는 reducer다. 차이는 메시지 id를 알아서 다뤄 준다는 점(같은 id면 교체).

`checkpointer` + 같은 `thread_id`로 `invoke`를 여러 번 하면 대화가 이어진다. `thread_id`가 다르면 별개 대화다.

**쓰는 곳**: 사용자별/세션별 대화. `thread_id`에 보통 세션 ID나 사용자 ID를 넣는다.

### 10_tool_chat.py — 메시지 기반 에이전트

`07`의 구조 + `09`의 메시지 목록. 실제 LangGraph 에이전트와 같은 모양이다.

칸 이름 대신 **메시지 종류**로 상태를 판단한다.

| 마지막 메시지 | 다음 행동 |
|---|---|
| `HumanMessage` + 도구 필요 | `tool_calls`가 있는 `AIMessage` 남김 |
| `ToolMessage` | 결과를 문장으로 정리해 종료 |
| `HumanMessage` + 도구 불필요 | 바로 답하고 종료 |

```python
def should_lookup(state):
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "lookup"
    return "end"
```

**쓰는 곳**: LLM을 붙일 때 그대로 쓰는 형태. 모델이 `tool_calls`를 채우면 도구로, 아니면 종료로 간다.

### 11_chat_memory.py — 여러 턴

`10`의 그래프에 checkpointer만 붙였다. 인사한 뒤 날씨를 물으면, 앞 대화가 남은 채로 그 턴에 도구가 끼어든다.

두 번째 `invoke`에는 새 메시지 하나만 넣는데, reducer가 기존 목록 뒤에 붙인다.

### 12_approve_tool.py — 도구 실행 전 승인

`10` + `06`. `agent`가 도구를 쓰겠다고 하면 바로 실행하지 않고 `approve`에서 멈춘다.

```python
def approve(state) -> Command[Literal["lookup"]]:
    answer = interrupt({"question": "lookup 실행할까요?"})
    if str(answer).lower() in ("y", "yes", "승인"):
        return Command(goto="lookup")
    return Command(goto=END, update={"messages": [AIMessage(content="취소했습니다.")]})
```

`Command`는 **이동과 상태 갱신을 한 번에** 한다. `add_conditional_edges`로도 같은 일을 할 수 있지만, 노드 안에서 결정할 때는 `Command`가 간결하다.

**쓰는 곳**: 배포 롤백, 리소스 삭제, 결제처럼 되돌리기 비싼 조치. 위험한 도구만 이 경로로 보내고 안전한 조회는 바로 실행하는 식으로 나눈다.

### 13_subgraph.py — 그래프 안의 그래프

컴파일된 그래프를 노드 자리에 그대로 넣는다.

```python
outer.add_node("lookup", inner_app)   # 함수 대신 그래프
```

칠판 키 이름이 같으면 값이 그대로 오간다(바깥이 쓴 `city`를 안쪽이 읽음).

**쓰는 곳**:
- 한 노드가 여러 단계로 커졌을 때 (조회 = 인증 → 캐시 → API → 파싱)
- 같은 조각을 여러 그래프에서 재사용할 때
- 팀/파일 단위로 나눠 각자 테스트할 때 (안쪽만 따로 `invoke` 가능)

**안 쓰는 게 나을 때**: 안쪽이 함수 하나면 그냥 함수로 둔다.

도면은 기본적으로 안쪽을 한 칸으로 그린다. 펼쳐 보려면:

```python
app.get_graph(xray=True).draw_mermaid()
```

### 14_send.py — 개수가 변하는 병렬

`05`는 노드를 미리 두 개 그렸다. 개수가 고정이다. `Send`는 실행 중에 정한다.

```python
def fanout(state):
    return [Send("lookup", {"city": c}) for c in state["cities"]]

graph.add_conditional_edges("plan", fanout, ["lookup"])
```

각 `lookup`은 칠판 전체가 아니라 `Send`에 담은 `{"city": ...}`만 받는다. 결과는 reducer로 다시 합친다.

**쓰는 곳**: 검색 결과 N건 요약, 서버 N대 점검, 파일 N개 처리처럼 **개수를 미리 모르는** 병렬 작업.

**주의**: 개수가 항상 2~3개로 고정이면 `05` 방식이 더 읽기 쉽다.

### 15_sqlite.py — 영속 저장

`InMemorySaver`는 프로세스가 죽으면 사라진다. 파일에 남기려면:

```python
with SqliteSaver.from_conn_string("checkpoints.db") as saver:
    app = graph.compile(checkpointer=saver)
    app.invoke(..., {"configurable": {"thread_id": "chat-1"}})
```

이 예제는 한 파일 안에서 `compile`을 두 번 한다. 프로그램이 껐다 켜진 상황을 흉내 낸 것이고, `thread_id`가 같으니 대화가 이어진다.

**쓰는 곳**: 로컬 개발, 단일 인스턴스 서비스. 실서비스 다중 인스턴스는 `PostgresSaver`를 쓴다. 역할은 같고 저장소만 다르다.

---

## 자주 만나는 에러

| 증상 | 원인 | 해결 |
|---|---|---|
| `InvalidUpdateError: can receive only one value per step` | 병렬 노드가 같은 키에 쓰는데 reducer 없음 | `Annotated[list, operator.add]` |
| `GraphRecursionError` | 루프에 정지 조건 없음 | 시도 횟수 상한을 칠판에 두기 |
| `interrupt`가 무시되거나 에러 | `checkpointer` 미설정 | `compile(checkpointer=...)` |
| 재개했는데 처음부터 다시 실행 | `thread_id`가 다름 | 같은 `config` 재사용 |
| 노드 반환이 반영 안 됨 | dict가 아니거나 키 오타 | State에 정의된 키인지 확인 |
| 폴더 옮긴 뒤 venv 활성화 실패 | `activate`의 절대 경로 | `.venv` 지우고 재생성 |

---

## 보조 파일

- `show_graph.py` — `compile()`된 그래프를 Mermaid로 출력. `show(app, xray=True)`면 subgraph까지 펼침
- `requirements.txt` — 직접 쓰는 패키지만 버전 고정

---

## 다음 단계

여기까지가 그래프 뼈대다. 그래프를 더 늘리기 전에 **`07` / `10`의 판단 `if`를 실제 LLM 호출로 바꾸는 것**이 다음이다. 그래프 구조는 손대지 않는다.

먼저 결정적으로 도는 골격을 만들고 나중에 LLM을 붙이는 순서를 지키면, 문제가 생겼을 때 "흐름 버그"와 "판단 품질" 중 어느 쪽인지 바로 구분된다. 반대로 하면 원인 분리가 안 된다.
