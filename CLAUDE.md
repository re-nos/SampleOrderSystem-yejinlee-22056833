# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 현황

이 저장소는 아직 초기 단계로, 소스 코드가 작성되지 않은 상태입니다. `.venv`(Python 3.14.4)만 구성되어 있습니다.
코드가 추가되면 이 문서의 "아키텍처" 섹션을 실제 구조에 맞게 업데이트해야 합니다.

## 개발 환경

- Python 버전: 3.14.4 (`.venv`에 구성됨)
- 가상환경 활성화: `.venv\Scripts\activate` (PowerShell: `.venv\Scripts\Activate.ps1`)
- 의존성은 `requirements.txt` 또는 `pyproject.toml`이 추가되는 시점에 이 섹션에 설치/관리 명령을 명시할 것

## 테스트

- 테스트 프레임워크: pytest
- 테스트 전체 실행: `pytest`
- 단일 테스트 파일 실행: `pytest tests/test_파일명.py`
- 단일 테스트 함수 실행: `pytest tests/test_파일명.py::test_함수명`
- (`pytest`가 아직 의존성에 추가되지 않았다면 `pip install pytest` 후 사용)

## 린트/포맷

- 아직 도구가 정해지지 않음. 도구 선정 후 이 섹션에 실행 명령(예: `ruff check .`, `black .`)을 추가할 것

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

## 아키텍처

(코드가 추가되면 모듈 구성, 데이터 흐름, 주요 컴포넌트 간 관계 등 "여러 파일을 읽어야 파악 가능한" 큰 그림을 이 섹션에 기록할 것)
