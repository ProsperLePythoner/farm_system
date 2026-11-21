document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.querySelector(
        'input[type="password"]'
    );

    if (!passwordInput) return;

    const parent = passwordInput.parentElement;

    parent.classList.add("password-field-wrapper");

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "password-toggle";
    toggle.setAttribute("aria-label", "Show password");

    toggle.innerHTML = `
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 5c-5 0-9.27 3.11-11 7
            1.73 3.89 6 7 11 7s9.27-3.11 11-7
            c-1.73-3.89-6-7-11-7zm0 12
            a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"/>
            <circle cx="12" cy="12" r="2.5"/>
        </svg>
    `;

    parent.appendChild(toggle);

    toggle.addEventListener("click", () => {
        const show = passwordInput.type === "password";

        passwordInput.type = show ? "text" : "password";
        toggle.setAttribute(
            "aria-label",
            show ? "Hide password" : "Show password"
        );

        toggle.innerHTML = show
            ? `<svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M3 3l18 18M10.6 10.6a2 2 0 0 0 2.8 2.8
                M9.9 5.2A11 11 0 0 1 12 5
                c5 0 9.27 3.11 11 7a12 12 0 0 1-4 4.6
                M6.2 6.2A12 12 0 0 0 1 12c1.73 3.89
                6 7 11 7 1 0 2-.2 2.9-.5"/>
               </svg>`
            : `<svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 5c-5 0-9.27 3.11-11 7
                1.73 3.89 6 7 11 7s9.27-3.11 11-7
                c-1.73-3.89-6-7-11-7zm0 12
                a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"/>
                <circle cx="12" cy="12" r="2.5"/>
               </svg>`;
    });
});