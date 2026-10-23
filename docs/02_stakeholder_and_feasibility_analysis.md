# HMS — Stakeholder & Feasibility Analysis

## 1. Stakeholder Analysis

| Stakeholder Group | Primary Interests & Goals | Responsibilities & System Interactions | Potential Pain Points / Concerns |
| :--- | :--- | :--- | :--- |
| **Institutional Management** | Campus safety, audit compliance, financial oversight, resource utilization. | Reviews executive occupancy reports, revenue dashboards, and system audit logs. | System reliability, data breaches, regulatory compliance. |
| **Hostel Wardens** | Discipline, fair room allocation, emergency response, visitor control. | Reviews seat applications, assigns beds, approves outpasses, issues notices, signs off clearances. | High administrative overhead, disputes regarding waitlist order. |
| **Accounts Staff** | Error-free fee collections, receipt issuance, expense management, refund auditing. | Enters payments, reconciles dues, generates PDF receipts, processes deposits and fines. | Accidental duplicate entries, reconciliation mismatches. |
| **Maintenance Staff** | Clear job assignments, priority indicators, tracking spare parts/work status. | Inspects assigned tickets, performs repairs, logs resolution details. | Unclear complaint descriptions, lack of access to resident rooms. |
| **Residents (Students)** | Fair seat allocation, transparent fee records, timely complaint resolution, outpasses. | Submits applications, tracks dues, downloads receipts, logs tickets, requests outpasses. | Privacy leaks, delays in maintenance, complex interfaces. |

---

## 2. Feasibility Study

### 2.1 Technical Feasibility
- **Platform Maturity:** Python 3.12 and Django 5.0 provide a battle-tested MVT framework with built-in ORM, security protections (CSRF, SQL injection prevention, XSS escaping), and cryptographic password hashing (PBKDF2 SHA-256).
- **Client Requirements:** The presentation layer utilizes standard HTML5, CSS3, and modern Vanilla JavaScript, requiring no heavy client-side compiler, ensuring fast loading across desktop, tablet, and mobile browsers.
- **Verdict:** Highly Feasible.

### 2.2 Operational Feasibility
- The system mirrors standard collegiate hostel workflows (Seat Application &rarr; Review &rarr; Allocation &rarr; Outpass &rarr; Checkout Clearance).
- The intuitive visual dashboard (top royal blue navbar, dark slate sidebar, and high-contrast statistical cards) reduces user onboarding time to under 15 minutes.
- **Verdict:** Highly Feasible.

### 2.3 Economic Feasibility
- The selected stack is entirely open-source (Python, Django, Tailwind CDN, Chart.js, ReportLab, SQLite/PostgreSQL), requiring zero proprietary software licensing fees.
- Hosting can be deployed on standard commodity Linux virtual machines or cloud containers.
- **Verdict:** Highly Feasible.

### 2.4 Legal & Privacy Feasibility
- Adheres to data minimization principles. Personal student data (emergency contacts, room assignments, payment histories) are protected through strict server-side role-based access control (RBAC).
- Insecure direct object references (IDOR) are prevented by verifying session ownership on every protected endpoint.
- **Verdict:** Highly Feasible.
