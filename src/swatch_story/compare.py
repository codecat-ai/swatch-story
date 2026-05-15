from __future__ import annotations

import csv
import io
from html import escape
from pathlib import Path
from typing import Any

from swatch_story.report import markdown_escape, write_json_report

COMPARE_CSV_HEADER = [
    "section",
    "field",
    "value",
    "category",
    "hex",
    "before_percent",
    "after_percent",
    "delta_percent",
]


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


def render_compare_text_report(
    report: dict[str, Any], *, title: str = "Palette Drift Report"
) -> str:
    before = report["before"]
    after = report["after"]
    rows = [
        ("Before source name", str(before["source"])),
        ("Before source path", str(before["source_path"])),
        ("After source name", str(after["source"])),
        ("After source path", str(after["source_path"])),
        (
            "Before dominant colors",
            _format_text_color_list([entry["hex"] for entry in before["palette"]]),
        ),
        (
            "After dominant colors",
            _format_text_color_list([entry["hex"] for entry in after["palette"]]),
        ),
        ("Shared colors", _format_text_color_list(report["shared"])),
        ("Added colors", _format_text_color_list(report["added"])),
        ("Removed colors", _format_text_color_list(report["removed"])),
        ("Drift score", f"{report['drift_score']}%"),
    ]
    lines = [_single_line(title), ""]
    lines.extend(f"{label}: {_single_line(value)}" for label, value in rows)
    return "\n".join(lines) + "\n"


def render_compare_html_report(
    report: dict[str, Any], *, title: str = "Palette Drift Report"
) -> str:
    safe_title = escape(title)
    before = report["before"]
    after = report["after"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f7f5;
      color: #222222;
    }}
    body {{
      margin: 0;
      padding: 32px;
    }}
    main {{
      max-width: 1080px;
      margin: 0 auto;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 2.4rem;
      line-height: 1.05;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 1.3rem;
    }}
    .meta {{
      margin: 0 0 24px;
      color: #555555;
    }}
    .summary,
    .sides,
    .drift {{
      display: grid;
      gap: 14px;
    }}
    .summary {{
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      margin: 0 0 28px;
    }}
    .sides {{
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      margin: 0 0 28px;
    }}
    .drift {{
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }}
    .panel {{
      border: 1px solid #dddddd;
      border-radius: 8px;
      background: #ffffff;
      padding: 16px;
    }}
    dt {{
      color: #666666;
      font-size: 0.78rem;
      font-weight: 700;
      margin: 0 0 4px;
      text-transform: uppercase;
    }}
    dd {{
      margin: 0 0 12px;
      overflow-wrap: anywhere;
    }}
    dd:last-child {{
      margin-bottom: 0;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid #dddddd;
      border-radius: 999px;
      padding: 6px 10px;
      background: #ffffff;
      font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
      font-size: 0.9rem;
    }}
    .swatch {{
      width: 18px;
      height: 18px;
      border: 1px solid rgba(0, 0, 0, 0.2);
      border-radius: 50%;
      flex: 0 0 auto;
    }}
    .palette-preview {{
      display: flex;
      min-height: 38px;
      overflow: hidden;
      border: 1px solid #dddddd;
      border-radius: 6px;
      margin: 0 0 16px;
      background: #f7f7f5;
    }}
    .preview-swatch {{
      flex: 1 1 0;
      min-width: 28px;
      border: 0;
      border-right: 1px solid rgba(0, 0, 0, 0.16);
    }}
    .preview-swatch:last-child {{
      border-right: 0;
    }}
    .none {{
      color: #666666;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{safe_title}</h1>
    <p class="meta">
      {escape(str(before["source_path"]))} -> {escape(str(after["source_path"]))}
    </p>
    <dl class="summary" aria-label="Palette drift summary">
      <div class="panel">
        <dt>Before dominant</dt>
        <dd>{_format_html_optional_color(before["dominant"])}</dd>
      </div>
      <div class="panel">
        <dt>After dominant</dt>
        <dd>{_format_html_optional_color(after["dominant"])}</dd>
      </div>
      <div class="panel">
        <dt>Drift score</dt>
        <dd>{escape(str(report["drift_score"]))}%</dd>
      </div>
    </dl>
    <section class="sides" aria-label="Compared image palettes">
      {_render_compare_side("Before", before)}
      {_render_compare_side("After", after)}
    </section>
    <section class="drift" aria-label="Palette color changes">
      {_render_color_group("Shared colors", report["shared"])}
      {_render_color_group("Added colors", report["added"])}
      {_render_color_group("Removed colors", report["removed"])}
    </section>
  </main>
</body>
</html>
"""


def write_compare_html_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_compare_html_report(report), encoding="utf-8")


def render_compare_markdown_report(
    report: dict[str, Any], *, title: str = "Palette Drift Report"
) -> str:
    before = report["before"]
    after = report["after"]
    rows = [
        ("Before source name", str(before["source"])),
        ("Before source path", str(before["source_path"])),
        ("After source name", str(after["source"])),
        ("After source path", str(after["source_path"])),
        (
            "Before dominant colors",
            _format_markdown_color_list([entry["hex"] for entry in before["palette"]]),
        ),
        (
            "After dominant colors",
            _format_markdown_color_list([entry["hex"] for entry in after["palette"]]),
        ),
        ("Shared colors", _format_markdown_color_list(report["shared"])),
        ("Added colors", _format_markdown_color_list(report["added"])),
        ("Removed colors", _format_markdown_color_list(report["removed"])),
        ("Drift score", f"{report['drift_score']}%"),
    ]
    lines = [
        f"# {markdown_escape(title)}",
        "",
        "| Field | Value |",
        "| --- | --- |",
    ]
    for label, value in rows:
        lines.append(f"| {markdown_escape(label)} | {_format_markdown_value(value)} |")
    return "\n".join(lines) + "\n\n"


def write_compare_markdown_report(
    report: dict[str, Any], output_path: str | Path
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_compare_markdown_report(report), encoding="utf-8")


def write_compare_text_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_compare_text_report(report), encoding="utf-8")


def render_compare_csv_report(report: dict[str, Any]) -> str:
    before = report["before"]
    after = report["after"]
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(COMPARE_CSV_HEADER)
    writer.writerows(
        [
            ["metadata", "before_source", before["source_path"], "", "", "", "", ""],
            ["metadata", "after_source", after["source_path"], "", "", "", "", ""],
            ["metadata", "drift_score", report["drift_score"], "", "", "", "", ""],
            [
                "metadata",
                "dominant_before_hex",
                before["dominant"] or "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "metadata",
                "dominant_after_hex",
                after["dominant"] or "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "metadata",
                "shared_count",
                len(report["shared"]),
                "",
                "",
                "",
                "",
                "",
            ],
            ["metadata", "added_count", len(report["added"]), "", "", "", "", ""],
            [
                "metadata",
                "removed_count",
                len(report["removed"]),
                "",
                "",
                "",
                "",
                "",
            ],
        ]
    )

    before_palette = _palette_by_hex(before)
    after_palette = _palette_by_hex(after)
    for hex_color in report["shared"]:
        before_percent = before_palette[hex_color]["percent"]
        after_percent = after_palette[hex_color]["percent"]
        writer.writerow(
            [
                "color",
                "",
                "",
                "shared",
                hex_color,
                before_percent,
                after_percent,
                after_percent - before_percent,
            ]
        )
    for hex_color in report["added"]:
        writer.writerow(
            [
                "color",
                "",
                "",
                "added",
                hex_color,
                "",
                after_palette[hex_color]["percent"],
                "",
            ]
        )
    for hex_color in report["removed"]:
        writer.writerow(
            [
                "color",
                "",
                "",
                "removed",
                hex_color,
                before_palette[hex_color]["percent"],
                "",
                "",
            ]
        )
    return output.getvalue()


def write_compare_csv_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_compare_csv_report(report), encoding="utf-8", newline="")


def write_compare_json(report: dict[str, Any], output_path: str | Path) -> None:
    write_json_report(report, output_path)


def _format_optional_color(value: str | None) -> str:
    return value if value is not None else "none"


def _palette_by_hex(side: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["hex"]: entry for entry in side["palette"]}


def _format_color_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _format_text_color_list(values: list[str]) -> str:
    return ", ".join(values) if values else "None"


def _format_html_optional_color(value: str | None) -> str:
    return escape(value) if value is not None else "None"


def _format_markdown_color_list(values: list[str]) -> str:
    if not values:
        return "None"
    return ", ".join(f"`{markdown_escape(value)}`" for value in values)


def _format_markdown_value(value: str) -> str:
    return markdown_escape(value)


def _single_line(value: object) -> str:
    without_controls = "".join(
        " " if _is_control_character(character) else character
        for character in str(value)
    )
    return " ".join(without_controls.split())


def _is_control_character(value: str) -> bool:
    codepoint = ord(value)
    return codepoint < 32 or 127 <= codepoint < 160


def _render_compare_side(label: str, side: dict[str, Any]) -> str:
    size = side.get("size") or {}
    width = size.get("width")
    height = size.get("height")
    size_label = (
        f"{width} x {height}px"
        if width is not None and height is not None
        else "Unknown"
    )
    return f"""      <article class="panel">
        <h2>{escape(label)}</h2>
        {_render_palette_preview(label, side["palette"])}
        <dl>
          <dt>Source name</dt>
          <dd>{escape(str(side["source"]))}</dd>
          <dt>Source path</dt>
          <dd>{escape(str(side["source_path"]))}</dd>
          <dt>Image size</dt>
          <dd>{escape(size_label)}</dd>
          <dt>Dominant colors</dt>
          <dd>{_render_color_list([entry["hex"] for entry in side["palette"]])}</dd>
        </dl>
      </article>"""


def _render_palette_preview(label: str, palette: list[dict[str, Any]]) -> str:
    preview_label = f"{escape(label)} palette preview"
    if not palette:
        return (
            f'<div class="palette-preview" aria-label="{preview_label}">'
            '<span class="none">None</span></div>'
        )
    swatches = "\n".join(
        f'          <span class="preview-swatch" '
        f'style="background: {_safe_css_hex_color(str(entry["hex"]))}" '
        f'aria-label="{escape(_preview_swatch_label(entry))}" '
        f'title="{escape(_preview_swatch_label(entry))}"></span>'
        for entry in palette
    )
    return f"""        <div class="palette-preview" aria-label="{preview_label}">
{swatches}
        </div>"""


def _preview_swatch_label(entry: dict[str, Any]) -> str:
    hint = entry.get("name", entry.get("label"))
    if hint:
        return f"{entry['hex']} {hint}"
    return str(entry["hex"])


def _render_color_group(label: str, values: list[str]) -> str:
    return f"""      <article class="panel">
        <h2>{escape(label)}</h2>
        {_render_color_list(values)}
      </article>"""


def _render_color_list(values: list[str]) -> str:
    if not values:
        return '<p class="none">None</p>'
    items = "\n".join(
        f'          <li class="chip"><span class="swatch" '
        f'style="background: {_safe_css_hex_color(value)}"></span>{escape(value)}</li>'
        for value in values
    )
    return f"""<ul class="chips">
{items}
        </ul>"""


def _safe_css_hex_color(value: str) -> str:
    return value if _is_hex_color(value) else "transparent"


def _is_hex_color(value: str) -> bool:
    return (
        len(value) == 7
        and value[0] == "#"
        and all(character in "0123456789abcdefABCDEF" for character in value[1:])
    )
