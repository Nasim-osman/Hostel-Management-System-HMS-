# HMS — System Architecture Document

## 1. Architectural Style & Overview
HMS is built on a 3-tier, clean **Model-View-Template (MVT)** architectural pattern, extended with an explicit **Service Layer** for multi-model atomic transactions.

```
+-------------------------------------------------------------------+
|                        PRESENTATION LAYER                         |
|   HTML5 + Tailwind CSS + Vanilla JS + Chart.js + Reusable Cards   |
+---------------------------------+---------------------------------+
                                  | HTTP / HTTPS Requests
                                  v
+-------------------------------------------------------------------+
|                     APPLICATION & ROUTING LAYER                   |
|          Django URL Dispatcher & Role-Based Middleware            |
|       (@role_required, AuthenticationMiddleware, CSRF Guard)      |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                      BUSINESS / SERVICE LAYER                     |
|           apps.allocations.services.AllocationService             |
|           apps.finance.receipts.generate_receipt_pdf              |
|           apps.audit.models.log_audit                             |
|           apps.notifications.management.commands.send_reminders   |
+---------------------------------+---------------------------------+
                                  | ORM Queries / Transactions
                                  v
+-------------------------------------------------------------------+
|                        DATA PERSISTENCE LAYER                     |
|                  Django ORM & Relational Database                 |
|             (Development: SQLite / Production: PostgreSQL)        |
+-------------------------------------------------------------------+
```

## 2. Key Architectural Decisions
1. **Modular App Separation:** Each operational domain resides in a self-contained Django application under `apps/` (accounts, rooms, residents, allocations, finance, complaints, dining, visitors, attendance, notices, audit, notifications, abtesting, reports).
2. **Encapsulated Service Functions:** Critical business logic (such as bed allocation, room transfers, and clearance releases) is isolated in `AllocationService` with `@transaction.atomic` decorators to eliminate race conditions and orphaned database states.
3. **Defense-in-Depth Authorization:** Role checks are never performed solely in template conditionals. Every view is decorated with server-side decorators (`@role_required`, `warden_or_admin_only`, `resident_access_only`) which raise `PermissionDenied` (HTTP 403) or redirect unauthorized actors.
4. **Environment-Agnostic Database:** Relational mapping uses standard Django ORM migrations, allowing seamless transitions from SQLite to PostgreSQL by updating `.env` parameters without altering application code.
