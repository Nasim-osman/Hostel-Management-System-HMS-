# HMS — Software Requirements Specification (SRS)

## 1. Introduction
### 1.1 Purpose
This Software Requirements Specification (SRS) establishes the complete functional and non-functional requirements for the **HMS (Hostel Management System)**, designed for educational collegiate residences.

### 1.2 Document Conventions
- Requirements are uniquely identified using prefixes:
  - `FR-xxx`: Functional Requirements
  - `NFR-xxx`: Non-Functional Requirements
  - `BR-xxx`: Business Rules

---

## 2. Overall System Description
HMS implements a 3-tier architecture following Django's Model-View-Template (MVT) pattern, encapsulating business logic into dedicated service layers and ensuring atomic transactional guarantees at the database level.

---

## 3. Functional Requirements (Mapping All 23 Features)

| Requirement ID | Feature Name | Responsible Role | Preconditions | Main Behavior & Acceptance Criteria | Test Case ID | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-001** | Authentication & RBAC | All Users | Valid account credentials | Authenticates users using PBKDF2 hashing; redirects users to role-specific dashboard; denies unauthorized access with HTTP 403. | UT-004, SEC-001, SEC-002 | Complete |
| **FR-002** | Resident Management | Warden, Admin | Authorized session | Registers student profiles with unique student ID, academic department, emergency contacts, and status. | UT-001, IT-004 | Complete |
| **FR-003** | Room & Bed Management | Warden, Admin | Block configured | Tracks hostel blocks, room types, capacities, individual beds, and occupancy states; prevents over-capacity bed additions. | UT-001, UT-002 | Complete |
| **FR-004** | Seat Application & Allocation | Resident, Warden | Resident registered | Allows residents to submit seat applications; wardens approve and atomically allocate vacant beds via `AllocationService`. | IT-001, IT-002 | Complete |
| **FR-005** | Fee & Payment Management | Accounts, Admin | Charge created | Records payments against resident charges; calculates outstanding balances; updates status from UNPAID to PAID. | UT-003, IT-004 | Complete |
| **FR-006** | Complaint & Maintenance Management | Resident, Maintenance | Active resident | Residents submit tickets with room association; wardens assign to staff; staff updates status to Resolved with notes. | IT-006 | Complete |
| **FR-007** | Notice & Announcement Management | Warden, Admin | Staff session | Creates and publishes announcements targeted to All, Residents, or Staff; residents only see published circulars. | IT-004 | Complete |
| **FR-008** | Role-Specific Dashboards & Reports | All Roles | Authenticated user | Primary hostel dashboard with 8 KPI cards (Rooms, Payments, Amenities, Donut Occupancy, Mess Menu, Tickets, Visitors, Reports). | SEC-006 | Complete |
| **FR-009** | Visitor Management | Warden, Admin | Resident active | Logs visitor identity, destination room, and purpose; issues gate pass; records check-out timestamp. | IT-004 | Complete |
| **FR-010** | Attendance & Outpass | Warden, Resident | Resident active | Records daily night roll-call attendance; residents submit outpasses; wardens approve and monitor overdue returns. | IT-004 | Complete |
| **FR-011** | Expense Management | Accounts, Admin | Staff session | Logs hostel operating expenditures across Utilities, Mess, Repairs, and Cleaning with invoice references. | IT-004 | Complete |
| **FR-012** | Fines & Refunds | Accounts, Warden | Active record | Issues disciplinary fines to residents; records caution deposit refunds upon institutional checkout. | IT-004 | Complete |
| **FR-013** | Automated Reminders | System / Cron | Scheduled process | Management command `send_reminders` alerts users of upcoming fee due dates, overdue outpasses, and urgent tickets. | IT-004 | Complete |
| **FR-014** | Downloadable PDF Receipts | Resident, Accounts | Verified payment | Generates branded ReportLab PDF receipts with unique receipt number, resident name, amount, and verifier stamp. | IT-007 | Complete |
| **FR-015** | Seat Waiting List | Warden, Admin | Pending application | Maintains prioritized queue for students awaiting accommodation vacancies; moves students automatically. | IT-001 | Complete |
| **FR-016** | Room Transfer Workflow | Resident, Warden | Resident assigned | Submits transfer request; wardens select vacant target bed; atomically releases old bed and reassigns new bed. | IT-003 | Complete |
| **FR-017** | Checkout & Institutional Clearance | Resident, Warden, Accounts | Resident active | Multi-step sign-off: Property clearance &rarr; Accounts dues clearance &rarr; Warden final approval releasing bed. | IT-004 | Complete |
| **FR-018** | Immutable Audit Logs | Admin | Sensitive event | Records timestamp, actor, action, module, target object, and client IP address; protected from alteration. | SEC-002, SEC-005 | Complete |
| **FR-019** | Data Export & Backup | Admin, Accounts | Staff session | Exports tabular records as RFC-compliant CSV files; management command `backup_db` creates timestamped backups. | IT-005 | Complete |
| **FR-020** | Global Search & Filtering | All Roles | Authenticated user | Search bar on top navigation searches residents, rooms, tickets, notices, and payments with permission scoping. | IT-004 | Complete |
| **FR-021** | Accessible & Responsive UI | All Users | Any web client | Responsive layouts across desktop, tablet, and mobile; WCAG AA contrast, visible focus rings, semantic HTML. | UX-001 | Complete |
| **FR-022** | Automated CI Pipeline | Developer / CI | GitHub push / PR | GitHub Actions workflow validates Python 3.12, migration consistency, system checks, and executes test suite. | SEC-001 | Complete |
| **FR-023** | Controlled A/B Testing | Warden, Admin | Experiment active | Evaluates Variant A (standard grid) vs Variant B (urgent actions banner); tracks impressions, clicks, and CTR lift. | IT-004 | Complete |

---

## 4. Non-Functional Requirements (NFR)
- **NFR-001 (Security):** All user passwords stored using PBKDF2 SHA-256 with individual salts. CSRF tokens enforced on all POST forms.
- **NFR-002 (Integrity):** Database transactions (`transaction.atomic`) enforce atomic operations on bed allocation, transfers, and fee reconciliations.
- **NFR-003 (Privacy):** Strict IDOR protection ensures residents cannot view or modify another student's profile, tickets, or receipts.
- **NFR-004 (Performance):** Page render times under 200ms for typical database queries via ORM `select_related` and `prefetch_related`.
- **NFR-005 (Reliability):** Automated daily backup command generates both JSON fixtures and SQLite binary snapshots.
- **NFR-006 (Usability):** Role-specific navigation and quick-login demonstration switchers for immediate evaluation.

---

## 5. Requirements Traceability Matrix (RTM)

```text
[Requirement ID]  -->  [App / Module]  -->  [Database Model]       -->  [Automated Test Case]  -->  [Status]
FR-001 (Auth)     -->  accounts        -->  accounts.User          -->  SEC-001, SEC-002       -->  VERIFIED
FR-002 (Resident) -->  residents       -->  ResidentProfile        -->  UT-001, IT-004         -->  VERIFIED
FR-003 (Rooms)    -->  rooms           -->  Room, Bed, Amenity     -->  UT-001, UT-002         -->  VERIFIED
FR-004 (Alloc)    -->  allocations     -->  SeatAllocation         -->  IT-001, IT-002         -->  VERIFIED
FR-005 (Finance)  -->  finance         -->  ResidentCharge, Payment-->  UT-003, IT-004         -->  VERIFIED
FR-006 (Tickets)  -->  complaints      -->  Complaint              -->  IT-006                 -->  VERIFIED
FR-007 (Notices)  -->  notices         -->  Notice                 -->  IT-004                 -->  VERIFIED
FR-008 (Dashboard)-->  dashboard       -->  All aggregate models   -->  SEC-006                -->  VERIFIED
FR-009 (Visitors) -->  visitors        -->  VisitorLog             -->  IT-004                 -->  VERIFIED
FR-010 (Outpass)  -->  attendance      -->  OutpassRequest         -->  IT-004                 -->  VERIFIED
FR-011 (Expense)  -->  finance         -->  HostelExpense          -->  IT-004                 -->  VERIFIED
FR-012 (Fines)    -->  finance         -->  Fine, Refund           -->  IT-004                 -->  VERIFIED
FR-013 (Reminders)-->  notifications   -->  InAppNotification      -->  IT-004                 -->  VERIFIED
FR-014 (Receipts) -->  finance         -->  Payment                -->  IT-007                 -->  VERIFIED
FR-015 (Waitlist) -->  allocations     -->  WaitingListEntry       -->  IT-001                 -->  VERIFIED
FR-016 (Transfer) -->  allocations     -->  RoomTransferRequest    -->  IT-003                 -->  VERIFIED
FR-017 (Checkout) -->  allocations     -->  CheckoutClearance      -->  IT-004                 -->  VERIFIED
FR-018 (Audit)    -->  audit           -->  AuditLog               -->  SEC-002, SEC-005       -->  VERIFIED
FR-019 (Export)   -->  reports         -->  All exportable models  -->  IT-005                 -->  VERIFIED
FR-020 (Search)   -->  reports         -->  Cross-model query      -->  IT-004                 -->  VERIFIED
FR-021 (UI/UX)    -->  templates       -->  Base layout, tailwind  -->  UX-001                 -->  VERIFIED
FR-022 (CI/CD)    -->  .github         -->  GitHub Actions runner  -->  SEC-001                -->  VERIFIED
FR-023 (A/B Test) -->  abtesting       -->  Experiment, MetricEvent-->  IT-004                 -->  VERIFIED
```
