/*
 * Display preferences: applied before first paint.
 *
 * Loaded (blocking) from <head> in templates/base/base.html so the right
 * theme and list layout are on <html> before anything is drawn; otherwise a
 * dark-theme user would see a white flash on every page.
 *
 * Preferences live in this browser only (localStorage):
 *   farm.theme  = auto | light | dark     ("auto" follows the device setting)
 *   farm.lists  = auto | table | cards    ("auto" = cards on small screens)
 *
 * Result on <html>:
 *   data-theme="light|dark"   always resolved (see css/base/tokens.css)
 *   class "stack-tables"      tables render as cards (see css/components/tables.css)
 *   class "js"                JavaScript is available
 *
 * window.FarmPrefs.get() / .set(name, value) are used by prefs.js.
 */
(function () {
    "use strict";

    var root = document.documentElement;
    var hasMatchMedia = typeof window.matchMedia === "function";
    var darkQuery = hasMatchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
    var smallQuery = hasMatchMedia ? window.matchMedia("(max-width: 720px)") : null;

    var ALLOWED = {
        theme: ["auto", "light", "dark"],
        lists: ["auto", "table", "cards"]
    };

    function read(name) {
        try {
            var value = window.localStorage.getItem("farm." + name);
            return ALLOWED[name].indexOf(value) > -1 ? value : "auto";
        } catch (error) {
            // Storage can be blocked (private mode, strict settings).
            return "auto";
        }
    }

    var api = {
        get: function () {
            return { theme: read("theme"), lists: read("lists") };
        },
        set: function (name, value) {
            if (!ALLOWED[name] || ALLOWED[name].indexOf(value) === -1) {
                return;
            }
            try {
                window.localStorage.setItem("farm." + name, value);
            } catch (error) {
                // Not saved, but still applied for this page view.
            }
            api.apply(name, value);
        },
        apply: function (overrideName, overrideValue) {
            var prefs = api.get();
            if (overrideName) {
                prefs[overrideName] = overrideValue;
            }
            var dark = prefs.theme === "dark" ||
                (prefs.theme === "auto" && darkQuery !== null && darkQuery.matches);
            var stack = prefs.lists === "cards" ||
                (prefs.lists === "auto" && smallQuery !== null && smallQuery.matches);

            root.setAttribute("data-theme", dark ? "dark" : "light");
            root.classList.toggle("stack-tables", stack);
            root.classList.add("js");
        }
    };

    window.FarmPrefs = api;
    api.apply();

    // Follow the device when it switches theme or the window is resized.
    [darkQuery, smallQuery].forEach(function (query) {
        if (!query) {
            return;
        }
        var handler = function () { api.apply(); };
        if (query.addEventListener) {
            query.addEventListener("change", handler);
        } else if (query.addListener) {
            query.addListener(handler);
        }
    });
})();
