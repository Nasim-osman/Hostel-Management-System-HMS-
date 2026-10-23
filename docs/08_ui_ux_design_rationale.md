# HMS — UI/UX Design System & Layout Rationale

## 1. Visual Direction & Design Fidelity
The HMS user interface is modeled directly after modern university administrative standards, providing high data scannability, clear visual hierarchy, and an exact match to the provided reference dashboard layout.

### Color Palette Tokens
| Token | Hex Value | Semantic Purpose |
| :--- | :--- | :--- |
| `--hms-blue-header` | `#0060af` | Primary branding header, top bar, and primary call-to-action buttons. |
| `--hms-sidebar-bg` | `#1a2634` | High-contrast dark slate navigation sidebar. |
| `--hms-page-bg` | `#f4f6f9` | Eye-strain reducing neutral light grayish-blue background. |
| `--hms-card-bg` | `#ffffff` | Clean white card surfaces with subtle border `#edf2f7` and 1px drop shadow. |
| `--hms-green` | `#16a34a` | Positive metrics: Occupied rooms, paid fees, operational status. |
| `--hms-red` | `#dc2626` | Urgent alerts: Vacant rooms, unpaid dues, overdue outpasses, penalty fines. |

---

## 2. Grid Architecture & Dashboard Breakdown

The primary Hostel Management Dashboard layout (`templates/dashboard/hostel_dashboard.html`) mirrors the reference image across 8 dedicated modular cards:

1. **Rooms KPI Card (Col 4):**
   - 3-column comparative view:
     - Total: `200` (`#0060af`, font-size 26px bold)
     - Occupied: `150` (`#16a34a`, font-size 26px bold)
     - Vacant: `50` (`#dc2626`, font-size 26px bold)
2. **Payment Summary Card (Col 4):**
   - 2-column financial health view:
     - Paid: `৳ 1,20,345` (bold emerald green)
     - Unpaid: `৳ 20,345` (bold dark slate)
3. **Amenities Status Card (Col 4):**
   - Horizontal status ribbon displaying Light, Water, Wifi, Laundry, and Hot Water with operational status badges.
4. **Tenants / Capacity Donut Card (Col 4):**
   - Interactive Chart.js circular progress ring showing `75%` occupancy in the center.
   - Right-side counter displaying total capacity `500` and occupied `375`.
5. **Mess (Today's Meal) Card (Col 4):**
   - Structured timetable:
     - **Breakfast:** `3 Idli Sambar`
     - **Lunch:** Veg (`Sprouts | 3 Chapatis | Rice | Dal`) & Non-Veg (`Egg Biryani`)
     - **Dinner:** Veg (`Sprouts | 3 Chapatis | Rice | Dal`) & Non-Veg (`Egg Curry | 3 Chapatis | Rice`)
6. **Tickets / Unsolved Complaints Card (Col 4):**
   - Live maintenance feed with student avatars, names, and snippets:
     - Mike Ross: *Water not Comming*
     - Jennifer Grint: *Light is not available since last night*
     - Casey Allen: *Wifi is not working since past week, please fix it.*
     - Tina Harris: *Laundry is not working properly, please look into this quickly*
     - Rick Butcher: *Hot water tap is broken, please fix it urgently*
7. **Visitors Card (Col 6):**
   - Counter `Total 2`, displaying active security locations:
     - `Building A | Floor 2nd | Room 201`
     - `Building A | Floor 1st | Room 103`
8. **Reports Card (Col 6):**
   - Quick-action analytical links: `Total Number of Vacant Room` (50) and `Total Fees Collected` (৳ 1,20,345).

---

## 3. Responsive & Accessibility Implementation
- **WCAG 2.2 AA Contrast Compliance:** Text-to-background contrast ratios exceed 4.5:1 on all interactive cards.
- **Form Controls:** Every input possesses explicit labels, focus rings (`focus:ring-2 focus:ring-blue-600`), and visible validation errors.
- **Screen Reader Support:** Semantic HTML5 elements (`<header>`, `<aside>`, `<main>`, `<article>`, `<table>`) are used exclusively.
