/* Studio 7:14 — the small amount of behaviour the static site actually needs.
   Replaces the Radix sheet that used to drive the mobile menu. No dependencies. */

(function () {
  "use strict";

  var body = document.body;
  var trigger = document.querySelector(".menu-trigger");
  var panel = document.getElementById("mobile-menu");
  var scrim = document.querySelector(".mobile-menu-scrim");
  var closeBtn = document.querySelector(".menu-close");
  if (!trigger || !panel) return;

  var lastFocused = null;

  function focusables() {
    return Array.prototype.filter.call(
      panel.querySelectorAll('a[href], button:not([disabled])'),
      function (el) { return el.offsetParent !== null; }
    );
  }

  function open() {
    lastFocused = document.activeElement;
    panel.hidden = false;
    // next frame, so the transform transition has a start state to run from
    requestAnimationFrame(function () {
      body.classList.add("menu-open");
      trigger.setAttribute("aria-expanded", "true");
      var f = focusables();
      if (f.length) f[0].focus();
    });
  }

  function close() {
    body.classList.remove("menu-open");
    trigger.setAttribute("aria-expanded", "false");
    var done = function () {
      panel.hidden = true;
      panel.removeEventListener("transitionend", done);
    };
    panel.addEventListener("transitionend", done);
    // fallback if the transition is suppressed (reduced motion, background tab)
    setTimeout(done, 420);
    if (lastFocused) lastFocused.focus();
  }

  trigger.addEventListener("click", function () {
    body.classList.contains("menu-open") ? close() : open();
  });
  if (closeBtn) closeBtn.addEventListener("click", close);
  if (scrim) scrim.addEventListener("click", close);

  document.addEventListener("keydown", function (e) {
    if (!body.classList.contains("menu-open")) return;

    if (e.key === "Escape") { close(); return; }

    // Keep tabbing inside the panel while it is open
    if (e.key === "Tab") {
      var f = focusables();
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      }
    }
  });

  // Close on resize up to desktop, so the panel can't be left open behind the
  // desktop nav after a rotation.
  var mq = window.matchMedia("(min-width: 900px)");
  var onChange = function (e) { if (e.matches && body.classList.contains("menu-open")) close(); };
  mq.addEventListener ? mq.addEventListener("change", onChange) : mq.addListener(onChange);

  // Header scroll state. The Manus capture froze .is-scrolled into the markup
  // because the page was mid-scroll when it was grabbed; drive it properly.
  var header = document.querySelector(".site-header");
  if (header) {
    var syncHeader = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    syncHeader();
    window.addEventListener("scroll", syncHeader, { passive: true });
  }

  // Mark the current page in both navs.
  var here = location.pathname.replace(/\/+$/, "") || "/";
  document.querySelectorAll(".desktop-nav-link, .mobile-nav-link").forEach(function (a) {
    var href = a.getAttribute("href") || "";
    if (href.charAt(0) !== "/") return;
    if (href.replace(/\/+$/, "") === here) a.setAttribute("aria-current", "page");
  });
})();
