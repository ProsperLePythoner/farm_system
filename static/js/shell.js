(function () {
    const toggle = document.querySelector(".nav-toggle");
    const sidebar = document.getElementById("main-navigation");
    const backdrop = document.querySelector(".nav-backdrop");

    if (!toggle || !sidebar) {
        return;
    }

    function isMobileNav() {
        return window.matchMedia("(max-width: 800px)").matches;
    }

    function setOpen(open) {
        document.body.classList.toggle("nav-open", open);
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
        toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
        if (isMobileNav()) {
            sidebar.toggleAttribute("inert", !open);
        } else {
            sidebar.removeAttribute("inert");
        }
    }

    if (isMobileNav()) {
        setOpen(false);
    }

    toggle.addEventListener("click", function () {
        setOpen(!document.body.classList.contains("nav-open"));
    });

    if (backdrop) {
        backdrop.addEventListener("click", function () {
            setOpen(false);
        });
    }

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            setOpen(false);
        }
    });

    sidebar.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
            setOpen(false);
        });
    });

    window.matchMedia("(min-width: 801px)").addEventListener("change", function (event) {
        if (event.matches) {
            setOpen(false);
        }
    });
})();
