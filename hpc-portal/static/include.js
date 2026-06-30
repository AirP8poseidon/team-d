/* 공통 네비 자가주입 (팀장 소유) — 결정 4A.
 * 각 페이지는 <div id="nav-placeholder"></div> + <script src="/static/include.js"></script>
 * 한 줄만 두면 된다. _nav.html 을 fetch 해 주입하고, 현재 경로에 맞는 링크에 .active 부여.
 */
(function () {
  function markActive(root) {
    // 현재 파일명(예: monitoring.html -> monitoring)을 키로 .active 설정
    var path = location.pathname;
    var file = path.substring(path.lastIndexOf("/") + 1) || "index.html";
    var page = file.replace(".html", "") || "index";
    var links = root.querySelectorAll(".links a[data-page]");
    for (var i = 0; i < links.length; i++) {
      if (links[i].getAttribute("data-page") === page) {
        links[i].classList.add("active");
      }
    }
  }

  function inject() {
    var placeholder = document.getElementById("nav-placeholder");
    if (!placeholder) return;
    fetch("/static/_nav.html")
      .then(function (r) { return r.text(); })
      .then(function (html) {
        placeholder.innerHTML = html;
        markActive(placeholder);
      })
      .catch(function (e) { console.error("nav 주입 실패", e); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inject);
  } else {
    inject();
  }
})();
