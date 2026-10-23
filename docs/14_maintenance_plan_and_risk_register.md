# HMS — Maintenance Plan & Institutional Risk Register

## 1. System Maintenance Plan
To ensure high availability and data integrity throughout the academic year, HMS follows scheduled maintenance policies:

| Cadence | Maintenance Activity | Responsible Role | Execution Procedure |
| :--- | :--- | :--- | :--- |
| **Daily (02:00 AM)** | Database Backup & Snapshots | System Daemon / Admin | Execute `python manage.py backup_db`. Verify backup file size and persistence in `backups/`. |
| **Daily (08:00 AM)** | Automated Reminder Notifications | System Daemon / Warden | Execute `python manage.py send_reminders`. Notifies residents of dues and overdue outpasses. |
| **Weekly** | Audit Trail Inspection | System Administrator | Review `/audit/` for privilege escalations, unauthorized export attempts, or anomalous logins. |
| **Monthly** | Database Optimization & Vacuuming | Database Administrator | Execute `VACUUM ANALYZE` (PostgreSQL) or `VACUUM` (SQLite) to maintain query response times. |
| **Quarterly** | Dependency Security Patching | DevOps Engineer | Run `pip list --outdated`, review CVE bulletins, test patches in staging, and update `requirements.txt`. |

---

## 2. Institutional Risk Register

| Risk ID | Description & Impact | Probability | Impact | Mitigation Strategy | Risk Owner |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **RSK-01** | Concurrent bed allocation conflict during high-traffic admission semester. | Medium | High | Atomic database transactions with row-level locks (`select_for_update`) reject simultaneous conflicting requests. | Software Architect |
| **RSK-02** | Insecure Direct Object Reference (IDOR) exposing student emergency contacts or invoices. | Low | High | Strict server-side ownership checks (`request.user == resident.user`) in view logic. | Security Engineer |
| **RSK-03** | Data loss due to unexpected hardware or storage failure. | Low | Critical | Automated dual-format backups (JSON data fixtures and database binary snapshots) archived off-server. | System Administrator |
| **RSK-04** | Disputed waiting list priority or accusations of manual favoritism. | Medium | Medium | Automated FIFO queue numbering with immutable timestamps and visible queue positions. | Hostel Warden |
| **RSK-05** | Unauthorized modification of fee receipts or waiver entries. | Low | High | Financial records require explicit accounts verification; all fee operations generate immutable audit log entries. | Accounts Officer |
