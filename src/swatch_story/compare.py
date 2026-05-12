from __future__ import annotations

from pathlib import Path
from typing import Any

from swatch_story.report import write_json_report


def compare_summaries(
    before_summary: dict[str, Any], after_summary: dict[str, Any]
) -> dict[str, Any]:
    before_hexes = [entry["hex"] for entry in before_summary["palette"]]
    after_hexes = [entry["hex"] for entry in after_summary["palette"]]
    before_set = set(before_hexes)
    after_set = set(after_hexes)
    shared_set = before_set & after_set
    union = before_set | after_set

    return {
        "before": _comparison_side(before_summary),
        "after": _comparison_side(after_summary),
        "shared": [hex_color for hex_color in before_hexes if hex_color in shared_set],
        "added": [
            hex_color for hex_color in after_hexes if hex_color not in before_set
        ],
        "removed": [
            hex_color for hex_color in before_hexes if hex_color not in after_set
        ],
        "drift_score": round((1 - (len(shared_set) / len(union))) * 100, 2)
        if union
        else 0.0,
    }


def _comparison_side(summary: dict[str, Any]) -> dict[str, Any]:
    palette = summary["palette"]
    return {
        "source": summary["source"],
        "source_path": summary.get("source_path", summary["source"]),
        "dominant": palette[0]["hex"] if palette else None,
        "size": summary.get("size"),
        "settings": summary.get("settings", {}),
        "palette": palette,
    }


def render_compare_text(report: dict[str, Any]) -> str:
    before = report["before"]
    after = report["after"]
    lines = [
        f"Palette comparison: {before['source_path']} -> {after['source_path']}",
        f"Before dominant: {_format_optional_color(before['dominant'])}",
        f"After dominant: {_format_optional_color(after['dominant'])}",
        f"Shared colors: {_format_color_list(report['shared'])}",
        f"Added colors: {_format_color_list(report['added'])}",
        f"Removed colors: {_format_color_list(report['removed'])}",
        f"Drift score: {report['drift_score']}%",
    ]
    return "\n".join(lines) + "\n"


def write_compare_json(report: dict[str, Any], output_path: str | Path) -> None:
    write_json_report(report, output_path)


def _format_optional_color(value: str | None) -> str:
    return value if value is not None else "none"


def _format_color_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"
