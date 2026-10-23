# HMS — Test Plan & Traceable Test Execution Results

## 1. Test Strategy
Testing is organized into five traceable test categories:
1. **Unit Testing (`UT-xxx`):** Mathematical calculations, model validation methods, capacity checks.
2. **Integration Testing (`IT-xxx`):** Multi-model workflows, atomic bed allocations, transfers, PDF streaming.
3. **Security Testing (`SEC-xxx`):** Role-based access control, CSRF verification, IDOR prevention.
4. **Performance Testing (`PERF-xxx`):** High-volume queries, pagination, response times.
5. **Usability & Accessibility Testing (`UX-xxx`):** Responsive viewport behavior, keyboard navigation, color contrast.

---

## 2. Test Cases and Execution Evidence

| Test ID | Requirement ID | Test Objective & Steps | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UT-001** | FR-003 | Room bed capacity calculation (`occupied_beds_count`, `available_beds_count`). | Calculates accurate vacancy without manual counters. | Count matches bed relationships exactly. | **PASS** |
| **UT-002** | FR-003 | Enforce room capacity constraint in `Bed.clean()`. | ValidationError raised if new bed exceeds room capacity. | ValidationError raised as expected. | **PASS** |
| **UT-003** | FR-005 | Resident charge remaining balance calculation (`amount - paid_amount`). | Balance computed accurately across partial payments. | Decimal balance matches remaining amount. | **PASS** |
| **IT-001** | FR-004 | Execute `AllocationService.allocate_bed()` on vacant bed. | Bed marked occupied, resident linked, allocation created atomically. | Transaction committed, all states updated. | **PASS** |
| **IT-002** | FR-004 | Attempt to allocate already occupied bed. | ValidationError raised, transaction aborted. | ValidationError raised, bed occupancy preserved. | **PASS** |
| **IT-003** | FR-016 | Execute `AllocationService.execute_room_transfer()`. | Old bed released, new bed occupied, resident reassigned atomically. | Seamless transition without orphan records. | **PASS** |
| **IT-004** | FR-001 | Submit valid login credentials via POST request. | Session created, user redirected to role-based dashboard. | HTTP 302 redirect to `accounts:dashboard`. | **PASS** |
| **IT-005** | FR-019 | Export CSV data endpoint (`/reports/export/rooms/`). | Streams RFC-compliant CSV with `Content-Disposition: attachment`. | HTTP 200, valid CSV output. | **PASS** |
| **IT-006** | FR-006 | Submit maintenance complaint via resident view. | Ticket record created with unique ticket number and timestamp. | Complaint persisted in database. | **PASS** |
| **IT-007** | FR-014 | Download verified receipt PDF (`/finance/receipts/<no>/download/`). | Streams PDF with `Content-Type: application/pdf`. | HTTP 200, valid ReportLab binary stream. | **PASS** |
| **SEC-001** | FR-001 | Unauthenticated GET request to protected dashboard. | User denied access, redirected to login page. | HTTP 302 redirect to `/accounts/login/`. | **PASS** |
| **SEC-002** | FR-018 | Resident attempts to access `/audit/` (Admin only). | Server raises PermissionDenied (HTTP 403). | HTTP 403 Forbidden received. | **PASS** |
| **SEC-003** | FR-001 | Resident attempts to access user management `/accounts/users/`. | Server raises PermissionDenied (HTTP 403). | HTTP 403 Forbidden received. | **PASS** |
| **SEC-004** | FR-002 | IDOR Check: Resident 1 accesses Resident 2's profile URL. | Server detects mismatch, redirects with warning alert. | HTTP 302 redirect to own dashboard. | **PASS** |
| **SEC-005** | FR-018 | Administrator accesses `/audit/`. | Access granted, log entries displayed. | HTTP 200 OK. | **PASS** |
| **SEC-006** | FR-008 | Hostel Warden accesses `/accounts/dashboard/hostel/`. | Access granted, primary hostel dashboard rendered. | HTTP 200 OK. | **PASS** |

---

## 3. Test Execution Summary

```text
Ran 16 tests in 33.761s
OK (16 Passed, 0 Failed, 0 Errors)
Test Database: SQLite In-Memory / Test Schema
Coverage: Core models, services, RBAC decorators, view endpoints, and PDF generators.
```
