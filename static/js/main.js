/* =========================================================
   Typing effect
   ========================================================= */
const TYPED_STRINGS = [
  "AI Engineer | Embedded Systems Developer",
  "Builder of AI-Powered Hardware Solutions",
  "Smart Glasses | Medical AI | Edge Computing",
  "Computer Vision & NLP Specialist",
  "Raspberry Pi & IoT Enthusiast",
];

(function initTyping() {
  const el = document.getElementById("typed-text");
  if (!el) return;
  let si = 0, ci = 0, deleting = false;
  const TYPE_SPEED = 55, DELETE_SPEED = 30, PAUSE = 1800;

  function tick() {
    const str = TYPED_STRINGS[si];
    if (!deleting) {
      el.textContent = str.slice(0, ++ci);
      if (ci === str.length) { deleting = true; setTimeout(tick, PAUSE); return; }
    } else {
      el.textContent = str.slice(0, --ci);
      if (ci === 0) { deleting = false; si = (si + 1) % TYPED_STRINGS.length; }
    }
    setTimeout(tick, deleting ? DELETE_SPEED : TYPE_SPEED);
  }
  tick();
})();

/* =========================================================
   Navbar – scroll & mobile toggle
   ========================================================= */
(function initNavbar() {
  const navbar   = document.getElementById("navbar");
  const links    = document.getElementById("nav-links");
  const hamburger = document.getElementById("hamburger");
  const sections = document.querySelectorAll("section[id]");

  window.addEventListener("scroll", () => {
    navbar.classList.toggle("scrolled", window.scrollY > 30);
    highlightNav();
    document.getElementById("scroll-top")
      .classList.toggle("visible", window.scrollY > 400);
  });

  hamburger?.addEventListener("click", () => {
    links.classList.toggle("open");
    const open = links.classList.contains("open");
    hamburger.setAttribute("aria-expanded", open);
    hamburger.querySelectorAll("span").forEach((s, i) => {
      if (!open) {
        s.style.transform = "";
        s.style.opacity = "1";
        return;
      }
      if (i === 0) {
        s.style.transform = "rotate(45deg) translate(5px,5px)";
      } else if (i === 1) {
        s.style.opacity = "0";
      } else if (i === 2) {
        s.style.transform = "rotate(-45deg) translate(5px,-5px)";
      }
    });
  });

  // Close mobile menu on link click
  links?.querySelectorAll("a").forEach(a =>
    a.addEventListener("click", () => links.classList.remove("open"))
  );

  function highlightNav() {
    let current = "";
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 80) current = s.id;
    });
    document.querySelectorAll(".nav-links a").forEach(a => {
      a.classList.toggle("active", a.getAttribute("href") === "#" + current);
    });
  }
})();

/* =========================================================
   Scroll-to-top
   ========================================================= */
document.getElementById("scroll-top")?.addEventListener("click", () =>
  window.scrollTo({ top: 0, behavior: "smooth" })
);

/* =========================================================
   Intersection Observer – fade-in animation
   ========================================================= */
(function initFadeIn() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add("visible"); obs.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".fade-in").forEach(el => obs.observe(el));
})();

/* =========================================================
   Counter animation for stat numbers
   ========================================================= */
(function initCounters() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el  = e.target;
      const end = parseInt(el.dataset.count, 10);
      const dur = 1400;
      const step = Math.ceil(end / (dur / 16));
      let cur = 0;
      const timer = setInterval(() => {
        cur = Math.min(cur + step, end);
        el.textContent = cur + (el.dataset.suffix || "");
        if (cur >= end) clearInterval(timer);
      }, 16);
      obs.unobserve(el);
    });
  }, { threshold: 0.5 });
  document.querySelectorAll(".stat-num[data-count]").forEach(el => obs.observe(el));
})();

/* =========================================================
   Form tabs
   ========================================================= */
(function initTabs() {
  document.querySelectorAll(".form-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const parent = tab.closest(".form-card");
      parent.querySelectorAll(".form-tab").forEach(t => t.classList.remove("active"));
      parent.querySelectorAll(".form-panel").forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      const panel = parent.querySelector("#" + tab.dataset.target);
      if (panel) panel.classList.add("active");
    });
  });
})();

/* =========================================================
   Form submission
   ========================================================= */
async function submitForm(formId, endpoint) {
  const form    = document.getElementById(formId);
  const msgEl   = form.querySelector(".form-message");
  const btn     = form.querySelector(".form-submit");

  const data = {};
  new FormData(form).forEach((v, k) => data[k] = v);

  btn.disabled = true;
  btn.textContent = "Sending…";
  msgEl.style.display = "none";
  msgEl.className = "form-message";

  try {
    const res  = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    msgEl.textContent = json.message || json.error;
    msgEl.classList.add(json.success ? "success" : "error");
    msgEl.style.display = "block";
    if (json.success) form.reset();
  } catch {
    msgEl.textContent = "Network error – please try again.";
    msgEl.classList.add("error");
    msgEl.style.display = "block";
  } finally {
    btn.disabled = false;
    btn.textContent = btn.dataset.label || "Send";
  }
}

document.getElementById("service-form")?.addEventListener("submit", e => {
  e.preventDefault();
  submitForm("service-form", "/api/contact");
});

document.getElementById("order-form")?.addEventListener("submit", e => {
  e.preventDefault();
  submitForm("order-form", "/api/order");
});

/* =========================================================
   Smooth anchor scroll (offset for fixed navbar)
   ========================================================= */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener("click", e => {
    const target = document.querySelector(a.getAttribute("href"));
    if (!target) return;
    e.preventDefault();
    const top = target.getBoundingClientRect().top + window.scrollY - 70;
    window.scrollTo({ top, behavior: "smooth" });
  });
});
