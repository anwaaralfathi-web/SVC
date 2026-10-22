# SVC Assess — Security Review & Remediation Plan

**Scope reviewed:** `svc_assess_ppeng01.py` and `requirements (1).txt` found in the available project files. The deployed Streamlit app, Streamlit settings, Git repository permissions, secrets, and live database were not inspected. Do not treat this report as a live penetration test.

## Immediate finding
The reviewed source uses fixed lecturer/admin PINs (`1234` and `8888`) in the interface and contains a student-ID/password lookup flow backed by a hard-coded `STUDENT_CREDENTIALS` structure. The lecturer workspace runs queries over the submissions table without filtering by authenticated lecturer identity. The code also uses `INSERT OR REPLACE` for a submission ID derived from student + assignment, so another submission for the same pair may overwrite an earlier row. The similarity function calculates a `web_match` from word count and an `ai_pattern_score` from common phrases; these are not reliable internet similarity or AI-writing detection and should not be presented as such.

## Containment artifact included
`svc_assess_ppeng01_emergency_security_hold.py` is an intentionally fail-closed copy. It stops before opening/initializing the database or rendering student data. It is **not** a functioning protected assessment app; it is an emergency containment option while real authentication and authorization are implemented. It does not change or delete the existing database. Do not overwrite the current deployed app without first coordinating downtime and making a verified backup.

## Required remediation before real student use

### P0 — Identity and authorization
1. Disable fixed PINs and all embedded/default student passwords.
2. Integrate college-approved OIDC/SSO using Streamlit's supported authentication flow and server-side secrets.
3. Map the authenticated identity to an approved roster and role. Deny access by default if the identity, role, or roster entry is missing/disabled.
4. Enforce permissions in every data-access function, not only in the UI. Student reads must filter by the authenticated student's verified ID. Lecturer reads/updates/deletes must filter by assigned lecturer/course/cohort. Admin-only actions must check the server-side role.
5. Require re-authentication or suitable step-up confirmation for destructive actions and grade release.

### P0 — Data and hosting
1. Confirm which exact Git commit/file is deployed and who can access the GitHub repository and Streamlit app settings.
2. Do not assume local SQLite files or local uploaded files are durable or backed up on Community Cloud. Move production data to an institution-approved managed database and private object storage, or keep the pilot closed until a supported persistent design is in place.
3. Keep secrets only in Streamlit secrets or an approved secret manager; never commit them. Rotate any secret that may have been exposed.
4. Create encrypted backups, restrict access, document retention/deletion, and test restoration using a separate test environment.
5. Obtain college approval for hosting real student data and for sending submissions to any external AI provider.

### P1 — Submission integrity and file safety
1. Replace `INSERT OR REPLACE` with an explicit insert that creates a new attempt, or a deliberate versioned update with transaction/audit history.
2. Enforce maximum byte size server-side; validate file signatures and parsers, not just extensions; reject malformed/oversized PDFs and DOCX archives; use malware scanning where available; store with generated opaque IDs, not user filenames.
3. Keep uploaded files private and authorize every download against the same row-level policy. Never expose internal filesystem paths.
4. Return generic user-facing errors; log detailed exceptions only in private server logs without student text, passwords, tokens, or secrets.

### P1 — Assessment integrity
1. Remove synthetic `web_match` and heuristic `ai_pattern_score` from any display that implies detection. Label local phrase overlap precisely and show its comparison scope.
2. Treat AI marks as a draft; validate the response against the rubric and retain AI draft and lecturer-approved result separately.
3. Keep audit logs for submission, view/download where feasible, mark edits, release, deletion, and administrative changes. Audit logs must not contain passwords or full submission text.

## Acceptance tests before reopening
- Unauthenticated user cannot access any student, lecturer, admin, assignment, grade, or file data.
- Non-roster identity is denied.
- Student A cannot read/download Student B's submissions or grades, including by changing IDs or query parameters.
- Lecturer A cannot view/update/delete records outside their assigned scope.
- A student cannot access draft grades or release grades.
- Re-submitting does not silently replace a prior attempt.
- Wrong extension, spoofed file signature, oversized file, malformed PDF/DOCX, and empty submission are rejected safely.
- AI timeout/invalid output leaves the submission intact and does not auto-release a grade.
- Audit records identify the authenticated actor and action without leaking secrets or work content.
- A restore test recovers database metadata and uploaded files in a clean environment.
- All tests run against synthetic data; no live grades or student submissions are used for test fixtures.

## Streamlit Community Cloud checklist
- Verify the deployment points to the reviewed commit and correct entrypoint.
- Review app collaborators and GitHub repository collaborators; remove unneeded access.
- Review Secrets for the minimum required credentials and rotate exposed keys.
- Confirm SSO callback/redirect configuration with the college identity provider and use HTTPS.
- Confirm where SQLite/uploads physically persist and what happens on reboot/redeploy. Do not rely on local ephemeral files as the only copy.
- Review logs and repository history for accidental student data, credentials, and API keys.

## Scope limitation
The included emergency hold is a safe containment artifact, not a completed comprehensive production implementation. A working secure release requires the approved college SSO details/identity claims, lecturer-to-course assignment rules, and approved persistent storage design. Do not send passwords, `secrets.toml`, API keys, or real student data in chat.
