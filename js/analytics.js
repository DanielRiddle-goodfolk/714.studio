/* Studio 7:14 — Google Analytics 4.
 *
 * This file is inert unless build/inject.py wrote a measurement ID into the
 * script tag, which it only does for Netlify production builds. Deploy previews
 * and local work never receive the tag at all.
 *
 * Do not replace this with Google's copy-paste snippet. That snippet has no
 * hostname guard, and this workflow generates a deploy preview per pull request
 * — every one of them would land in the real numbers.
 */

(function () {
  "use strict";

  var tag = document.currentScript;
  var id = tag && tag.getAttribute("data-ga-id");
  if (!id) return;

  var host = location.hostname;

  // Second line of defence behind the build-time gate. Blocks localhost and any
  // Netlify preview URL (deploy-preview-12--site.netlify.app, branch--site…).
  var isLocal = host === "localhost" || host === "127.0.0.1" || host === "" ||
                host.endsWith(".local");
  var isPreview = host.indexOf("deploy-preview") !== -1 || host.indexOf("--") !== -1;
  if (isLocal || isPreview) return;

  // A wellness studio's visitors skew toward people who care about this.
  // Honouring the browser signal costs a little data and is the right call.
  if (navigator.doNotTrack === "1" || window.doNotTrack === "1") return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;

  gtag("js", new Date());
  gtag("config", id);

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
  document.head.appendChild(s);

  /* --- Conversion signals -------------------------------------------------
   * Booking currently lives on the Squarespace scheduler, so a booking attempt
   * looks like someone leaving the site. Without these events there is no way
   * to tell which page actually earns appointments — which is the one number
   * this site exists to move.
   *
   * Deliberately keyed on "leaves this origin" rather than on the 714.studio
   * hostname. After DNS cutover the new site owns that hostname, so a check for
   * it would silently stop matching exactly when the numbers start mattering.
   *
   * If booking moves to per-page embeds, these events need revisiting: an
   * embedded iframe generates no outbound click at all.
   */
  var BOOKING_HINT = /book|schedul|appoint|apothecary/i;

  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest && e.target.closest("a[href]");
    if (!a) return;

    var href = a.getAttribute("href") || "";
    var label = (a.textContent || "").trim().slice(0, 80);

    if (href.indexOf("tel:") === 0) {
      gtag("event", "phone_click", { page_path: location.pathname });
      return;
    }
    if (href.indexOf("mailto:") === 0) {
      gtag("event", "email_click", { page_path: location.pathname });
      return;
    }

    // Anything leaving this origin. a.hostname is empty for non-HTTP schemes.
    if (a.hostname && a.hostname !== location.hostname) {
      var booking = BOOKING_HINT.test(href) || BOOKING_HINT.test(label);
      gtag("event", booking ? "booking_click" : "outbound_click", {
        link_url: a.href,
        link_text: label,
        link_domain: a.hostname,
        page_path: location.pathname
      });
    }
  }, true);
})();
