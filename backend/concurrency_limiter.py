"""
========================================================================================
VoltCore Apex Academia - Multi-User Concurrency Limiter & Retry Engine
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/concurrency_limiter.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Concurrency throttling, transaction retry with exponential backoff, and rate-limiting
  header generation to protect backend SQLite and Flask endpoints during simultaneous
  multi-student laboratory logins and ESP32 telemetry bursts.
========================================================================================
"""

import time
import random
import sqlite3
import threading
from functools import wraps
from typing import Dict, Any, Callable, Optional, Tuple, List
from collections import defaultdict


class ConcurrencyLimiter:
    """
    Manages bounded concurrency semaphores and sliding-window rate limit headers.
    Prevents SQLite write-lock contention and CPU thrashing on the HP Victus 15.
    """

    def __init__(self, max_concurrent_writes: int = 4, default_rate_limit: int = 120):
        self.write_semaphore = threading.BoundedSemaphore(value=max_concurrent_writes)
        self.default_rate_limit = default_rate_limit
        self._request_history = defaultdict(list)
        self._lock = threading.Lock()

    def get_rate_limit_headers(
        self,
        client_key: str,
        limit: Optional[int] = None,
        window_seconds: int = 60
    ) -> Dict[str, str]:
        """
        Calculates and returns standard RFC-compliant rate limit HTTP headers.
        """
        now = time.time()
        effective_limit = limit or self.default_rate_limit

        with self._lock:
            # Prune timestamps older than window
            cutoff = now - window_seconds
            self._request_history[client_key] = [
                ts for ts in self._request_history[client_key] if ts > cutoff
            ]
            # Record this request
            self._request_history[client_key].append(now)
            count = len(self._request_history[client_key])
            remaining = max(0, effective_limit - count)
            reset_seconds = int(window_seconds - (now - self._request_history[client_key][0])) if count > 0 else window_seconds

        return {
            "X-RateLimit-Limit": str(effective_limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(max(1, reset_seconds)),
            "X-RateLimit-Policy": f"{effective_limit};w={window_seconds}"
        }


# Global concurrency limiter instance
concurrency_limiter = ConcurrencyLimiter()


def transaction_retry(max_retries: int = 3, initial_delay: float = 0.01, backoff_factor: float = 2.0):
    """
    Decorator that catches transient SQLite lock contention ('database is locked')
    and retries with jittered exponential backoff.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as exc:
                    last_exception = exc
                    err_msg = str(exc).lower()
                    if "locked" in err_msg or "busy" in err_msg:
                        if attempt < max_retries:
                            # Apply exponential backoff with random jitter (±20%)
                            jitter = random.uniform(0.8, 1.2)
                            sleep_time = delay * jitter
                            time.sleep(sleep_time)
                            delay *= backoff_factor
                            continue
                    raise exc
            raise last_exception
        return wrapper
    return decorator


def bounded_write_operation(func: Callable):
    """
    Decorator enforcing that write operations acquire the bounded write semaphore,
    ensuring max concurrent writers never exceed the configured threshold.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        acquired = concurrency_limiter.write_semaphore.acquire(timeout=5.0)
        if not acquired:
            raise sqlite3.OperationalError("Write semaphore acquisition timed out: server under heavy write contention")
        try:
            return func(*args, **kwargs)
        finally:
            concurrency_limiter.write_semaphore.release()
    return wrapper


def simulate_concurrent_load(
    pool,
    num_threads: int = 10,
    ops_per_thread: int = 5,
    write_ratio: float = 0.2
) -> Dict[str, Any]:
    """
    Simulates concurrent multi-user database traffic across worker threads.
    Validates zero lock contention under load.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    success_count = 0
    failure_count = 0
    latencies: List[float] = []
    errors: List[str] = []
    lock = threading.Lock()

    def worker_task(thread_id: int):
        thread_success = 0
        thread_failures = 0
        thread_latencies = []

        for op_idx in range(ops_per_thread):
            is_write = (op_idx % int(1.0 / write_ratio)) == 0 if write_ratio > 0 else False
            t0 = time.perf_counter()

            try:
                with pool.get_connection() as conn:
                    cur = conn.cursor()
                    if is_write:
                        # Safe test write with valid foreign key user and immediate rollback
                        cur.execute("SELECT user_id FROM users LIMIT 1;")
                        urow = cur.fetchone()
                        valid_uid = urow[0] if urow else "2023MITEC042"
                        cur.execute(
                            "INSERT INTO attendance (user_id, rfid_uid, node_id, status) VALUES (?, ?, ?, ?)",
                            (valid_uid, f"AA BB CC {thread_id:02X}", "ESP32_STAGING_TEST", "Lab-Verified")
                        )
                        conn.rollback()  # Do not pollute database
                    else:
                        cur.execute("SELECT count(*) FROM users LIMIT 1;")
                        _ = cur.fetchone()

                    elapsed_ms = (time.perf_counter() - t0) * 1000.0
                    thread_latencies.append(elapsed_ms)
                    thread_success += 1
            except Exception as e:
                thread_failures += 1
                with lock:
                    errors.append(f"Thread {thread_id} op {op_idx}: {str(e)}")

        with lock:
            nonlocal success_count, failure_count
            success_count += thread_success
            failure_count += thread_failures
            latencies.extend(thread_latencies)

    t_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_task, i) for i in range(num_threads)]
        for f in as_completed(futures):
            f.result()
    total_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

    total_ops = num_threads * ops_per_thread
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    return {
        "num_threads": num_threads,
        "ops_per_thread": ops_per_thread,
        "total_operations": total_ops,
        "successful_operations": success_count,
        "failed_operations": failure_count,
        "success_rate_percent": round((success_count / max(1, total_ops)) * 100.0, 2),
        "total_duration_ms": round(total_elapsed_ms, 2),
        "avg_latency_ms": round(avg_latency, 3),
        "max_latency_ms": round(max(latencies), 3) if latencies else 0.0,
        "errors": errors[:5],
        "zero_contention_passed": failure_count == 0
    }
