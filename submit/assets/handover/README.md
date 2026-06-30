# 핸드오버 묶음 — 각자 자기 파트로 시작하기

이 폴더는 **git으로 팀원에게 공유**하기 위한 개인별 착수 문서다. 각자 저장소를 받고(`git clone`/`git pull`), **자기 세션**에서 아래 자기 문서 + `../DEV_BLUEPRINT.md`를 첨부해 시작한다.

| 받는 사람 | 문서 | 담당 |
|---|---|---|
| 팀원1 | `member1_wiki_chat.md` | 정보공유(위키) + 실시간 채팅 위젯 |
| 팀원2 | `member2_stats_system.md` | 사용량 통계 + 시스템 상태 |
| (팀장) | `../DEV_BLUEPRINT.md` | index + monitoring + 공통 뼈대·통합 |

## 단일 진실 공급원
공통 규칙(파일 구조 §3, DB §4, 디자인 토큰 §5, API §6, **노드 명명 `node01~08`**)은 모두 `../DEV_BLUEPRINT.md`에 있다. 개인 문서와 충돌하면 DEV_BLUEPRINT가 우선.

## 팀장 통합 체크(공통 파일은 팀장만)
- [ ] `main.py`에 라우터 5개 등록: monitoring / wiki / chat / stats / system
- [ ] `_nav.html` 5링크: 홈 / 모니터링 / 정보공유 / 사용량 통계 / 시스템 상태
- [ ] **`index.html`에는 채팅 위젯 스크립트를 넣지 않는다** (나머지 4페이지에만)
- [ ] 노드 키 정합: monitoring·system·stats·node_usage 전부 `node01~08`
- [ ] 서버 1개로 5페이지 네비 이동 + node_usage 등록→모니터링 반영 스모크 테스트

## git 공유 팁
- 팀원은 자기 소유 파일만 커밋 → 충돌 거의 없음(파일 분리 설계).
- 공통 파일(`main.py`·`db.py`·`common.css`·`_nav.html`) 변경은 팀장에게 요청해 팀장이 커밋.
