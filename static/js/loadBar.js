(function () {
  const bar = document.getElementById("loadbar");
  if (!bar) return;

  let width = 0;
  let timer = null;

  function set(w) {
    width = w;
    bar.style.width = w + "%";
    bar.style.opacity = "1";
  }

  function start() {
    if (timer) return;
    set(8);
    timer = setInterval(function () {
      if (width < 90) set(width + (90 - width) * 0.12);
    }, 200);
  }

  function done() {
    clearInterval(timer);
    timer = null;
    set(100);
    setTimeout(function () { bar.style.opacity = "0"; }, 300);
    setTimeout(function () { bar.style.width = "0%"; }, 700);
  }

  start();
  window.addEventListener("load", done);

  document.addEventListener("click", function (e) {
    const a = e.target.closest("a");
    if (!a) return;
    const sameOrigin = a.href && a.origin === location.origin;
    const normal = !a.target && !a.hasAttribute("download") && a.getAttribute("href") &&
                   a.getAttribute("href").charAt(0) !== "#";
    if (sameOrigin && normal) start();
  });
})();