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

## 3. Orders
1. The `New Order` page isn't being very verbose about the unit price attribute (seems isolated, if you ask me)
2. Not sure what the `delete` button is doing after the Order Item/Item 1 etc. make it clearer for the user to understand
3. Numerical values for prices lack commas for easier readability [resolved]
4. Unit prices for sales orders for specific crops should only be set **ONCE** to prevent inconsistencies. The user 
should then be allowed to customize it later on.

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

# User Interface (UI)
1. Add consistent and smoother styling. The farm dashboard, for example, could use some improvements for sure.
2. Make tables and font more responsive for mobile users
3. Add relevant icons against action links to make the site more universally understood
4. Optionally enable visual display themes (e.g. light, dark, etc.) later on
5. Restyle all links (at least) so that they're displayed as clickable buttons, to favor 
mobile users.
6. Notice how *Crop Timeline* has nice and smooth shadows, borders and font styling. Extend this 
to other templates as well. Is it really good to have shadows btw?? Idk. We'll figure it out.
7. Optionally, add a settings link where the user can quickly adjust preferences and even core functionality for 
the application, such as by an admin.