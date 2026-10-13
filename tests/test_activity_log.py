"""Tests for the standard ring-buffer log backend (WEBAPP_LOGS_PAGE.md)."""

import json

from sfx_mcp.activity_log import (
    clear_logs,
    export_logs,
    log_activity,
    log_stats,
    query_logs,
)


def _seed() -> None:
    clear_logs()
    log_activity("http", "GET /api/health -> 200 (1ms)", level="INFO")
    log_activity("http", "GET /nope -> 404 (0ms)", level="WARNING")
    log_activity("server", "DB ready", level="INFO")
    log_activity("http", "GET /boom -> 500 (3ms)", level="ERROR")


def test_query_all_and_pagination() -> None:
    _seed()
    page1 = query_logs(limit=2, offset=0)
    assert page1["total"] == 4
    assert len(page1["entries"]) == 2
    page2 = query_logs(limit=2, offset=2)
    assert len(page2["entries"]) == 2
    assert page1["entries"][0]["id"] != page2["entries"][0]["id"]


def test_query_level_filter_is_minimum() -> None:
    _seed()
    assert query_logs(level="ERROR")["total"] == 1
    assert query_logs(level="WARNING")["total"] == 2
    assert query_logs()["total"] == 4


def test_query_kind_and_search() -> None:
    _seed()
    assert query_logs(kind="server")["total"] == 1
    assert query_logs(search="boom")["total"] == 1
    assert query_logs(search="nothing-here")["total"] == 0


def test_query_sort_and_after_id() -> None:
    _seed()
    desc = query_logs(sort="desc")["entries"]
    asc = query_logs(sort="asc")["entries"]
    assert desc[0]["id"] == asc[-1]["id"]
    newest_id = desc[0]["id"]
    assert query_logs(after_id=newest_id)["total"] == 0
    assert query_logs(after_id="0")["total"] == 4


def test_stats_shape() -> None:
    _seed()
    stats = log_stats()
    assert stats["total"] == 4
    assert stats["rotation"] == "ring_buffer"
    assert stats["by_level"]["ERROR"] == 1
    assert stats["by_kind"]["http"] == 3
    assert stats["newest"] is not None


def test_export_json_and_csv() -> None:
    _seed()
    body, media, name = export_logs(format="json")
    assert media == "application/json"
    assert name.startswith("sfx-mcp-logs-")
    assert len(json.loads(body)["entries"]) == 4
    csv_body, csv_media, csv_name = export_logs(format="csv")
    assert csv_media == "text/csv"
    assert csv_name.endswith(".csv")
    assert "id,timestamp,level,kind,detail,meta" in csv_body.splitlines()[0]


def test_clear() -> None:
    _seed()
    clear_logs()
    assert query_logs()["total"] == 0
    assert log_stats()["total"] == 0
