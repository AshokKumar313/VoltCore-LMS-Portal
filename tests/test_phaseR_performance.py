"""
========================================================================================
VoltCore Apex Academia - Phase R Unit Tests: Performance, Asset Optimization & Caching
Features 381–390 (Anna University Regulation 2023)
Platform Lead & Systems Architect: Ashok Kumar A
========================================================================================
"""

import os
import pytest
import sqlite3
import tempfile
from backend.performance_optimization_engine import (
    PageLoadSpeedMonitor,
    StaticAssetCompressor,
    SQLiteLRUQueryCache,
    JavaScriptBundleAnalyzer,
    ImageOptimizationAuditor,
    ClientHydrationProfiler,
    MemoryFootprintInspector,
    HttpCacheHeaderInspector,
    ServiceWorkerCacheManager,
    PlatformPerformanceScorecard
)


def test_page_load_speed_monitor_cwv_evaluation():
    """Feature 381: Verify Core Web Vitals grading and composite scoring."""
    # Fast, compliant vitals
    good_result = PageLoadSpeedMonitor.evaluate_vitals(
        lcp_ms=1200.0,
        inp_ms=45.0,
        cls_score=0.01,
        ttfb_ms=120.0,
        fcp_ms=800.0
    )
    assert good_result["is_cwv_compliant"] is True
    assert good_result["performance_score"] == 100.0
    assert good_result["overall_status"] == "OPTIMAL"

    # Degraded vitals
    poor_result = PageLoadSpeedMonitor.evaluate_vitals(
        lcp_ms=4500.0,
        inp_ms=600.0,
        cls_score=0.35,
        ttfb_ms=2100.0,
        fcp_ms=3500.0
    )
    assert poor_result["is_cwv_compliant"] is False
    assert poor_result["performance_score"] < 50.0
    assert poor_result["overall_status"] == "POOR"


def test_static_asset_compressor_gzip_and_brotli():
    """Feature 382: Verify static asset compression calculations."""
    sample_js = "function calculateFFT(data) { return data.map(x => Math.sin(x) * 2.0); }" * 50
    result = StaticAssetCompressor.compress_content(sample_js)

    assert result["raw_size_bytes"] > 0
    assert result["gzip_size_bytes"] < result["raw_size_bytes"]
    assert result["brotli_size_bytes"] <= result["gzip_size_bytes"]
    assert result["gzip_savings_pct"] > 50.0
    assert result["brotli_savings_pct"] > result["gzip_savings_pct"]
    assert result["recommended_encoding"] == "br"


def test_sqlite_lru_query_cache_hit_and_miss():
    """Feature 383: Verify thread-safe LRU query cache hit/miss behavior."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test_telemetry (id INTEGER PRIMARY KEY, metric TEXT, val REAL)")
        conn.execute("INSERT INTO test_telemetry VALUES (1, 'V_CORE', 1.05)")
        conn.commit()
        conn.close()

        cache = SQLiteLRUQueryCache(max_capacity=5, db_path=db_path)
        query = "SELECT * FROM test_telemetry WHERE metric = ?"
        params = ("V_CORE",)

        # 1st execution: Cache Miss
        miss_res = cache.execute_cached(query, params)
        assert miss_res["source"] == "CACHE_MISS"
        assert len(miss_res["data"]) == 1
        assert miss_res["data"][0]["metric"] == "V_CORE"

        # 2nd execution: Cache Hit
        hit_res = cache.execute_cached(query, params)
        assert hit_res["source"] == "CACHE_HIT"
        assert hit_res["hit_ratio"] == 50.0

        # Cache eviction
        for i in range(10):
            cache.put(f"SELECT {i}", (), [{"val": i}])
        assert len(cache._cache) <= 5

        cache.clear()
        assert cache.hits == 0
        assert cache.misses == 0
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_javascript_bundle_analyzer_budgets():
    """Feature 384: Verify chunk size budgets and tree-shaking metrics."""
    passing_chunks = [
        {"name": "index.js", "size_kb": 24.5, "gzip_kb": 8.1},
        {"name": "SecurityIntegrityHub.js", "size_kb": 42.0, "gzip_kb": 12.3},
        {"name": "vendor-react.js", "size_kb": 38.0, "gzip_kb": 11.2}
    ]
    audit_pass = JavaScriptBundleAnalyzer.audit_chunks(passing_chunks)
    assert audit_pass["budget_passed"] is True
    assert len(audit_pass["errors"]) == 0
    assert audit_pass["total_raw_kb"] == pytest.approx(104.5, rel=1e-2)

    exceeding_chunks = [
        {"name": "monolithic-vendor.js", "size_kb": 145.0, "gzip_kb": 48.0}
    ]
    audit_fail = JavaScriptBundleAnalyzer.audit_chunks(exceeding_chunks)
    assert audit_fail["budget_passed"] is False
    assert len(audit_fail["errors"]) == 1


def test_image_optimization_auditor_savings_and_srcset():
    """Feature 385: Verify image compression savings and responsive srcset generation."""
    raw_size = 100000  # 100 KB
    savings = ImageOptimizationAuditor.audit_image_savings("png", raw_size)

    assert savings["webp_savings_pct"] == 35.0
    assert savings["avif_savings_pct"] == 55.0
    assert savings["recommended_format"] == "AVIF"

    srcset = ImageOptimizationAuditor.generate_srcset("dsp-bode-plot.png", [480, 800, 1200])
    assert "dsp-bode-plot-480w.webp 480w" in srcset
    assert "dsp-bode-plot-1200w.webp 1200w" in srcset


def test_client_hydration_profiler_timing():
    """Feature 386: Verify partial hydration boundary evaluation."""
    islands_fast = [
        {"name": "VirtualOscilloscope", "hydration_time_ms": 12.4},
        {"name": "SecurityIntegrityHub", "hydration_time_ms": 15.1}
    ]
    eval_fast = ClientHydrationProfiler.evaluate_hydration(islands_fast)
    assert eval_fast["is_hydration_optimal"] is True
    assert eval_fast["total_hydration_time_ms"] == 27.5

    islands_slow = [
        {"name": "HeavyCanvasPlotter", "hydration_time_ms": 38.2}
    ]
    eval_slow = ClientHydrationProfiler.evaluate_hydration(islands_slow)
    assert eval_slow["is_hydration_optimal"] is False
    assert "HeavyCanvasPlotter" in eval_slow["slow_islands"]


def test_memory_footprint_inspector_thermal_safety():
    """Feature 387: Verify passive CPU/RAM thresholds on HP Victus."""
    safe_audit = MemoryFootprintInspector.audit_footprint(dom_node_count=850, memory_mb=145.2)
    assert safe_audit["is_thermal_safe"] is True
    assert safe_audit["dom_status"] == "SAFE"
    assert safe_audit["memory_status"] == "OPTIMAL"

    high_audit = MemoryFootprintInspector.audit_footprint(dom_node_count=2200, memory_mb=320.0)
    assert high_audit["is_thermal_safe"] is False
    assert high_audit["dom_status"] == "HIGH_DENSITY"
    assert high_audit["memory_status"] == "ELEVATED"


def test_http_cache_header_inspector_etag_and_304():
    """Feature 388: Verify RFC 7234 immutable headers and conditional requests."""
    content = b"console.log('VoltCore High Performance Build');"
    headers = HttpCacheHeaderInspector.generate_static_asset_headers(content)

    assert "public, max-age=31536000, immutable" in headers["Cache-Control"]
    assert "ETag" in headers

    etag = headers["ETag"]
    status_304 = HttpCacheHeaderInspector.evaluate_conditional_request(etag, etag)
    assert status_304 == 304

    status_200 = HttpCacheHeaderInspector.evaluate_conditional_request('"old_etag"', etag)
    assert status_200 == 200


def test_service_worker_cache_manager_manifest():
    """Feature 389: Verify offline pre-cache routes and caching strategies."""
    manifest = ServiceWorkerCacheManager.get_manifest()
    assert manifest["precache_routes_count"] >= 8
    assert "/" in manifest["routes"]
    assert "/security-integrity" in manifest["routes"]
    assert "/performance-optimization" in manifest["routes"]
    assert manifest["strategies"]["STATIC_ASSETS"] == "CacheFirst"
    assert manifest["strategies"]["API_TELEMETRY"] == "NetworkFirst"


def test_platform_performance_scorecard_and_lead_credentials():
    """Feature 390: Verify Lighthouse 100/100 scorecard and platform lead credentials."""
    scorecard = PlatformPerformanceScorecard.generate_scorecard()
    assert scorecard["categories"]["performance"] == 100
    assert scorecard["categories"]["accessibility"] == 100
    assert scorecard["categories"]["best_practices"] == 100
    assert scorecard["categories"]["seo"] == 100

    lead = scorecard["lead_architecture"]
    assert lead["systems_architect"] == "Ashok Kumar A"
    assert "MIT Campus" in lead["campus"]
    assert "AshokKumar313" in lead["public_github"]
    assert lead["total_features"] == 390
