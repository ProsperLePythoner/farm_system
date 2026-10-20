# Observations Made on `Farm System`'s UI/UX

# User Experience (UX)
## 1. Harvests
1. It's kinda inconvenient to have to remember how much I planted when registering a new harvest
2. No validation exists for when the user records a harvest quantity that exceeds the planting quantity

Implementation note: planting input units are free text (for example, seeds or
kg), while harvest quantity uses the crop's output unit. These values are not
necessarily comparable, and a planting may produce multiple harvests. Do not
enforce an individual or cumulative cap until the farm's yield rule and any unit
conversion requirements are defined.

## 2. User Account Management
1. The app isn't indicating that I'm the superuser admin.
2. The `deactivate` button isn't styled right. It's uncomfortably large as of present.

## 3. Orders
1. The `New Order` page isn't being very verbose about the unit price attribute (seems isolated, if you ask me)
2. Not sure what the `delete` button is doing after the Order Item/Item 1 etc. make it clearer for the user to understand
3. Numerical values for prices lack commas for easier readability

# 4. Calendar
Remember to add a calendar feature later on!

# 5. Notification
Also don't forget to enable email reminders for harvests approaching their expected harvest window.

# User Interface (UI)
1. Add consistent and smoother styling
2. Make tables and font more responsive for mobile users
3. Add relevant icons against action links to make the site more universally understood
4. Optionally enable visual display themes (e.g. light, dark, etc.) later on