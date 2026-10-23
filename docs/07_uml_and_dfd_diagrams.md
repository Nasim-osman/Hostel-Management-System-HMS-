# HMS — UML, Data Flow, and System Diagrams

This document contains all formal architectural, behavioral, and data-flow diagrams for the **HMS (Hostel Management System)**, rendered using standard Mermaid syntax.

---

## 9.1 System Context Diagram

```mermaid
graph TD
    Admin["System Administrator"] -->|System Config, User Roles, Audit Logs| HMS["HMS (Hostel Management System)"]
    Warden["Hostel Warden / Manager"] -->|Room Management, Seat Allocations, Outpasses, Notices| HMS
    Accounts["Accounts Staff"] -->|Fee Invoicing, Payment Verification, Expenses| HMS
    Maintenance["Maintenance Staff"] -->|Complaint Updates, Facility Status| HMS
    Resident["Student Resident"] -->|Seat Application, Tickets, Outpass, Fee View| HMS
    
    HMS -->|Receipt PDFs, Financial Exports| Accounts
    HMS -->|Live Occupancy & Roll-Call| Warden
    HMS -->|Assigned Work Orders| Maintenance
    HMS -->|In-App Alerts & Notifications| Resident
```

---

## 9.2 Use Case Diagram

```mermaid
graph LR
    subgraph Actors
        A((System Admin))
        W((Hostel Warden))
        AC((Accounts Staff))
        M((Maintenance Staff))
        R((Resident))
    end

    subgraph HMS System
        UC1[Manage Users & Roles]
        UC2[View Audit Logs]
        UC3[Manage Rooms & Capacity]
        UC4[Review Applications & Allocate Beds]
        UC5[Manage Waiting List & Transfers]
        UC6[Publish Official Notices]
        UC7[Record & Verify Payments]
        UC8[Generate Branded PDF Receipts]
        UC9[Manage Hostel Expenses]
        UC10[Submit & Track Maintenance Tickets]
        UC11[Assign & Resolve Maintenance Tickets]
        UC12[Request Outpasses & Check Night Attendance]
        UC13[Log Campus Visitors & Gate Passes]
        UC14[Initiate & Approve Checkout Clearance]
        UC15[View Dashboard & Export CSV Reports]
    end

    A --> UC1
    A --> UC2
    A --> UC15
    W --> UC3
    W --> UC4
    W --> UC5
    W --> UC6
    W --> UC12
    W --> UC13
    W --> UC14
    W --> UC15
    AC --> UC7
    AC --> UC8
    AC --> UC9
    AC --> UC14
    AC --> UC15
    M --> UC11
    R --> UC4
    R --> UC8
    R --> UC10
    R --> UC12
    R --> UC14
```

---

## 9.3 Data Flow Diagrams (DFDs)

### DFD Level 0 (Context Level)
```mermaid
graph TD
    User["Hostel Users (Admin, Warden, Staff, Resident)"] -->|Credentials, Forms, Requests| HMS_Core["0.0 HMS Application Engine"]
    HMS_Core -->|Dashboards, Reports, Alerts, PDF Receipts| User
    HMS_Core <-->|Read / Write Operational Data| DB[(HMS Relational Database)]
```

### DFD Level 1 (Major Subsystems)
```mermaid
graph TD
    Actor["User / Staff / Resident"] -->|Auth Credentials| P1["1.0 Authentication & Session Control"]
    P1 -->|Session Token & User Role| P2["2.0 Hostel Allocation Subsystem"]
    P1 -->|Role Verification| P3["3.0 Finance & Invoicing Subsystem"]
    P1 -->|Role Verification| P4["4.0 Maintenance Ticket Subsystem"]
    P1 -->|Role Verification| P5["5.0 Security, Visitors & Attendance"]

    P2 <-->|Allocations, Rooms, Beds| D1[(Rooms & Occupancy Store)]
    P3 <-->|Charges, Payments, Receipts| D2[(Financial Ledger Store)]
    P4 <-->|Tickets, Progress Notes| D3[(Maintenance Store)]
    P5 <-->|Gate Passes, Roll-Call, Outpasses| D4[(Attendance & Security Store)]
    
    P1 -.->|Security Events| D5[(Audit Log Store)]
    P2 -.->|Bed Transfers, Allocations| D5
    P3 -.->|Receipt Verifications| D5
```

---

## 9.4 Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    USER ||--o| RESIDENT_PROFILE : has
    USER ||--o{ AUDIT_LOG : generates
    HOSTEL_BLOCK ||--|{ ROOM : contains
    ROOM ||--|{ BED : contains
    RESIDENT_PROFILE ||--o| BED : assigned_to
    
    RESIDENT_PROFILE ||--o{ SEAT_APPLICATION : submits
    SEAT_APPLICATION ||--o| SEAT_ALLOCATION : fulfills
    SEAT_APPLICATION ||--o| WAITING_LIST_ENTRY : queues
    
    RESIDENT_PROFILE ||--o{ RESIDENT_CHARGE : incurs
    FEE_CATEGORY ||--o{ RESIDENT_CHARGE : defines
    RESIDENT_CHARGE ||--o{ PAYMENT : settles
    
    RESIDENT_PROFILE ||--o{ COMPLAINT : reports
    ROOM ||--o{ COMPLAINT : locates
    USER ||--o{ COMPLAINT : assigned_maintenance
    
    RESIDENT_PROFILE ||--o{ VISITOR_LOG : visited_by
    RESIDENT_PROFILE ||--o{ OUTPASS_REQUEST : applies
    RESIDENT_PROFILE ||--o{ ATTENDANCE_RECORD : marked_for
    RESIDENT_PROFILE ||--o| CHECKOUT_CLEARANCE : undergoes
```

---

## 9.5 Sequence Diagrams

### 1. User Authentication
```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Django_Auth as Accounts View
    participant DB as Database
    
    User->>Browser: Enters Username & Password
    Browser->>Django_Auth: POST /accounts/login/
    Django_Auth->>DB: Query User & Verify PBKDF2 Password Hash
    alt Credentials Valid
        DB-->>Django_Auth: User Record & Role
        Django_Auth->>Django_Auth: Create Authenticated Session
        Django_Auth-->>Browser: HTTP 302 Redirect to Role Dashboard
    else Invalid Credentials
        Django_Auth-->>Browser: Render login.html with error alert
    end
```

### 2. Seat Application & Approval
```mermaid
sequenceDiagram
    actor Resident
    actor Warden
    participant View as Allocations Module
    participant DB as Database

    Resident->>View: POST /allocations/applications/apply/
    View->>DB: Create SeatApplication (Status = PENDING)
    DB-->>Resident: Application Confirmed (Ref #)

    Warden->>View: GET /allocations/applications/
    View->>DB: Fetch Pending Applications
    DB-->>Warden: Render Application Details
    Warden->>View: POST review_application (action = 'approve')
    View->>DB: Update SeatApplication (Status = APPROVED)
    View-->>Warden: Ready for Bed Allocation
```

### 3. Bed Allocation (Atomic Transaction)
```mermaid
sequenceDiagram
    actor Warden
    participant Service as AllocationService
    participant DB as Database

    Warden->>Service: allocate_bed(resident, bed, actor)
    Service->>DB: BEGIN TRANSACTION
    Service->>DB: SELECT FOR UPDATE bed WHERE id=bed.id
    alt Bed is Occupied
        DB-->>Service: is_occupied == True
        Service-->>Warden: ValidationError: Bed already occupied!
        Service->>DB: ROLLBACK
    else Bed is Vacant
        Service->>DB: UPDATE bed SET is_occupied = True
        Service->>DB: UPDATE resident SET current_bed = bed, status = ACTIVE
        Service->>DB: INSERT INTO seat_allocation
        Service->>DB: UPDATE seat_application SET status = ALLOCATED
        Service->>DB: COMMIT TRANSACTION
        Service-->>Warden: Allocation Confirmed Successfully
    end
```

### 4. Payment Recording & Verification
```mermaid
sequenceDiagram
    actor Accounts
    actor Resident
    participant Finance as Finance Module
    participant PDF as ReportLab Generator
    participant DB as Database

    Accounts->>Finance: POST /finance/payments/record/
    Finance->>DB: BEGIN TRANSACTION
    Finance->>DB: INSERT Payment (Status = VERIFIED, Receipt = HMS-REC-XXXX)
    Finance->>DB: UPDATE ResidentCharge (paid_amount += amount)
    Finance->>DB: COMMIT TRANSACTION
    Finance-->>Accounts: Payment Verified & Stored

    Resident->>Finance: GET /finance/receipts/HMS-REC-XXXX/download/
    Finance->>Finance: Verify session user matches payment resident
    Finance->>PDF: generate_receipt_pdf(payment)
    PDF-->>Resident: Stream PDF with Content-Disposition attachment
```

### 5. Complaint Submission & Resolution
```mermaid
sequenceDiagram
    actor Resident
    actor Warden
    actor Maintenance
    participant System as Complaints View
    participant DB as Database

    Resident->>System: POST /complaints/submit/ (Title, Category, Room)
    System->>DB: INSERT Complaint (Status = SUBMITTED)
    DB-->>Resident: Ticket Created (Ref # HMS-TICK-XXXX)

    Warden->>System: Assign ticket to Maintenance Staff
    System->>DB: UPDATE Complaint (assigned_to = staff, status = ASSIGNED)

    Maintenance->>System: POST /complaints/resolve/ (Status = RESOLVED, notes)
    System->>DB: UPDATE Complaint (status = RESOLVED, resolved_at = NOW())
    System-->>Maintenance: Status updated successfully
```

### 6. Room Transfer Workflow
```mermaid
sequenceDiagram
    actor Resident
    actor Warden
    participant Service as AllocationService
    participant DB as Database

    Resident->>Service: Submit Transfer Request (Reason, Target Room)
    Warden->>Service: execute_room_transfer(transfer_req, new_bed, warden)
    Service->>DB: BEGIN TRANSACTION
    Service->>DB: Deactivate current allocation
    Service->>DB: Release current bed (is_occupied = False)
    Service->>DB: Occupy new bed (is_occupied = True)
    Service->>DB: Update resident current_bed = new_bed
    Service->>DB: Create new active SeatAllocation
    Service->>DB: Set transfer_req status = COMPLETED
    Service->>DB: COMMIT TRANSACTION
    Service-->>Warden: Room transfer executed atomically
```

### 7. Checkout & Clearance Workflow
```mermaid
sequenceDiagram
    actor Resident
    actor PropertyStaff as Property / Maintenance
    actor AccountsStaff as Accounts Officer
    actor Warden
    participant System as Clearance Service
    participant DB as Database

    Resident->>System: Request Checkout Clearance
    PropertyStaff->>System: Approve Property Clearance (Keys returned, fixtures intact)
    AccountsStaff->>System: Verify Dues Cleared (Zero balance remaining)
    Warden->>System: Final Sign-off
    System->>System: Verify Property AND Accounts checks are TRUE
    System->>DB: Release Bed (is_occupied = False)
    System->>DB: Set resident current_bed = NULL, status = CHECKED_OUT
    System->>DB: Mark clearance status = COMPLETED
    System-->>Resident: Official Institutional Clearance Certificate
```

---

## 9.6 State Transition Diagrams

### Seat Application Lifecycle
```mermaid
stateDiagram-v2
    [*] --> PENDING: Resident Submits Application
    PENDING --> APPROVED: Warden Reviews & Approves
    PENDING --> WAITLISTED: Capacity Full / Queued
    PENDING --> REJECTED: Ineligible / Incomplete
    WAITLISTED --> APPROVED: Vacancy Occurs
    APPROVED --> ALLOCATED: Bed Assigned by Warden
    ALLOCATED --> [*]
```

### Complaint Lifecycle
```mermaid
stateDiagram-v2
    [*] --> SUBMITTED: Resident Logs Ticket
    SUBMITTED --> ASSIGNED: Warden Assigns Staff
    ASSIGNED --> IN_PROGRESS: Staff Initiates Repair
    IN_PROGRESS --> RESOLVED: Repair Completed & Notes Added
    RESOLVED --> CLOSED: Resident Confirms Satisfaction
    CLOSED --> [*]
```

---

## 9.7 Deployment Topology

```mermaid
graph TD
    Client["Client Web Browser (Desktop / Mobile)"] -->|HTTPS (Port 443)| WebServer["Reverse Proxy (Nginx)"]
    WebServer -->|Static / Media Files| StaticStore["Static Directory (/staticfiles, /media)"]
    WebServer -->|WSGI Proxy (Port 8000)| DjangoApp["Gunicorn / Django Application Server"]
    DjangoApp -->|Database Connection| PostgresDB[(PostgreSQL / SQLite Database)]
```
