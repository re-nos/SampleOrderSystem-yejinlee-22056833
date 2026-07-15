# Phase 6. 통합 및 마무리 — 상세 계획

`PLAN.md`의 Phase 6 항목을 구체화한 문서입니다. 이 계획을 승인받은 뒤 구현을 시작합니다.

## 1. PoC 리뷰 요약

- `ConsoleMVC`의 `app.py`: 저장소/컨트롤러를 조립(composition root)하고 `MenuView.run()`을 호출하는 얇은 진입점. `CONSOLE_UI.md`에 정의된 메뉴 구조(시료 관리/시료 주문/승인·거절/모니터링/생산 라인/출고 처리/종료)는 PRD의 메인 메뉴와 정확히 일치 — 그대로 채택
- `DummyDataGenerator`의 `cli.py`: `--samples`/`--orders`/`--seed`/`--output-dir` 등 인자로 재현 가능한 더미 데이터를 생성. 다만 이 PoC는 별도 저장소(cross-repo 의존성)이므로 그대로 import하지 않고, **본 저장소 안에 동일한 접근 방식(시드 기반 랜덤 생성)을 재구현**하여 기존 Repository/모델과 스키마 불일치 위험을 없앰 (아래 3번 항목)

## 2. 설계 결정 사항 (확인 완료)

**턴 진행 트리거**: 메인 메뉴에서 어떤 명령을 선택하든(조회 포함) 해당 명령 처리가 끝나면 생산 라인이 자동으로 1턴 진행됩니다. PoC처럼 "진행 턴 수 입력"을 별도로 받지 않고, CLAUDE.md에 명시된 "콘솔 명령어 입력 단위의 턴 기반" 원칙을 그대로 구현합니다.

## 3. Phase 0~5 대비 변경 사항 / 추가 결정

- **더미 데이터 생성기**: `DummyDataGenerator` PoC를 cross-repo import하지 않고, 본 저장소의 `SampleRepository`/`OrderRepository`/`InventoryRepository`를 직접 사용하는 자체 생성 스크립트를 작성합니다. 범위를 단순화하여 시료 + 재고 + `RESERVED` 상태 주문만 생성하고(생산 큐/진행 중 주문 등 복잡한 상태 조합은 생성하지 않음), 생성 후에는 사용자가 콘솔에서 승인/생산/출고를 직접 진행하며 데모할 수 있도록 합니다.

## 4. 신규 파일

```
src/sample_order_system/
├── app.py                # (신규) composition root + 메인 메뉴 루프
├── dummy_data.py          # (신규) 시드 기반 더미 데이터 생성 (CLI 겸용)
tests/
├── test_app.py            # (신규) 메뉴 흐름 통합 테스트 (input/output 함수 주입)
└── test_dummy_data.py      # (신규)
```

## 5. 설계 상세

### `App` (`app.py`)
- `build_app(data_dir: str = "data") -> App`: 4개 Repository(`sample`/`order`/`inventory`/`production_queue`)와 6개 Controller를 조립
- `App.__init__(self, ..., input_func=input, output_func=print)`: 테스트에서 입출력을 주입할 수 있도록 콜러블로 분리 (Phase 1~5의 "순수 View 함수 + 입출력 분리" 원칙 유지)
- `run()`: 메인 메뉴 출력 → 입력 → `0`이면 종료, 아니면 해당 서브메뉴 처리 → **처리 후 `production_controller.advance_turns(1)` 자동 호출 및 결과 출력** → 반복
- 각 서브메뉴 핸들러(`_handle_sample`, `_handle_order`, `_handle_approval`, `_handle_monitoring`, `_handle_production`, `_handle_shipment`)는 필요한 입력을 받아 해당 Controller 호출 후 Phase 1~5에서 만든 `views/*_view.py`의 포맷 함수로 출력
- 모든 서브메뉴 처리는 `DomainError`를 잡아 `오류: {메시지}` 형태로 출력하고 앱이 종료되지 않도록 처리 (신규 예외 클래스 추가 없음, 기존 `common/exceptions.py` 재사용)
- 메인 메뉴 구성 (PRD/CONSOLE_UI.md와 동일):
  ```
  [1] 시료 관리 (등록/목록/이름검색)
  [2] 시료 주문
  [3] 주문 승인/거절
  [4] 모니터링 (상태별 건수/재고 현황)
  [5] 생산 라인 (현재 작업/대기열 조회)
  [6] 출고 처리
  [0] 종료
  ```

### `dummy_data.py`
- `generate(sample_count, order_count, seed, data_dir) -> None`: `random.Random(seed)`로 결정적 생성
  - 시료 `sample_count`개: `sample_id`(`S001`...), 임의 이름, `avg_production_time`(1.0~5.0 사이 실수), `yield_rate`(0.3~1.0 사이 실수)
  - 각 시료에 대응하는 `InventoryRecord` (임의 수량, 0~50)
  - 주문 `order_count`개: 임의 시료 참조, 임의 고객명, 임의 수량(1~20), 상태는 전부 `RESERVED`
  - 기존 `SampleRepository`/`InventoryRepository`/`OrderRepository`를 통해 저장 (스키마 자동 일치)
- CLI: `python -m sample_order_system.dummy_data --samples 10 --orders 30 --seed 42 --output-dir data`

## 6. TDD 테스트 케이스

**`test_app.py`** (입력 리스트를 순서대로 반환하는 fake `input_func`, 출력만 누적하는 fake `output_func` 사용)
- `0` 입력 시 즉시 종료
- 시료 등록 흐름: 메뉴 진입 → 등록 입력 → 등록 성공 메시지 출력 + 저장소 반영 확인
- 주문 접수 흐름: 등록된 시료에 주문 접수 → 성공 메시지
- 승인 흐름 → 재고 부족 시 생산 큐 등록 메시지
- 모니터링 조회 흐름 → 집계/재고 현황 출력
- 생산 라인 조회 흐름 → 현재 작업/대기열 출력
- 출고 처리 흐름 → 완료 메시지
- **명령 처리 후 자동 1턴 진행 검증**: 생산 큐에 항목이 있는 상태에서 임의 명령(예: 모니터링 조회) 1회 수행 후 `remaining_turns`가 1 감소했는지 확인
- 잘못된 시료 ID 등 도메인 예외 발생 시 앱이 종료되지 않고 `오류: ...` 메시지만 출력하는지 확인

**`test_dummy_data.py`**
- 동일한 `seed`로 두 번 생성 시 동일한 데이터가 생성되는지(재현성)
- `sample_count`/`order_count`만큼 정확히 생성되는지
- 생성된 주문의 `sample_id`가 모두 실제 생성된 시료 중 하나를 참조하는지
- 생성 후 각 Repository를 통해 정상 조회 가능한지 (스키마 일치 검증)

## 7. 완료 기준

- 위 테스트가 모두 통과
- 전체 `pytest` 통과 (Phase 0~5 회귀 포함)
- `python -m sample_order_system.app`을 실제로 실행하여 등록 → 주문 → 승인 → (필요 시 생산 진행) → 출고까지 한 사이클을 콘솔에서 직접 확인
- `reports/phase6.md` 작성 후 사용자 확인
