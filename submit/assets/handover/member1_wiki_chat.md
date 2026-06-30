# 팀원1 핸드오버 — 정보공유(위키) + 실시간 채팅 위젯

> **받는 법**: 팀 git 저장소를 `git clone`(또는 `git pull`) → **네 세션**에서 이 문서 + `00_plan/DEV_BLUEPRINT.md`를 첨부/붙여넣고 시작. 공통 규칙(디자인 토큰·노드 명명 등)은 DEV_BLUEPRINT가 단일 진실 공급원이다.

---

## 0. 네가 만들 것 (한 줄)
서버 환경·노하우를 모아 보는 **정보공유(위키)** 페이지와, 어느 페이지에서든 뜨는 **숨김/열기 토글 플로팅 채팅 위젯**.

## 1. 소유 파일 (★ 이것만 수정 — 공통 파일은 팀장 경유)
```
routers/wiki.py          # /api/wiki/*
routers/chat.py          # /api/chat/*
static/wiki.html         # 위키 화면 (기존 userA_part/wiki.html 재사용)
static/chat-widget.js    # ★ 자체 주입 플로팅 채팅 (CSS는 JS 안에서 <style> 주입)
```
> `main.py`·`db.py`·`common.css`·`_nav.html`은 **건드리지 말 것.** 라우터 2개 등록은 팀장이 `main.py`에 한 줄씩 해준다.

## 2. DB 테이블 (네 소유)
```sql
servers(id PK, name, os, spec, modules, ssh)
posts(id PK, title, author, body, created_at)
messages(id PK, sender, body, created_at)
```
- `servers`는 시드 3대: `gpu-cluster` / `cpu-cluster` / `fat-node`.
- 시간은 저장 ISO 문자열, 화면 표기 `"HH:MM"`.

## 3. API 엔드포인트 (네 소유)
```
GET  /api/wiki/servers              서버 환경 목록
GET  /api/wiki/posts?q=검색어        게시글 목록(검색, q 없으면 전체)
POST /api/wiki/posts                글 작성 {title, author, body}
GET  /api/chat/messages?after=id    id보다 큰 신규 메시지(폴링용). 없으면 전체
POST /api/chat/messages             메시지 전송 {sender, body}
```
- 각 API는 **다른 사람 코드 없이 `/docs`에서 단독 응답**해야 한다(통합 전제).

## 4. 화면·기능 요구사항

### 위키 (`wiki.html`)
1. **서버 환경 카드** — `GET /api/wiki/servers` 렌더(gpu/cpu/fat 3대, OS·스펙·모듈·ssh).
2. **사용법 가이드** — ssh → module/conda → sbatch 흐름 정적 안내.
3. **노하우 게시판** — 검색창(`?q=`) + 글쓰기 폼(`POST`). 작성 → 목록·검색 즉시 반영.

### 채팅 위젯 (`chat-widget.js`) ★ 핵심
- **자체 주입**: 이 스크립트 하나만 로드하면 스스로 **플로팅 버튼 + 채팅 패널 + 스타일(`<style>` 주입)**을 페이지에 붙인다. 다른 페이지 소유자는 `<script src="/static/chat-widget.js"></script>` **한 줄**만 추가하면 됨.
- **토글**: 평소 우하단 버튼만, 클릭 시 채팅창 열기/숨기기.
- **폴링**: 2~3초마다 `GET /api/chat/messages?after=<마지막id>`로 신규만 가져와 append. 내 메시지는 우측 말풍선.
- **전송**: 입력 → `POST /api/chat/messages {sender, body}`. `sender`는 최초 1회 이름 입력받아 보관(localStorage 등).
- **의존성 없게**: 외부 라이브러리 없이 바닐라 JS. `wiki.html`은 네가 직접 이 스크립트를 포함한다.

## 5. 통합 제약 (이것만 지키면 통합 OK)
- 채팅 위젯은 **완전 자기완결**이어야 한다 — 다른 페이지가 `<script>` 한 줄로 띄울 수 있게. 전역 변수 오염·CSS 충돌 최소화(클래스 prefix 예: `cw-`).
- **`index.html`에는 안 띄운다** — 팀장이 그 페이지에만 스크립트를 안 넣음(네가 신경 쓸 것 없음).
- 위키는 다른 페이지와 데이터 안 엮임 → 가장 독립적.

## 6. 완료 기준
- [ ] 글 작성 → DB 저장 → 목록·검색에 반영
- [ ] 서버 환경 3대가 화면에 카드로 표시
- [ ] `chat-widget.js` 한 줄 로드만으로 플로팅 채팅이 뜨고, 두 브라우저에서 메시지가 폴링으로 오감
- [ ] `/docs`에서 `/api/wiki/*`·`/api/chat/*` 단독 응답

## 7. 팀장에게 요청할 것
- `main.py`에 `wiki` · `chat` 라우터 2줄 등록.
- (공통) `common.css`·`_nav.html` 변경이 필요하면 요청.

## 8. 바로 붙여넣는 킥오프 프롬프트
```
나는 HPC 포털 팀원1, 정보공유(위키)와 실시간 채팅 담당이야. 첨부한 DEV_BLUEPRINT.md를 따른다.
내 소유 파일은 routers/wiki.py, routers/chat.py, static/wiki.html, static/chat-widget.js 뿐(공통 파일 X).
DEV_BLUEPRINT §4 servers/posts/messages 테이블, §6 /api/wiki/*·/api/chat/* 엔드포인트대로:
- 위키: 서버 환경 카드 + 사용법 가이드(ssh→module/conda→sbatch) + 검색되는 노하우 게시판 (userA_part/wiki.html 재사용)
- 채팅: 숨김/열기 토글되는 자체 주입 플로팅 위젯(chat-widget.js), 2~3초 after 폴링, 내 메시지 우측 말풍선.
  다른 페이지가 <script src="/static/chat-widget.js"></script> 한 줄로 띄울 수 있게, CSS는 JS에서 <style> 주입하고 클래스는 cw- prefix로.
디자인 토큰은 DEV_BLUEPRINT §5 준수. 각 API는 /docs에서 단독으로 응답하게.
```
