/*
 * Keeps the dashboard fresh without a full page reload.
 *
 * WHY POLLING: the site runs on serverless functions, which cannot hold a
 * WebSocket open. Asking for the panels every N seconds is the reliable
 * equivalent, and it stays cheap because:
 *   - it pauses while the tab is hidden and catches up when you return;
 *   - the server answers 304 (empty) when nothing changed;
 *   - failures back off instead of hammering the server.
 */

(function () {
    const live = document.getElementById("dashboard-live");
    if (!live) { return; }

    const statusEl = document.getElementById("live-status");
    const button = document.getElementById("live-refresh");
    const baseMs = Math.max(15, parseInt(live.dataset.interval, 10) || 60) * 1000;
    let etag = null;
    let timer = null;
    let failures = 0;
    let lastOk = Date.now();
    let inFlight = false;
    let stopped = false;  // set when the session has expired

    function setStatus(text, isProblem) {
        if (!statusEl) { return; }
        statusEl.textContent = text;
        statusEl.classList.toggle("is-problem", !!isProblem);
    }

    function ageText() {
        const s = Math.round((Date.now() - lastOk) / 1000);
        if (s < 10) { return "Updated just now"; }
        if (s < 90) { return "Updated " + s + "s ago"; }
        return "Updated " + Math.round(s / 60) + " min ago";
    }

    function schedule() {
        clearTimeout(timer);
        if (document.hidden || stopped) { return; }
        // 60s, then 2x, 4x ... up to 10 minutes while the server is unreachable.
        const delay = Math.min(baseMs * Math.pow(2, failures), 600000);
        timer = setTimeout(refresh, delay);
    }

    async function refresh() {
        if (inFlight) { return; }
        inFlight = true;
        try {
            const headers = { "X-Requested-With": "fetch" };
            if (etag) { headers["If-None-Match"] = etag; }
            const res = await fetch(live.dataset.url, {
                headers: headers,
                credentials: "same-origin",
                redirect: "manual",
            });
            if (res.type === "opaqueredirect" || res.status === 401 || res.status === 403) {
                stopped = true;  // nothing will work until the user signs in again
                setStatus("Session expired. Reload the page to sign in again.", true);
                return;
            }
            if (res.status === 200) {
                const html = await res.text();
                live.innerHTML = html;
                etag = res.headers.get("ETag");
            } else if (res.status !== 304) {
                throw new Error("HTTP " + res.status);
            }
            failures = 0;
            lastOk = Date.now();
            setStatus(ageText(), false);
        } catch (err) {
            failures += 1;
            setStatus("Offline. Showing the last update; retrying.", true);
        } finally {
            inFlight = false;
            schedule();
        }
    }

    document.addEventListener("visibilitychange", function () {
        if (document.hidden) { clearTimeout(timer); return; }
        if (stopped) { return; }
        // Back in view: refresh now if the data is older than one interval.
        if (Date.now() - lastOk >= baseMs) { refresh(); } else { schedule(); }
    });
    if (button) { button.addEventListener("click", function () { failures = 0; stopped = false; refresh(); }); }
    window.addEventListener("online", function () { failures = 0; refresh(); });
    setInterval(function () { if (!document.hidden && failures === 0) { setStatus(ageText(), false); } }, 15000);

    schedule();
})();