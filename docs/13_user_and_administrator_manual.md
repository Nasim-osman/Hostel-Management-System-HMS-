# HMS — User & Administrator Operations Manual

## 1. Demo Credentials Quick Reference
For evaluators, instructors, and demonstration testing, the system provides pre-configured demo credentials:

| Role | Username | Password | Default Landing View | Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `demo1234` | `/accounts/dashboard/hostel/` | System configuration, user account management, audit logs. |
| **Hostel Warden** | `warden` | `demo1234` | `/accounts/dashboard/hostel/` | Seat allocations, waiting list, room transfers, outpass approval, notices. |
| **Accounts Staff** | `accounts` | `demo1234` | `/finance/dashboard/` | Fee charge creation, payment entry, receipt verification, operating expenses. |
| **Maintenance Staff** | `maintenance` | `demo1234` | `/complaints/dashboard/` | Inspecting assigned tickets, logging repair notes, resolving tickets. |
| **Student Resident** | `resident_mike` | `demo1234` | `/residents/dashboard/` | Submitting seat applications, viewing room details, paying dues, downloading receipts. |

*(Note: On the login page `/accounts/login/`, you can simply click any of the 1-Click Demo buttons to log in instantly!)*

---

## 2. Standard Operating Procedures (SOPs)

### SOP-01: Reviewing Applications & Allocating a Bed (Warden)
1. Log in as `warden`.
2. Navigate to **Allocations** via the sidebar or top banner.
3. Click on **Review &rarr;** next to any pending application.
4. If approved, click **Approve for Bed Allocation**.
5. Select a vacant bed from the dropdown and click **Confirm Bed Allocation**.
6. The system atomically locks the bed, marks it occupied, links the resident, and updates capacity counters in real-time.

### SOP-02: Recording a Payment & Issuing a Branded Receipt (Accounts)
1. Log in as `accounts`.
2. Navigate to **Payment** &rarr; click **+ Record Payment**.
3. Select the resident and optional linked charge.
4. Input amount, payment method (UPI / Bank Transfer / Cash), and transaction reference.
5. Click **Record & Issue Receipt**.
6. The charge status updates automatically to Paid or Partially Paid.
7. Click the **PDF** button on the payment list to download the official branded receipt.

### SOP-03: Logging and Resolving a Complaint (Resident & Maintenance)
1. Log in as `resident_mike`.
2. Click **+ Log Ticket** on the resident dashboard.
3. Enter title (e.g., "Leaking Bathroom Faucet"), category ("Plumbing"), and description.
4. Click **Submit Ticket**.
5. Log in as `warden` &rarr; click ticket &rarr; assign to `maintenance`.
6. Log in as `maintenance` &rarr; open the work order &rarr; input resolution notes &rarr; select **Resolved** &rarr; click **Save Resolution Update**.

### SOP-04: Outpass Application & Return Verification (Resident & Warden)
1. Log in as `resident_mike` &rarr; click **Request Outpass**.
2. Input purpose (e.g. "Weekend Family Visit"), destination address, departure time, and parent phone.
3. Log in as `warden` &rarr; navigate to **Outpass** &rarr; click **Approve**.
4. When student leaves, click **Mark Departed**.
5. When student returns, click **Mark Returned** to log the return timestamp and clear curfew status.
