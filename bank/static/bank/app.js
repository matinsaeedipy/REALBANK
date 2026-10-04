(function () {
  var $ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // تم روشن/تیره
  $("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  });

  // کپی
  $("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var done = function () {
        btn.classList.add("copied");
        setTimeout(function () { btn.classList.remove("copied"); }, 1500);
      };
      if (navigator.clipboard) { navigator.clipboard.writeText(btn.getAttribute("data-copy")).then(done); }
    });
  });

  // شمارش موجودی
  $(".count").forEach(function (el) {
    var target = parseInt(el.getAttribute("data-value"), 10);
    var original = el.textContent;
    if (reduce || !isFinite(target) || target <= 0) return;
    var start = null, dur = 900;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased).toLocaleString("en-US");
      if (p < 1) requestAnimationFrame(step); else el.textContent = original;
    }
    requestAnimationFrame(step);
  });

  // کارت سه‌بعدی
  if (!reduce && window.matchMedia("(pointer: fine)").matches) {
    $("[data-tilt]").forEach(function (card) {
      card.addEventListener("pointermove", function (e) {
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        card.style.setProperty("--ry", ((x - 0.5) * 10).toFixed(2) + "deg");
        card.style.setProperty("--rx", ((0.5 - y) * 8).toFixed(2) + "deg");
        card.style.setProperty("--mx", (x * 100).toFixed(1) + "%");
        card.style.setProperty("--my", (y * 100).toFixed(1) + "%");
      });
      card.addEventListener("pointerleave", function () {
        card.style.setProperty("--rx", "0deg");
        card.style.setProperty("--ry", "0deg");
      });
    });
  }

  // نمایش/پنهان کردن رمز
  $("input[type=password]").forEach(function (input) {
    var wrap = document.createElement("span");
    wrap.className = "pw";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    var b = document.createElement("button");
    b.type = "button";
    b.className = "pw-toggle";
    b.setAttribute("aria-label", document.documentElement.lang === "fa" ? "نمایش یا پنهان کردن رمز" : "Show or hide password");
    b.innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-eye"/></svg>';
    b.addEventListener("click", function () {
      input.type = input.type === "password" ? "text" : "password";
    });
    wrap.appendChild(b);
  });

  // پیام‌ها
  $("[data-autohide]").forEach(function (m) {
    var hide = function () { m.classList.add("gone"); setTimeout(function () { m.remove(); }, 300); };
    var x = m.querySelector("[data-close]");
    if (x) x.addEventListener("click", hide);
    if (m.classList.contains("msg-success")) setTimeout(hide, 6000);
  });

  // مبلغ: پیش‌نمایش و دکمه‌های سریع
  var amount = document.getElementById("id_amount");
  var preview = document.getElementById("amount-preview");
  function showPreview() {
    if (!amount || !preview) return;
    var v = parseInt(amount.value, 10);
    preview.textContent = isFinite(v) && v > 0 ? v.toLocaleString("en-US") + " " + (preview.getAttribute("data-cur") || "") : "";
  }
  if (amount) {
    amount.addEventListener("input", showPreview);
    showPreview();
    $("[data-amount]").forEach(function (b) {
      b.addEventListener("click", function () {
        amount.value = b.getAttribute("data-amount");
        showPreview();
        amount.focus();
      });
    });
  }

  // چاپ رسید
  $("[data-print]").forEach(function (b) { b.addEventListener("click", function () { window.print(); }); });
})();
