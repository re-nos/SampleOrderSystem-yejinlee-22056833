# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 현황

반도체 시료 생산주문관리 콘솔 시스템(Sample Order System)을 개발하는 저장소입니다.
요구사항은 `S_Semi_Project_PRD.md`(상위 디렉터리)를 참고하고, 단계별 진행 계획은 `PLAN.md`를 참고합니다.
단계(Phase)별로 상세 계획 문서 작성 → 사용자 리뷰 → TDD 구현 → 사용자 확인 순으로 진행합니다. 자세한 절차는 `PLAN.md`의 "진행 방식" 섹션을 따릅니다.

## 개발 환경

- Python 버전: 3.14.4 (`.venv`에 구성됨)
- 가상환경 활성화: `.venv\Scripts\activate` (PowerShell: `.venv\Scripts\Activate.ps1`)
- 패키지 관리: `pip` + `requirements.txt` (의존성 추가 시 `pip freeze > requirements.txt`로 갱신)
- 데이터 영속성: JSON 파일 기반 (DB 미사용). 엔티티별 JSON 저장소 스키마는 Phase 0 상세 계획 문서에서 확정
- 생산 라인 시간 흐름: 콘솔 명령어 입력 단위의 턴(Turn) 기반 시뮬레이션 (실제 시간/비동기 처리 사용 안 함) — 메인 메뉴에서 어떤 명령을 처리하든 완료 후 자동으로 1턴 진행
- 앱 실행: `python -m sample_order_system.app` (기본 데이터 디렉터리 `data/`)
- 더미 데이터 생성: `python -m sample_order_system.dummy_data --samples 10 --orders 30 --seed 42 --output-dir data`

## 테스트

- 테스트 프레임워크: pytest (`requirements.txt`에 포함, `pip install -r requirements.txt`로 설치)
- 테스트 전체 실행: `pytest`
- 단일 테스트 파일 실행: `pytest tests/경로/test_파일명.py`
- 단일 테스트 함수 실행: `pytest tests/경로/test_파일명.py::test_함수명`
- `pytest.ini`에서 `pythonpath = src`를 설정하여 `src/sample_order_system` 패키지를 별도 설치 없이 임포트

## 커밋 컨벤션

[Conventional Commits](https://www.conventionalcommits.org/) 형식을 따르되, 설명은 한글로 작성합니다.

```
<type>: <설명>
```

**type 종류**
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 변경 (README, CLAUDE.md 등)
- `refactor`: 동작 변경 없는 코드 구조 개선
- `test`: 테스트 코드 추가/수정
- `chore`: 의존성 업데이트, 설정 변경 등 기타 작업

**예시**
```
feat: 샘플 주문 조회 API 추가
fix: 재고 수량 계산 오류 수정
docs: README 사용법 갱신
refactor: 주문 서비스 로직 분리
test: 주문 생성 테스트 추가
chore: 의존성 버전 업데이트
```

**작성 규칙**
- 제목은 명령형으로 간결하게 작성 (예: "~추가", "~수정")
- 하나의 커밋은 하나의 논리적 변경 단위만 포함
- 본문이 필요한 경우 제목 아래 빈 줄을 두고 "왜" 변경했는지를 설명 (무엇을 변경했는지는 diff로 확인 가능하므로 생략)

## 개발 프로세스 (TDD & Agentic Engineering)

- 모든 기능 구현은 TDD로 진행: 실패하는 테스트 작성 → 최소 구현으로 통과 → 리팩터링
- 각 Phase 시작 전 상세 계획 문서를 작성하고 사용자 리뷰를 받은 뒤에만 구현을 시작할 것
- 구현 완료 후 테스트 통과 여부를 확인하고, 사용자 확인을 받은 뒤 다음 Phase로 진행할 것
- 공통 로깅/예외 처리는 기능별로 산개시키지 않고 공용 모듈(`common`/`utils` 등)로 분리하여 재사용할 것 (구체적 위치는 Phase 0에서 확정)
- Phase 단위 작업은 완료 시 `reports/phase{N}.md`(각각 새 파일)로 기록하고, Phase 외 애드혹 변경 요청은 완료 후 `reports/changes.md` 한 파일에 항목을 append하는 방식으로 기록할 것

## PoC 참고 저장소

미션1에서 개발된 PoC 저장소로, 구조/유틸 재사용 시 참고합니다 (GitHub `re-nos` 조직).
- `ConsoleMVC-yejinlee-22056833`: MVC 스켈레톤 구조 참고
- `DataPersistence-yejinlee-22056833`: JSON 기반 CRUD 영속성 로직 참고
- `DataMonitor-yejinlee-22056833`: 모니터링 도구 구현 참고
- `DummyDataGenerator-yejinlee-22056833`: 더미 데이터 생성기 참고

## 아키텍처

MVC 패턴을 따르며, 소스는 `src/sample_order_system/` 아래에 위치합니다 (테스트 시 `pytest.ini`의 `pythonpath = src`로 임포트).

```
src/sample_order_system/
├── models/       # Sample/SampleSummary, Order(+OrderStatus), InventoryRecord,
│                 # ProductionQueueEntry, StockStatus dataclass 엔티티/DTO
├── storage/      # json_file_storage.py — 원자적(atomic) JSON read/write 저수준 계층
├── repository/   # Repository[T] 추상 인터페이스 + JsonRepository 공통 CRUD
│                 # + Sample/Order/Inventory/ProductionQueue Repository
├── controllers/  # Sample/Order/Approval/Production/Monitoring/Shipment Controller
├── views/        # 각 도메인별 순수 포맷팅 함수(sample_view/order_view/approval_view/
│                 # production_view/monitoring_view/shipment_view) — input() 없음
├── common/       # exceptions.py(DomainError 계층), logging_config.py
├── dummy_data.py # 시드 기반 더미 데이터 생성기 (CLI: `python -m sample_order_system.dummy_data`)
└── app.py        # 조립부(composition root) + 콘솔 메인 메뉴 루프, 실행: `python -m sample_order_system.app`
```

- **Model**: 도메인 엔티티(dataclass) + `JsonRepository`를 통한 CRUD. Repository는 순수 CRUD만 담당하며 비즈니스 로직(상태 전이, 생산량 계산 등)은 Controller가 담당
- **Controller**: 메뉴별 흐름 제어(시료 관리/주문/승인·거절/모니터링/생산 라인/출고) 및 상태 전이 로직(`RESERVED → REJECTED/PRODUCING/CONFIRMED → RELEASE`)
- **View**: 콘솔 입출력 전담, 비즈니스 로직 없음 (실제 `input()`/`print()`는 `App`이 담당하고, `views/*`는 순수 포맷팅 함수만 제공)
- **`App`(`app.py`)**: 메인 메뉴 루프. `input_func`/`output_func`를 주입 가능하게 설계해 콘솔 없이 테스트 가능(`tests/test_app.py`). 어떤 명령을 처리하든 완료 후 `ProductionController.advance_turns(1)`을 자동 호출해 생산 라인을 1턴 진행시킴 (CLAUDE.md에 정의된 턴 기반 시뮬레이션 원칙)
- **공통 예외**: 모든 계층은 `common/exceptions.py`의 `DomainError` 하위 클래스(`NotFoundError`/`ValidationError`/`InvalidStateTransitionError`)만 사용하고, `App`이 이를 잡아 `오류: ...` 메시지로 출력
- 런타임 JSON 데이터 파일은 `data/`에 저장되며 git 추적 대상이 아님 (`.gitignore` 처리, 테스트는 `tmp_path` 임시 디렉터리 사용)

세부 모듈 구성은 코드가 추가되는 대로 이 섹션에 갱신합니다.
