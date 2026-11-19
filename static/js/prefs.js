/*
 * Display preferences dialog (theme and list layout).
 * Markup: templates/base/prefs_dialog.html. Storage: prefs-init.js.
 */
(function () {
    "use strict";

    var dialog = document.getElementById("prefs-dialog");
    var openButton = document.getElementById("prefs-open");

    if (!dialog || !openButton || !window.FarmPrefs) {
        return;
    }

    // The button is hidden in the HTML and only shown once it can work.
    openButton.hidden = false;

    function syncRadios() {
        var prefs = window.FarmPrefs.get();
        dialog.querySelectorAll('input[type="radio"]').forEach(function (radio) {
            radio.checked = prefs[radio.name] === radio.value;
        });
    }

    openButton.addEventListener("click", function () {
        syncRadios();
        if (typeof dialog.showModal === "function") {
            dialog.showModal();
        } else {
            dialog.setAttribute("open", "");
        }
    });

    // Changes apply immediately; there is no Save button to forget.
    dialog.addEventListener("change", function (event) {
        var target = event.target;
        if (target && target.type === "radio") {
            window.FarmPrefs.set(target.name, target.value);
        }
    });

    // A click on the dimmed area (the <dialog> element itself) closes it.
    dialog.addEventListener("click", function (event) {
        if (event.target === dialog && typeof dialog.close === "function") {
            dialog.close();
        }
    });
})();
