# Crop Timeline — UI/UX Improvements

## Objective

Improve the existing Field Board page into a clearer, more informative **Crop Timeline** for the Agribusiness Management System.

The page should help users quickly understand:

- Which fields are currently growing crops
- When each planting is expected to become harvest-ready
- Which harvest windows are approaching, open, completed, or missed
- Which harvests have already been recorded
- What actions need attention

This is primarily a **UI/UX refinement task**, not a complete redesign or backend rewrite.

---

## 1. Rename the View

Replace the user-facing name **Field Board** with **Crop Timeline**.

Update relevant user-facing references, including:

- Page heading
- Sidebar navigation label
- Breadcrumbs, if present
- Page descriptions
- Relevant template text

Use the name `Crop Timeline` consistently.

Do not rename Django apps, models, URL namespaces, database fields, or internal Python classes solely for cosmetic reasons.

Existing URLs and reverse URL references should remain functional.

---

## 2. Replace the Sidebar Icon

The current Field Board icon is shared with the Field Dashboard, making the two views difficult to distinguish.

Use a dedicated timeline-related icon.

### Preferred icon

- Google Material Symbols: `view_timeline`

### Alternatives

- `event_note`
- `calendar_month`

Use the icon library and integration already implemented in the project.

Do not introduce another icon library or external dependency.

Ensure the icon:
- Is visually distinguishable from the Field Dashboard icon
- Uses the existing sidebar styling
- Has appropriate alignment and sizing
- Remains accessible, with the navigation label providing its meaning

---

## 3. Improve Timeline Semantics

Inspect the existing timeline implementation before modifying it.

The timeline currently includes:

- Horizontal planting growth bars
- Harvest-window opening markers
- Recorded harvest event dots
- Field rows
- Date-axis labels

Make the visual meaning of each element unmistakable.

### Growth bar

The horizontal growth bar represents the period from planting until the expected harvest-window opening.

Requirements:
- Clearly communicate that this is the crop's growth period.
- Include a tooltip or accessible label with the planting date and expected harvest-window opening date.
- Avoid implying that the bar represents the entire harvest window.
- Ensure the bar remains understandable when very short or partially outside the visible timeline.

### Harvest-window marker

The existing marker indicates the **opening date of the expected harvest window**, not the actual harvest date.

Requirements:
- Explicitly identify it as the harvest-window opening.
- Provide a tooltip or accessible label containing the relevant date.
- Use the existing harvest status colors consistently.
- Ensure the marker remains visually distinguishable from recorded harvest event dots.

### Recorded harvest event dots

These represent actual recorded harvest dates.

Requirements:
- Distinguish them clearly from expected harvest-window markers.
- Add a tooltip or accessible label containing the harvest date and relevant recorded quantity, where available.
- If multiple harvest records occur close together, prevent the markers from becoming indistinguishable.
- Consider a small marker cluster or count indicator when events overlap.

Do not misrepresent recorded harvest events as expected harvest dates.

---

## 4. Consider Showing the Entire Harvest Window

Currently, the timeline appears to emphasize the harvest-window opening date with a marker.

Consider adding a subtle horizontal band representing the full expected harvest window.

For example, if the expected harvest window runs from November 21 to November 23:

- The growth bar ends at November 21.
- The harvest-window band spans November 21–23.
- Recorded harvest dots appear on their actual dates.

Requirements:
- The band must be visually distinct from the growth bar.
- It must not obscure recorded harvest markers.
- It should use a subtle background or border.
- Its start and end dates should be available through a tooltip or accessible text.
- Ensure the band remains visible for short windows.

**Important:** Verify the actual harvest-window duration and date calculations in the existing Django view before implementing this. Do not assume the window is always three days.

If displaying the full window introduces unnecessary complexity or clutter, retain the opening marker but improve its labeling.

---

## 5. Improve the Date Axis

The timeline is anchored around the current date and displays a selected future period.

Improve the axis so users can understand the dates represented by the horizontal positions.

Requirements:
- Make date labels more informative than unlabeled grid divisions.
- Clearly identify the current date.
- Ensure labels remain readable on narrow screens.
- Avoid excessive labels that create visual clutter.
- Make the selected timeline duration obvious.
- Ensure timeline rows and axis labels remain aligned.

Consider a subtle **Today** indicator running vertically through the timeline.

This indicator should:
- Use a distinct but unobtrusive style.
- Avoid being confused with harvest markers.
- Remain aligned across all field rows.

Verify whether the current axis starts at today or includes earlier dates before changing the behavior.

---

## 6. Clarify Timeline Statuses

Review the existing planting statuses and their colors.

Statuses currently include variations such as:

- Growing
- Soon
- Ready
- Partial
- Done
- Missed

Requirements:
- Use consistent colors throughout the page.
- Provide a clear legend explaining the colors and markers.
- Avoid relying on color alone to communicate status.
- Include textual status labels where appropriate.
- Distinguish expected harvest-window status from recorded harvest progress.

Do not introduce new statuses unless the existing business logic supports them.

Check that completed or missed plantings do not appear misleadingly active.

---

## 7. Improve Timeline Clipping and Edge Cases

The existing timeline uses percentage positions and clamps dates outside the selected range to the left or right edge.

Review how this behaves for:

- Plantings that began before the timeline
- Harvest windows beyond the selected duration
- Harvest windows that have already passed
- Very short growth periods
- Plantings with missing or incomplete dates
- Recorded harvests outside the visible timeline

Requirements:
- Avoid markers appearing to represent incorrect dates.
- Where practical, use directional indicators or labels for dates outside the timeline.
- Do not silently move a marker to the edge without communicating that its actual date lies outside the visible range.
- Handle missing dates safely without breaking the page.

Do not alter the underlying business rules simply to make the visualization easier.

---

## 8. Improve Readability and Interaction

Review the overall layout and make the timeline easier to scan.

Potential improvements:
- Better spacing between field rows
- Clearer separation between fields
- More legible crop and field names
- Better alignment of labels and timeline tracks
- Improved contrast for markers and bars
- More useful hover/focus tooltips
- Reduced visual clutter

The timeline should remain usable with a keyboard and on mobile devices.

Tooltips must not be the only way to access important information on touch devices.

Keep the design consistent with the existing application styling, typography, colors, and components.

---

## 9. Preserve Existing Functionality

Do not unnecessarily modify:

- Planting creation and editing
- Harvest recording
- Harvest calculations
- Crop or field relationships
- Permissions
- Existing filters
- Existing dashboard functionality
- Database models or migrations

The page currently includes filters, planting details, harvest actions, and supporting sections such as picking lists, crop mix, and weekly harvest activity.

Preserve these features unless a change is necessary for the requested UI improvements.

Ensure existing links and Django URL names continue working.

---

## 10. Responsive Behavior

Review the timeline at desktop, tablet, and mobile widths.

Requirements:
- Field names and timeline tracks must remain readable.
- Avoid compressing the timeline until markers and bars become meaningless.
- Consider horizontal scrolling for the timeline area on narrow screens.
- Keep field labels visible or clearly associated with their rows.
- Prevent tooltips, buttons, and labels from overflowing their containers.
- Preserve access to filters and planting actions.

Do not make the entire page horizontally scroll if only the timeline section needs scrolling.

---

## 11. Accessibility

Ensure:
- Marker meaning is available through text or accessible labels.
- Color is not the sole indicator of status.
- Keyboard users can access relevant interactive elements.
- Focus indicators remain visible.
- Contrast is sufficient.
- Tooltips do not replace essential information.

Use semantic HTML and existing accessibility conventions.

---

## 12. Implementation and Testing

Before changing code:

1. Inspect the current template, view, CSS, URL configuration, and sidebar.
2. Understand how timeline positions and status classes are currently calculated.
3. Identify which improvements can be implemented entirely in the template and CSS.
4. Modify backend code only when necessary.

After implementation:

- Check Django template rendering.
- Run the project's existing tests.
- Check for Django system-check errors.
- Verify all existing filters still work.
- Verify harvest recording links work.
- Check timeline behavior for past, current, and future harvest windows.
- Check mobile and desktop layouts.
- Ensure the Field Dashboard icon remains unchanged.
- Confirm no unnecessary migrations were introduced.

Provide a concise summary of:
- Files modified
- UI changes made
- Any backend changes
- Tests performed
- Remaining limitations

## Design Principle

The Crop Timeline should make the difference between **expected crop development**, **expected harvest availability**, and **actual recorded harvest activity** immediately understandable.

Prioritize clarity and operational usefulness over decorative complexity.
