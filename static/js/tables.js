/*
 * Prepares tables for the "cards" layout (css/components/tables.css).
 *
 * The column headings stay the single source of truth: each cell gets its
 * heading copied into data-label, and the first cell / the Actions cell are
 * marked so CSS can style them. Reading the rendered DOM also means columns
 * hidden by permission checks in the template are handled correctly.
 *
 * Roles are set explicitly because browsers drop table semantics from
 * elements whose display is changed to block, which cards mode does.
 */
(function () {
    "use strict";

    var each = Array.prototype.forEach;

    document.querySelectorAll(".table-scroll table").forEach(function (table) {
        var headings = [];
        each.call(table.querySelectorAll("thead th"), function (th) {
            headings.push(th.textContent.replace(/\s+/g, " ").trim());
        });

        table.setAttribute("role", "table");
        each.call(table.querySelectorAll("thead, tbody"), function (group) {
            group.setAttribute("role", "rowgroup");
        });
        each.call(table.querySelectorAll("tr"), function (row) {
            row.setAttribute("role", "row");
        });
        each.call(table.querySelectorAll("th"), function (th) {
            th.setAttribute("role", "columnheader");
        });

        each.call(table.querySelectorAll("tbody tr"), function (row) {
            each.call(row.children, function (cell, index) {
                if (cell.tagName !== "TD") {
                    return;
                }
                var label = headings[index] || "";
                cell.setAttribute("role", "cell");
                cell.setAttribute("data-label", label);

                if (index === 0) {
                    cell.setAttribute("data-cell", "primary");
                } else if (/^actions?$/i.test(label)) {
                    cell.setAttribute("data-cell", "actions");
                }

                var hasContent = cell.textContent.trim() !== "" ||
                    cell.querySelector("a, button, form, input, img") !== null;
                if (!hasContent) {
                    cell.setAttribute("data-empty", "");
                }
            });
        });
    });
})();
