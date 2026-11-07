"""
========================================================================================
VoltCore Apex Academia - Test Suite: Stage 6 & Stage 7 Security & Production Verification
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Test Module: tests/test_stage6_stage7_production_security.py
Platform Lead & Educational Systems Director: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Verifies:
  1. STAGE 6: Isolated Ephemeral Student Code Execution Security
     - Safe Python, C, C++, and JavaScript execution
     - Pre-execution AST security blocking dangerous imports (os, subprocess, socket)
     - Execution timeout enforcement (< 2.0s) and runaway loop termination
     - Ephemeral workspace directory creation and automatic cleanup
     - Docker production container execution specification
     - Server API endpoint contract (/api/sandbox/execute, /api/sandbox/spec)
  2. STAGE 7: Production Readiness, Structured Logging & Security Invariants
     - Full production readiness audit (/api/production/readiness)
     - SQLite WAL mode and zero foreign key violations across databases
     - Structured JSON logging with automated credential redaction
     - Safe error messaging (zero stack trace or internal path leakage)
     - Zero private data or credential leakage across codebase
     - Multi-stage Dockerfile and GitHub Actions workflow compliance
========================================================================================
"""

import os
import sys
import json
import pytest
from io import BytesIO
from typing import Dict, Any

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.sandbox_code_executor import (
    EphemeralSandboxExecutor,
    SandboxSecurityValidator,
    ephemeral_sandbox_executor
)
from backend.structured_logger import (
    StructuredLogger,
    SafeErrorHandler,
    sanitize_payload,
    structured_logger,
    safe_error_handler
)
from backend.production_readiness_engine import (
    ProductionReadinessEngine,
    production_readiness_engine
)
from attendance_server import FallbackHTTPHandler


class DummyServer:
    pass


class MockSocket:
    def __init__(self, data: bytes):
        self.data = data
        self.output = BytesIO()

    def makefile(self, mode: str, *args, **kwargs):
        if 'r' in mode:
            return BytesIO(self.data)
        return self.output

    def sendall(self, b: bytes):
        self.output.write(b)


# ========================================================================================
# 1. STAGE 6: STUDENT CODE EXECUTION SECURITY
# ========================================================================================

class TestStage6SandboxExecutionSecurity:
    """Verifies isolation, resource constraints, and AST whitelisting in student sandbox."""

    @pytest.fixture
    def executor(self):
        return EphemeralSandboxExecutor(fallback_simulated=True)

    def test_safe_python_execution(self, executor):
        """Standard educational Python algorithms execute cleanly and return stdout."""
        code = "print(sum([x * 2 for x in range(5)]))"
        res = executor.execute("python", code, timeout_seconds=2.0, student_id="2023MITEC042")
        assert res["status"] == "SUCCESS"
        assert res["exit_code"] == 0
        assert res["stdout"].strip() == "20"
        assert res["sandbox_cleaned"] is True
        assert res["security_audit"]["passed"] is True

    def test_python_ast_security_blocks_os_import(self, executor):
        """Pre-execution AST scanner immediately blocks prohibited os import."""
        malicious_code = "import os\nos.system('dir')"
        res = executor.execute("python", malicious_code)
        assert res["status"] == "SECURITY_VIOLATION"
        assert res["exit_code"] == -1
        assert "Security Violation" in res["stderr"]
        assert "os" in res["stderr"]
        assert res["security_audit"]["passed"] is False

    def test_python_ast_security_blocks_subprocess_import(self, executor):
        """Pre-execution AST scanner blocks subprocess spawning."""
        malicious_code = "from subprocess import Popen\nPopen(['cmd'])"
        res = executor.execute("python", malicious_code)
        assert res["status"] == "SECURITY_VIOLATION"
        assert "subprocess" in res["stderr"]

    def test_python_ast_security_blocks_eval_and_open(self, executor):
        """Blocks dangerous builtins eval, exec, and arbitrary file write open()."""
        code_eval = "eval('1 + 1')"
        res_eval = executor.execute("python", code_eval)
        assert res_eval["status"] == "SECURITY_VIOLATION"
        assert "eval" in res_eval["stderr"]

        code_open = "with open('secret.txt', 'w') as f: f.write('hack')"
        res_open = executor.execute("python", code_open)
        assert res_open["status"] == "SECURITY_VIOLATION"
        assert "open" in res_open["stderr"]

    def test_execution_timeout_enforcement(self, executor):
        """Runaway loops terminate strictly at timeout and report TIMEOUT status."""
        infinite_loop = "while True:\n    pass"
        res = executor.execute("python", infinite_loop, timeout_seconds=1.0)
        assert res["status"] == "TIMEOUT"
        assert res["exit_code"] == -9
        assert "timed out" in res["stderr"].lower()
        assert res["sandbox_cleaned"] is True

    def test_c_code_execution_and_security(self, executor):
        """C code execution validates entry point and rejects socket headers."""
        safe_c = """
        #include <stdio.h>
        int main() {
            printf("VoltCore C Kernel\\n");
            return 0;
        }
        """
        res_safe = executor.execute("c", safe_c)
        assert res_safe["status"] == "SUCCESS"
        assert "VoltCore C Kernel" in res_safe["stdout"]

        dangerous_c = """
        #include <stdio.h>
        #include <sys/socket.h>
        int main() {
            system("whoami");
            return 0;
        }
        """
        res_dang = executor.execute("c", dangerous_c)
        assert res_dang["status"] == "SECURITY_VIOLATION"
        assert "Security Violation" in res_dang["stderr"]

    def test_cpp_code_execution_and_security(self, executor):
        """C++ code execution validates main and rejects process execution primitives."""
        safe_cpp = """
        #include <iostream>
        int main() {
            std::cout << "DSP Filter Converged" << std::endl;
            return 0;
        }
        """
        res_safe = executor.execute("cpp", safe_cpp)
        assert res_safe["status"] == "SUCCESS"
        assert "DSP Filter Converged" in res_safe["stdout"]

        dangerous_cpp = """
        #include <iostream>
        int main() {
            fork();
            return 0;
        }
        """
        res_dang = executor.execute("cpp", dangerous_cpp)
        assert res_dang["status"] == "SECURITY_VIOLATION"
        assert "fork" in res_dang["stderr"]

    def test_javascript_code_execution_and_security(self, executor):
        """JavaScript execution rejects child_process, fs, and net access."""
        safe_js = "console.log('VoltCore Client State Synchronized');"
        res_safe = executor.execute("javascript", safe_js)
        assert res_safe["status"] == "SUCCESS"
        assert "VoltCore Client State Synchronized" in res_safe["stdout"]

        dangerous_js = "const cp = require('child_process'); cp.execSync('calc');"
        res_dang = executor.execute("javascript", dangerous_js)
        assert res_dang["status"] == "SECURITY_VIOLATION"
        assert "child_process" in res_dang["stderr"]

    def test_docker_production_spec(self, executor):
        """Validates that formal Docker execution specification complies with non-root security."""
        spec = executor.get_docker_production_spec()
        assert "--network none" in spec["command_template"]
        assert "--memory 64m" in spec["command_template"]
        assert "--user 1000:1000" in spec["command_template"]
        assert "--cap-drop ALL" in spec["command_template"]
        assert spec["security_flags"]["network"] == "none"

    def test_sandbox_server_endpoints(self):
        """Verifies /api/sandbox/execute and /api/sandbox/spec via FallbackHTTPHandler."""
        # 1. Test POST /api/sandbox/execute
        body = json.dumps({
            "language": "python",
            "source_code": "print('Sandbox HTTP Verified')",
            "student_id": "2023MITEC042"
        }).encode("utf-8")
        req = (
            b"POST /api/sandbox/execute HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: " + str(len(body)).encode("utf-8") + b"\r\n\r\n"
            + body
        )
        sock = MockSocket(req)
        FallbackHTTPHandler(sock, ("127.0.0.1", 8080), DummyServer())
        resp = sock.output.getvalue().decode("utf-8")
        assert "200 OK" in resp
        assert "Sandbox HTTP Verified" in resp

        # 2. Test GET /api/sandbox/spec
        req_spec = b"GET /api/sandbox/spec HTTP/1.1\r\nHost: localhost\r\n\r\n"
        sock_spec = MockSocket(req_spec)
        FallbackHTTPHandler(sock_spec, ("127.0.0.1", 8080), DummyServer())
        resp_spec = sock_spec.output.getvalue().decode("utf-8")
        assert "200 OK" in resp_spec
        assert "voltcore/sandbox-runner:2026" in resp_spec


# ========================================================================================
# 2. STAGE 7: PRODUCTION READINESS & OBSERVABILITY
# ========================================================================================

class TestStage7ProductionReadinessAndObservability:
    """Verifies production health, structured logging, safe errors, and privacy invariants."""

    def test_structured_logger_json_and_redaction(self):
        """Structured logger emits RFC 3339 timestamps and redacts credentials."""
        logger = StructuredLogger(service_name="test_service")
        log_entry = logger.info(
            "Student authenticated",
            correlation_id="req_test_123",
            client_id="2023MITEC042",
            extra={
                "password": "plain_password",
                "api_key": "AIzaSy_fake",
                "jwt": "header.payload.sig",
                "safe_field": "ECE_R2023"
            }
        )
        assert log_entry["service"] == "test_service"
        assert log_entry["level"] == "INFO"
        assert log_entry["correlation_id"] == "req_test_123"
        assert log_entry["context"]["safe_field"] == "ECE_R2023"
        # Verify credential redaction
        assert log_entry["context"]["password"] == "[REDACTED_CREDENTIAL]"
        assert log_entry["context"]["api_key"] == "[REDACTED_CREDENTIAL]"
        assert log_entry["context"]["jwt"] == "[REDACTED_CREDENTIAL]"

    def test_safe_error_handler_prevents_leakage(self):
        """Safe error handler generates sanitized error payloads without internal paths."""
        raw_exc = Exception("Internal database failure at C:\\Users\\Ashok\\voltcore_lms.db: line 42")
        err = safe_error_handler.format_client_error(
            status_code=500,
            correlation_id="inc_unit_test_999",
            internal_exception=raw_exc
        )
        assert err["status"] == "ERROR"
        assert err["error_code"] == "INTERNAL_SERVER_ERROR"
        assert err["correlation_id"] == "inc_unit_test_999"
        # Verify zero leak of local path or line number in client message
        assert "C:\\" not in err["message"]
        assert "voltcore_lms.db" not in err["message"]
        assert "line 42" not in err["message"]

    def test_production_readiness_audit_overall_grade(self):
        """Full readiness audit reports GRADE_A_ENTERPRISE and READY status."""
        report = production_readiness_engine.collect_full_readiness_audit()
        assert report["status"] == "READY"
        assert report["production_grade"] == "GRADE_A_ENTERPRISE"
        assert report["databases"]["voltcore_lms"]["is_wal"] is True
        assert report["databases"]["voltcore_lms"]["integrity"] == "ok"
        assert report["databases"]["voltcore_telemetry"]["is_wal"] is True
        assert report["deployment_infrastructure"]["passed"] is True
        assert report["pwa_offline_sync"]["passed"] is True

    def test_zero_private_credentials_in_codebase(self):
        """Scans repository guaranteeing zero occurrence of private admin email or phone."""
        res = production_readiness_engine.verify_privacy_invariants()
        assert res["passed"] is True, f"Privacy violations detected: {res.get('violations')}"
        assert res["violations_count"] == 0

    def test_production_readiness_server_endpoint(self):
        """Verifies GET /api/production/readiness server route dispatches correctly."""
        req = b"GET /api/production/readiness HTTP/1.1\r\nHost: localhost\r\n\r\n"
        sock = MockSocket(req)
        FallbackHTTPHandler(sock, ("127.0.0.1", 8080), DummyServer())
        resp = sock.output.getvalue().decode("utf-8")
        assert "200 OK" in resp
        assert "GRADE_A_ENTERPRISE" in resp
        assert "READY" in resp
