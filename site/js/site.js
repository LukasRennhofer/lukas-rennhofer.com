document.addEventListener("DOMContentLoaded", () => {
  const siteHeader = document.querySelector(".site-header");
  const mobileNavToggle = document.getElementById("mobile-nav-toggle");
  const themeToggle = document.getElementById("theme-toggle");
  const themeMedia = window.matchMedia("(prefers-color-scheme: dark)");
  const themeKey = "theme-mode";
  const modes = ["auto", "light", "dark"];
  const modeIcons = {
    auto: "/assets/images/general/auto_mode.svg",
    light: "/assets/images/general/light_mode.svg",
    dark: "/assets/images/general/dark_mode.svg",
  };

  const getStoredMode = () => {
    const mode = localStorage.getItem(themeKey);
    return modes.includes(mode) ? mode : "auto";
  };

  const applyTheme = (mode) => {
    if (mode === "light" || mode === "dark") {
      document.documentElement.setAttribute("data-theme", mode);
    } else {
      document.documentElement.removeAttribute("data-theme");
    }

    if (themeToggle) {
      const label = mode === "auto" ? "Auto" : mode === "light" ? "Light" : "Dark";
      const iconSrc = modeIcons[mode] || modeIcons.auto;
      themeToggle.innerHTML = '<span class="theme-icon" aria-hidden="true"></span>';
      themeToggle.style.setProperty("--theme-icon", `url('${iconSrc}')`);
      themeToggle.setAttribute("aria-label", `Theme mode: ${label}`);
      themeToggle.setAttribute("title", `Theme: ${label}`);
    }
  };

  let activeMode = getStoredMode();
  applyTheme(activeMode);

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const idx = modes.indexOf(activeMode);
      activeMode = modes[(idx + 1) % modes.length];
      localStorage.setItem(themeKey, activeMode);
      applyTheme(activeMode);
    });
  }

  themeMedia.addEventListener("change", () => {
    if (activeMode === "auto") {
      applyTheme("auto");
    }
  });

  if (mobileNavToggle && siteHeader) {
    const syncMobileState = (open) => {
      siteHeader.classList.toggle("nav-open", open);
      document.body.style.overflow = open ? "hidden" : "";
      mobileNavToggle.setAttribute("aria-expanded", open ? "true" : "false");
    };

    mobileNavToggle.addEventListener("click", () => {
      const next = !siteHeader.classList.contains("nav-open");
      syncMobileState(next);
    });

    document.querySelectorAll(".masthead-nav a").forEach((link) => {
      link.addEventListener("click", () => syncMobileState(false));
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 820) {
        syncMobileState(false);
      }
    });
  }

  const links = document.querySelectorAll(".masthead-nav a, .blog-subnav a");
  const currentPath = window.location.pathname;

  for (const link of links) {
    const href = link.getAttribute("href");
    if (!href) {
      continue;
    }
    if (currentPath === href || (href !== "/" && currentPath.startsWith(href))) {
      link.setAttribute("aria-current", "page");
      link.style.color = "var(--text)";
    }
  }

  const slides = Array.from(document.querySelectorAll(".slide"));
  const nextBtn = document.querySelector("[data-slide-next]");
  const prevBtn = document.querySelector("[data-slide-prev]");
  const dots = Array.from(document.querySelectorAll("[data-slide-dot]"));

  if (slides.length > 0) {
    let index = slides.findIndex((slide) => slide.classList.contains("is-active"));
    if (index < 0) {
      index = 0;
      slides[0].classList.add("is-active");
    }

    if (dots.length > 0) {
      dots.forEach((dot) => dot.classList.remove("is-active"));
      if (dots[index]) {
        dots[index].classList.add("is-active");
      }
    }

    const showSlide = (newIndex) => {
      slides[index].classList.remove("is-active");
      index = (newIndex + slides.length) % slides.length;
      slides[index].classList.add("is-active");

      if (dots.length > 0) {
        dots.forEach((dot) => dot.classList.remove("is-active"));
        if (dots[index]) {
          dots[index].classList.add("is-active");
        }
      }
    };

    nextBtn?.addEventListener("click", () => showSlide(index + 1));
    prevBtn?.addEventListener("click", () => showSlide(index - 1));

    dots.forEach((dot) => {
      dot.addEventListener("click", () => {
        const target = Number(dot.getAttribute("data-slide-dot"));
        if (Number.isFinite(target)) {
          showSlide(target);
        }
      });
    });

    setInterval(() => {
      showSlide(index + 1);
    }, 5000);
  }
});
