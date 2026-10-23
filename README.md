# HMS — Hostel Management System

[![HMS CI Pipeline](https://github.com/hms/hms/actions/workflows/ci.yml/badge.svg)](https://github.com/hms/hms/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Tests](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

> **Official Project Name:** HMS  
> **Full Title:** HMS — Hostel Management System  
> **Repository Folder:** `hms`

HMS is an enterprise-grade web application developed to centralize, digitize, and automate residential hostel operations for universities and collegiate institutions. It replaces manual paper registers and fragmented spreadsheets with a secure, role-based platform covering admissions, transactional room/bed allocation, fee accounting, branded PDF receipt generation, maintenance ticketing, visitor logging, night roll-call attendance, outpass tracking, and empirical A/B testing.

---

## 📸 Interface Preview & Design Fidelity
The interface is designed to match standard university residential administrative portals:
- **Header:** Rich Royal Blue (`#0060af`) with quick search, notification bell with unread badge, and profile menu.
- **Sidebar:** Dark Slate Navy (`#1a2634`) with vertical navigation icons and labels.
- **Dashboard:** 8 high-contrast operational cards:
  - **Rooms:** Total 200, Occupied 150, Vacant 50
  - **Payment:** Paid ₹ 1,20,345 & Unpaid ₹ 20,345
  - **Amenities:** Light, Water, Wifi, Laundry, Hot Water status
  - **Tenants:** Donut ring showing 75% occupancy (Capacity 500, Occupied 375)
  - **Mess:** Today's meal (Breakfast, Lunch, Dinner veg/non-veg)
  - **Tickets:** Unsolved issues feed (Mike Ross, Jennifer Grint, Casey Allen, Tina Harris, Rick Butcher)
  - **Visitors:** Active security log with room locations
  - **Reports:** Vacancy and fee collection summaries

---

## 🚀 Key Features (All 23 Implemented)

1. **Authentication & Role-Based Access Control:** Secure password hashing (PBKDF2 SHA-256), session security, and server-side role enforcement across 5 roles.
2. **Resident Management:** Student registration, unique resident IDs (`HMS-RES-2026-xxx`), academic programs, emergency contacts, and profile updates.
3. **Room & Bed Management:** Blocks, floors, room types, bed-level tracking, and strict capacity enforcement preventing overbooking.
4. **Seat Application & Allocation:** Student seat applications, warden approvals, and atomic transactional bed allocations (`AllocationService`).
5. **Fee & Payment Management:** Resident charges, installment balances, payment entry, and automatic invoice settlement.
6. **Complaint & Maintenance Management:** Digital service desk tracking tickets from Submission &rarr; Assignment &rarr; In Progress &rarr; Resolution.
7. **Notice & Announcement Management:** Official administrative circulars with audience targeting (All, Residents, Staff).
8. **Role-Specific Dashboards:** Custom landing views for Administrators, Wardens, Accounts, Maintenance Staff, and Residents.
9. **Visitor Management:** Visitor check-in, host resident identification, destination tracking, and security gate pass issuance.
10. **Attendance & Outpass:** Daily night roll-call attendance recording, outpass applications, and overdue curfew tracking.
11. **Expense Management:** Tracking operating expenditures across utilities, mess supplies, housekeeping, and repairs.
12. **Fines & Refunds:** Disciplinary penalty management and caution deposit refunds upon institutional checkout.
13. **Automated Reminders:** Scheduled background command (`python manage.py send_reminders`) alerting users of due fees, overdue outpasses, and urgent complaints.
14. **Downloadable PDF Receipts:** ReportLab-powered official receipts with unique receipt numbers, resident details, and accounts verification stamp.
15. **Seat Waiting List:** Automatic FIFO queue priority management for students awaiting accommodation vacancies.
16. **Room Transfer Workflow:** Resident transfer requests and atomic bed reassignments without dangling or orphaned states.
17. **Checkout & Clearance Workflow:** Multi-departmental sign-off (Property &rarr; Accounts &rarr; Warden Approval) releasing beds.
18. **Immutable Audit Logs:** Security audit trail recording actor, action, timestamp, module, target item, and client IP address.
19. **Data Export & Backup:** Authorized RFC-compliant CSV exports and administrative backup command (`python manage.py backup_db`).
20. **Global Search & Filtering:** Unified search bar querying residents, rooms, tickets, payments, and notices with permission scoping.
21. **Accessible & Responsive UI:** Responsive layouts across desktop, tablet, and mobile; WCAG AA contrast, visible focus rings, and semantic HTML5.
22. **Automated CI Pipeline:** GitHub Actions workflow executing Django checks, migration validation, and automated test suites.
23. **Controlled A/B Testing:** Live controlled experiment (`DASHBOARD_URGENT_ACTIONS`) evaluating Variant A vs Variant B with real-time conversion metrics.

---

## 👥 User Roles & Demo Credentials

For evaluation and demonstration testing, the system includes pre-configured demo accounts (password: `demo1234`):

| Role | Username | Password | Default Dashboard | Key Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `demo1234` | `/accounts/dashboard/hostel/` | Full system oversight, user account management, audit logs, database backups. |
| **Hostel Warden** | `warden` | `demo1234` | `/accounts/dashboard/hostel/` | Seat allocation, waiting list, room transfers, outpass approvals, notices. |
| **Accounts Staff** | `accounts` | `demo1234` | `/finance/dashboard/` | Fee invoicing, payment entry, receipt verification, operating expenses. |
| **Maintenance Staff** | `maintenance` | `demo1234` | `/complaints/dashboard/` | Assigned work orders, status updates, repair resolution logs. |
| **Student Resident** | `resident_mike` | `demo1234` | `/residents/dashboard/` | Personal profile, room view, fee history, ticket submission, outpass requests. |

*(Note: On the login page `/accounts/login/`, you can use the **1-Click Demo Buttons** to log in as any role immediately without manual typing!)*

---

## 🛠️ Technology Stack
- **Backend:** Python 3.12, Django 5.0 (MVT architecture)
- **Database:** SQLite (default for development) / PostgreSQL (production-ready)
- **Frontend:** Django Templates, Tailwind CSS (CDN), Vanilla JavaScript, Chart.js
- **Document Generation:** ReportLab 5.0 (PDF Receipts), Python `csv` module (Data Exports)
- **Testing:** Django Test Runner & Pytest (Unit, Integration, Security, RBAC)
- **CI/CD:** GitHub Actions (`.github/workflows/ci.yml`)

---

## 💻 Local Installation & Setup

### Prerequisites
- Python 3.12+ installed
- Git installed

### 1. Clone & Set Up Environment
```bash
# Clone the repository
git clone <repository-url> hms
cd hms

# Create and activate Python virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 2. Apply Migrations & Seed Demo Data
```bash
# Apply database schema migrations
python manage.py migrate

# Populate realistic demo records matching the dashboard image
python manage.py seed_data
```

### 3. Run Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your web browser. You will be redirected to the login page where you can use the 1-Click Demo buttons to explore any user role!

---

## 🧪 Running Automated Tests

HMS includes 16 automated test cases covering model constraints, transactional services, security boundaries, and PDF generation.

```bash
# Run the complete test suite
python manage.py test --verbosity=2
```

### Test Suite Summary:
```text
Creating test database for alias 'default'...
Found 16 test(s).
System check identified no issues (0 silenced).
................
----------------------------------------------------------------------
Ran 16 tests in 33.761s

OK
Destroying test database for alias 'default'...
```

---

## ⚙️ Administrative Commands

### Automated Reminder Daemon
Scans for due/overdue fees, overdue student outpasses, and urgent unassigned complaints:
```bash
python manage.py send_reminders
```

### Database Backup & Snapshot Command
Creates timestamped JSON data fixtures and database snapshots in `backups/`:
```bash
python manage.py backup_db
```

---

## 📂 Project Architecture & Directory Structure

```text
hms/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated Continuous Integration workflow
├── apps/
│   ├── accounts/                  # Custom User model, RBAC decorators, authentication
│   ├── rooms/                     # Blocks, Rooms, Beds, Amenities (Light, Water, Wifi, etc.)
│   ├── residents/                 # ResidentProfile, emergency contacts, student portal
│   ├── allocations/               # SeatApplication, AllocationService, Transfers, Clearance
│   ├── finance/                   # Charges, Payments, Receipts, Fines, Refunds, Expenses
│   ├── complaints/                # Maintenance work orders, categories, resolution logs
│   ├── dining/                    # Daily MealMenu (Breakfast, Lunch, Dinner), feedback
│   ├── visitors/                  # VisitorLog, campus gate pass generation, check-in/out
│   ├── attendance/                # Night roll-call attendance, OutpassRequest, curfew tracking
│   ├── notices/                   # Administrative announcements & bulletin board
│   ├── audit/                     # Immutable security audit trail
│   ├── notifications/             # In-app notifications & automated reminder daemon
│   ├── abtesting/                 # Controlled A/B testing experiment & metrics engine
│   └── reports/                   # Operational analytics, global search, CSV exports
├── backups/                       # Automated administrative backup store
├── config/                        # Django project root settings, URLs, WSGI, ASGI
├── docs/                          # Formal Software Engineering course deliverables
│   ├── 01_project_proposal_and_problem_statement.md
│   ├── 02_stakeholder_and_feasibility_analysis.md
│   ├── 03_software_requirements_specification_srs.md
│   ├── 04_agile_development_plan_and_backlog.md
│   ├── 05_system_architecture_and_components.md
│   ├── 06_database_design_and_erd.md
│   ├── 07_uml_and_dfd_diagrams.md
│   ├── 08_ui_ux_design_rationale.md
│   ├── 09_test_plan_and_traceable_test_cases.md
│   ├── 10_security_and_privacy_assessment.md
│   ├── 11_ab_testing_methodology_and_findings.md
│   ├── 12_ci_cd_and_deployment_guide.md
│   ├── 13_user_and_administrator_manual.md
│   ├── 14_maintenance_plan_and_risk_register.md
│   └── 15_final_project_report.md
├── static/                        # CSS, design tokens, JavaScript
├── templates/                     # Reusable Django HTML5 templates & dashboard views
├── tests/                         # Unit, integration, security, and RBAC test suites
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── manage.py                      # Django administrative management entry point
└── requirements.txt               # Pinned Python package dependencies
```

---

## 📚 Complete Documentation Index
All formal Software Engineering course documentation is organized under the [`docs/`](docs/) directory:
- [01. Project Proposal & Problem Statement](docs/01_project_proposal_and_problem_statement.md)
- [02. Stakeholder & Feasibility Analysis](docs/02_stakeholder_and_feasibility_analysis.md)
- [03. Software Requirements Specification (SRS)](docs/03_software_requirements_specification_srs.md)
- [04. Agile Scrum Development Plan & Sprint Backlog](docs/04_agile_development_plan_and_backlog.md)
- [05. System Architecture & Component Design](docs/05_system_architecture_and_components.md)
- [06. Database Design & Entity Relationships](docs/06_database_design_and_erd.md)
- [07. UML, DFD, Sequence & State Diagrams (Mermaid)](docs/07_uml_and_dfd_diagrams.md)
- [08. UI/UX Design System & Layout Rationale](docs/08_ui_ux_design_rationale.md)
- [09. Test Plan & Traceable Execution Results](docs/09_test_plan_and_traceable_test_cases.md)
- [10. Security & Privacy Assessment (OWASP Top 10)](docs/10_security_and_privacy_assessment.md)
- [11. A/B Testing Methodology & Evaluation Report](docs/11_ab_testing_methodology_and_findings.md)
- [12. CI/CD Pipeline & Deployment Guide](docs/12_ci_cd_and_deployment_guide.md)
- [13. User & Administrator Operations Manual](docs/13_user_and_administrator_manual.md)
- [14. Maintenance Plan & Risk Register](docs/14_maintenance_plan_and_risk_register.md)
- [15. Final Software Engineering Project Report](docs/15_final_project_report.md)

---

## 🔒 Security & Privacy Notice
- Passwords are encrypted using Django's PBKDF2 with SHA-256 algorithm.
- Production deployments must generate a fresh `SECRET_KEY` and set `DEBUG=False` in `.env`.
- Cross-Site Request Forgery (CSRF) protection is enforced on every form.
- Insecure Direct Object References (IDOR) are strictly prevented by server-side session checks.
