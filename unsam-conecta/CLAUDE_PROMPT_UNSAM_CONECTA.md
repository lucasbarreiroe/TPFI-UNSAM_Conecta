# SYSTEM PROMPT & ARCHITECTURE SPECIFICATION FOR AI ASSISTANT (CLAUDE / COPILOT)
## Context: UNSAM Conecta - Software MVP Generation

**Role:** You are an Expert Software Architect, Full-Stack Developer, and UI/UX Designer. 
**Task:** Build the MVP for "UNSAM Conecta", a centralized university platform for event discovery, management, and analytics (Group 6 Project).
**Target Deployment Environment:** Render (Web Services for backend/frontend, PostgreSQL managed database).

---

### 1. PROJECT OVERVIEW & VALUE PROPOSITION
**UNSAM Conecta** solves the "information gap" and fragmentation of academic, cultural, and sports events at the National University of San Martin (UNSAM). 
It centralizes event offerings into a single, self-managed calendar. 
* **Users:** Students, Teachers, Staff (Consumers) / Academic Units & External Allies (Organizers).
* **Core Value:** 1-click registration, personalized recommendations, automated reminders, and institutional metrics dashboards.
* **Sustentability:** The architecture must account for "Premium Accounts" for external entities.

### 2. ARCHITECTURAL DRIVERS & QUALITY ATTRIBUTES (Software Engineering Alignment)
Based on Software Engineering best practices (Attribute-Driven Design & 4+1 Architectural View Model):
* **Availability & Scalability (Risk Mitigation):** The system must handle traffic spikes (e.g., mass event registration). The API must be **stateless** to allow horizontal scaling behind a load balancer. Provide solutions like a "virtual waiting room" logic or queue if traffic exceeds thresholds.
* **Performance:** Fast calendar loading. Use database indexing for event dates, tags, and categories.
* **Security:** JWT-based authentication. Strict Role-Based Access Control (RBAC) separating `USER` (Students/Staff), `ORGANIZER` (Referents), and `ADMIN`. Secure password hashing.
* **Modifiability:** Use a Layered Architecture (Routes -> Controllers -> Services -> Data Access). 
* **Testability:** Write unit and integration tests using **Given-When-Then** (BDD) structure to avoid ambiguities.

### 3. TECH STACK DIRECTIVE
* **Backend API:** Node.js with Express.js (or Python FastAPI if preferred, but strictly strongly typed).
* **Database:** PostgreSQL with Prisma ORM (or SQLAlchemy for Python).
* **Frontend (UI):** React (Vite) + Tailwind CSS + Lucide Icons.
* **Background Jobs:** `node-cron` (or Celery) for sending 24h and 1h event reminders.
* **Deployment:** Render (`render.yaml` configuration + Dockerfile).

---

### 4. DATA MODEL (Schema Guidelines)
You must define the following core entities to satisfy the User Stories:
* **User:** `id`, `email`, `passwordHash`, `role` (USER, ORGANIZER, EXTERNAL_PREMIUM), `fullName`, `dni`, `phone`, `interests` (Array of Strings), `preferredNotificationChannel` (EMAIL, PHONE).
* **Event:** `id`, `title`, `description`, `organizerId`, `category` (ECyT, EPyG, EH, etc.), `location`, `startTime`, `endTime`, `capacity`, `currentEnrollment`, `status`, `tags`.
* **Registration:** `id`, `userId`, `eventId`, `status` (CONFIRMED, CANCELLED), `createdAt`.
* **Review/Survey:** `id`, `registrationId`, `rating` (1 to 5), `comment`, `createdAt`.

---

### 5. API SPECIFICATION (Strict RESTful Endpoints)
Generate cleanly separated API endpoints. Include request validation.

**Epic 1: Auth, Exploration & Personalization (Calendar)**
* `POST /api/auth/register` (Include interests & preferred notification channel)
* `POST /api/auth/login` (Returns JWT)
* `GET /api/events` (Optimized for the Calendar View. Supports query params: `?category=`, `?startDate=`, `?tags=`, `?recommendedForUser=true`).
* `GET /api/events/:id`

**Epic 2: Inscriptions, Retention & Reminders**
* `POST /api/events/:id/register` (1-Click Registration: Creates a Registration, checks capacity limits transactionally to prevent overbooking).
* `POST /api/events/:id/cancel` (Frees up capacity).
* `POST /api/registrations/:id/review` (Submit post-event rating 1-5 and text).

**Epic 3: Institutional Automanagement & Metrics**
* `POST /api/events` (Protected: ORGANIZER. Fields: Name, School/Company, Dates, Description, Filters/Tags).
* `PUT /api/events/:id` | `DELETE /api/events/:id`
* `GET /api/metrics/dashboard` (Protected: ORGANIZER. Returns aggregated data: total enrollments, average stars, pie/bar chart formats).

---

### 6. UI/UX GUIDELINES
* **Theme:** Clean, modern university branding. Professional aesthetic.
* **Calendar View:** Interactive, responsive grid/list. Users must be able to filter by category (Academic, Sports, Cultural).
* **1-Click Action:** The "Enroll" (Inscribirse) button must be prominent, frictionless, and provide immediate visual feedback.
* **Dashboard:** Use Chart.js or Recharts to display visual metrics for Organizers (Pie charts for categories/attendance, Bar charts for ratings).
* **Accessibility:** Ensure WCAG compliance (contrast, aria-labels). Mobile-first approach is mandatory, as students will use phones via QR codes.

---

### 7. STEP-BY-STEP EXECUTION PLAN FOR AI ASSISTANT
AI Assistant, follow these steps strictly when generating the codebase:

**STEP 1: Initialize Project, Architecture & Database Setup**
* Initialize the backend framework. 
* Setup the Database schema as defined above.
* Create a Dockerfile and `render.yaml` for Render deployment.

**STEP 2: Core Architecture & Auth**
* Implement server, global error handling, and request validation middleware.
* Implement JWT Authentication and RBAC middleware.

**STEP 3: CRUD API Implementation (The Core Logic)**
* Build the Events, Registrations, and Reviews services.
* **Critical:** Ensure transactional integrity for the Registration logic. When a user registers, `currentEnrollment` must increment safely to avoid race conditions causing overbooking (Database Row Locking or Atomic Updates).

**STEP 4: Background Workers (Hypothesis Validation)**
* Implement the notification scheduler (`cron`).
* Create a job that checks events starting in 24 hours and 1 hour, and simulates sending notifications to enrolled users based on their `preferredNotificationChannel`. This is crucial for validating the MVP hypothesis.

**STEP 5: Frontend & Dashboard Integration**
* Scaffold the React frontend components.
* Build the 3 main views: 
    1. Explore/Calendar View (Filters and recommendations). 
    2. User Profile (My Registrations & Surveys). 
    3. Organizer Dashboard (Visual Metrics & Event Creation Form).

**STEP 6: Quality Assurance & Testing**
* Generate unit tests using the **Given-When-Then** format. 
* *Example:* `GIVEN a registered student, WHEN they click cancel registration, THEN the capacity is freed and the event agenda is updated.`

---

### 8. INITIATION PROMPT
**PROMPT TO AI:** "Acknowledge these instructions. Begin by outputting the full Database Schema file (e.g., `schema.prisma` or equivalent models), followed by a detailed directory structure for the MVP. Do not write the full code yet. Await my explicit command to generate each subsequent module step-by-step."
