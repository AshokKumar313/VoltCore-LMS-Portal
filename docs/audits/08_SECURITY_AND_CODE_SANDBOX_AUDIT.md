# VoltCore Apex Academia — Complete LMS Current Status Audit
# 08. Security and Code Sandbox Audit

**Audit Date**: November 7, 2026  
**Auditor**: Senior Cybersecurity Analyst & Application Security Specialist  
**Audit Location**: `docs/audits/08_SECURITY_AND_CODE_SANDBOX_AUDIT.md`

---

## 1. Executive Security Evaluation

VoltCore Apex Academia adopts a hybrid architecture to isolate student code execution from the server host. By shifting dynamic microcontroller simulation (ESP32, Arduino) client-side into sandboxed browser iframes (Wokwi) and implementing custom cycle-accurate software emulators in Python, the platform avoids the severe security pitfalls of executing arbitrary un-sandboxed C/C++ compiler toolchains on the host operating system.

However, targeted static inspection identified **one high-severity vulnerability** in dynamic Python expression parsing and several medium-severity configuration risks.

---

## 2. Student Code Execution Vectors & Sandboxing

| Code Execution Domain | Execution Environment | Isolation Boundary | Host Escape Risk | Status |
| :--- | :--- | :--- | :--- | :--- |
| **C / C++ Firmware** | Client-Side Wokwi Simulator | Browser Iframe / WebAssembly Sandbox | **None** (Executes in student's browser) | SECURE |
| **RISC-V Assembly** | Python `RiscV5StagePipeline` | In-memory simulated register/RAM array | **None** (Pure software emulation, max 1000 cycles) | SECURE |
| **SPICE Netlists** | Python `NonLinearMNASolver` | Matrix equations & Newton-Raphson math | **None** (Parsed via regex into matrix nodes) | SECURE |
| **SVA Assertions** | Python `SystemVerilogAssertionAnalyzer` | Python `eval(expr, {"__builtins__": None})` | **HIGH RISK** (Object traversal sandbox escape) | VULNERABLE |
| **Boolean Expressions**| Python `DigitalElectronicsEngine` | Python `eval(expr, {"__builtins__": None})` | **HIGH RISK** (Object traversal sandbox escape) | VULNERABLE |

---

## 3. Detailed Vulnerability Analysis

### High-Severity Vulnerability: Sandbox Escape via Python `eval()`
- **Vulnerable Locations**:
  1. [`backend/vlsi_physical_design_engine.py`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/backend/vlsi_physical_design_engine.py#L256):
     ```python
     return bool(eval(clean_expr, {"__builtins__": None}, {}))
     ```
  2. [`backend/digital_electronics_engine.py`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/backend/digital_electronics_engine.py#L327):
     ```python
     result = eval(expr, {"__builtins__": None}, safe_env)
     ```
- **Exploitation Mechanism**:
  Passing `{"__builtins__": None}` does not prevent an attacker from navigating Python's class hierarchy via object traversal:
  ```python
  ().__class__.__bases__[0].__subclasses__()
  ```
  An attacker can locate subclasses such as `os._wrap_close` or `subprocess.Popen` to execute arbitrary commands on the host operating system or inside the Docker container.
- **Impact**: Full Remote Code Execution (RCE) on the server process.
- **Recommended Remediation**:
  Replace `eval()` with Python's `ast.parse()` and a custom `ast.NodeVisitor` that strictly permits only boolean operators (`ast.And`, `ast.Or`, `ast.Not`), bitwise operators, and literal identifiers. Never pass raw user strings to `eval()`.

---

## 4. Host Filesystem & Process Security

1. **Host Isolation**:
   - The LMS backend does **not** compile student code via host system binaries (`gcc`, `clang`, `make`, `iverilog`).
   - No temporary binary files are created, compiled, or executed on the Windows host.
2. **Process Limits & Concurrency**:
   - [`backend/concurrency_limiter.py`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/backend/concurrency_limiter.py) enforces thread-level semaphores:
     ```python
     self._heavy_task_semaphore = threading.Semaphore(8)
     ```
   - All simulation loops enforce strict cycle or iteration bounds (e.g., RISC-V max cycles: 1000; MNA Newton-Raphson max iterations: 100).
3. **Docker Security Posture**:
   - In [`docker-compose.yml`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/docker-compose.yml), the container runs with explicit CPU and memory caps:
     - API Gateway: `cpus: '0.75'`, `memory: 256M`.
     - Redis Cache: `cpus: '0.25'`, `memory: 64M`.
     - Nginx Proxy: `cpus: '0.50'`, `memory: 128M`.
   - The host Docker socket (`/var/run/docker.sock`) is **strictly absent** from volume mounts, preventing Docker-in-Docker escape attacks.

---

## 5. Network Security & Header Hardening

1. **OWASP Security Headers**:
   [`backend/security_middleware.py`](file:///c:/Users/Ashok%20kumar%20A/OneDrive/Documents/VoltCore-LMS-Portal/backend/security_middleware.py) injects mandatory security headers on every response:
   - `X-Content-Type-Options: nosniff` (Prevents MIME-sniffing attacks).
   - `X-Frame-Options: SAMEORIGIN` (Mitigates clickjacking).
   - `X-XSS-Protection: 1; mode=block`.
   - `Content-Security-Policy: default-src 'self' ...` (Restricts unauthorized script origins).
   - `Referrer-Policy: strict-origin-when-cross-origin`.
2. **Rate Limiting**:
   - In-memory token bucket rate limiting (120 req/min per client IP) prevents automated denial-of-service (DoS) and brute-force password guessing.
3. **CORS Configuration**:
   - Currently configured as `Access-Control-Allow-Origin: *` for local development. For production deployment, this must be restricted to the specific institution domain (e.g., `https://voltcore.org`).

---

## 6. Authentication & Credential Storage

1. **Password Hashing**:
   - Handled via `lms_database.hash_password()` using **PBKDF2-HMAC-SHA256 with 600,000 iterations** and 16-byte random salts.
   - Verification uses `hmac.compare_digest()` to prevent timing side-channel attacks.
2. **Admin Metadata Isolation**:
   - Functions like `get_admin_audit_metadata()` strictly redact private contact telemetry (`SECURE_ADMIN_EMAIL`, `SECURE_ADMIN_PHONE`) unless the requesting user possesses an authenticated admin token.
3. **Medium-Severity Finding**:
   - A fallback JWT secret key (`MIT_CHROMEPET_ECE_SECURE_JWT_KEY_2026_@P3X`) is present in `docker-compose.yml`. In a production release, the application must refuse to start if `VOLTCORE_JWT_SECRET` is not set to a cryptographically random secret.
