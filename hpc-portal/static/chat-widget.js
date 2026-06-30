/*
 * chat-widget.js — 자체 주입 플로팅 채팅 위젯 (팀원1 소유)
 *
 * 사용법: 어떤 페이지든 아래 한 줄만 추가하면 우하단에 채팅 버튼이 뜬다.
 *   <script src="/static/chat-widget.js"></script>
 *
 * 특징(통합 안전):
 *  - 외부 라이브러리 0개(바닐라 JS). 스타일은 이 파일에서 <style>로 주입.
 *  - 전역 오염 최소화: 모든 클래스 cw- prefix, IIFE로 캡슐화.
 *  - 2~3초 폴링: GET /api/chat/messages?after=<마지막id> 로 신규만 append (T7 초기 50건).
 *  - 전송: POST /api/chat/messages {sender, body}. sender는 최초 1회 입력받아 localStorage 보관.
 *  - 점유 선언 보드: GET/POST /api/chat/reservations, POST .../{id}/release.
 *  - 메시지 검색: GET /api/chat/messages?q=키워드.
 *  - index.html 에는 이 스크립트를 넣지 않는다(FR-C4, 팀장 담당).
 */
(function () {
  "use strict";
  if (window.__cwLoaded) return;       // 중복 주입 방지
  window.__cwLoaded = true;

  var POLL_MS = 2500;                   // 폴링 주기(2~3초)
  var API = "/api/chat/messages";
  var lastId = 0;
  var pollTimer = null;
  var open = false;

  // ---------- 1) 스타일 주입 ----------
  var css = ""
    + ".cw-btn{position:fixed;right:22px;bottom:22px;width:58px;height:58px;border-radius:50%;"
    + "background:#1d4ed8;color:#fff;border:none;cursor:pointer;box-shadow:0 6px 18px rgba(15,23,42,.28);"
    + "font-size:26px;z-index:9998;transition:.15s;display:flex;align-items:center;justify-content:center;}"
    + ".cw-btn:hover{filter:brightness(1.08);transform:translateY(-1px);}"
    + ".cw-badge{position:absolute;top:-3px;right:-3px;min-width:18px;height:18px;padding:0 5px;border-radius:9px;"
    + "background:#b91c1c;color:#fff;font-size:11px;font-weight:700;display:none;align-items:center;justify-content:center;}"
    + ".cw-panel{position:fixed;right:22px;bottom:92px;width:340px;max-width:calc(100vw - 36px);height:460px;max-height:calc(100vh - 130px);"
    + "background:#fff;border:1px solid #d8dee9;border-radius:16px;box-shadow:0 14px 40px rgba(15,23,42,.26);"
    + "z-index:9999;display:none;flex-direction:column;overflow:hidden;font-family:'Malgun Gothic','Apple SD Gothic Neo',Arial,sans-serif;}"
    + ".cw-panel.cw-show{display:flex;}"
    + ".cw-head{background:#0f172a;color:#fff;padding:12px 14px;display:flex;align-items:center;justify-content:space-between;}"
    + ".cw-head b{font-size:14px;}"
    + ".cw-head .cw-who{font-size:11px;color:#cbd5e1;margin-left:6px;cursor:pointer;text-decoration:underline;}"
    + ".cw-x{background:none;border:none;color:#cbd5e1;font-size:20px;cursor:pointer;line-height:1;}"
    + ".cw-x:hover{color:#fff;}"
    + ".cw-body{flex:1;overflow-y:auto;padding:12px;background:#f4f6fb;}"
    + ".cw-row{display:flex;margin-bottom:9px;}"
    + ".cw-row.cw-me{justify-content:flex-end;}"
    + ".cw-bub{max-width:78%;padding:7px 11px;border-radius:12px;font-size:13px;line-height:1.45;word-break:break-word;"
    + "background:#fff;border:1px solid #e2e8f0;color:#172033;}"
    + ".cw-row.cw-me .cw-bub{background:#1d4ed8;color:#fff;border-color:#1d4ed8;}"
    + ".cw-name{font-size:11px;color:#64748b;margin:0 0 2px 2px;}"
    + ".cw-time{font-size:10px;color:#94a3b8;margin-top:3px;text-align:right;}"
    + ".cw-row.cw-me .cw-time{color:#bfdbfe;}"
    + ".cw-foot{display:flex;gap:6px;padding:9px;border-top:1px solid #e2e8f0;background:#fff;}"
    + ".cw-foot input{flex:1;border:1px solid #d8dee9;border-radius:9px;padding:9px 11px;font-size:13px;outline:none;}"
    + ".cw-foot input:focus{border-color:#1d4ed8;}"
    + ".cw-send{border:none;background:#1d4ed8;color:#fff;border-radius:9px;padding:0 14px;font-size:13px;font-weight:600;cursor:pointer;}"
    + ".cw-send:hover{filter:brightness(.95);}"
    // --- 헤더 검색 토글 ---
    + ".cw-head-acts{display:flex;align-items:center;gap:8px;}"
    + ".cw-ico{background:none;border:none;color:#cbd5e1;font-size:16px;cursor:pointer;line-height:1;padding:0;}"
    + ".cw-ico:hover{color:#fff;}"
    + ".cw-search{display:none;padding:8px 10px;border-bottom:1px solid #e2e8f0;background:#fff;}"
    + ".cw-search.cw-show{display:block;}"
    + ".cw-search input{width:100%;box-sizing:border-box;border:1px solid #d8dee9;border-radius:9px;padding:7px 10px;font-size:13px;outline:none;}"
    + ".cw-search input:focus{border-color:#1d4ed8;}"
    // --- 점유 선언 핀 섹션 ---
    + ".cw-pin{border-bottom:1px solid #e2e8f0;background:#f8fafc;padding:7px 10px;}"
    + ".cw-pin-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:5px;}"
    + ".cw-pin-top b{font-size:11px;color:#0f172a;letter-spacing:.3px;}"
    + ".cw-pin-add{border:1px solid #1d4ed8;background:#fff;color:#1d4ed8;border-radius:7px;padding:2px 8px;font-size:11px;font-weight:600;cursor:pointer;}"
    + ".cw-pin-add:hover{background:#1d4ed8;color:#fff;}"
    + ".cw-pin-list{display:flex;flex-direction:column;gap:4px;}"
    + ".cw-pin-item{display:flex;align-items:center;justify-content:space-between;gap:6px;font-size:11.5px;color:#172033;background:#fff;border:1px solid #e2e8f0;border-radius:7px;padding:4px 7px;}"
    + ".cw-pin-item .cw-pin-txt{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}"
    + ".cw-pin-item .cw-pin-txt b{color:#1d4ed8;}"
    + ".cw-pin-empty{font-size:11px;color:#64748b;padding:2px 0;}"
    + ".cw-pin-rel{flex:none;border:none;background:#e2e8f0;color:#64748b;border-radius:6px;padding:2px 7px;font-size:10.5px;cursor:pointer;}"
    + ".cw-pin-rel:hover{background:#b91c1c;color:#fff;}"
    + ".cw-pin-form{display:none;flex-direction:column;gap:4px;margin-top:5px;}"
    + ".cw-pin-form.cw-show{display:flex;}"
    + ".cw-pin-form input{border:1px solid #d8dee9;border-radius:7px;padding:5px 8px;font-size:12px;outline:none;}"
    + ".cw-pin-form input:focus{border-color:#1d4ed8;}"
    + ".cw-pin-form .cw-pin-submit{border:none;background:#1d4ed8;color:#fff;border-radius:7px;padding:5px;font-size:12px;font-weight:600;cursor:pointer;}";
  var styleEl = document.createElement("style");
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ---------- 2) DOM 생성 ----------
  var btn = document.createElement("button");
  btn.className = "cw-btn";
  btn.setAttribute("aria-label", "채팅 열기");
  btn.innerHTML = "💬<span class='cw-badge' id='cwBadge'>0</span>";

  var panel = document.createElement("div");
  panel.className = "cw-panel";
  panel.innerHTML = ""
    + "<div class='cw-head'><div><b>HPC 채팅</b><span class='cw-who' id='cwWho'></span></div>"
    + "<div class='cw-head-acts'>"
    + "<button class='cw-ico' id='cwSearchBtn' aria-label='검색' title='메시지 검색'>🔍</button>"
    + "<button class='cw-x' id='cwClose' aria-label='닫기'>×</button></div></div>"
    + "<div class='cw-search' id='cwSearch'><input id='cwSearchInput' type='text' placeholder='메시지 검색…' autocomplete='off' /></div>"
    + "<div class='cw-pin' id='cwPin'>"
    + "<div class='cw-pin-top'><b>📌 지금 점유 중</b>"
    + "<button class='cw-pin-add' id='cwPinAdd'>＋ 점유 선언</button></div>"
    + "<div class='cw-pin-list' id='cwPinList'></div>"
    + "<div class='cw-pin-form' id='cwPinForm'>"
    + "<input id='cwPinNode' type='text' placeholder='노드 (예: node04)' autocomplete='off' />"
    + "<input id='cwPinUntil' type='text' placeholder='언제까지 (예: ~18:00)' autocomplete='off' />"
    + "<input id='cwPinPurpose' type='text' placeholder='용도 (예: ResNet 학습)' autocomplete='off' />"
    + "<button class='cw-pin-submit' id='cwPinSubmit'>선언 등록</button></div></div>"
    + "<div class='cw-body' id='cwBody'></div>"
    + "<div class='cw-foot'><input id='cwInput' type='text' placeholder='메시지 입력…' autocomplete='off' />"
    + "<button class='cw-send' id='cwSend'>전송</button></div>";

  document.body.appendChild(btn);
  document.body.appendChild(panel);

  var bodyEl = panel.querySelector("#cwBody");
  var inputEl = panel.querySelector("#cwInput");
  var badgeEl = btn.querySelector("#cwBadge");
  var whoEl = panel.querySelector("#cwWho");
  var unread = 0;

  var RES_API = "/api/chat/reservations";
  var RES_POLL_MS = 5000;
  var resTimer = null;
  var searchMode = false;          // 검색 모드: 폴링이 본문을 덮어쓰지 않게 보호

  // ---------- 3) 사용자 이름 ----------
  function getSender() { return localStorage.getItem("cw_sender") || ""; }
  function askSender(force) {
    var cur = getSender();
    if (cur && !force) return cur;
    var name = window.prompt("채팅에서 사용할 이름을 입력하세요", cur || "");
    if (name && name.trim()) {
      localStorage.setItem("cw_sender", name.trim());
      renderWho();
      return name.trim();
    }
    return cur;
  }
  function renderWho() {
    var s = getSender();
    whoEl.textContent = s ? "(" + s + ")" : "(이름 설정)";
  }
  whoEl.addEventListener("click", function () { askSender(true); });

  // ---------- 4) 렌더 ----------
  function hhmm(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return "";
    return ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
  }
  function appendMsg(m) {
    var me = getSender() && m.sender === getSender();
    var row = document.createElement("div");
    row.className = "cw-row" + (me ? " cw-me" : "");
    var nameHtml = me ? "" : "<div class='cw-name'></div>";
    row.innerHTML = nameHtml + "<div><div class='cw-bub'></div><div class='cw-time'></div></div>";
    if (!me) row.querySelector(".cw-name").textContent = m.sender;
    row.querySelector(".cw-bub").textContent = m.body;
    row.querySelector(".cw-time").textContent = hhmm(m.created_at);
    bodyEl.appendChild(row);
  }
  function scrollBottom() { bodyEl.scrollTop = bodyEl.scrollHeight; }

  // ---------- 5) 폴링 ----------
  function poll() {
    if (searchMode) return;   // 검색 중에는 폴링이 본문을 덮어쓰지 않음
    fetch(API + "?after=" + lastId)
      .then(function (r) { return r.json(); })
      .then(function (list) {
        if (searchMode) return;
        if (!Array.isArray(list) || list.length === 0) return;
        var nearBottom = bodyEl.scrollHeight - bodyEl.scrollTop - bodyEl.clientHeight < 60;
        list.forEach(function (m) {
          appendMsg(m);
          lastId = Math.max(lastId, m.id);
          if (!open && getSender() && m.sender !== getSender()) unread++;
        });
        if (open || nearBottom) scrollBottom();
        if (unread > 0) { badgeEl.textContent = unread; badgeEl.style.display = "flex"; }
      })
      .catch(function () { /* 네트워크 일시 오류는 다음 폴링에서 복구 */ });
  }
  function startPolling() {
    if (pollTimer) return;
    poll();
    pollTimer = setInterval(poll, POLL_MS);
  }

  // ---------- 6) 전송 ----------
  function send() {
    var text = inputEl.value.trim();
    if (!text) return;
    var sender = askSender(false);
    if (!sender) return;
    inputEl.value = "";
    fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sender: sender, body: text }),
    })
      .then(function (r) { return r.json(); })
      .then(function () { poll(); })   // 전송 직후 즉시 갱신
      .catch(function () { inputEl.value = text; });
  }
  panel.querySelector("#cwSend").addEventListener("click", send);
  inputEl.addEventListener("keydown", function (e) { if (e.key === "Enter") send(); });

  // ---------- 6.5) 점유 선언 보드 ----------
  var pinListEl = panel.querySelector("#cwPinList");
  var pinFormEl = panel.querySelector("#cwPinForm");
  var pinNodeEl = panel.querySelector("#cwPinNode");
  var pinUntilEl = panel.querySelector("#cwPinUntil");
  var pinPurposeEl = panel.querySelector("#cwPinPurpose");

  function renderReservations(list) {
    pinListEl.innerHTML = "";
    if (!Array.isArray(list) || list.length === 0) {
      var empty = document.createElement("div");
      empty.className = "cw-pin-empty";
      empty.textContent = "선언된 점유가 없습니다.";
      pinListEl.appendChild(empty);
      return;
    }
    var me = getSender();
    list.forEach(function (r) {
      var item = document.createElement("div");
      item.className = "cw-pin-item";
      var txt = document.createElement("span");
      txt.className = "cw-pin-txt";
      var nodeB = document.createElement("b");
      nodeB.textContent = r.node;
      txt.appendChild(nodeB);
      var rest = " · " + (r.until || "-") + " · " + r.who
        + (r.purpose ? " · " + r.purpose : "");
      txt.appendChild(document.createTextNode(rest));
      item.appendChild(txt);
      if (me && r.who === me) {
        var rel = document.createElement("button");
        rel.className = "cw-pin-rel";
        rel.textContent = "해제";
        rel.addEventListener("click", function () { releaseReservation(r.id); });
        item.appendChild(rel);
      }
      pinListEl.appendChild(item);
    });
  }
  function loadReservations() {
    fetch(RES_API)
      .then(function (r) { return r.json(); })
      .then(renderReservations)
      .catch(function () { /* 다음 폴링에서 복구 */ });
  }
  function releaseReservation(rid) {
    fetch(RES_API + "/" + rid + "/release", { method: "POST" })
      .then(function () { loadReservations(); })
      .catch(function () {});
  }
  function submitReservation() {
    var who = askSender(false);
    if (!who) return;
    var node = pinNodeEl.value.trim();
    if (!node) { pinNodeEl.focus(); return; }
    var payload = {
      node: node, who: who,
      until: pinUntilEl.value.trim(), purpose: pinPurposeEl.value.trim(),
    };
    fetch(RES_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (r) { return r.json(); })
      .then(function () {
        pinNodeEl.value = ""; pinUntilEl.value = ""; pinPurposeEl.value = "";
        pinFormEl.classList.remove("cw-show");
        loadReservations();
      })
      .catch(function () {});
  }
  panel.querySelector("#cwPinAdd").addEventListener("click", function () {
    pinFormEl.classList.toggle("cw-show");
    if (pinFormEl.classList.contains("cw-show")) pinNodeEl.focus();
  });
  panel.querySelector("#cwPinSubmit").addEventListener("click", submitReservation);
  [pinNodeEl, pinUntilEl, pinPurposeEl].forEach(function (el) {
    el.addEventListener("keydown", function (e) { if (e.key === "Enter") submitReservation(); });
  });
  function startResPolling() {
    if (resTimer) return;
    loadReservations();
    resTimer = setInterval(loadReservations, RES_POLL_MS);
  }

  // ---------- 6.6) 메시지 검색 ----------
  var searchWrap = panel.querySelector("#cwSearch");
  var searchInput = panel.querySelector("#cwSearchInput");
  var searchDebounce = null;

  function runSearch(q) {
    fetch(API + "?q=" + encodeURIComponent(q))
      .then(function (r) { return r.json(); })
      .then(function (list) {
        if (!searchMode) return;
        bodyEl.innerHTML = "";
        if (Array.isArray(list)) list.forEach(appendMsg);
        scrollBottom();
      })
      .catch(function () {});
  }
  function exitSearch() {
    searchMode = false;
    bodyEl.innerHTML = "";
    lastId = 0;          // 폴링이 전체를 다시 그리도록 리셋
    poll();
  }
  searchInput.addEventListener("input", function () {
    var q = searchInput.value.trim();
    if (searchDebounce) clearTimeout(searchDebounce);
    if (!q) { exitSearch(); return; }
    searchMode = true;
    searchDebounce = setTimeout(function () { runSearch(q); }, 200);
  });
  panel.querySelector("#cwSearchBtn").addEventListener("click", function () {
    searchWrap.classList.toggle("cw-show");
    if (searchWrap.classList.contains("cw-show")) {
      searchInput.focus();
    } else {
      searchInput.value = "";
      exitSearch();
    }
  });

  // ---------- 7) 토글 ----------
  function openPanel() {
    open = true;
    panel.classList.add("cw-show");
    unread = 0; badgeEl.style.display = "none";
    renderWho();
    scrollBottom();
    inputEl.focus();
  }
  function closePanel() { open = false; panel.classList.remove("cw-show"); }
  btn.addEventListener("click", function () { open ? closePanel() : openPanel(); });
  panel.querySelector("#cwClose").addEventListener("click", closePanel);

  // ---------- 8) 시작 ----------
  renderWho();
  startPolling();      // 닫혀 있어도 폴링하여 안 읽은 메시지 배지 표시
  startResPolling();   // 점유 선언 보드 5초 폴링(메시지와 별개 타이머)
})();
