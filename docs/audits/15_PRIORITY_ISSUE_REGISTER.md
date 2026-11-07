# VoltCore Apex Academia — Complete LMS Current Status Audit
# 15. Priority Issue Register

**Audit Date**: November 7, 2026  
**Auditor**: Principal Software Quality Assurance Architect & Security Analyst  
**Audit Location**: `docs/audits/15_PRIORITY_ISSUE_REGISTER.md`

---

## 1. Issue Classification Rubric

- **Critical**: Severe security vulnerability, arbitrary code execution, or immediate data loss risk.
- **High**: Major architectural breakdown, authentication bypass, or core feature failure.
- **Medium**: Partial defect, test regression, configuration gap, or performance inefficiency.
- **Low**: Minor visual anomaly, code duplication, or cosmetic inconsistency.

---

## 2. Priority Issue Register Table

| Issue ID | Description | Severity | Affected Module | Evidence | User / Security / Performance Impact | Recommended Solution | Complexity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SEC-001** | Arbitrary Code Execution via Python `eval()` | **Critical** | `backend/vlsi_physical_design_engine.py` (L256), `backend/digital_electronics_engine.py` (L327) | `eval(expr, {"__builtins__": None}, safe_env)` | **Security**: Object traversal via `().__class__.__bases__[0].__subclasses__()` allows full server RCE. | Replace `eval()` with `ast.parse()` and a restricted AST NodeVisitor. | Low (2–3 hours) |
| **AUTH-001**| Un-guarded Static Frontend Routes | **High** | `src/pages/*.astro` (`enterprise-admin`, `faculty-admin`) | Astro pages render without checking client auth token or redirecting to `/login`. | **Security**: Unauthenticated visitors can view admin and faculty interfaces. | Implement client-side Auth Context & Route Guard in `MainLayout.astro` or Astro middleware. | Medium (4–6 hours) |
| **TEST-001**| 13 Legacy Institutional Test Failures | **Medium** | `tests/test_phase11_collaboration.py`, `tests/test_phase8_concurrency_staging.py`, etc. | `pytest tests/ -q` reports 13 failures expecting `"Madras Institute of Technology"`. | **User**: False-alarm CI build failures on GitHub Actions. | Update test assertions to match sanitized institutional branding (`"Autonomous Engineering Cluster"`). | Low (1 hour) |
| **DB-001**  | Fragmented Dual-Database Architecture | **Medium** | `backend/*.py`, `voltcore_lms.db`, `voltcore_telemetry.db` | Duplicate tables (`student_portfolios`, `study_groups`) exist in both databases. | **Data Integrity**: Inconsistent persistence depending on which API endpoint writes the record. | Unify all schemas into `voltcore_lms.db` or create an explicit router in `sqlite_wal_optimizer.py`. | Medium (4–5 hours) |
| **ARCH-001**| Monolithic Server Architecture | **Medium** | `attendance_server.py` | Monolithic file spanning 9,739 lines of code and 430 routes. | **Performance / Maintainability**: Slower IDE indexing, difficult code review. | Refactor routes into modular Flask Blueprints (`routes/vlsi.py`, `routes/mna.py`, etc.). | High (8–10 hours) |
| **DEP-001** | Client-Backend API Origin Gap | **Medium** | `src/components/*.jsx`, `docker-compose.yml` | React islands fetch `http://localhost:5000` rather than configurable domain. | **User**: Mixed Content / CORS blocks when frontend is deployed to HTTPS GitHub Pages. | Introduce `PUBLIC_API_URL` environment configuration in Astro. | Low (2 hours) |
| **SEC-002** | Hardcoded Fallback JWT Secret Key | **Medium** | `docker-compose.yml`, `backend/security_auth.py` | `MIT_CHROMEPET_ECE_SECURE_JWT_KEY_2026_@P3X` used as default. | **Security**: Predictable token signing key if environment variable is omitted. | Require startup to crash with an error if `VOLTCORE_JWT_SECRET` is unset in production. | Low (30 mins) |
| **PERF-001**| Aggressive `client:load` Island Hydration | **Low** | `src/pages/*.astro`, `src/components/*.jsx` | Off-screen islands (DSO, MNA Workbench) load immediately on initial page request. | **Performance**: Main-thread JavaScript execution delays initial mobile rendering. | Switch off-screen components to `client:visible` or `client:idle`. | Low (1 hour) |
| **ROUT-001**| Missing Direct Route Alias `/stm32-academy` | **Low** | `src/pages/` | Files live at `/embedded-systems/stm32-academy/`, direct navigation to `/stm32-academy` 404s. | **User**: Broken links for users attempting direct URL navigation. | Add Astro redirect `/stm32-academy` $\to$ `/embedded-systems/stm32-academy`. | Low (15 mins) |
| **UI-001**  | Redundant Duplicate React Components | **Low** | `src/components/` | `ResearchDiscoveryHub` vs `ResearchInnovationHub`, `SecurityAuditDashboard` vs `SecurityIntegrityHub`. | **Maintainability**: Confusing component selection and increased bundle footprint. | Deprecate and remove redundant duplicate components. | Low (2 hours) |

---

## 3. Defect vs. Architectural Recommendation Separation

### Actual Defects (Must be Corrected)
- `SEC-001`: Python `eval()` vulnerability in expression parsers.
- `TEST-001`: 13 legacy test assertions failing in Pytest.
- `ROUT-001`: Missing route redirect for `/stm32-academy`.

### Architectural Enhancements (Planned Improvements)
- `AUTH-001`: Client-side route guard in Astro.
- `DB-001`: Unification of dual SQLite databases.
- `ARCH-001`: Blueprint refactoring of `attendance_server.py`.
- `DEP-001`: Configurable `PUBLIC_API_URL` for cloud hosting.
