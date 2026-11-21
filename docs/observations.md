# Observations Made on `Farm System`'s UI/UX

# User Experience (UX)
## 1. Harvests
1. It's kinda inconvenient to have to remember how much I planted when registering a new harvest [resolved]
2. No validation exists for when the user records a harvest quantity that exceeds the planting quantity
3. Something weird is going on with the harvest output unit attribute as displayed by the 
`Harvests` template. I created a test crop `test_crop` and initially (I don't recall how tho) 
named its (probably harvesting unit, but that's selected from a dropdown???) harvest output 
unit to **eh?** on purpose. Later on, viewing the `Recorded Harvests` page I'm surprised to 
find that its entry field *Quantity* is written as *2,000.00 eh?*. I don't want that. But 
*WHERE exactly is the harvest output unit???*, obviously the planting unit can't match the harvest unit???
4. Currently, a harvested crop does not display its status as harvested even when a harvest has 
been recorded within the specified window. Fix this.

Implementation note: planting input units are free text (for example, seeds or
kg), while harvest quantity uses the crop's output unit. These values are not
necessarily comparable, and a planting may produce multiple harvests. Do not
enforce an individual or cumulative cap until the farm's yield rule and any unit
conversion requirements are defined.

## 2. User Account Management
1. The app isn't indicating that I'm the superuser admin. [resolved]
2. The `deactivate` button isn't styled right. It's uncomfortably large as of present. [resolved]
3. In the `Create User` template, the `role` field is empty so the user has nothing to choose 
from during user creation; apparently you can't even create a new user unless their role is 
specified. Also, we need a very clear distinction of the level of access that 
every kind of user gets from farm_system.
4. We don't want to have empty *action* fields to show users that there's some functionality 
they're limited from accessing. That should be the developer's secret (and of course, other admins).
5. I managed to add the email field to the Update User form, but the user's email only shows up on 
the user list after I manually update that field in the admin site! Dammit.

## 3. Orders
1. The `New Order` page isn't being very verbose about the unit price attribute (seems isolated, if you ask me)
2. Not sure what the `delete` button is doing after the Order Item/Item 1 etc. make it clearer for the user to understand
3. Numerical values for prices lack commas for easier readability [resolved]
4. Unit prices for sales orders for specific crops should only be set **ONCE** to prevent inconsistencies. The user 
should then be allowed to customize it later on.
5. The system should allow the sales manager to register when a customer is EXPECTED to 
pay for their respective order, to make email reminders more specific and less frequent.

# 4. Calendar
Remember to add a calendar feature later on!

# 5. Notification
Also don't forget to enable email reminders for harvests approaching their expected harvest window.

# 6. Crop Timeline
1. The statistics card dealing with harvest windows opening withing 7 days seems inaccurate. Test and refine this with 
explicitly created data for this purpose.
2. Test and refine the search filter for fields and crops. It's not working right.
3. Enable the user to navigate to a more detailed timeline for each crop, supporting graphical 
display and aggregation of useful data. Also useful statistics could be included as per type of user 
viewing the application.

# 7. Dashboard
1. As of present, the dashboard displays a fixed calendar with a 14-day timespan. This 
should be customized to enable the user to alter the timespan (e.g. 30 days, 3 months, etc.)

# 8. Plantings
1. The Plantings template must reflect the real status of actual plantings. It's okay that 
once a planting is ready for harvest, it says so expliciitly. However, the system must allow the 
user to know whether a ready-for-harvest planting has in fact *already* been harvested, to prevent 
ambiguity.

# 9. Sales Orders
1. The Sales Orders page allows order filtering with only two values, *All orders* and 
*Unpaid or part-paid*, which isn't helpful enough. The user should be able to filter completely 
unpaid and partially unpaid orders separately.

# User Interface (UI)
1. Add consistent and smoother styling.
2. Make tables and font more responsive for mobile users (is a tabular structure modern even? 
probably should allow the user to select their preferred kind of display)
3. Add relevant icons against action links to make the site more universally understood [check]
4. Optionally enable visual display themes (e.g. light, dark, etc.) later on [optional if it 
introduces much complexity]
5. Restyle all links (at least, if that's a great idea) so that they're displayed as clickable 
buttons, to favor mobile users. Mobile-native (even desktop) UI, modern everything, but still minimalist.
6. Notice how *Crop Timeline* has nice and smooth shadows, borders and font styling. Extend this 
to other templates as well. Is it really good to have shadows btw?? Idk. We'll figure it out.
7. Optionally, add a settings link where the user can quickly adjust preferences and even core functionality for 
the application, such as by an admin.
8. Give it a favicon.