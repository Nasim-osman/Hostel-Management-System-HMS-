# HMS — Database Design & Data Integrity

## 1. Relational Schema & Normalization
The HMS database schema is designed in Third Normal Form (3NF) to eliminate data redundancy, ensure referential integrity, and protect historical financial transactions.

### Key Entities:
1. **User (`accounts_user`):** Custom user model with `role` choices (ADMIN, WARDEN, ACCOUNTS, MAINTENANCE, RESIDENT).
2. **HostelBlock (`rooms_hostelblock`):** Building name, block code, floors, gender policy.
3. **Room (`rooms_room`):** Block FK, room number, floor, room type, capacity, base fee. Unique on `(block, room_number)`.
4. **Bed (`rooms_bed`):** Room FK, bed number, occupancy status. Unique on `(room, bed_number)`.
5. **Amenity (`rooms_amenity`):** Utility name (Light, Water, Wifi, Laundry, Hot Water), status (Operational, Degraded, Outage).
6. **ResidentProfile (`residents_residentprofile`):** User 1-to-1, unique `student_id`, course, emergency contact, status, `current_bed` FK (1-to-1).
7. **SeatApplication (`allocations_seatapplication`):** Resident FK, room type preference, block preference, review notes, status.
8. **SeatAllocation (`allocations_seatallocation`):** Resident FK, Bed FK, allocated by FK, active flag, vacated timestamp.
9. **WaitingListEntry (`allocations_waitinglistentry`):** Application 1-to-1, queue priority number, status.
10. **RoomTransferRequest (`allocations_roomtransferrequest`):** Resident FK, current bed FK, target room FK, reason, status.
11. **CheckoutClearance (`allocations_checkoutclearance`):** Resident FK, target checkout date, property clearance boolean, accounts clearance boolean, warden approval boolean, status.
12. **FeeCategory (`finance_feecategory`):** Name, default amount, frequency (Monthly, Semester, Annual, One-time).
13. **ResidentCharge (`finance_residentcharge`):** Resident FK, FeeCategory FK, amount, paid amount, due date, status.
14. **Payment (`finance_payment`):** Unique `receipt_number`, Resident FK, Charge FK, amount, payment date, method, transaction reference, status, verified by FK.
15. **Fine (`finance_fine`):** Resident FK, reason, amount, status, issued by FK.
16. **Refund (`finance_refund`):** Resident FK, reason, amount, status, approved by FK.
17. **HostelExpense (`finance_hostelexpense`):** Category, title, payee, amount, expense date, invoice number, recorded by FK.
18. **Complaint (`complaints_complaint`):** Unique `ticket_number`, Resident FK, Room FK, title, category, priority, status, assigned to FK, resolution notes.
19. **MealMenu (`dining_mealmenu`):** Meal type (Breakfast, Lunch, Dinner), timing, veg items, non-veg items, active flag.
20. **VisitorLog (`visitors_visitorlog`):** Visitor name, phone, Resident FK, destination, purpose, check-in/out timestamps, status, gate pass number.
21. **AttendanceRecord (`attendance_attendancerecord`):** Resident FK, date, status (Present, Absent, Leave, Outpass). Unique on `(resident, date)`.
22. **OutpassRequest (`attendance_outpassrequest`):** Resident FK, purpose, destination, departure/return timestamps, parent phone, status, approved by FK.
23. **Notice (`notices_notice`):** Title, content, category, target audience, publish date, published flag, created by FK.
24. **AuditLog (`audit_auditlog`):** Actor FK, action, module, target representation, IP address, details, timestamp.
25. **Experiment / MetricEvent (`abtesting_*`):** A/B test experiments, deterministic user variant assignments, and metric event logs.

## 2. Critical Database Integrity Rules Enforced:
- **No Overbooking:** A bed record has a boolean flag `is_occupied` and a 1-to-1 relationship with `ResidentProfile.current_bed`. An atomic database lock (`select_for_update`) prevents two concurrent transactions from allocating the same bed.
- **Capacity Integrity:** Bed additions validate `room.beds.count() < room.capacity` before insertion.
- **Monetary Precision:** All currency fields use `DecimalField(max_digits=10, decimal_places=2)` to avoid floating-point rounding errors.
- **Audit Immobility:** Financial payments and audit records cannot be silently deleted or updated without generating audit log entries.
