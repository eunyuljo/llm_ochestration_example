# LangGraph 기초

LangGraph는 LLM 라이브러리가 아니라 **상태를 들고 노드를 따라 흐르는 그래프**다.
이 폴더는 API 키 없이, 작은 예제를 순서대로 실행하며 뼈대를 익히기 위한 실습이다.

모델 호출은 아직 없다. `if`로 판단을 흉내 낸다. 그래프가 익숙해진 뒤 `agent` 함수만 LLM으로 바꾸면 된다.

## 환경

Python 3.13, 패키지 버전은 `requirements.txt`에 고정되어 있다.

```bash
cd 10-LangGraph
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

폴더를 옮겼으면 venv를 복사하지 말고 위처럼 다시 만든다. `activate`에 예전 절대 경로가 박혀 있다.

각 파일을 실행하면 그래프가 Mermaid로 먼저 출력된다.

```bash
python 01_hello.py
```

## 파일

번호 순서대로 실행한다.

| 파일 | 내용 |
|---|---|
| `01_hello.py` | State, 노드, `START → greet → END` |
| `02_pipeline.py` | 노드 두 개를 이어서 같은 칠판을 채움 |
| `03_branch.py` | `add_conditional_edges` — 입력에 따라 길 분기 |
| `04_loop.py` | 같은 노드로 되돌아가기. 정지 조건이 필요함 |
| `05_reducer.py` | 병렬 노드가 같은 키를 쓸 때 reducer |
| `06_interrupt.py` | 중간에 멈추고 `Command(resume=...)`로 재개 |
| `07_agent.py` | 판단 노드 + 도구 + 다시 판단 |
| `08_stream.py` | `invoke`(최종만) vs `stream`(중간 칠판) |
| `09_chat.py` | `messages` + `add_messages` + thread 기억 |
| `10_tool_chat.py` | 채팅 목록에 도구 호출이 붙는 에이전트 |
| `11_chat_memory.py` | 10 + 여러 턴이 같은 thread로 이어짐 |
| `12_approve_tool.py` | 도구 실행 전 사람 승인 |
| `13_subgraph.py` | 그래프를 노드처럼 넣기 |
| `14_send.py` | 실행 중에 같은 노드를 N번 병렬 복제 |
| `15_sqlite.py` | checkpointer를 파일(`checkpoints.db`)에 저장 |

보조 파일:

- `show_graph.py` — `compile()`된 그래프를 Mermaid로 출력
- `requirements.txt` — 의존성 버전

`05`는 의도적으로 한 번 깨진다.

```bash
python 05_reducer.py broken   # InvalidUpdateError
python 05_reducer.py          # reducer로 정상
```

`13`은 안쪽 그래프를 펼쳐 보려면 `get_graph(xray=True)`를 쓴다.

## 모델

노드는 칠판 전체가 아니라 **바꿀 키만** dict로 반환한다. 그래프가 기존 state에 합친다.

- 기본: 같은 키는 덮어쓰기
- 여러 노드가 한 스텝에 같은 키를 쓰면 reducer (`operator.add`, `add_messages`)
- 멈춤/재개와 대화 기억은 checkpointer + `thread_id`가 세트

```text
START → 노드 → (고정 엣지 | 조건 분기 | Send) → … → END
```

## 다음

여기까지가 그래프 뼈대다. 이어서 할 일은 `07` / `10`의 판단 `if`를 실제 LLM 호출로 바꾸는 것이다. 그래프 구조는 그대로 둔다.
