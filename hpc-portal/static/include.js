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

  function addMobileToggle(placeholder) {
    // 모바일(≤760px)에서 사이드바를 다시 여는 햄버거 버튼. CSS(.side-toggle)는 theme.css 소유.
    if (document.querySelector(".side-toggle")) return;
    var side = placeholder.querySelector(".side");
    if (!side) return;
    var tog = document.createElement("button");
    tog.className = "side-toggle";
    tog.setAttribute("aria-label", "메뉴 열기");
    tog.innerHTML = "☰";
    tog.addEventListener("click", function () { side.classList.toggle("open"); });
    // 사이드바 밖을 누르면 닫힘
    document.addEventListener("click", function (e) {
      if (side.classList.contains("open") && !side.contains(e.target) && e.target !== tog) {
        side.classList.remove("open");
      }
    });
    document.body.appendChild(tog);
  }

  function inject() {
    var placeholder = document.getElementById("nav-placeholder");
    if (!placeholder) return;
    fetch("/static/_nav.html")
      .then(function (r) { return r.text(); })
      .then(function (html) {
        placeholder.innerHTML = html;
        markActive(placeholder);
        addMobileToggle(placeholder);
      })
      .catch(function (e) { console.error("nav 주입 실패", e); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inject);
  } else {
    inject();
  }
})();
