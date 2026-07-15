# Phase 0. 프로젝트 기반 구축 — 상세 계획

`PLAN.md`의 Phase 0 항목을 구체화한 문서입니다. 이 계획을 승인받은 뒤 구현을 시작합니다.

## 1. PoC 리뷰 요약

GitHub `re-nos` 조직의 4개 PoC를 리뷰한 결과, 아래와 같이 재사용/참고합니다.

| PoC | 참고할 점 |
|---|---|
| `ConsoleMVC` | `src/<pkg>/{models,controllers,views}` + `app.py` 조립부 구조를 그대로 채택 |
| `DataPersistence` | `Repository[T]` 추상 인터페이스 + `JsonRepository` 공통 구현 + 도메인별 `SampleRepository`/`OrderRepository` 특화 패턴, 저수준 `json_file_storage.py`(원자적 read/write) 채택 |
| `DataMonitor` | 상태별 건수 집계(REJECTED 제외) 및 재고 잔여율 기반 상태 판정(고갈/부족/여유) 로직 구조를 Phase 4에서 참고 |
| `DummyDataGenerator` | 도메인 모델 필드 구성(Sample/Order/InventoryRecord/ProductionQueueEntry)을 JSON 스키마 설계에 반영, Phase 6 통합 시 CLI 재사용 |

## 2. 디렉터리 구조 확정

```
sample_order_system/
├── src/
│   └── sample_order_system/
│       ├── models/          # Sample, Order, ProductionQueueEntry 등 dataclass 엔티티 + OrderStatus Enum
│       ├── storage/
│       │   └── json_file_storage.py   # 원자적 JSON read/write 저수준 계층
│       ├── repository/
│       │   ├── base.py      # Repository[T] 추상 클래스
│       │   ├── json_repository.py     # JsonRepository 공통 CRUD 구현
│       │   ├── sample_repository.py
│       │   └── order_repository.py
│       ├── controllers/     # 유스케이스별 컨트롤러 (Phase 1부터 순차 추가)
│       ├── views/           # 콘솔 입출력, 메뉴 라우팅
│       ├── common/
│       │   ├── exceptions.py   # 도메인 예외 계층
│       │   └── logging_config.py
│       └── app.py           # 조립부(composition root), 메인 진입점
├── data/                     # 런타임 JSON 데이터 파일 (git 추적 제외, .gitignore에 추가)
├── tests/
│   └── (src 구조를 미러링: tests/models, tests/repository, ...)
├── plans/                    # 단계별 상세 계획 문서 (본 문서 포함)
├── requirements.txt
├── PLAN.md
└── CLAUDE.md
```

- `data/`는 런타임 산출물이므로 `.gitignore`에 추가 (테스트는 `tmp_path` 임시 디렉터리 사용, `data/`에 직접 쓰지 않음)
- 패키지 설치 없이 `src/` 레이아웃으로 두고, 테스트 실행 시 `PYTHONPATH=src` 또는 `pytest.ini`의 `pythonpath` 설정으로 임포트 (별도 `pyproject.toml` 패키징은 도입하지 않음 — pip+venv 방침과 일치)

## 3. JSON 영속성 스키마

각 엔티티는 `data/<entity>.json`에 리스트 형태로 저장합니다 (`DummyDataGenerator`의 필드 구성을 기준으로 확정).

**`sample.json`**
```json
[{"sample_id": "S001", "name": "시료A", "avg_production_time": 3, "yield_rate": 0.8}]
```

**`order.json`**
```json
[{"order_id": "O001", "sample_id": "S001", "customer_name": "고객A", "quantity": 10,
  "status": "RESERVED", "created_at": "2026-07-15T10:00:00"}]
```

**`inventory.json`** (시료별 현재 재고 수량)
```json
[{"sample_id": "S001", "quantity": 5}]
```

**`production_queue.json`** (FIFO 생산 큐, `PRODUCING` 주문에 대응)
```json
[{"order_id": "O001", "sample_id": "S001", "actual_production_qty": 7,
  "total_production_turns": 21, "remaining_turns": 15}]
```
- `actual_production_qty = ceil(부족분 / 수율)`, `total_production_turns = 평균생산시간 * 실생산량`
- `remaining_turns`는 턴 진행 시 감소, 0이 되면 완료 처리(`PRODUCING → CONFIRMED`, `inventory` 갱신)

## 4. 공통 모듈 설계

- `common/exceptions.py`: `DomainError`(base) → `NotFoundError`, `ValidationError`, `InvalidStateTransitionError`
  - Repository/Controller 전 계층에서 이 예외들만 사용하고, 상위(View)에서 사용자 메시지로 변환
- `common/logging_config.py`: `setup_logging()` 하나로 표준 `logging` 모듈 구성 (콘솔 핸들러, 레벨은 환경변수 또는 기본 INFO). 각 모듈은 `logging.getLogger(__name__)`만 사용

## 5. 의존성 (`requirements.txt`)

```
pytest
pytest-cov
```
JSON 처리는 표준 라이브러리(`json`, `dataclasses`)만 사용하므로 런타임 의존성은 없음.

## 6. 테스트 계획 (TDD)

Phase 0 자체는 기능이 아닌 기반 구조이므로, 아래 항목에 대해 먼저 테스트를 작성합니다.

- `storage/json_file_storage.py`: 존재하지 않는 파일 read 시 빈 리스트 반환, write 후 read 왕복(round-trip) 검증, 쓰기 도중 예외 발생해도 원본 파일 손상되지 않음(원자적 쓰기)
- `repository/json_repository.py`: `add`/`get`/`list`/`update`/`delete` 기본 CRUD, 존재하지 않는 ID 조회 시 `NotFoundError`
- `common/exceptions.py`: 예외 계층 구조(`isinstance`) 검증

## 7. CLAUDE.md 반영 사항

구현 완료 후 "아키텍처" 섹션을 위 디렉터리 구조 확정본으로 갱신합니다 (현재는 개략적 MVC 설명만 있음).

## 8. 완료 기준

- 위 디렉터리 구조가 생성되고 `storage`/`repository`/`common` 모듈에 대한 pytest 테스트가 모두 통과
- `pytest` 실행 명령이 `CLAUDE.md`에 명시된 대로 정상 동작
- 사용자가 구조와 스키마를 확인 후 승인
