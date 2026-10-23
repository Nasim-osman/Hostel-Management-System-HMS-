# HMS — Security & Privacy Assessment (OWASP Top 10)

## 1. Role-Based Access Control (RBAC) Matrix

| Operation / Endpoint | System Admin | Hostel Warden | Accounts Staff | Maintenance Staff | Resident |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Manage User Accounts & Roles** | **Full** | Denied | Denied | Denied | Denied |
| **View Audit Trail Logs** | **Full** | Denied | Denied | Denied | Denied |
| **Manage Rooms & Capacity** | **Full** | **Full** | Read Only | Read Only | Read Only |
| **Review & Allocate Beds** | **Full** | **Full** | Denied | Denied | Denied |
| **Submit Seat Application** | Denied | Denied | Denied | Denied | **Own Only** |
| **Manage Room Transfers** | **Full** | **Full** | Denied | Denied | **Request Own** |
| **Assign Fee Charges** | **Full** | Denied | **Full** | Denied | Denied |
| **Record & Verify Payments** | **Full** | Read Only | **Full** | Denied | Denied |
| **Download Payment Receipts** | **Full** | **Full** | **Full** | Denied | **Own Only** |
| **Manage Maintenance Tickets** | **Full** | **Assign** | Denied | **Resolve** | **Submit Own** |
| **Issue Penalties / Fines** | **Full** | **Full** | **Full** | Denied | View Own |
| **Process Checkout Clearance**| **Full** | **Final Sign**| **Dues Sign** | **Prop Sign** | **Request Own** |
| **Log Campus Visitors** | **Full** | **Full** | Denied | Denied | View Own |
| **Mark Roll-Call Attendance** | **Full** | **Full** | Denied | Denied | View Own |
| **Export Operational CSV Data** | **Full** | **Full** | **Finance Only**| Denied | Denied |

---

## 2. OWASP Top 10 Vulnerability Mitigations

### 1. Broken Access Control (A01:2021)
- **Mitigation:** Server-side decorators (`@role_required`) enforce authorization before view code executes. Insecure Direct Object References (IDOR) are blocked by verifying user ownership (e.g. `request.user == resident.user`).

### 2. Cryptographic Failures (A02:2021)
- **Mitigation:** Passwords hashed with PBKDF2 algorithm using SHA-256 hash and unique salts. Sensitive keys and database passwords stored in `.env` variables excluded from Git.

### 3. Injection (A03:2021)
- **Mitigation:** Django ORM uses parameterized SQL queries exclusively. No raw string interpolation is permitted.

### 4. Insecure Design (A04:2021)
- **Mitigation:** Database transactions (`transaction.atomic`) with row-level locks prevent race conditions during concurrent bed allocations. Multi-step checkout clearance requires three independent departmental approvals.

### 5. Security Misconfiguration (A05:2021)
- **Mitigation:** `DEBUG` mode is toggleable via `.env`. Custom error handlers prevent stack trace leakage to students.

### 6. Vulnerable and Outdated Components (A06:2021)
- **Mitigation:** Direct dependencies pinned in `requirements.txt`. Continuous integration automated pipeline scans for updates and vulnerabilities.

### 7. Identification and Authentication Failures (A07:2021)
- **Mitigation:** Django's built-in session engine manages sessions with HTTPOnly cookies, automatic expiration, and session regeneration on password change.

### 8. Software and Data Integrity Failures (A08:2021)
- **Mitigation:** Strict schema validation on model saves. Cryptographic hashes protect downloaded fixtures and backups.

### 9. Security Logging and Monitoring Failures (A09:2021)
- **Mitigation:** Centralized `AuditLog` records actor, action, timestamp, module, target representation, and IP address for every sensitive administrative operation.

### 10. Server-Side Request Forgery (SSRF) (A10:2021)
- **Mitigation:** HMS makes no arbitrary external server-side requests based on unvalidated user input.
