/* 플로팅 채팅 위젯 (팀원1 소유 — 동작하는 스텁).
 * <script src="/static/chat-widget.js"></script> 한 줄로 임의 페이지에 탑재.
 * 자체 CSS·DOM 을 주입하고, 2.5초 간격 after=id 증분 폴링 + POST 전송.
 * index 페이지에는 넣지 않는다 (FR-C4).
 */
(function () {
  var POLL_MS = 2500;
  var lastId = 0;
  var sender = "익명" + Math.floor(Math.random() * 1000);

  // ── 스타일 주입 ─────────────────────────────────────────────────────────
  var css = ""
    + "#cw-toggle{position:fixed;right:20px;bottom:20px;z-index:9998;width:56px;height:56px;"
    + "border-radius:50%;border:none;background:#1d4ed8;color:#fff;font-size:22px;cursor:pointer;"
    + "box-shadow:0 4px 12px rgba(0,0,0,.25);}"
    + "#cw-box{position:fixed;right:20px;bottom:88px;z-index:9999;width:300px;height:400px;display:none;"
    + "flex-direction:column;background:#fff;border:1px solid #d8dee9;border-radius:12px;overflow:hidden;"
    + "box-shadow:0 8px 24px rgba(0,0,0,.2);font-family:'Malgun Gothic','Apple SD Gothic Neo',Arial,sans-serif;}"
    + "#cw-box.open{display:flex;}"
    + "#cw-head{background:#0f172a;color:#fff;padding:10px 12px;font-weight:600;font-size:14px;}"
    + "#cw-log{flex:1;overflow-y:auto;padding:10px;font-size:13px;background:#f4f6fb;}"
    + "#cw-log .msg{margin-bottom:8px;}"
    + "#cw-log .msg b{color:#1d4ed8;}"
    + "#cw-form{display:flex;border-top:1px solid #d8dee9;}"
    + "#cw-input{flex:1;border:none;padding:10px;font-size:13px;outline:none;}"
    + "#cw-send{border:none;background:#1d4ed8;color:#fff;padding:0 14px;cursor:pointer;}";
  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  // ── DOM 주입 ────────────────────────────────────────────────────────────
  var toggle = document.createElement("button");
  toggle.id = "cw-toggle";
  toggle.textContent = "💬";

  var box = document.createElement("div");
  box.id = "cw-box";
  box.innerHTML = ""
    + '<div id="cw-head">실시간 채팅</div>'
    + '<div id="cw-log"></div>'
    + '<form id="cw-form">'
    + '  <input id="cw-input" type="text" placeholder="메시지 입력..." autocomplete="off" />'
    + '  <button id="cw-send" type="submit">전송</button>'
    + "</form>";

  document.body.appendChild(toggle);
  document.body.appendChild(box);

  var logEl = box.querySelector("#cw-log");
  var formEl = box.querySelector("#cw-form");
  var inputEl = box.querySelector("#cw-input");

  toggle.addEventListener("click", function () {
    box.classList.toggle("open");
  });

  function hhmm(iso) {
    try { return new Date(iso).toTimeString().slice(0, 5); } catch (e) { return ""; }
  }

  function append(m) {
    var div = document.createElement("div");
    div.className = "msg";
    div.innerHTML = "<b></b> <span></span> <small></small>";
    div.querySelector("b").textContent = m.sender;
    div.querySelector("span").textContent = m.body;
    div.querySelector("small").textContent = hhmm(m.created_at);
    logEl.appendChild(div);
    logEl.scrollTop = logEl.scrollHeight;
    if (m.id > lastId) lastId = m.id;
  }

  function poll() {
    var url = "/api/chat/messages" + (lastId ? "?after=" + lastId : "");
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (rows) { (rows || []).forEach(append); })
      .catch(function (e) { /* 폴링 실패는 조용히 무시 */ });
  }

  formEl.addEventListener("submit", function (e) {
    e.preventDefault();
    var body = inputEl.value.trim();
    if (!body) return;
    inputEl.value = "";
    fetch("/api/chat/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sender: sender, body: body }),
    })
      .then(function (r) { return r.json(); })
      .then(function (m) { append(m); })
      .catch(function (e) { console.error("전송 실패", e); });
  });

  poll();
  setInterval(poll, POLL_MS);
})();
