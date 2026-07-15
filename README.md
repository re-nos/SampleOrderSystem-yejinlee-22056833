# Sample Order System

반도체 시료 생산주문관리 콘솔 시스템입니다. 가상의 반도체 회사 "S-Semi"가 다양한 반도체 시료를 생산하여 고객(연구소, 팹리스, 대학 등)에게 납품하는 과정을, 콘솔 기반 애플리케이션으로 관리합니다.

담당자가 시료를 등록하고, 고객 주문을 접수하고, 재고 상황에 따라 승인·거절 및 생산 라인 등록을 처리하고, 생산이 완료되면 출고까지 진행하는 전체 흐름을 하나의 콘솔 메뉴에서 다룹니다.

## 주요 기능

메인 메뉴에서 아래 6가지 기능을 제공합니다.

| 메뉴 | 기능 |
|---|---|
| [1] 시료 관리 | 시료 등록(ID/이름/평균 생산시간/수율), 목록 조회, 이름 검색 |
| [2] 시료 주문 | 시료ID/고객명/수량을 입력해 주문 접수 (입력 내용 확인 후 `RESERVED` 상태로 예약) |
| [3] 주문 승인/거절 | 대기 중인 예약 목록에서 번호로 선택 → 재고/부족분 확인 → 승인(재고 충분 시 즉시 `CONFIRMED`, 부족 시 생산 라인 등록 후 `PRODUCING`) 또는 거절(`REJECTED`) |
| [4] 모니터링 | 상태별 주문 건수(`RESERVED`/`CONFIRMED`/`PRODUCING`/`RELEASE`) 및 시료별 재고 현황(여유/부족/고갈, 잔여율) 조회 |
| [5] 생산라인 조회 | 현재 처리 중인 작업(진행률, 완료 예정 시각)과 FIFO 대기 목록 조회 |
| [6] 출고 처리 | `CONFIRMED` 상태 주문을 번호로 선택해 출고(`RELEASE`) 처리 |

메인 메뉴에서 명령을 하나 처리할 때마다 생산 라인이 자동으로 1턴 진행됩니다(콘솔 명령어 입력 단위의 턴 기반 시뮬레이션 — 실제 시계와 무관하게 결정적으로 동작).

화면 레이아웃 예시는 [`UI_Console_Examples.md`](UI_Console_Examples.md)를 참고하세요.

## 기술 스택

- **언어**: Python 3.14
- **패키지 관리**: `pip` + `requirements.txt`
- **데이터 영속성**: JSON 파일 (DB 미사용) — 시료/주문/재고/생산 큐를 각각 별도 JSON으로 저장
- **테스트**: pytest, TDD 방식으로 개발
- **아키텍처**: MVC (Model/Controller/View 책임 분리)

## 실행 방법

### 1. 가상환경 설정 및 의존성 설치

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 앱 실행

```powershell
python -m sample_order_system.app
```

기본적으로 `data/` 디렉터리에 JSON 파일을 생성해 데이터를 저장합니다. 처음 실행하면 등록된 시료/주문이 없는 빈 상태로 시작합니다.

### 3. 더미 데이터로 미리 체험해보기

시료/재고/주문이 채워진 상태로 바로 살펴보고 싶다면 실행 전에 더미 데이터를 생성하세요.

```powershell
python -m sample_order_system.dummy_data --samples 10 --orders 30 --seed 42 --output-dir data
python -m sample_order_system.app
```

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--samples` | 생성할 시료 개수 | 10 |
| `--orders` | 생성할 주문 개수(모두 `RESERVED` 상태) | 30 |
| `--seed` | 재현 가능한 결과를 위한 랜덤 시드 | 없음(매번 다름) |
| `--output-dir` | 생성된 JSON을 저장할 디렉터리 | `data` |

### 4. 테스트 실행

```powershell
pytest
```

- 단일 파일: `pytest tests/경로/test_파일명.py`
- 단일 함수: `pytest tests/경로/test_파일명.py::test_함수명`
- `pytest.ini`에 `pythonpath = src`가 설정되어 있어 별도 설치 없이 `src/sample_order_system` 패키지를 임포트합니다.

## 프로젝트 구조

```
src/sample_order_system/
├── models/       # Sample, Order(+OrderStatus), InventoryRecord, ProductionQueueEntry 등 엔티티/DTO
├── storage/      # json_file_storage.py — 원자적(atomic) JSON read/write
├── repository/   # JsonRepository 공통 CRUD + 도메인별 Repository
├── controllers/  # Sample/Order/Approval/Production/Monitoring/Shipment Controller
├── views/        # 도메인별 순수 포맷팅 함수 (input() 없음) + 색상/정렬 유틸
├── common/       # 공통 예외(DomainError 계층), 로깅 설정
├── dummy_data.py # 더미 데이터 생성기
└── app.py        # 조립부(composition root) + 콘솔 메인 메뉴 루프

tests/            # src 구조를 미러링하는 pytest 테스트 (TDD)
```

## 문서

이 프로젝트는 Agentic Engineering(Claude Code)을 활용해 개발되었으며, 관련 문서는 다음과 같습니다.

- [`CLAUDE.md`](CLAUDE.md) — 개발 환경, 커밋 컨벤션, 아키텍처, 개발 프로세스 등 Claude Code를 위한 가이드
- [`PLAN.md`](PLAN.md) — 전체 진행 계획 (Phase 0~6 단계별 개요)
- [`plans/`](plans) — Phase별 상세 구현 계획 문서
- [`reports/`](reports) — Phase별 완료 보고서(`phase{N}.md`) 및 애드혹 변경 이력(`changes.md`)
- [`UI_Console_Examples.md`](UI_Console_Examples.md) — 콘솔 화면 UI 예시

## 개발 방식

TDD(실패하는 테스트 작성 → 최소 구현 → 리팩터링)와 단계별 계획-리뷰-구현-확인 프로세스로 진행되었습니다. 자세한 절차는 `CLAUDE.md`의 "개발 프로세스" 섹션을 참고하세요.
