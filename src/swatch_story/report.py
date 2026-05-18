from __future__ import annotations

import csv
import io
import json
import struct
from copy import deepcopy
from html import escape
from pathlib import Path
from typing import Any


def write_json_report(
    summary: dict[str, Any], output_path: str | Path, *, precision: int | None = None
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    report_summary = _summary_with_precision(summary, precision)
    path.write_text(
        json.dumps(report_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_tokens_report(
    summary: dict[str, Any],
    output_path: str | Path,
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            render_tokens_report(summary, title=title, precision=precision),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def render_tokens_report(
    summary: dict[str, Any],
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> dict[str, Any]:
    report_summary = _summary_with_precision(summary, precision)
    return {
        "$schema": "https://design-tokens.github.io/community-group/format/",
        "source": report_summary["source"],
        "title": title,
        "color": {
            entry["label"]: _design_token_entry(entry, precision=precision)
            for entry in report_summary["palette"]
        },
    }


def _design_token_entry(
    entry: dict[str, Any], *, precision: int | None = None
) -> dict[str, Any]:
    return {
        "$type": "color",
        "$value": entry["hex"],
        "description": (
            f"Rank {entry['rank']} color covering "
            f"{_format_decimal(entry['percent'], precision)}% of sampled pixels. "
            f"Use {entry['best_text_color']} text for readable contrast."
        ),
        "extensions": {
            "swatchStory": {
                "rank": entry["rank"],
                "rgb": entry["rgb"],
                "percent": entry["percent"],
                "luminance": entry["luminance"],
                "contrastWithBlack": entry["contrast_with_black"],
                "contrastWithWhite": entry["contrast_with_white"],
                "bestTextColor": entry["best_text_color"],
            }
        },
    }


CSV_HEADER = [
    "rank",
    "hex",
    "r",
    "g",
    "b",
    "count",
    "percent",
    "luminance",
    "contrast_with_black",
    "contrast_with_white",
    "best_text_color",
    "label",
    "name",
]

SVG_FONT = (
    "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "
    "'Segoe UI', sans-serif"
)


def render_csv_report(summary: dict[str, Any], *, precision: int | None = None) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(CSV_HEADER)
    for entry in summary["palette"]:
        red, green, blue = entry["rgb"]
        writer.writerow(
            [
                entry["rank"],
                entry["hex"],
                red,
                green,
                blue,
                entry["count"],
                _format_decimal(entry["percent"], precision),
                _format_decimal(entry["luminance"], precision),
                _format_decimal(entry["contrast_with_black"], precision),
                _format_decimal(entry["contrast_with_white"], precision),
                entry["best_text_color"],
                entry["label"],
                entry.get("name", ""),
            ]
        )
    return output.getvalue()


def write_csv_report(
    summary: dict[str, Any], output_path: str | Path, *, precision: int | None = None
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_csv_report(summary, precision=precision),
        encoding="utf-8",
        newline="",
    )


def render_ase_report(summary: dict[str, Any], *, title: str = "Swatch Story") -> bytes:
    blocks = [_ase_block(0xC001, _ase_string(title))]
    for entry in summary["palette"]:
        red, green, blue = (value / 255 for value in entry["rgb"])
        data = b"".join(
            [
                _ase_string(_ase_swatch_name(entry)),
                b"RGB ",
                struct.pack(">fffH", red, green, blue, 0),
            ]
        )
        blocks.append(_ase_block(0x0001, data))
    blocks.append(_ase_block(0xC002, b""))
    return b"".join(
        [
            b"ASEF",
            struct.pack(">HHI", 1, 0, len(blocks)),
            *blocks,
        ]
    )


def _ase_block(block_type: int, data: bytes) -> bytes:
    return struct.pack(">HI", block_type, len(data)) + data


def _ase_string(value: object) -> bytes:
    text = _single_line(value)
    encoded = f"{text}\0".encode("utf-16-be")
    return struct.pack(">H", len(encoded) // 2) + encoded


def _ase_swatch_name(entry: dict[str, Any]) -> str:
    label = _single_line(entry["label"])
    if "name" in entry:
        label = f"{label} {_single_line(entry['name'])}"
    return label


def _single_line(value: object) -> str:
    return " ".join(str(value).split())


def write_ase_report(
    summary: dict[str, Any], output_path: str | Path, *, title: str = "Swatch Story"
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render_ase_report(summary, title=title))


def render_css_report(summary: dict[str, Any]) -> str:
    lines = ["/* Generated by swatch-story. */", ":root {"]
    for entry in summary["palette"]:
        label = entry["label"]
        rgb = ", ".join(str(value) for value in entry["rgb"])
        if "name" in entry:
            lines.append(f"  /* {escape_css_comment(str(entry['name']))} */")
        lines.extend(
            [
                f"  --swatch-story-{label}: {entry['hex']};",
                f"  --swatch-story-{label}-rgb: {rgb};",
                (
                    f"  --swatch-story-{label}-contrast-black: "
                    f"{entry['contrast_with_black']};"
                ),
                (
                    f"  --swatch-story-{label}-contrast-white: "
                    f"{entry['contrast_with_white']};"
                ),
                f"  --swatch-story-{label}-text: {entry['best_text_color']};",
            ]
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def escape_css_comment(value: str) -> str:
    return value.replace("*/", "* /")


def write_css_report(summary: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_css_report(summary), encoding="utf-8")


def render_gpl_report(summary: dict[str, Any], *, title: str = "Swatch Story") -> str:
    safe_title = " ".join(str(title).split())
    palette = summary["palette"]
    lines = [
        "GIMP Palette",
        f"Name: {safe_title}",
        f"Columns: {len(palette)}",
        "# Generated by swatch-story.",
    ]
    for entry in palette:
        red, green, blue = entry["rgb"]
        label = _single_line(entry["label"])
        if "name" in entry:
            label = f"{label} {entry['name']}"
        lines.append(f"{red:3d} {green:3d} {blue:3d} {label}")
    return "\n".join(lines) + "\n"


def write_gpl_report(
    summary: dict[str, Any], output_path: str | Path, *, title: str = "Swatch Story"
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_gpl_report(summary, title=title), encoding="utf-8")


def render_markdown_report(
    summary: dict[str, Any],
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> str:
    source = markdown_escape(str(summary["source"]))
    width = summary["size"]["width"]
    height = summary["size"]["height"]
    settings = summary.get("settings", {})
    cluster_distance = markdown_escape(str(settings.get("cluster_distance", 0)))
    cluster_space = markdown_escape(str(settings.get("cluster_space", "rgb")))
    palette = summary["palette"]
    include_names = any("name" in entry for entry in palette)
    header = "| Rank | Color | RGB | Percent | Luminance | Contrast | Text | Label |"
    divider = "| ---: | --- | --- | ---: | ---: | --- | --- | --- |"
    if include_names:
        header = (
            "| Rank | Color | Name | RGB | Percent | Luminance | Contrast | "
            "Text | Label |"
        )
        divider = "| ---: | --- | --- | --- | ---: | ---: | --- | --- | --- |"
    lines = [
        f"# {markdown_escape(title)}",
        "",
        f"Source: `{source}`  ",
        f"Size: {width} x {height} px  ",
        f"Colors: {len(palette)}  ",
        f"Cluster distance: {cluster_distance}  ",
        f"Cluster space: {cluster_space}",
        "",
        header,
        divider,
    ]
    for entry in palette:
        rgb = ", ".join(str(value) for value in entry["rgb"])
        row = [
            str(entry["rank"]),
            f"`{markdown_escape(entry['hex'])}`",
        ]
        if include_names:
            row.append(markdown_escape(str(entry.get("name", ""))))
        row.extend(
            [
                f"`{markdown_escape(rgb)}`",
                f"{_format_decimal(entry['percent'], precision)}%",
                _format_decimal(entry["luminance"], precision),
                _format_contrast_pair(entry, precision, separator="; "),
                markdown_escape(entry["best_text_color"]),
                markdown_escape(entry["label"]),
            ]
        )
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n\n"


def markdown_escape(value: str) -> str:
    return (
        escape(value)
        .replace("|", "\\|")
        .replace("\r\n", "<br>")
        .replace("\r", "<br>")
        .replace("\n", "<br>")
    )


def write_markdown_report(
    summary: dict[str, Any],
    output_path: str | Path,
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_markdown_report(summary, title=title, precision=precision),
        encoding="utf-8",
    )


def render_batch_markdown_report(
    summaries: list[dict[str, Any]],
    *,
    title: str = "Swatch Story Batch Review",
    precision: int | None = None,
) -> str:
    settings = _settings_summary(summaries[0]) if summaries else "Settings: none"
    lines = [
        f"# {markdown_escape(title)}",
        "",
        f"Images: {len(summaries)}  ",
        markdown_escape(settings),
        "",
    ]
    for summary in summaries:
        source = markdown_escape(str(summary["source"]))
        source_path = markdown_escape(
            str(summary.get("source_path", summary["source"]))
        )
        width = summary["size"]["width"]
        height = summary["size"]["height"]
        lines.extend(
            [
                f"## {source}",
                "",
                f"Source path: `{source_path}`  ",
                f"Size: {width} x {height} px  ",
                f"Dominant colors: {_batch_markdown_dominant(summary, precision)}",
                "",
                _batch_markdown_table(summary, precision),
                "",
                "Contrast guidance:",
            ]
        )
        for entry in summary["palette"]:
            lines.append(
                "- "
                f"`{markdown_escape(str(entry['hex']))}`: "
                f"{markdown_escape(_batch_guidance(entry, precision))}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _batch_markdown_dominant(summary: dict[str, Any], precision: int | None) -> str:
    return ", ".join(
        f"`{markdown_escape(str(entry['hex']))}` "
        f"{_format_decimal(entry['percent'], precision)}%"
        for entry in summary["palette"][:3]
    )


def _batch_markdown_table(summary: dict[str, Any], precision: int | None) -> str:
    palette = summary["palette"]
    include_names = any("name" in entry for entry in palette)
    header = "| Rank | Color | RGB | Percent | Luminance | Text | Label |"
    divider = "| ---: | --- | --- | ---: | ---: | --- | --- |"
    if include_names:
        header = "| Rank | Color | Name | RGB | Percent | Luminance | Text | Label |"
        divider = "| ---: | --- | --- | --- | ---: | ---: | --- | --- |"
    lines = [header, divider]
    for entry in palette:
        rgb = ", ".join(str(value) for value in entry["rgb"])
        row = [
            str(entry["rank"]),
            f"`{markdown_escape(str(entry['hex']))}`",
        ]
        if include_names:
            row.append(markdown_escape(str(entry.get("name", ""))))
        row.extend(
            [
                f"`{markdown_escape(rgb)}`",
                f"{_format_decimal(entry['percent'], precision)}%",
                _format_decimal(entry["luminance"], precision),
                markdown_escape(str(entry["best_text_color"])),
                markdown_escape(str(entry["label"])),
            ]
        )
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _batch_guidance(entry: dict[str, Any], precision: int | None) -> str:
    return (
        f"Use {_single_line(entry['best_text_color'])} text; "
        f"contrast {_format_contrast_pair(entry, precision, separator='; ')}"
    )


def write_batch_markdown_report(
    summaries: list[dict[str, Any]],
    output_path: str | Path,
    *,
    title: str = "Swatch Story Batch Review",
    precision: int | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_batch_markdown_report(
            summaries,
            title=title,
            precision=precision,
        ),
        encoding="utf-8",
    )


def render_wcag_audit_report(
    summary: dict[str, Any],
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> str:
    source = markdown_escape(str(summary["source"]))
    source_path = markdown_escape(str(summary.get("source_path", summary["source"])))
    width = summary["size"]["width"]
    height = summary["size"]["height"]
    settings = markdown_escape(_settings_summary(summary))
    lines = [
        f"# {markdown_escape(title)} WCAG Audit",
        "",
        f"Source: `{source}`  ",
        f"Source path: `{source_path}`  ",
        f"Image size: {width} x {height} px  ",
        f"Settings: {settings.removeprefix('Settings: ')}",
        "",
        (
            "Thresholds: normal AA >= 4.5, large AA >= 3.0, "
            "normal AAA >= 7.0, large AAA >= 4.5."
        ),
        "",
        (
            "| Rank | Color | Label | Preferred text | Black text readiness | "
            "White text readiness | Recommendation |"
        ),
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in summary["palette"]:
        label = _wcag_audit_label(entry)
        preferred = str(entry["best_text_color"])
        preferred_ratio = float(entry[f"contrast_with_{preferred}"])
        recommendation_passes = _wcag_readiness(preferred_ratio)
        if recommendation_passes == "No WCAG text pass":
            recommendation = "No black or white text reaches WCAG thresholds."
        else:
            recommendation = f"Use {preferred} text; passes {recommendation_passes}."
        lines.append(
            "| "
            + " | ".join(
                [
                    str(entry["rank"]),
                    f"`{markdown_escape(str(entry['hex']))}`",
                    markdown_escape(label),
                    markdown_escape(preferred),
                    markdown_escape(
                        _wcag_readiness(float(entry["contrast_with_black"]))
                    ),
                    markdown_escape(
                        _wcag_readiness(float(entry["contrast_with_white"]))
                    ),
                    markdown_escape(recommendation),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n\n"


def _wcag_audit_label(entry: dict[str, Any]) -> str:
    label = _single_line(entry["label"])
    if "name" in entry:
        label = f"{label}, {_single_line(entry['name'])}"
    return label


def _wcag_readiness(ratio: float) -> str:
    passes = []
    if ratio >= 4.5:
        passes.append("AA normal")
    if ratio >= 3.0:
        passes.append("AA large")
    if ratio >= 7.0:
        passes.append("AAA normal")
    if ratio >= 4.5:
        passes.append("AAA large")
    if not passes:
        return "No WCAG text pass"
    return ", ".join(passes)


def write_wcag_audit_report(
    summary: dict[str, Any],
    output_path: str | Path,
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_wcag_audit_report(summary, title=title, precision=precision),
        encoding="utf-8",
    )


def render_text_report(
    summary: dict[str, Any],
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> str:
    settings = summary.get("settings", {})
    width = summary["size"]["width"]
    height = summary["size"]["height"]
    palette = summary["palette"]
    colors = _single_line(settings.get("colors", len(palette)))
    sample_step = _single_line(settings.get("sample_step", "unknown"))
    sample_limit = _single_line(settings.get("sample_limit", "unknown"))
    cluster_distance = _single_line(settings.get("cluster_distance", 0))
    cluster_space = _single_line(settings.get("cluster_space", "rgb"))
    sort = _single_line(settings.get("sort", "frequency"))
    ignored_color = _single_line(settings.get("ignore_color", "none"))
    names_enabled = bool(
        settings.get("color_names", any("name" in entry for entry in palette))
    )
    names_label = "included" if names_enabled else "not included"
    lines = [
        _single_line(title),
        "",
        f"Source: {_single_line(summary['source'])}",
        f"Image size: {width} x {height} px",
        (
            f"Settings: colors {colors}; sample step {sample_step}; "
            f"sample limit {sample_limit}; "
            f"cluster distance {cluster_distance}; cluster space {cluster_space}; "
            f"sort {sort}; "
            f"ignored color {ignored_color}; names {names_label}"
        ),
        "",
        "Swatches:",
    ]
    for entry in palette:
        red, green, blue = entry["rgb"]
        line = (
            f"{entry['rank']}. {_single_line(entry['hex'])} | "
            f"rgb({red}, {green}, {blue}) | "
            f"{_format_decimal(entry['percent'], precision)}% | "
            f"{_single_line(entry['label'])} | "
            f"contrast {_format_contrast_pair(entry, precision)} | "
            f"text {_single_line(entry['best_text_color'])}"
        )
        if "name" in entry:
            line = f"{line} | name {_single_line(entry['name'])}"
        lines.append(line)
    return "\n".join(lines) + "\n"


def write_text_report(
    summary: dict[str, Any],
    output_path: str | Path,
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_text_report(summary, title=title, precision=precision),
        encoding="utf-8",
    )


def render_svg_report(
    summary: dict[str, Any],
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> str:
    palette = summary["palette"]
    width = 960
    row_height = 128
    top_height = 190
    bottom_padding = 32
    height = top_height + (len(palette) * row_height) + bottom_padding
    safe_title = escape(str(title), quote=True)
    source = escape(str(summary["source"]), quote=True)
    image_width = escape(str(summary["size"]["width"]), quote=True)
    image_height = escape(str(summary["size"]["height"]), quote=True)
    settings = escape(_settings_summary(summary), quote=True)
    swatches = "\n".join(
        _render_svg_swatch(
            entry,
            y=top_height + (index * row_height),
            precision=precision,
        )
        for index, entry in enumerate(palette)
    )
    title_text = _svg_text(
        40,
        56,
        safe_title,
        fill="#222222",
        size=34,
        weight=700,
    )
    source_text = _svg_text(40, 94, f"Source: {source}", fill="#555555")
    size_text = _svg_text(
        40,
        124,
        f"Image: {image_width} x {image_height} px",
        fill="#555555",
    )
    settings_text = _svg_text(40, 154, settings, fill="#555555")
    svg_attrs = (
        f'xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" '
        'role="img" aria-labelledby="title desc"'
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg {svg_attrs}>
  <title id="title">{safe_title}</title>
  <desc id="desc">Palette swatch sheet for {source}</desc>
  <rect width="100%" height="100%" fill="#f7f7f5"/>
  {title_text}
  {source_text}
  {size_text}
  {settings_text}
{swatches}
</svg>
"""


def _settings_summary(summary: dict[str, Any]) -> str:
    settings = summary.get("settings", {})
    palette = summary["palette"]
    colors = _single_line(settings.get("colors", len(palette)))
    sample_step = _single_line(settings.get("sample_step", "unknown"))
    sample_limit = _single_line(settings.get("sample_limit", "unknown"))
    cluster_distance = _single_line(settings.get("cluster_distance", 0))
    cluster_space = _single_line(settings.get("cluster_space", "rgb"))
    sort = _single_line(settings.get("sort", "frequency"))
    ignored_color = _single_line(settings.get("ignore_color", "none"))
    names_enabled = bool(
        settings.get("color_names", any("name" in entry for entry in palette))
    )
    names_label = "included" if names_enabled else "not included"
    return (
        f"Settings: colors {colors}; sample step {sample_step}; "
        f"sample limit {sample_limit}; cluster distance {cluster_distance}; "
        f"cluster space {cluster_space}; sort {sort}; ignored color {ignored_color}; "
        f"names {names_label}"
    )


def _render_svg_swatch(
    entry: dict[str, Any], *, y: int, precision: int | None = None
) -> str:
    hex_color = escape(str(entry["hex"]), quote=True)
    label = escape(_single_line(entry["label"]), quote=True)
    text_color = escape(_single_line(entry["best_text_color"]), quote=True)
    name = ""
    if "name" in entry:
        name = f" | Name {escape(_single_line(entry['name']), quote=True)}"
    details = escape(
        (
            f"{_format_decimal(entry['percent'], precision)}% | "
            f"Luminance {_format_decimal(entry['luminance'], precision)} | "
            f"Contrast {_format_contrast_pair(entry, precision, separator='; ')} | "
            f"Label {_single_line(entry['label'])} | "
            f"Text {_single_line(entry['best_text_color'])}"
        ),
        quote=True,
    )
    swatch_title = escape(f"{entry['rank']}. {entry['hex']}", quote=True)
    title_text = _svg_text(
        174,
        38,
        swatch_title,
        fill="#222222",
        size=23,
        weight=700,
    )
    details_text = _svg_text(174, 64, details, fill="#555555", size=16)
    label_text = _svg_text(174, 88, f"{label}{name}", fill="#555555", size=16)
    hex_text = _svg_text(
        42,
        59,
        hex_color,
        fill=text_color,
        size=18,
        weight=700,
    )
    return f"""  <g transform="translate(40 {y})">
    <rect x="0" y="0" width="880" height="104" rx="8" fill="#ffffff" stroke="#dddddd"/>
    <rect x="18" y="18" width="132" height="68" rx="6" fill="{hex_color}"/>
    {title_text}
    {details_text}
    {label_text}
    {hex_text}
  </g>"""


def _svg_text(
    x: int,
    y: int,
    text: str,
    *,
    fill: str,
    size: int = 17,
    weight: int | None = None,
) -> str:
    weight_attr = f' font-weight="{weight}"' if weight is not None else ""
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{SVG_FONT}" '
        f'font-size="{size}"{weight_attr}>{text}</text>'
    )


def write_svg_report(
    summary: dict[str, Any],
    output_path: str | Path,
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_svg_report(summary, title=title, precision=precision),
        encoding="utf-8",
    )


def render_html_report(
    summary: dict[str, Any],
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
    thumbnail_href: str | None = None,
) -> str:
    safe_title = escape(title)
    source_name = escape(str(summary["source"]))
    source_path = escape(str(summary.get("source_path", summary["source"])))
    width = summary["size"]["width"]
    height = summary["size"]["height"]
    settings = summary.get("settings", {})
    colors = escape(str(settings.get("colors", len(summary["palette"]))))
    cluster_distance = escape(str(settings.get("cluster_distance", 0)))
    cluster_space = escape(str(settings.get("cluster_space", "rgb")))
    sample_step = settings.get("sample_step")
    sample_step_label = (
        f"Every {escape(str(sample_step))} pixel"
        if sample_step is not None
        else "Automatic"
    )
    names_enabled = bool(
        settings.get(
            "color_names",
            any("name" in entry for entry in summary["palette"]),
        )
    )
    swatches = "\n".join(
        render_swatch(entry, precision=precision) for entry in summary["palette"]
    )
    palette_count = len(summary["palette"])
    dominant = escape(str(summary["palette"][0]["hex"])) if palette_count else "none"
    swatch_label = "swatch" if palette_count == 1 else "swatches"
    names_label = "Included" if names_enabled else "Not included"
    sort_label = escape(str(settings.get("sort", "frequency")))
    ignore_color = settings.get("ignore_color")
    ignore_color_html = ""
    if ignore_color is not None:
        ignore_color_html = f"""      <div>
        <dt>Ignored color</dt>
        <dd>{escape(str(ignore_color))}</dd>
      </div>
"""
    preview_html = ""
    if thumbnail_href is not None:
        thumbnail_src = escape(thumbnail_href, quote=True)
        thumbnail_alt = escape(f"Thumbnail preview of {summary['source']}", quote=True)
        preview_html = f"""    <section class="source-preview"
      aria-label="Source image preview">
      <h2>Source preview</h2>
      <img src="{thumbnail_src}" alt="{thumbnail_alt}">
    </section>
"""
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
      max-width: 960px;
      margin: 0 auto;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 2.4rem;
      line-height: 1.05;
    }}
    .meta {{
      margin: 0 0 24px;
      color: #555555;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 0 0 28px;
    }}
    .summary div {{
      border: 1px solid #dddddd;
      border-radius: 8px;
      background: #ffffff;
      padding: 14px;
    }}
    dt {{
      color: #666666;
      font-size: 0.78rem;
      font-weight: 700;
      margin: 0 0 4px;
      text-transform: uppercase;
    }}
    dd {{
      margin: 0;
      overflow-wrap: anywhere;
    }}
    .source-preview {{
      margin: 0 0 28px;
    }}
    .source-preview h2 {{
      margin: 0 0 10px;
      font-size: 1.1rem;
    }}
    .source-preview img {{
      display: block;
      max-width: 320px;
      max-height: 320px;
      width: auto;
      height: auto;
      border: 1px solid #dddddd;
      border-radius: 8px;
      background: #ffffff;
    }}
    .palette {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
    }}
    .swatch {{
      min-height: 290px;
      border: 1px solid rgba(0, 0, 0, 0.16);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 16px;
      box-sizing: border-box;
    }}
    .rank {{
      font-size: 0.85rem;
      opacity: 0.72;
    }}
    .hex {{
      font-size: 1.35rem;
      font-weight: 700;
      overflow-wrap: anywhere;
    }}
    .details,
    .guidance {{
      font-size: 0.92rem;
      line-height: 1.45;
    }}
    .details dl,
    .guidance dl {{
      margin: 12px 0 0;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{safe_title}</h1>
    <p class="meta">
      {palette_count} {swatch_label}; dominant color is {dominant}.
    </p>
    <dl class="summary" aria-label="Image and extraction summary">
      <div>
        <dt>Image name</dt>
        <dd>{source_name}</dd>
      </div>
      <div>
        <dt>Image path</dt>
        <dd>{source_path}</dd>
      </div>
      <div>
        <dt>Image size</dt>
        <dd>{width} x {height}px</dd>
      </div>
      <div>
        <dt>Requested colors</dt>
        <dd>{colors}</dd>
      </div>
      <div>
        <dt>Sample step</dt>
        <dd>{sample_step_label}</dd>
      </div>
      <div>
        <dt>Cluster distance</dt>
        <dd>{cluster_distance}</dd>
      </div>
      <div>
        <dt>Cluster space</dt>
        <dd>{cluster_space}</dd>
      </div>
      <div>
        <dt>Color names</dt>
        <dd>{names_label}</dd>
      </div>
      <div>
        <dt>Sort</dt>
        <dd>{sort_label}</dd>
      </div>
{ignore_color_html}\
    </dl>
{preview_html}\
    <section class="palette" aria-label="Extracted color palette">
{swatches}
    </section>
  </main>
</body>
</html>
"""


def render_batch_html_report(
    summaries: list[dict[str, Any]],
    *,
    title: str = "Swatch Story Batch Review",
    precision: int | None = None,
) -> str:
    safe_title = escape(title)
    settings = escape(
        _settings_summary(summaries[0]) if summaries else "Settings: none"
    )
    image_count = len(summaries)
    cards = "\n".join(
        _render_batch_image_card(summary, precision=precision) for summary in summaries
    )
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
      max-width: 1120px;
      margin: 0 auto;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 2.2rem;
      line-height: 1.1;
    }}
    .meta {{
      margin: 0 0 24px;
      color: #555555;
    }}
    .image-card {{
      border: 1px solid #dddddd;
      border-radius: 8px;
      background: #ffffff;
      margin: 0 0 18px;
      padding: 18px;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 1.35rem;
      overflow-wrap: anywhere;
    }}
    dl {{
      margin: 0;
    }}
    .image-meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 0 0 16px;
    }}
    .image-meta div {{
      border: 1px solid #eeeeee;
      border-radius: 8px;
      padding: 12px;
    }}
    dt {{
      color: #666666;
      font-size: 0.78rem;
      font-weight: 700;
      margin: 0 0 4px;
      text-transform: uppercase;
    }}
    dd {{
      margin: 0;
      overflow-wrap: anywhere;
    }}
    .palette {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
    }}
    .swatch {{
      border: 1px solid rgba(0, 0, 0, 0.16);
      border-radius: 8px;
      min-height: 190px;
      padding: 14px;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .hex {{
      font-size: 1.2rem;
      font-weight: 700;
    }}
    .details {{
      font-size: 0.92rem;
      line-height: 1.45;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{safe_title}</h1>
    <p class="meta">{image_count} audited images. {settings}</p>
{cards}
  </main>
</body>
</html>
"""


def _render_batch_image_card(
    summary: dict[str, Any], *, precision: int | None = None
) -> str:
    source = escape(str(summary["source"]))
    source_path = escape(str(summary.get("source_path", summary["source"])))
    width = summary["size"]["width"]
    height = summary["size"]["height"]
    dominant = escape(_batch_html_dominant(summary, precision))
    swatches = "\n".join(
        _render_batch_swatch(entry, precision=precision) for entry in summary["palette"]
    )
    return f"""    <section class="image-card">
      <h2>{source}</h2>
      <dl class="image-meta">
        <div>
          <dt>Source path</dt>
          <dd>{source_path}</dd>
        </div>
        <div>
          <dt>Image size</dt>
          <dd>{width} x {height}px</dd>
        </div>
        <div>
          <dt>Dominant colors</dt>
          <dd>{dominant}</dd>
        </div>
      </dl>
      <section class="palette" aria-label="Palette for {source}">
{swatches}
      </section>
    </section>"""


def _batch_html_dominant(summary: dict[str, Any], precision: int | None) -> str:
    return ", ".join(
        f"{entry['hex']} {_format_decimal(entry['percent'], precision)}%"
        for entry in summary["palette"][:3]
    )


def _render_batch_swatch(entry: dict[str, Any], *, precision: int | None = None) -> str:
    hex_color = escape(str(entry["hex"]))
    label = escape(str(entry["label"]))
    rgb = escape(", ".join(str(value) for value in entry["rgb"]))
    style = escape(f"background: {entry['hex']}; color: {entry['best_text_color']}")
    name_line = ""
    if "name" in entry:
        name_line = f"""          <dt>Common name</dt>
          <dd>{escape(str(entry["name"]))}</dd>
"""
    return f"""        <article class="swatch" style="{style}">
          <div>
            <div class="hex">{hex_color}</div>
            <div>{label}</div>
          </div>
          <dl class="details">
{name_line}\
            <dt>RGB</dt>
            <dd>{rgb}</dd>
            <dt>Share</dt>
            <dd>{_format_decimal(entry["percent"], precision)}%</dd>
            <dt>Contrast guidance</dt>
            <dd>{escape(_batch_guidance(entry, precision))}</dd>
            <dt>Relative luminance</dt>
            <dd>{_format_decimal(entry["luminance"], precision)}</dd>
          </dl>
        </article>"""


def write_batch_html_report(
    summaries: list[dict[str, Any]],
    output_path: str | Path,
    *,
    title: str = "Swatch Story Batch Review",
    precision: int | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_batch_html_report(
            summaries,
            title=title,
            precision=precision,
        ),
        encoding="utf-8",
    )


def write_html_thumbnail(
    image_path: str | Path,
    output_path: str | Path,
    *,
    max_dimension: int = 320,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    from PIL import Image

    with Image.open(image_path) as image:
        thumbnail = image.convert("RGB")
        thumbnail.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        thumbnail.save(path)


def render_swatch(entry: dict[str, Any], *, precision: int | None = None) -> str:
    hex_color = escape(entry["hex"])
    text_color = escape(entry["best_text_color"])
    label = escape(entry["label"])
    rgb = ", ".join(str(value) for value in entry["rgb"])
    style = escape(f"background: {entry['hex']}; color: {entry['best_text_color']}")
    contrast_black = float(entry["contrast_with_black"])
    contrast_white = float(entry["contrast_with_white"])
    contrast = max(contrast_black, contrast_white)
    contrast_text = escape(f"{_format_decimal(contrast, precision)}:1")
    black_contrast_text = escape(
        f"{_format_decimal(entry['contrast_with_black'], precision)}:1"
    )
    white_contrast_text = escape(
        f"{_format_decimal(entry['contrast_with_white'], precision)}:1"
    )
    guidance = "WCAG AA for normal text" if contrast >= 4.5 else "Use for large text"
    name_line = ""
    if "name" in entry:
        name_line = f"""            <dt>Common name</dt>
            <dd>{escape(str(entry["name"]))}</dd>
"""
    return f"""      <article class="swatch" style="{style}">
        <div class="rank">#{entry["rank"]} - {label}</div>
        <div>
          <div class="hex">{hex_color}</div>
          <div class="details">
            <dl>
{name_line}\
              <dt>RGB</dt>
              <dd>{escape(rgb)}</dd>
              <dt>Share</dt>
              <dd>{_format_decimal(entry["percent"], precision)}% of sampled pixels</dd>
              <dt>Relative luminance</dt>
              <dd>{_format_decimal(entry["luminance"], precision)}</dd>
            </dl>
          </div>
          <div class="guidance">
            <dl>
              <dt>Best readable text</dt>
              <dd>Use {text_color} text</dd>
              <dt>Contrast ratio</dt>
              <dd>{contrast_text}; {guidance}</dd>
              <dt>Black contrast</dt>
              <dd>{black_contrast_text}</dd>
              <dt>White contrast</dt>
              <dd>{white_contrast_text}</dd>
            </dl>
          </div>
        </div>
      </article>"""


def write_html_report(
    summary: dict[str, Any],
    output_path: str | Path,
    *,
    title: str = "Swatch Story",
    precision: int | None = None,
    thumbnail_href: str | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_html_report(
            summary,
            title=title,
            precision=precision,
            thumbnail_href=thumbnail_href,
        ),
        encoding="utf-8",
    )


def _format_decimal(value: object, precision: int | None) -> str:
    if precision is None:
        return str(value)
    return f"{float(value):.{precision}f}"


def _format_contrast_pair(
    entry: dict[str, Any], precision: int | None, *, separator: str = " "
) -> str:
    black = _format_decimal(entry["contrast_with_black"], precision)
    white = _format_decimal(entry["contrast_with_white"], precision)
    return f"black {black}:1{separator}white {white}:1"


def _summary_with_precision(
    summary: dict[str, Any], precision: int | None
) -> dict[str, Any]:
    if precision is None:
        return summary
    report_summary = deepcopy(summary)
    for entry in report_summary["palette"]:
        entry["percent"] = round(float(entry["percent"]), precision)
        entry["luminance"] = round(float(entry["luminance"]), precision)
        entry["contrast_with_black"] = round(
            float(entry["contrast_with_black"]), precision
        )
        entry["contrast_with_white"] = round(
            float(entry["contrast_with_white"]), precision
        )
    return report_summary
