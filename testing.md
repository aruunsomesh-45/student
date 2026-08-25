# 🧪 Mindset Platform — Full-Stack Testing PRD

## 1. Purpose

This document defines the complete testing strategy for the Student-Teacher Mindset & Personality Assessment Platform.

The goal is to validate the entire application against the project PRD, including:

- Frontend/UI
- Responsive behavior
- Accessibility and usability
- Authentication and role-based authorization
- Assessment/quiz flows
- Psychometric scoring
- Student dashboard
- Teacher dashboard
- Student playbook
- Private teacher notes
- PDF generation
- Demo-data seeding
- Backend/Django views and services
- Database integrity
- API/integration behavior
- Environment-variable configuration
- Security
- Error handling
- Performance
- Production readiness

The application is expected to support Student, Teacher, and Admin roles, School/UG/PG academic tiers, tier-specific assessments, VARK/mindset/stress scoring, student results, teacher analytics, private notes, seeded demo data, and PDF reports.

---

## 2. Source-of-Truth Requirements

The test implementation MUST use the project PRD as the functional source of truth.

Core requirements identified from the PRD:

| Area | Requirement |
|---|---|
| Accounts | Custom Django user with Student/Teacher/Admin roles |
| Academic tiers | School, UG, PG |
| Authentication | Signup, login, logout, role-based redirection |
| Authorization | Student/Teacher/Admin access boundaries |
| Assessments | Tier-specific questions |
| Quiz | 15 questions per assessment |
| Categories | VARK, Mindset, Stress, Communication |
| Scoring | Normalized 0–100 scores |
| Persona | Dominant learning persona |
| Student dashboard | Persona, scores, study strategies |
| Teacher dashboard | Roster, metrics, filters, search |
| Teacher playbook | Motivation, communication, stress pillars |
| Teacher notes | Private, persisted, timestamped |
| Demo data | 1 teacher + 25 students + submissions |
| Reports | One-page downloadable PDF |
| UI | Responsive, dark/light mode, animations |
| Database | Relationships and persisted assessment data |
| API/integrations | Every configured external/internal endpoint must work |
| Configuration | URLs/endpoints/secrets must come from environment configuration |

---

# 3. Testing Rules

## 3.1 Test Environment

Before testing:

- [ ] Create a clean virtual environment.
- [ ] Install dependencies from the project's dependency file.
- [ ] Configure a dedicated test environment.
- [ ] Run migrations on the test database.
- [ ] Load required seed/demo data.
- [ ] Start the Django development/test server.
- [ ] Confirm static files and media handling.
- [ ] Confirm all required environment variables are present.
- [ ] Confirm the application starts without configuration errors.

## 3.2 No Hardcoded URLs

All configurable URLs/endpoints MUST be environment-driven.

Inspect:

- `.env`
- `.env.example`
- Django settings
- frontend configuration
- JavaScript configuration
- API service modules
- fetch/axios calls
- redirect configuration
- external-service configuration
- report/download URLs
- authentication endpoints

Search the codebase for hardcoded:

- `http://`
- `https://`
- API base URLs
- localhost URLs
- production domains
- third-party service URLs

Expected behavior:

- [ ] API base URL comes from environment configuration.
- [ ] Frontend API URL comes from environment configuration where applicable.
- [ ] Backend external-service URLs come from environment configuration.
- [ ] No secret/API key is committed to source code.
- [ ] `.env` is ignored by version control.
- [ ] `.env.example` documents required variables without exposing secrets.
- [ ] Changing the configured base URL changes the application behavior without source-code modification.
- [ ] Missing required environment variables produce a clear startup/configuration error.
- [ ] Development and production configurations can use different URLs.

Example expected configuration pattern:

```env
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=True
DATABASE_URL=...
API_BASE_URL=...
FRONTEND_URL=...
```

The exact variable names MUST follow the implementation. Do not invent a second configuration system if one already exists.

---

# 4. Test Levels

Testing is divided into:

1. Static/code/configuration testing
2. Unit testing
3. Backend integration testing
4. Database testing
5. API/integration testing
6. Frontend component/page testing
7. End-to-end testing
8. Responsive testing
9. Accessibility testing
10. Security testing
11. Performance testing
12. Regression testing
13. Production-readiness testing

---

# 5. Test Priority

| Priority | Meaning |
|---|---|
| P0 | Application cannot safely operate without fixing it |
| P1 | Core functionality is broken |
| P2 | Important functionality/degraded UX |
| P3 | Cosmetic/minor issue |

P0 examples:

- Authentication bypass
- Student accessing teacher data
- Teacher accessing another teacher's private notes
- Broken database migrations
- Incorrect assessment scores
- Missing production API URL
- Exposed secrets
- Application cannot start

P1 examples:

- Quiz cannot submit
- Results do not render
- Teacher filters do not work
- PDF cannot be generated

P2 examples:

- Search has minor UX issue
- Tablet layout is awkward
- Loading state is missing

P3 examples:

- Minor spacing inconsistency
- Non-critical animation issue

---

# 6. Environment & Configuration Testing

## 6.1 Environment Variable Inventory

Create a configuration inventory from the actual codebase.

| Variable | Required | Used By | Secret? | Default Allowed? | Test |
|---|---:|---|---:|---:|---|
| Django secret | Yes | Backend | Yes | No | [ ] |
| Database URL/config | Yes | Backend | Yes/No | Depends | [ ] |
| API base URL | If applicable | Frontend/API | No | Depends | [ ] |
| Frontend URL | If applicable | Backend/auth | No | Depends | [ ] |
| External API URL | If applicable | Integration | No | No | [ ] |
| External API key | If applicable | Integration | Yes | No | [ ] |

The final inventory MUST be generated from the actual project rather than assumed variable names.

## 6.2 Configuration Tests

- [ ] Application starts with valid `.env`.
- [ ] Application fails safely when required configuration is missing.
- [ ] Invalid URL configuration is rejected or handled.
- [ ] Development URLs are not accidentally used in production.
- [ ] Production URLs are not accidentally used in local development.
- [ ] No secret values appear in HTML.
- [ ] No secret values appear in JavaScript bundles.
- [ ] No secret values appear in API responses.
- [ ] No secrets appear in logs.
- [ ] No hardcoded external endpoints exist where configuration is expected.

---

# 7. Frontend Testing

## 7.1 Global UI

For every page:

- [ ] Page loads without console errors.
- [ ] Page has correct title.
- [ ] Navigation works.
- [ ] Logo/brand links work.
- [ ] Buttons work.
- [ ] Links work.
- [ ] Forms have visible labels.
- [ ] Loading states work.
- [ ] Empty states work.
- [ ] Error states work.
- [ ] Success states work.
- [ ] Back/forward browser navigation works.
- [ ] Refresh does not unexpectedly destroy valid application state.
- [ ] Images load correctly.
- [ ] Icons load correctly.
- [ ] Fonts load correctly.
- [ ] CSS loads correctly.
- [ ] JavaScript loads without errors.

## 7.2 Landing/Core Pages

- [ ] Landing page renders correctly.
- [ ] CTA links reach the intended flow.
- [ ] Login CTA works.
- [ ] Registration CTA works.
- [ ] Navigation links are correct.
- [ ] Dark/light mode works if available.
- [ ] Animations do not block interaction.
- [ ] Reduced-motion users are not negatively affected.

---

# 8. Authentication Testing

## 8.1 Registration

Student:

- [ ] Student can register.
- [ ] Required fields validate.
- [ ] Invalid email is rejected.
- [ ] Missing required fields are rejected.
- [ ] Password validation works.
- [ ] Duplicate account is rejected.
- [ ] Academic tier can be stored.
- [ ] Role is correctly assigned.
- [ ] Successful registration redirects to the correct student flow.

Teacher:

- [ ] Teacher can register if registration is intended to be public.
- [ ] Teacher role is stored correctly.
- [ ] Teacher is redirected to `/dashboard/teacher/` or the actual configured equivalent.

Admin:

- [ ] Admin cannot be created through an insecure public registration path.
- [ ] Admin permissions are restricted appropriately.

## 8.2 Login

- [ ] Valid credentials succeed.
- [ ] Invalid credentials fail safely.
- [ ] Student is redirected to assessment/student area.
- [ ] Teacher is redirected to teacher dashboard.
- [ ] Admin is redirected to admin area.
- [ ] Session is created correctly.
- [ ] Session expires according to configuration.
- [ ] Logout destroys authentication state.
- [ ] Protected pages reject unauthenticated users.

## 8.3 Authorization

Test every protected route using:

- Anonymous user
- Student
- Teacher
- Admin
- Wrong-owner teacher
- Wrong student

Expected:

- [ ] Students cannot access teacher dashboard.
- [ ] Students cannot access teacher notes.
- [ ] Students cannot modify teacher-only data.
- [ ] Teachers cannot access another teacher's private information unless explicitly permitted.
- [ ] Users cannot modify another user's submission.
- [ ] Admin-only actions require admin permissions.
- [ ] Direct URL manipulation cannot bypass role checks.

---

# 9. Assessment/Quiz Testing

## 9.1 Tier Routing

Test:

- School
- UG
- PG

For each:

- [ ] Correct questions are loaded.
- [ ] Questions from another tier are excluded.
- [ ] Exactly 15 questions are presented where the PRD requires 15.
- [ ] Question order is valid.
- [ ] Choices belong to the correct question.
- [ ] Required answers are enforced.

## 9.2 Quiz UI

- [ ] Progress indicator updates correctly.
- [ ] One answer can be selected as intended.
- [ ] Selection state is visually clear.
- [ ] Keyboard navigation works.
- [ ] Mobile controls are usable.
- [ ] Previous/next behavior works if implemented.
- [ ] Browser refresh behavior is safe.
- [ ] Double-submit is prevented.
- [ ] Submission button cannot cause duplicate submissions.

## 9.3 Submission

- [ ] Valid quiz submission succeeds.
- [ ] Invalid payload is rejected.
- [ ] Missing answers are rejected where required.
- [ ] Unknown question IDs are rejected.
- [ ] Choices from another question cannot be submitted successfully.
- [ ] A student cannot submit answers for another student.
- [ ] Submission is persisted.
- [ ] Submission timestamp is generated.
- [ ] Tier is persisted correctly.

---

# 10. Psychometric Scoring Testing

The PRD defines normalized scoring as:

Score = (Sum of Weights / Max Possible Weight) × 100

## 10.1 Unit Tests

Create deterministic fixtures for:

- All Visual
- All Auditory
- All Kinesthetic
- Mixed VARK
- Maximum Growth
- Minimum Growth
- Maximum Stress
- Minimum Stress
- Boundary values
- Zero-weight answers
- Unexpected/invalid answers

For each:

- [ ] Calculated values are mathematically correct.
- [ ] Scores stay within expected 0–100 bounds.
- [ ] Persona selection is deterministic.
- [ ] Tie handling is deterministic.
- [ ] Invalid payloads fail safely.
- [ ] Scoring does not depend on UI state.

## 10.2 Regression Tests

Every known scoring bug MUST become a permanent automated test.

---

# 11. Student Dashboard Testing

- [ ] Student can view own results.
- [ ] Persona title is correct.
- [ ] Persona summary is correct.
- [ ] VARK scores match stored submission.
- [ ] Growth/mindset score matches stored submission.
- [ ] Stress score matches stored submission.
- [ ] Study strategies are displayed.
- [ ] Dashboard does not expose another student's data.
- [ ] Empty-result state works when no assessment exists.
- [ ] Refresh preserves correct results.
- [ ] Mobile layout works.
- [ ] Charts/progress bars match backend values.

---

# 12. Teacher Dashboard Testing

## 12.1 Roster

- [ ] Teacher can see permitted students.
- [ ] 25+ seeded students render correctly.
- [ ] Student cards contain correct information.
- [ ] No unauthorized student appears.

## 12.2 Metrics

Verify:

- [ ] Total students tested.
- [ ] Dominant class learning modality.
- [ ] Percentage calculations.
- [ ] Stress watchlist count.
- [ ] Empty-cohort calculations.
- [ ] Boundary percentages.

## 12.3 Filters

Test:

- [ ] School filter.
- [ ] UG filter.
- [ ] PG filter.
- [ ] Learning style filter.
- [ ] Stress alert filter.
- [ ] Multiple filters together.
- [ ] Clear filters.
- [ ] No-results state.

## 12.4 Search

- [ ] Search by name.
- [ ] Search by email.
- [ ] Case-insensitive search.
- [ ] Partial search.
- [ ] No-result search.
- [ ] Search combined with filters.
- [ ] Search input is safely handled.

---

# 13. Student Playbook Testing

Verify the three pillars:

1. Motivation cues
2. Communication style
3. Stress triggers

Tests:

- [ ] Correct student is displayed.
- [ ] Correct persona data is displayed.
- [ ] Motivation information is accurate.
- [ ] Communication information is accurate.
- [ ] Stress information is accurate.
- [ ] Teacher can access permitted playbook.
- [ ] Student cannot access teacher-only playbook functionality if prohibited.
- [ ] Invalid student ID is handled.
- [ ] Unauthorized student access is rejected.

---

# 14. Teacher Private Notes Testing

- [ ] Teacher can create a note.
- [ ] Note is persisted.
- [ ] Note timestamp is created.
- [ ] Notes display chronologically.
- [ ] Empty note is rejected.
- [ ] Excessively large input is handled.
- [ ] HTML/script injection is sanitized/escaped.
- [ ] Student cannot view private notes.
- [ ] Unauthorized teacher cannot access notes.
- [ ] Teacher can only modify/delete notes if the feature explicitly supports it.
- [ ] CSRF protection works for POST requests.

---

# 15. PDF Report Testing

- [ ] PDF generation endpoint is accessible only to authorized users.
- [ ] PDF is generated successfully.
- [ ] PDF downloads with correct content type.
- [ ] PDF opens without corruption.
- [ ] Student identity is correct.
- [ ] Persona is correct.
- [ ] Scores are correct.
- [ ] Report is one page where required.
- [ ] Layout is readable.
- [ ] Long names do not break the document.
- [ ] Missing data is handled gracefully.
- [ ] Unauthorized users cannot generate another user's report.

---

# 16. Demo Data / Seed Testing

Run the project's seed command.

Expected:

- [ ] One demo teacher exists.
- [ ] 25 realistic students are created.
- [ ] Students span School/UG/PG.
- [ ] Test submissions are populated.
- [ ] Related records are valid.
- [ ] Running the seed command twice does not create unintended duplicates if idempotency is expected.
- [ ] Seeded passwords are safe and documented for development only.
- [ ] Demo data is never accidentally enabled in production.

---

# 17. Backend Testing

## 17.1 Django Views

For every view:

- [ ] Valid request returns expected status.
- [ ] Invalid request returns expected status.
- [ ] Unauthorized request is rejected.
- [ ] Wrong HTTP method is rejected.
- [ ] Expected template is rendered.
- [ ] Expected context is present.
- [ ] Database query is correct.
- [ ] Redirect destination is correct.
- [ ] Errors are handled safely.

## 17.2 Forms

- [ ] Valid form passes.
- [ ] Required fields validate.
- [ ] Invalid values fail.
- [ ] Boundary values are tested.
- [ ] Malicious values are safely handled.

## 17.3 Services

Test scoring and recommendation services independently from views.

- [ ] Pure business logic is covered.
- [ ] Edge cases are covered.
- [ ] No database dependency exists unless required.
- [ ] Service output is deterministic.

---

# 18. Database Testing

## 18.1 Migration Testing

- [ ] Fresh database can migrate from zero.
- [ ] Existing database can migrate forward.
- [ ] Migration rollback is safe where supported.
- [ ] No migration errors occur.
- [ ] Database schema matches models.

## 18.2 Relationship Testing

Verify:

User → Submission

Question → Choice

Teacher → TeacherNote

Student → TeacherNote

Tests:

- [ ] Foreign keys are correct.
- [ ] Cascade behavior is intentional.
- [ ] Related names work.
- [ ] Orphan records cannot be created accidentally.
- [ ] Deleted users behave according to business rules.

## 18.3 Constraints

- [ ] Required fields cannot be null.
- [ ] Choice weights accept valid ranges.
- [ ] Invalid tiers are rejected.
- [ ] Invalid roles are rejected.
- [ ] Duplicate data is prevented where uniqueness is required.
- [ ] Database indexes exist for high-frequency searches where needed.

## 18.4 Data Integrity

- [ ] Stored score equals calculated score.
- [ ] Stored tier equals assessment tier.
- [ ] Submission belongs to correct student.
- [ ] Teacher notes belong to correct teacher/student.
- [ ] Dashboard aggregates match raw records.

---

# 19. API & Integration Testing

First inventory every API endpoint actually present in the codebase.

For each endpoint record:

| Endpoint | Method | Auth | Input | Output | Env URL | Status |
|---|---|---|---|---|---|---|

For every API:

- [ ] Base URL is configuration-driven.
- [ ] Correct HTTP method is used.
- [ ] Request headers are correct.
- [ ] Authentication is correct.
- [ ] Request payload is validated.
- [ ] Response status is validated.
- [ ] Response schema is validated.
- [ ] Timeout exists.
- [ ] Network errors are handled.
- [ ] Invalid responses are handled.
- [ ] Rate-limit responses are handled.
- [ ] Retry behavior is safe where appropriate.
- [ ] No sensitive data is logged.
- [ ] API secrets are not exposed to the browser.
- [ ] CORS configuration is correct.
- [ ] HTTPS is used in production.

## 19.1 Frontend-to-Backend Integration

Test:

Browser → Request → Django → Database → Response → UI

For every major user action:

- [ ] Request reaches backend.
- [ ] Backend validates input.
- [ ] Database updates correctly.
- [ ] Response is correct.
- [ ] UI updates correctly.
- [ ] Errors propagate correctly.

---

# 20. URL & Routing Testing

Build a complete route inventory.

Test:

- [ ] `/`
- [ ] authentication routes
- [ ] assessment routes
- [ ] student routes
- [ ] teacher dashboard routes
- [ ] playbook routes
- [ ] notes routes
- [ ] report routes
- [ ] admin routes
- [ ] static/media routes as applicable
- [ ] API routes as applicable

For every route:

- [ ] GET works where supported.
- [ ] POST works where supported.
- [ ] Authentication is correct.
- [ ] Authorization is correct.
- [ ] Invalid IDs return proper errors.
- [ ] Invalid methods return proper errors.
- [ ] Redirects are correct.
- [ ] No unexpected 404/500 responses.

---

# 21. Responsive Testing

Test at minimum:

| Device Class | Width |
|---|---:|
| Small mobile | 320px |
| Mobile | 375px |
| Large mobile | 430px |
| Tablet portrait | 768px |
| Tablet landscape | 1024px |
| Laptop | 1280px |
| Desktop | 1440px |
| Large desktop | 1920px |

For every important page:

- [ ] No horizontal overflow.
- [ ] No clipped content.
- [ ] No overlapping cards.
- [ ] Navigation adapts correctly.
- [ ] Buttons remain tappable.
- [ ] Forms fit screen width.
- [ ] Tables/cards adapt appropriately.
- [ ] Text remains readable.
- [ ] Modals fit viewport.
- [ ] Charts remain usable.
- [ ] PDF/download controls remain accessible.
- [ ] Touch targets are usable.
- [ ] Sticky/fixed elements do not cover content.
- [ ] Animations do not cause layout overflow.

Pages:

- [ ] Landing page
- [ ] Login
- [ ] Registration
- [ ] Assessment
- [ ] Student results
- [ ] Teacher dashboard
- [ ] Student playbook
- [ ] Teacher notes
- [ ] PDF/report UI

---

# 22. Browser Compatibility

Test latest stable versions of:

- [ ] Chrome
- [ ] Edge
- [ ] Firefox
- [ ] Safari where available

Verify:

- [ ] Layout
- [ ] Forms
- [ ] JavaScript
- [ ] Animations
- [ ] Authentication
- [ ] Downloads
- [ ] Print/PDF behavior

---

# 23. Accessibility Testing

- [ ] Keyboard-only navigation.
- [ ] Visible focus states.
- [ ] Logical tab order.
- [ ] Semantic headings.
- [ ] Labels associated with inputs.
- [ ] Buttons have accessible names.
- [ ] Images have appropriate alt text.
- [ ] Color is not the only way information is communicated.
- [ ] Contrast is sufficient.
- [ ] Form errors are understandable.
- [ ] Screen-reader-friendly structure.
- [ ] Reduced-motion preference is respected where animations are used.

---

# 24. Security Testing

## Authentication

- [ ] Passwords are never stored in plaintext.
- [ ] Session cookies use secure configuration in production.
- [ ] CSRF protection is enabled.
- [ ] Login brute-force protections are considered.
- [ ] Logout invalidates the session.

## Authorization

- [ ] IDOR testing on student IDs.
- [ ] IDOR testing on submission IDs.
- [ ] IDOR testing on notes.
- [ ] Teacher-to-teacher isolation.
- [ ] Student-to-student isolation.
- [ ] Admin-only functionality protected.

## Input Security

Test:

- [ ] XSS payloads.
- [ ] SQL injection-like input.
- [ ] HTML injection.
- [ ] Template injection attempts.
- [ ] Malformed JSON/API payloads.
- [ ] Oversized inputs.
- [ ] Invalid IDs.
- [ ] Unexpected enum values.

## Secrets

- [ ] `.env` is not committed.
- [ ] Secret keys are not frontend-visible.
- [ ] API keys are not embedded in templates.
- [ ] API keys are not embedded in static JavaScript.
- [ ] Secrets are not logged.

---

# 25. Error Handling

Intentionally trigger:

- Invalid login
- Invalid registration
- Missing question
- Invalid answer
- Missing submission
- Invalid student ID
- Unauthorized request
- Database failure
- API timeout
- Invalid API response
- Missing environment variable
- PDF generation failure
- Missing image/media
- Server error

Verify:

- [ ] User receives a useful error.
- [ ] No stack trace is exposed in production.
- [ ] Sensitive information is not exposed.
- [ ] Error status code is correct.
- [ ] Application remains usable after recoverable errors.

---

# 26. Performance Testing

Measure:

- Initial page load.
- Login response.
- Quiz rendering.
- Quiz submission.
- Student dashboard.
- Teacher dashboard.
- Search.
- Filters.
- Playbook loading.
- Notes submission.
- PDF generation.

For the 25+ student dashboard:

- [ ] No obvious N+1 query problem.
- [ ] Aggregations are efficient.
- [ ] Search remains responsive.
- [ ] Filtering remains responsive.
- [ ] Page does not perform unnecessary full-table work.

Frontend:

- [ ] No unnecessary repeated API calls.
- [ ] Images are optimized.
- [ ] Static assets are efficiently served.
- [ ] Animations remain smooth.
- [ ] Large pages do not freeze the browser.

---

# 27. End-to-End Test Scenarios

## E2E-001 Student Journey

1. Open landing page.
2. Register as student.
3. Select academic tier.
4. Complete login/redirect.
5. Open assessment.
6. Answer 15 questions.
7. Submit assessment.
8. Verify database submission.
9. Verify scoring.
10. Verify persona.
11. Verify student dashboard.
12. Refresh dashboard.
13. Verify results persist.
14. Logout.

Expected: complete journey succeeds without manual intervention.

## E2E-002 Teacher Journey

1. Login as teacher.
2. Open teacher dashboard.
3. Verify 25+ students.
4. Verify aggregate metrics.
5. Filter by School.
6. Filter by UG.
7. Filter by PG.
8. Filter by learning style.
9. Filter stress watchlist.
10. Search by student name.
11. Search by email.
12. Open student playbook.
13. Review three pillars.
14. Add private note.
15. Refresh.
16. Verify note persists.
17. Verify student cannot access the note.

## E2E-003 Authorization Journey

- Login as student.
- Attempt teacher dashboard URL.
- Attempt playbook URL.
- Attempt private-note URL.
- Attempt another student's result URL.

Expected: every unauthorized action is blocked.

## E2E-004 Report Journey

- Login as authorized teacher.
- Open student.
- Generate PDF.
- Download PDF.
- Open PDF.
- Validate identity, persona, scores and layout.

---

# 28. Regression Suite

Every completed feature MUST have automated regression coverage.

Minimum regression groups:

- [ ] Authentication
- [ ] Role authorization
- [ ] Assessment loading
- [ ] Quiz submission
- [ ] Scoring
- [ ] Student results
- [ ] Teacher dashboard
- [ ] Filters
- [ ] Search
- [ ] Playbook
- [ ] Notes
- [ ] PDF
- [ ] Seed command
- [ ] Environment configuration
- [ ] API integrations

---

# 29. Automated Testing Requirements

Recommended Django tests:

```text
apps/
├── accounts/
│   └── tests/
│       ├── test_models.py
│       ├── test_forms.py
│       ├── test_views.py
│       └── test_permissions.py
│
├── assessments/
│   └── tests/
│       ├── test_models.py
│       ├── test_views.py
│       ├── test_scoring.py
│       └── test_submission.py
│
├── dashboard/
│   └── tests/
│       ├── test_student_dashboard.py
│       ├── test_teacher_dashboard.py
│       ├── test_playbook.py
│       └── test_notes.py
│
└── reports/
    └── tests/
        └── test_pdf.py
```

Add end-to-end browser tests for the critical journeys.

---

# 30. Test Data Strategy

Create controlled fixtures for:

- Anonymous user
- Student without submission
- Student with School submission
- Student with UG submission
- Student with PG submission
- Teacher with students
- Teacher without students
- Admin
- High-stress student
- Low-stress student
- Visual-dominant student
- Auditory-dominant student
- Kinesthetic-dominant student
- Student with tied scores
- Invalid/malformed records

Never rely exclusively on random data for deterministic scoring tests.

---

# 31. Test Reporting

Every test failure MUST record:

```text
Test ID:
Feature:
Environment:
URL:
User Role:
Preconditions:
Steps:
Expected:
Actual:
Severity:
Screenshot/Video:
Console Error:
Backend Error:
Database State:
API Request:
API Response:
Likely Root Cause:
Suggested Fix:
Status:
```

Status values:

- PASS
- FAIL
- BLOCKED
- NOT TESTED
- NEEDS REVIEW

---

# 32. Defect Severity

## P0 — Critical

Examples:

- Authentication bypass
- Authorization bypass
- Data leakage
- Exposed secrets
- Corrupted database data
- Incorrect scoring affecting every student
- Production application cannot start

## P1 — High

Examples:

- Quiz submission broken
- Student dashboard broken
- Teacher dashboard broken
- PDF generation broken
- Major API integration failure

## P2 — Medium

Examples:

- Filter failure
- Search edge case
- Responsive issue on a supported device
- Minor data presentation issue

## P3 — Low

Examples:

- Minor spacing
- Cosmetic animation issue
- Non-critical visual inconsistency

---

# 33. Definition of Done

The website is considered fully tested only when:

- [ ] All critical PRD requirements are mapped to tests.
- [ ] All P0 issues are resolved.
- [ ] All P1 issues are resolved or explicitly accepted.
- [ ] Authentication passes.
- [ ] Authorization passes.
- [ ] Assessment flow passes.
- [ ] Scoring tests pass.
- [ ] Student dashboard passes.
- [ ] Teacher dashboard passes.
- [ ] Playbook passes.
- [ ] Private notes pass.
- [ ] PDF generation passes.
- [ ] Database integrity passes.
- [ ] API integrations pass.
- [ ] Environment-variable URL validation passes.
- [ ] No secrets are exposed.
- [ ] Responsive testing passes across required breakpoints.
- [ ] Accessibility baseline passes.
- [ ] Security baseline passes.
- [ ] E2E critical journeys pass.
- [ ] Regression suite passes.
- [ ] Production configuration is validated.
- [ ] Final test report is generated.

---

# 34. Final Full-Stack Test Execution Order

Use this exact order when testing the real codebase:

### Phase 1 — Codebase & Configuration Audit

- [ ] Inspect project structure.
- [ ] Identify frontend.
- [ ] Identify Django apps.
- [ ] Identify database.
- [ ] Identify API/integration modules.
- [ ] Identify all routes.
- [ ] Identify all environment variables.
- [ ] Identify hardcoded URLs.
- [ ] Identify secrets/configuration risks.

### Phase 2 — Backend & Database

- [ ] Run migrations.
- [ ] Run model tests.
- [ ] Run view tests.
- [ ] Run permission tests.
- [ ] Run scoring tests.
- [ ] Run database integrity tests.
- [ ] Run seed command.
- [ ] Validate seeded data.

### Phase 3 — API & Integration

- [ ] Inventory endpoints.
- [ ] Validate environment-driven URLs.
- [ ] Test requests/responses.
- [ ] Test authentication.
- [ ] Test failures/timeouts.
- [ ] Test CORS/CSRF where applicable.
- [ ] Verify no secret exposure.

### Phase 4 — Frontend

- [ ] Test every page.
- [ ] Test every form.
- [ ] Test navigation.
- [ ] Test loading/error/empty states.
- [ ] Test browser console.
- [ ] Test frontend/backend data flow.

### Phase 5 — Responsive

- [ ] 320px
- [ ] 375px
- [ ] 430px
- [ ] 768px
- [ ] 1024px
- [ ] 1280px
- [ ] 1440px
- [ ] 1920px

### Phase 6 — Security

- [ ] Authentication
- [ ] Authorization
- [ ] CSRF
- [ ] XSS
- [ ] IDOR
- [ ] Secret exposure
- [ ] Input validation

### Phase 7 — E2E

- [ ] Student journey
- [ ] Teacher journey
- [ ] Authorization journey
- [ ] PDF journey

### Phase 8 — Regression & Release

- [ ] Run complete automated suite.
- [ ] Run complete manual critical-path suite.
- [ ] Fix P0/P1 defects.
- [ ] Re-test failed cases.
- [ ] Run regression suite.
- [ ] Validate production environment variables.
- [ ] Validate production URLs.
- [ ] Produce final PASS/FAIL report.

---

# 35. Final Acceptance Statement

The application can be marked **FULL-STACK TEST PASSED** only when the implementation satisfies the PRD requirements and all critical user journeys pass across frontend, responsive UI, backend, database, API/integration, security, configuration, and end-to-end testing.

A test must never be marked PASS merely because a page renders. PASS requires verification of the complete data flow where applicable:

```text
UI
 ↓
Request
 ↓
Route
 ↓
View/API
 ↓
Validation
 ↓
Business Logic
 ↓
Database
 ↓
Response
 ↓
UI State
```

For environment-driven integrations:

```text
.env
 ↓
Application Configuration
 ↓
Configured URL
 ↓
API Request
 ↓
External/Internal Service
 ↓
Response
 ↓
Backend/Frontend
```

The final test report MUST identify any missing PRD requirement, hardcoded URL, broken integration, incorrect score, unauthorized data access, database inconsistency, responsive defect, or production configuration problem before release.
