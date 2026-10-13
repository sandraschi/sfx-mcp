"""In-memory event log for web dashboard - tail, filter, export, rotation.

Fleet pattern per mcp-central-docs/standards/WEBAPP_LOGS_PAGE.md.
Ported from bookmarks-mcp activity_log.py (reference implementation).
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
from collections import deque
from datetime import UTC, datetime
from threading import Lock
from typing import Any, Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
SortOrder = Literal["asc", "desc"]

_LEVEL_RANK = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}

_DEFAULT_MAX = 2000
_max_entries = max(100, min(int(os.environ.get("SFX_LOG_MAX_ENTRIES", str(_DEFAULT_MAX))), 50_000))
_lock = Lock()
_entries: deque[dict[str, Any]] = deque(maxlen=_max_entries)


def max_entries() -> int:
    return _max_entries


def _normalize_level(level: str | None) -> LogLevel:
    value = (level or "INFO").upper()
    if value not in _LEVEL_RANK:
        return "INFO"
    return value  # type: ignore[return-value]


def log_activity(
    kind: str,
    detail: str,
    *,
    level: str | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = {
        "id": f"{datetime.now(UTC).timestamp():.6f}",
        "timestamp": datetime.now(UTC).isoformat(),
        "level": _normalize_level(level),
        "kind": kind,
        "detail": detail,
        "meta": meta or {},
    }
    with _lock:
        _entries.appendleft(entry)
    return entry


def clear_logs() -> None:
    with _lock:
        _entries.clear()


def _matches(
    entry: dict[str, Any], *, level: str | None, kind: str | None, search: str | None
) -> bool:
    if level:
        min_rank = _LEVEL_RANK.get(level.upper(), 0)
        if _LEVEL_RANK.get(str(entry.get("level", "INFO")), 0) < min_rank:
            return False
    if kind and entry.get("kind") != kind:
        return False
    if search:
        needle = search.lower()
        hay = f"{entry.get('kind', '')} {entry.get('detail', '')} {json.dumps(entry.get('meta', {}))}".lower()
        if needle not in hay:
            return False
    return True


def query_logs(
    *,
    limit: int = 50,
    offset: int = 0,
    level: str | None = None,
    kind: str | None = None,
    search: str | None = None,
    sort: SortOrder = "desc",
    after_id: str | None = None,
) -> dict[str, Any]:
    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    with _lock:
        rows = list(_entries)

    if after_id:
        try:
            after_ts = float(after_id)
            rows = [row for row in rows if float(row["id"]) > after_ts]
        except ValueError:
            pass

    filtered = [row for row in rows if _matches(row, level=level, kind=kind, search=search)]
    filtered.sort(key=lambda row: row.get("timestamp", ""), reverse=(sort == "desc"))
    total = len(filtered)
    page = filtered[offset : offset + limit]

    return {
        "entries": page,
        "total": total,
        "limit": limit,
        "offset": offset,
        "max_entries": _max_entries,
        "sort": sort,
    }


def log_stats() -> dict[str, Any]:
    with _lock:
        rows = list(_entries)

    by_level: dict[str, int] = {key: 0 for key in _LEVEL_RANK}
    by_kind: dict[str, int] = {}
    for row in rows:
        lvl = str(row.get("level", "INFO"))
        by_level[lvl] = by_level.get(lvl, 0) + 1
        kind = str(row.get("kind", "unknown"))
        by_kind[kind] = by_kind.get(kind, 0) + 1

    return {
        "total": len(rows),
        "max_entries": _max_entries,
        "rotation": "ring_buffer",
        "by_level": by_level,
        "by_kind": by_kind,
        "oldest": rows[-1]["timestamp"] if rows else None,
        "newest": rows[0]["timestamp"] if rows else None,
    }


def export_logs(
    *,
    format: str = "json",
    level: str | None = None,
    kind: str | None = None,
    search: str | None = None,
    sort: SortOrder = "desc",
) -> tuple[str, str, str]:
    payload = query_logs(
        limit=_max_entries,
        offset=0,
        level=level,
        kind=kind,
        search=search,
        sort=sort,
    )
    entries = payload["entries"]
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    if format == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=["id", "timestamp", "level", "kind", "detail", "meta"],
        )
        writer.writeheader()
        for row in entries:
            writer.writerow(
                {
                    "id": row.get("id"),
                    "timestamp": row.get("timestamp"),
                    "level": row.get("level"),
                    "kind": row.get("kind"),
                    "detail": row.get("detail"),
                    "meta": json.dumps(row.get("meta") or {}),
                }
            )
        return buffer.getvalue(), "text/csv", f"sfx-mcp-logs-{stamp}.csv"

    body = json.dumps({"exported_at": datetime.now(UTC).isoformat(), "entries": entries}, indent=2)
    return body, "application/json", f"sfx-mcp-logs-{stamp}.json"


class ActivityLogHandler(logging.Handler):
    """Capture Python logging records into the in-memory ring buffer."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = record.levelname
            if level == "WARN":
                level = "WARNING"
            log_activity(
                kind="server",
                detail=record.getMessage(),
                level=level,
                meta={"logger": record.name, "module": record.module},
            )
        except Exception:
            self.handleError(record)


def install_log_handler() -> None:
    root = logging.getLogger()
    for handler in root.handlers:
        if isinstance(handler, ActivityLogHandler):
            return
    handler = ActivityLogHandler()
    handler.setLevel(logging.INFO)
    root.addHandler(handler)
