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
- 생산 라인 시간 흐름: 콘솔 명령어 입력 단위의 턴(Turn) 기반 시뮬레이션 (실제 시간/비동기 처리 사용 안 함)

## 테스트

- 테스트 프레임워크: pytest
- 테스트 전체 실행: `pytest`
- 단일 테스트 파일 실행: `pytest tests/test_파일명.py`
- 단일 테스트 함수 실행: `pytest tests/test_파일명.py::test_함수명`
- (`pytest`가 아직 의존성에 추가되지 않았다면 `pip install pytest` 후 사용)

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

## PoC 참고 저장소

미션1에서 개발된 PoC 저장소로, 구조/유틸 재사용 시 참고합니다 (GitHub `re-nos` 조직).
- `ConsoleMVC-yejinlee-22056833`: MVC 스켈레톤 구조 참고
- `DataPersistence-yejinlee-22056833`: JSON 기반 CRUD 영속성 로직 참고
- `DataMonitor-yejinlee-22056833`: 모니터링 도구 구현 참고
- `DummyDataGenerator-yejinlee-22056833`: 더미 데이터 생성기 참고

## 아키텍처

MVC 패턴을 따르며, 책임 분리는 다음과 같습니다.
- **Model**: 시료(Sample), 주문(Order), 생산 라인(ProductionLine) 등 도메인 엔티티 + JSON 파일 기반 Repository(CRUD)
- **Controller**: 메뉴별 흐름 제어(시료 관리/주문/승인·거절/모니터링/생산 라인/출고) 및 상태 전이 로직(`RESERVED → REJECTED/PRODUCING/CONFIRMED → RELEASE`)
- **View**: 콘솔 입출력 전담, 비즈니스 로직 없음

세부 모듈 구성은 코드가 추가되는 대로 이 섹션에 갱신합니다.
