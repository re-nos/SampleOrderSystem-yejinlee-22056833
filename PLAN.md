# PLAN.md

Sample Order System (반도체 시료 생산주문관리 콘솔 시스템) 프로젝트 진행 계획입니다.
요구사항 원문은 `S_Semi_Project_PRD.md`를 참고합니다.

## 결정된 개발 방침

- **패키지 관리**: `pip` + `.venv` (`requirements.txt`)
- **데이터 영속성**: JSON 파일 기반
- **테스트 프레임워크**: `pytest`, TDD 방식으로 개발
- **생산 라인 시간 흐름**: 콘솔 명령어 입력 단위의 턴(Turn) 기반 시뮬레이션
- **아키텍처**: MVC (Model/View/Controller 책임 분리, 자세한 내용은 `CLAUDE.md` 참고)

## PoC 참고 저장소 (GitHub `re-nos` 조직, 미션1에서 개발 완료)

| 저장소 | 용도 |
|---|---|
| `ConsoleMVC-yejinlee-22056833` | MVC 스켈레톤 구조 |
| `DataPersistence-yejinlee-22056833` | JSON 기반 CRUD 영속성 |
| `DataMonitor-yejinlee-22056833` | 실시간 모니터링 도구 |
| `DummyDataGenerator-yejinlee-22056833` | 테스트용 더미 데이터 생성기 |

각 Phase에서 해당 PoC의 구조/코드를 참고하여 재사용 가능한 부분은 이식하고, 프로젝트 요구사항에 맞게 조정합니다.

## 진행 방식 (모든 단계 공통)

각 Phase는 아래 순서로 진행합니다.

1. **상세 계획 작성**: Phase 착수 전 해당 단계의 상세 구현 계획 문서를 `plans/phase{N}.md`에 작성한다 (대상 파일/클래스, 테스트 케이스 목록, 참고할 PoC 코드 등 포함)
2. **리뷰**: 사용자가 상세 계획을 검토하고 승인한다
3. **TDD 구현**: 실패하는 테스트 작성 → 최소 구현으로 통과 → 리팩터링을 반복하며 구현, 각 단계마다 커밋
4. **완료 보고**: Phase 완료 시 `reports/phase{N}.md`에 구현 항목/테스트 결과/계획 대비 차이/커밋 이력을 정리한다
5. **확인**: 테스트 통과 및 동작을 사용자가 확인한 뒤 다음 Phase로 진행

## Phase 0. 프로젝트 기반 구축

- PoC 4개 저장소 코드 리뷰, 재사용 가능한 구조/유틸 파악
- 프로젝트 디렉터리 구조 확정 (`model/`, `view/`, `controller/`, `tests/` 등)
- `requirements.txt` 정리 (pytest 등 개발 의존성 포함)
- JSON 영속성 스키마 설계 (시료/주문/생산 라인 데이터 파일 구조)
- 공통 로깅/예외 처리 모듈 설계 방향 확정
- `CLAUDE.md` 아키텍처 섹션을 확정된 구조로 갱신

## Phase 1. 시료 관리

- Sample 모델 정의 (ID, 이름, 평균 생산시간, 수율) + JSON Repository CRUD
- 시료 등록 / 목록 조회 / 이름 검색 Controller, View 구현
- TDD: 등록 정상 케이스, 중복 ID, 조회/검색 정상 및 결과 없음 케이스

## Phase 2. 시료 주문 접수

- Order 모델 정의 (상태: `RESERVED`/`REJECTED`/`PRODUCING`/`CONFIRMED`/`RELEASE`)
- 주문 접수 기능 (시료 ID, 고객명, 수량 입력) → `RESERVED` 상태로 저장
- TDD: 정상 접수, 존재하지 않는 시료 ID, 잘못된 수량(0 이하 등) 케이스

## Phase 3. 주문 승인/거절 및 생산 라인

- 승인 로직: 재고 충분 시 즉시 `CONFIRMED`, 부족 시 생산 라인 등록 후 `PRODUCING`
- 거절 로직: 즉시 `REJECTED`
- 생산 라인: 단일 라인, FIFO 큐
  - 실 생산량 = `ceil(부족분 / 수율)`
  - 총 생산 시간 = `평균 생산시간 * 실 생산량`
- 턴 기반 진행: 턴이 진행될 때마다 생산 큐 처리, 완료 시 해당 주문 `PRODUCING → CONFIRMED`
- TDD: 재고 정확히 일치/부족 경계값, 수율 반올림(ceil) 케이스, FIFO 순서 검증, 턴 진행에 따른 완료 처리 검증

## Phase 4. 모니터링

- 상태별 주문 건수 집계 (`RESERVED`/`CONFIRMED`/`PRODUCING`/`RELEASE`, `REJECTED`는 제외)
- 시료별 재고 현황(여유/부족/고갈 상태, 잔여율) 계산
- `DataMonitor` PoC의 조회 도구 패턴 참고
- TDD: 집계 정확성, 상태 분류 경계값 케이스

## Phase 5. 출고 처리

- `CONFIRMED` 상태 주문 선택 → `RELEASE` 전환
- TDD: 정상 출고, `CONFIRMED`가 아닌 주문에 대한 출고 시도 예외 케이스

## Phase 6. 통합 및 마무리

- 콘솔 메인 메뉴 진입점에 전체 기능(시료 관리/주문/승인·거절/모니터링/생산 라인/출고) 통합
- `DummyDataGenerator` PoC를 활용해 데모/테스트용 더미 데이터 생성 스크립트 통합
- 전체 `pytest` 실행 및 상태 흐름(`RESERVED → REJECTED/PRODUCING/CONFIRMED → RELEASE`) 통합 테스트로 정합성 검증
- `CLAUDE.md` 등 문서 최종 정리
- 커밋 이력/클린 코드 최종 점검

## Phase 완료 기준

- 해당 Phase 관련 `pytest` 테스트가 모두 통과할 것
- 사용자가 실제 콘솔 동작을 확인하고 승인할 것
