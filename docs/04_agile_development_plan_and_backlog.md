# HMS — Agile Scrum Development Plan & Product Backlog

## 1. Development Methodology Rationale
HMS was developed using an **Agile Scrum-inspired iterative development methodology**.
### Why Agile Iterative Development is Essential for HMS:
1. **Incremental Validation:** Instead of waiting for a monolithic system delivery, core foundational layers (Auth, RBAC, Room Modeling) were designed and verified first, followed by dependent operational layers (Allocations, Finance, Clearances).
2. **Early Defect Detection:** Automated unit and integration tests were executed at each sprint boundary, isolating regression errors before complex workflows were introduced.
3. **Traceability:** User stories and acceptance criteria remained tightly synchronized with the SRS throughout development.

---

## 2. Sprint Breakdown (Sprint 0 through Sprint 6)

### Sprint 0 — Initiation & Requirements
- **Sprint Goal:** Define project charter, problem statement, stakeholder analysis, and initial IEEE-style SRS with 23 features.
- **User Stories:** As a system architect, I want to establish measurable requirements and business rules so that implementation is verifiable.
- **Tasks:**
  - Create problem statement and feasibility study.
  - Compile FR-001 through FR-023.
  - Establish Git version control and project structure.
- **Completion Status:** Completed & Verified.

### Sprint 1 — Architecture & Foundations
- **Sprint Goal:** Implement Django project foundations, custom User model, 5 system roles, and UI layout matching provided design.
- **Planned Features:** Feature 1 (Auth & RBAC), Feature 8 (Base Dashboard & Layout), Feature 21 (Responsive UI).
- **Tasks:**
  - Configure custom `accounts.User` with Role choices (ADMIN, WARDEN, ACCOUNTS, MAINTENANCE, RESIDENT).
  - Implement `@role_required` decorators and session security.
  - Build top navigation bar (`#0060af`), dark slate sidebar (`#1a2634`), and responsive main content area.
- **Testing:** `test_rbac.py` verifying unauthorized redirects and role isolation.
- **Completion Status:** Completed & Verified.

### Sprint 2 — Hostel Operations
- **Sprint Goal:** Implement blocks, rooms, individual beds, capacity constraints, seat applications, and transactional bed allocations.
- **Planned Features:** Feature 2 (Resident Management), Feature 3 (Room & Bed Management), Feature 4 (Seat Application & Allocation), Feature 15 (Waiting List), Feature 16 (Room Transfers).
- **Tasks:**
  - Create `HostelBlock`, `Room`, `Bed`, and `Amenity` models.
  - Enforce atomic bed allocation via `AllocationService.allocate_bed`.
  - Implement waiting list priority queues and room transfer workflows.
- **Testing:** `test_models.py` (UT-001, UT-002) and `test_services.py` (IT-001, IT-002, IT-003).
- **Completion Status:** Completed & Verified.

### Sprint 3 — Financial Management
- **Sprint Goal:** Implement student billing, payment entry, receipt verification, branded PDF generation, fines, refunds, and operating expenses.
- **Planned Features:** Feature 5 (Fee & Payment), Feature 11 (Expense Management), Feature 12 (Fines & Refunds), Feature 14 (Downloadable Receipts).
- **Tasks:**
  - Create `FeeCategory`, `ResidentCharge`, `Payment`, `Fine`, `Refund`, and `HostelExpense` models.
  - Implement ReportLab-powered PDF receipt generator with official branding and verification stamp.
  - Build Accounts Dashboard with real-time aggregates.
- **Testing:** `test_views.py` (IT-007) verifying HTTP 200 and application/pdf headers.
- **Completion Status:** Completed & Verified.

### Sprint 4 — Resident Services & Administration
- **Sprint Goal:** Implement maintenance ticketing, mess meal schedules, visitor gate passes, night attendance, outpass management, and institutional clearances.
- **Planned Features:** Feature 6 (Complaints), Feature 7 (Notices), Feature 9 (Visitors), Feature 10 (Attendance & Outpass), Feature 17 (Checkout & Clearance).
- **Tasks:**
  - Build ticketing lifecycle: SUBMITTED &rarr; ASSIGNED &rarr; IN_PROGRESS &rarr; RESOLVED &rarr; CLOSED.
  - Implement daily meal menus (Breakfast, Lunch, Dinner veg/non-veg) and resident feedback.
  - Create multi-step clearance workflow (Property &rarr; Accounts &rarr; Warden Approval).
- **Testing:** Complaint submission and resolution integration tests.
- **Completion Status:** Completed & Verified.

### Sprint 5 — Operational Controls, Search & Audit
- **Sprint Goal:** Deliver immutable audit trails, scheduled automated reminders, database backup commands, and global search.
- **Planned Features:** Feature 13 (Automated Reminders), Feature 18 (Audit Logs), Feature 19 (Data Export & Backup), Feature 20 (Global Search).
- **Tasks:**
  - Implement `AuditLog` model and `log_audit` helper function.
  - Create management command `python manage.py send_reminders`.
  - Create management command `python manage.py backup_db`.
  - Implement CSV export streaming for residents, rooms, payments, complaints, visitors, and expenses.
- **Testing:** Test backup and reminder commands synchronously.
- **Completion Status:** Completed & Verified.

### Sprint 6 — Quality Assurance, A/B Testing & Delivery
- **Sprint Goal:** Execute test suites, implement controlled A/B testing experiment, establish CI pipeline, and compile project documentation.
- **Planned Features:** Feature 22 (CI Pipeline), Feature 23 (Controlled A/B Testing).
- **Tasks:**
  - Create `.github/workflows/ci.yml` pipeline.
  - Implement A/B testing experiment `DASHBOARD_URGENT_ACTIONS` evaluating Variant A vs Variant B.
  - Run full test suite (16 tests, 100% pass rate).
  - Prepare demonstration fixtures and comprehensive documentation.
- **Completion Status:** Completed & Handed Over.
