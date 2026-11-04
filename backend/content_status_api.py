"""
========================================================================================
VoltCore Apex Academia - Content Lifecycle & Status Management API
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/content_status_api.py
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Lifecycle Stages:
  1. Draft: Preliminary authoring / raw notes
  2. AI-Generated: Synthesized outline / initial draft
  3. Human-Reviewed: Code-checked by embedded teaching assistants
  4. Faculty-Approved: Anna University Department Faculty editorial sign-off
  5. Published: Live production curriculum module deployed to students
========================================================================================
"""

import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union

# Ensure project root is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

import lms_database

VALID_STATUSES = list(lms_database.VALID_LIFECYCLE_STATUSES)


def get_content_status_report() -> Dict[str, Any]:
    """
    Returns full content status distribution, stage counts, and module details.
    """
    lms_database.init_db()
    modules = lms_database.get_all_module_statuses()

    stage_counts = {
        "Draft": 0,
        "AI-Generated": 0,
        "Human-Reviewed": 0,
        "Faculty-Approved": 0,
        "Published": 0
    }

    total_quality = 0.0
    for m in modules:
        status = m.get("status", "Draft")
        stage_counts[status] = stage_counts.get(status, 0) + 1
        total_quality += m.get("quality_score", 0.0)

    avg_quality = round(total_quality / len(modules), 2) if modules else 0.0
    published_pct = round((stage_counts["Published"] / len(modules)) * 100, 1) if modules else 0.0

    return {
        "status": "success",
        "institution": "Madras Institute of Technology (MIT) Campus, Anna University",
        "department": "Department of Electronics Engineering",
        "total_modules": len(modules),
        "stage_distribution": stage_counts,
        "published_rate_percent": published_pct,
        "average_quality_score": avg_quality,
        "modules": modules,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def update_content_status_entry(
    payload: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Tuple[Dict[str, Any], int]:
    """
    Validates and updates module lifecycle status with changelog record.
    Supports either a payload dictionary or keyword arguments.
    """
    data = dict(payload) if isinstance(payload, dict) else {}
    data.update(kwargs)

    raw_code = data.get("module_code") or data.get("module_id") or ""
    module_code = raw_code.strip().upper()
    new_status = (data.get("status") or data.get("new_status") or "").strip()
    author = (data.get("author") or data.get("changed_by") or "Anna University Faculty Reviewer").strip()
    comment = (data.get("comment") or data.get("notes") or "").strip()

    if not module_code:
        return {"status": "error", "success": False, "message": "Missing required field: 'module_code'."}, 400

    if not new_status:
        return {"status": "error", "success": False, "message": "Missing required field: 'status'."}, 400

    try:
        res = lms_database.update_module_lifecycle_status(
            module_code=module_code,
            new_status=new_status,
            author=author,
            comment=comment
        )
        res["success"] = True
        return res, 200
    except ValueError as e:
        return {"status": "error", "success": False, "message": str(e), "error": str(e)}, 400
    except Exception as e:
        return {"status": "error", "success": False, "message": f"Database update error: {str(e)}", "error": str(e)}, 500


def get_changelog_history(module_code: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """
    Returns changelog audit trail for curriculum modules.
    """
    logs = lms_database.get_module_changelog(module_code=module_code, limit=limit)
    return {
        "status": "success",
        "count": len(logs),
        "module_code": module_code or "ALL",
        "changelog": logs,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
