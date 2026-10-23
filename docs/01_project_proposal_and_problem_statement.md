# HMS — Project Proposal & Problem Statement

## 1. Executive Summary & Identity
- **Official Project Name:** HMS
- **Full Project Name:** HMS — Hostel Management System
- **Repository / Directory:** `hms`
- **Application Type:** Enterprise Web Application for Residential Educational Institutions
- **Development Stack:** Python 3.12, Django 5.0 (MVT), Vanilla CSS & Tailwind styling, Chart.js, ReportLab PDF, SQLite (Development) / PostgreSQL (Production).

## 2. Problem Statement
Educational residential institutions (universities, colleges, and polytechnics) typically accommodate hundreds or thousands of students. Traditional hostel administration suffers from deep operational inefficiencies:
1. **Fragmented Paper-Based Records:** Student admission forms, room allocation binders, physical registers, and outpass paper slips are prone to loss, damage, duplicate assignments, and audit manipulation.
2. **Conflicting Room & Bed Allocations:** Manual room assignment frequently creates double-booking or over-capacity conditions without transactional safeguards.
3. **Unstructured Fee Tracking & Leakage:** Hand-written receipts, untracked partial fee installments, and lack of reconciliations create accounting discrepancies between accounts departments and hostel wardens.
4. **Informal Complaint Resolution:** Resident maintenance complaints (plumbing leaks, electrical outages, Wi-Fi breakdowns) submitted informally via word-of-mouth or WhatsApp groups lack accountability, prioritization, and resolution SLAs.
5. **Security & Visitor Vulnerabilities:** Physical gate registers fail to provide real-time occupancy awareness or verify visitor authorization and overnight curfew returns.

## 3. Project Objectives
HMS centralizes, digitizes, and automates the complete operational lifecycle of student residential facilities:
- **Centralize Resident Records:** Maintain unique resident profiles, emergency contact records, academic courses, and admission statuses.
- **Transactional Bed Allocation:** Ensure zero double-booking through atomic database transactions and strict capacity enforcement.
- **Financial Accountability:** Provide transparent fee structures, track partial and complete payments, generate branded tamper-evident PDF receipts, and log operating expenses.
- **Digital Service Desk:** Track maintenance complaints from submission to assignment and resolution with time-stamped notes.
- **Access Control & Security:** Log visitor gate passes, monitor night roll-call attendance, and enforce outpass departure/return tracking.
- **Strict Role-Based Security:** Protect resident privacy by isolating records across 5 distinct roles: Administrator, Warden, Accounts, Maintenance, and Resident.

## 4. Scope and Institutional Assumptions
- **In-Scope:** All 23 mandatory features across residential accommodation, seat queues, transfers, room clearances, fees, receipts, maintenance ticketing, visitor logging, night attendance, announcements, in-app notifications, CSV exports, automated reminders, and A/B dashboard testing.
- **Explicit Exclusions:** External commercial SMS gateways or live banking APIs requiring paid vendor contracts are omitted in favor of robust in-app notifications and verified transaction references.
