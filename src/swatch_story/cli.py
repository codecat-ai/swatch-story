from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from swatch_story.compare import (
    baseline_report,
    compare_summaries,
    render_compare_text,
    write_baseline_html_report,
    write_baseline_json,
    write_baseline_markdown_report,
    write_baseline_text_report,
    write_compare_csv_report,
    write_compare_html_report,
    write_compare_json,
    write_compare_markdown_report,
    write_compare_text_report,
)
from swatch_story.gallery import GalleryError, create_gallery
from swatch_story.palette import (
    DEFAULT_SAMPLE_LIMIT,
    MAX_CLUSTER_DISTANCE,
    MAX_COLORS,
    MIN_CLUSTER_DISTANCE,
    MIN_COLORS,
    VALID_CLUSTER_SPACES,
    VALID_SORTS,
    PaletteError,
    normalize_ignore_color,
    normalize_matte,
    summarize_image,
    validate_sample_limit,
)
from swatch_story.report import (
    write_ase_report,
    write_batch_html_report,
    write_batch_markdown_report,
    write_css_report,
    write_csv_report,
    write_gpl_report,
    write_html_report,
    write_html_thumbnail,
    write_json_report,
    write_markdown_report,
    write_svg_report,
    write_text_report,
    write_tokens_report,
    write_wcag_audit_report,
)

LABEL_PREFIX_PATTERN = re.compile(r"[a-z][a-z0-9-]*\Z")
PRESET_KEYS = {
    "colors",
    "sample_step",
    "sample_limit",
    "ignore_color",
    "matte",
    "cluster_distance",
    "cluster_space",
    "sort",
    "names",
    "precision",
    "label_prefix",
    "title",
    "min_delta_percent",
}
SHARED_PRESET_KEYS = {
    "colors",
    "sample_step",
    "sample_limit",
    "ignore_color",
    "matte",
    "cluster_distance",
    "cluster_space",
    "sort",
    "names",
}
MAIN_PRESET_KEYS = SHARED_PRESET_KEYS | {
    "precision",
    "label_prefix",
    "title",
}
COMPARE_PRESET_KEYS = SHARED_PRESET_KEYS | {
    "precision",
    "title",
    "min_delta_percent",
}
BATCH_PRESET_KEYS = SHARED_PRESET_KEYS | {
    "precision",
    "title",
}
BASELINE_PRESET_KEYS = COMPARE_PRESET_KEYS
PRESET_FLAG_BY_KEY = {key: f"--{key.replace('_', '-')}" for key in PRESET_KEYS}


def cluster_distance_value(value: str) -> int:
    try:
        distance = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "--cluster-distance must be an integer"
        ) from exc
    if distance < MIN_CLUSTER_DISTANCE or distance > MAX_CLUSTER_DISTANCE:
        raise argparse.ArgumentTypeError(
            f"--cluster-distance must be between {MIN_CLUSTER_DISTANCE} "
            f"and {MAX_CLUSTER_DISTANCE}"
        )
    return distance


def precision_value(value: str) -> int:
    try:
        precision = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--precision must be an integer") from exc
    if precision < 0 or precision > 6:
        raise argparse.ArgumentTypeError("--precision must be between 0 and 6")
    return precision


def min_delta_percent_value(value: str) -> float:
    try:
        percent = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "--min-delta-percent must be a number"
        ) from exc
    if percent < 0:
        raise argparse.ArgumentTypeError("--min-delta-percent must be 0 or greater")
    return percent


def label_prefix_value(value: str) -> str:
    if not LABEL_PREFIX_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "--label-prefix must start with a lowercase letter and contain only "
            "lowercase letters, numbers, and hyphens"
        )
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swatch-story",
        description=(
            "Extract a local image color story as console, JSON, design-token "
            "JSON, CSV, HTML, CSS, Markdown, plain text, GIMP palette, and "
            "Adobe ASE output."
        ),
    )
    parser.add_argument("image", help="Local image path")
    add_palette_options(parser)
    parser.add_argument("--json", dest="json_path", help="Write JSON report to PATH")
    parser.add_argument(
        "--tokens",
        dest="tokens_path",
        help="Write design-token JSON report to PATH",
    )
    parser.add_argument("--csv", dest="csv_path", help="Write CSV report to PATH")
    parser.add_argument(
        "--html", dest="html_path", help="Write standalone HTML to PATH"
    )
    parser.add_argument(
        "--html-thumbnail",
        dest="html_thumbnail_path",
        help=(
            "Write a local thumbnail image to PATH and link it from --html. "
            "Requires --html."
        ),
    )
    parser.add_argument(
        "--css", dest="css_path", help="Write CSS custom properties to PATH"
    )
    parser.add_argument(
        "--markdown", dest="markdown_path", help="Write Markdown report to PATH"
    )
    parser.add_argument(
        "--wcag-audit",
        dest="wcag_audit_path",
        help="Write WCAG-oriented Markdown audit report to PATH",
    )
    parser.add_argument(
        "--text", dest="text_path", help="Write plain-text report to PATH"
    )
    parser.add_argument(
        "--svg", dest="svg_path", help="Write standalone SVG swatch sheet to PATH"
    )
    parser.add_argument(
        "--gpl", dest="gpl_path", help="Write GIMP .gpl palette to PATH"
    )
    parser.add_argument(
        "--ase", dest="ase_path", help="Write Adobe Swatch Exchange .ase to PATH"
    )
    parser.add_argument(
        "--title",
        default="Swatch Story",
        help=(
            "Title for design-token JSON, HTML, Markdown, text, GIMP palette, "
            "and ASE output"
        ),
    )
    parser.add_argument(
        "--precision",
        type=precision_value,
        default=None,
        metavar="N",
        help=(
            "Decimal places for report percentages and luminance values, 0-6. "
            "Default preserves existing output."
        ),
    )
    parser.add_argument(
        "--label-prefix",
        type=label_prefix_value,
        default=None,
        metavar="PREFIX",
        help=(
            "Replace palette labels with PREFIX-1, PREFIX-2, etc. PREFIX must "
            "start with a lowercase letter and contain only lowercase letters, "
            "numbers, and hyphens."
        ),
    )
    return parser


def build_compare_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swatch-story compare",
        description="Compare palette drift between two local images.",
    )
    parser.add_argument("before_image", help="Local image path for the earlier image")
    parser.add_argument("after_image", help="Local image path for the later image")
    add_palette_options(parser)
    parser.add_argument("--json", dest="json_path", help="Write JSON report to PATH")
    parser.add_argument("--csv", dest="csv_path", help="Write CSV report to PATH")
    parser.add_argument(
        "--html", dest="html_path", help="Write standalone HTML report to PATH"
    )
    parser.add_argument(
        "--markdown", dest="markdown_path", help="Write Markdown report to PATH"
    )
    parser.add_argument(
        "--text", dest="text_path", help="Write plain-text report to PATH"
    )
    parser.add_argument(
        "--min-delta-percent",
        type=min_delta_percent_value,
        default=0.0,
        metavar="N",
        help=(
            "Only include shared-color delta detail rows when the absolute "
            "percentage change is at least N. Default: 0.0."
        ),
    )
    parser.add_argument(
        "--title",
        default="Palette Drift Report",
        help="Title for HTML, Markdown, and text compare reports",
    )
    parser.add_argument(
        "--precision",
        type=precision_value,
        default=None,
        metavar="N",
        help=(
            "Decimal places for report percentages and luminance values, 0-6. "
            "Default preserves existing output."
        ),
    )
    return parser


def build_gallery_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swatch-story gallery",
        description=(
            "Generate deterministic sample PNG fixtures and optional gallery metadata."
        ),
    )
    parser.add_argument("output_dir", help="Directory where gallery files are written")
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Write only PNG fixtures and skip README.md",
    )
    parser.add_argument(
        "--manifest",
        action="store_true",
        help="Write manifest.json with expected sample metadata",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        metavar="TAG",
        help="Generate only gallery samples containing TAG. May be repeated.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing gallery files",
    )
    return parser


def build_presets_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swatch-story presets",
        description=(
            "List and validate local JSON preset files before a review session."
        ),
    )
    parser.add_argument("preset_paths", nargs="+", help="Local JSON preset paths")
    parser.add_argument(
        "--json",
        dest="json_path",
        help="Write preset validation JSON report to PATH",
    )
    return parser


def build_batch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swatch-story batch",
        description="Combine multiple local image palette audits into one team report.",
    )
    parser.add_argument("images", nargs="+", help="Local image paths")
    add_palette_options(parser)
    parser.add_argument(
        "--title",
        default="Swatch Story Batch Review",
        help="Title for Markdown and HTML batch reports",
    )
    parser.add_argument(
        "--precision",
        type=precision_value,
        default=None,
        metavar="N",
        help=(
            "Decimal places for report percentages and luminance values, 0-6. "
            "Default preserves existing output."
        ),
    )
    parser.add_argument(
        "--markdown", dest="markdown_path", help="Write Markdown batch report to PATH"
    )
    parser.add_argument(
        "--html", dest="html_path", help="Write standalone HTML batch report to PATH"
    )
    return parser


def build_baseline_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swatch-story baseline",
        description="Compare one baseline image against candidate image palettes.",
    )
    parser.add_argument("baseline_image", help="Local baseline image path")
    parser.add_argument("candidate_images", nargs="+", help="Local candidate paths")
    add_palette_options(parser)
    parser.add_argument("--json", dest="json_path", help="Write JSON report to PATH")
    parser.add_argument(
        "--markdown", dest="markdown_path", help="Write Markdown report to PATH"
    )
    parser.add_argument(
        "--html", dest="html_path", help="Write standalone HTML report to PATH"
    )
    parser.add_argument(
        "--text", dest="text_path", help="Write plain-text report to PATH"
    )
    parser.add_argument(
        "--min-delta-percent",
        type=min_delta_percent_value,
        default=0.0,
        metavar="N",
        help=(
            "Only include shared-color delta detail rows when the absolute "
            "percentage change is at least N. Default: 0.0."
        ),
    )
    parser.add_argument(
        "--title",
        default="Baseline Drift Review",
        help="Title for JSON, HTML, Markdown, and text baseline reports",
    )
    parser.add_argument(
        "--precision",
        type=precision_value,
        default=None,
        metavar="N",
        help=(
            "Decimal places for report percentages and luminance values, 0-6. "
            "Default preserves existing output."
        ),
    )
    return parser


def add_palette_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--preset",
        dest="preset_path",
        help="Read extraction and report defaults from a local JSON preset file.",
    )
    parser.add_argument("--colors", type=int, default=6, help="Palette size, 2-12")
    parser.add_argument(
        "--sample-step",
        type=int,
        default=None,
        help="Sample every N pixels. Defaults to an automatic value.",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=DEFAULT_SAMPLE_LIMIT,
        help="Target sampled pixels for automatic sampling. Defaults to 10000.",
    )
    parser.add_argument(
        "--ignore-color",
        default=None,
        metavar="HEX",
        help=("Exclude sampled pixels matching #rrggbb or rrggbb before ranking."),
    )
    parser.add_argument(
        "--matte",
        default=None,
        metavar="HEX",
        help=(
            "Composite transparent pixels over #rrggbb or rrggbb before extraction. "
            "Default: white."
        ),
    )
    parser.add_argument(
        "--cluster-distance",
        type=cluster_distance_value,
        default=0,
        metavar="N",
        help=(
            "Group similar sampled RGB colors before ranking when N is 1-255. "
            "Default: 0, exact RGB buckets."
        ),
    )
    parser.add_argument(
        "--cluster-space",
        choices=VALID_CLUSTER_SPACES,
        default="rgb",
        help=("Color space used by --cluster-distance: rgb or lab. Default: rgb."),
    )
    parser.add_argument(
        "--sort",
        choices=VALID_SORTS,
        default="frequency",
        help=(
            "Order selected palette entries by frequency, luminance, or hue. "
            "Default: frequency."
        ),
    )
    parser.add_argument(
        "--names",
        action="store_true",
        help="Include approximate common color-name hints in reports and summaries.",
    )


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["compare"]:
        return compare_main(argv[1:])
    if argv[:1] == ["gallery"]:
        return gallery_main(argv[1:])
    if argv[:1] == ["presets"]:
        return presets_main(argv[1:])
    if argv[:1] == ["batch"]:
        return batch_main(argv[1:])
    if argv[:1] == ["baseline"]:
        return baseline_main(argv[1:])

    parser = build_parser()
    args = parser.parse_args(argv)
    apply_preset(parser, args, argv, MAIN_PRESET_KEYS)
    if args.html_thumbnail_path and not args.html_path:
        parser.error("--html-thumbnail requires --html")

    try:
        summary = summarize_image(
            Path(args.image),
            colors=args.colors,
            sample_step=args.sample_step,
            sample_limit=args.sample_limit,
            include_color_names=args.names,
            ignore_color=args.ignore_color,
            matte=args.matte,
            cluster_distance=args.cluster_distance,
            cluster_space=args.cluster_space,
            sort=args.sort,
        )
    except PaletteError as exc:
        print(f"swatch-story: {exc}", file=sys.stderr)
        return 2

    if args.label_prefix is not None:
        apply_label_prefix(summary, args.label_prefix)

    if args.json_path:
        write_json_report(summary, args.json_path, precision=args.precision)
    if args.tokens_path:
        write_tokens_report(
            summary,
            args.tokens_path,
            title=args.title,
            precision=args.precision,
        )
    if args.csv_path:
        write_csv_report(summary, args.csv_path, precision=args.precision)
    if args.html_path:
        thumbnail_href = None
        if args.html_thumbnail_path:
            write_html_thumbnail(args.image, args.html_thumbnail_path)
            thumbnail_href = relative_href(
                Path(args.html_path),
                Path(args.html_thumbnail_path),
            )
        write_html_report(
            summary,
            args.html_path,
            title=args.title,
            precision=args.precision,
            thumbnail_href=thumbnail_href,
        )
    if args.css_path:
        write_css_report(summary, args.css_path)
    if args.markdown_path:
        write_markdown_report(
            summary,
            args.markdown_path,
            title=args.title,
            precision=args.precision,
        )
    if args.wcag_audit_path:
        write_wcag_audit_report(
            summary,
            args.wcag_audit_path,
            title=args.title,
            precision=args.precision,
        )
    if args.text_path:
        write_text_report(
            summary,
            args.text_path,
            title=args.title,
            precision=args.precision,
        )
    if args.svg_path:
        write_svg_report(
            summary,
            args.svg_path,
            title=args.title,
            precision=args.precision,
        )
    if args.gpl_path:
        write_gpl_report(summary, args.gpl_path, title=args.title)
    if args.ase_path:
        write_ase_report(summary, args.ase_path, title=args.title)

    print_summary(summary, precision=args.precision)
    return 0


def apply_label_prefix(summary: dict, prefix: str) -> None:
    for entry in summary["palette"]:
        entry["label"] = f"{prefix}-{entry['rank']}"


def apply_preset(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
    argv: Sequence[str],
    applicable_keys: set[str],
) -> None:
    if not getattr(args, "preset_path", None):
        return
    preset = load_preset(parser, args.preset_path)
    for key in applicable_keys:
        if key in preset and PRESET_FLAG_BY_KEY[key] not in argv:
            setattr(args, key, preset[key])


def load_preset(parser: argparse.ArgumentParser, preset_path: str) -> dict[str, Any]:
    parsed = urlparse(preset_path)
    if parsed.scheme and "://" in preset_path:
        parser.error("preset path must be a local file")

    path = Path(preset_path)
    if not path.is_file():
        parser.error(f"preset file not found: {path}")

    try:
        raw_preset = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        parser.error(f"could not read preset file: {exc}")
    except json.JSONDecodeError as exc:
        parser.error(f"invalid preset JSON: {exc.msg}")

    if not isinstance(raw_preset, dict):
        parser.error("preset must be a JSON object")

    unknown_keys = sorted(set(raw_preset) - PRESET_KEYS)
    if unknown_keys:
        parser.error(f"unknown preset key: {unknown_keys[0]}")

    return {
        key: validate_preset_value(parser, key, value)
        for key, value in raw_preset.items()
    }


def validate_preset_value(
    parser: argparse.ArgumentParser, key: str, value: object
) -> Any:
    try:
        if key == "colors":
            colors = int_preset_value(key, value)
            if colors < MIN_COLORS or colors > MAX_COLORS:
                raise argparse.ArgumentTypeError(
                    f"--colors must be between {MIN_COLORS} and {MAX_COLORS}"
                )
            return colors
        if key == "sample_step":
            if value is None:
                return None
            sample_step = int_preset_value(key, value)
            if sample_step < 1:
                raise argparse.ArgumentTypeError("--sample-step must be 1 or greater")
            return sample_step
        if key == "sample_limit":
            sample_limit = int_preset_value(key, value)
            validate_sample_limit(sample_limit)
            return sample_limit
        if key == "cluster_distance":
            return cluster_distance_value(str(int_preset_value(key, value)))
        if key == "cluster_space":
            if not isinstance(value, str) or value not in VALID_CLUSTER_SPACES:
                choices = ", ".join(VALID_CLUSTER_SPACES)
                raise argparse.ArgumentTypeError(
                    f"--cluster-space must be one of: {choices}"
                )
            return value
        if key == "precision":
            if value is None:
                return None
            return precision_value(str(int_preset_value(key, value)))
        if key == "min_delta_percent":
            return min_delta_percent_value(str(float_preset_value(key, value)))
        if key == "ignore_color":
            if value is None:
                return None
            if not isinstance(value, str):
                raise argparse.ArgumentTypeError("--ignore-color must be a string")
            normalize_ignore_color(value)
            return value
        if key == "matte":
            if value is None:
                return None
            if not isinstance(value, str):
                raise argparse.ArgumentTypeError("--matte must be a string")
            normalize_matte(value)
            return value
        if key == "sort":
            if not isinstance(value, str) or value not in VALID_SORTS:
                choices = ", ".join(VALID_SORTS)
                raise argparse.ArgumentTypeError(f"--sort must be one of: {choices}")
            return value
        if key == "names":
            if not isinstance(value, bool):
                raise argparse.ArgumentTypeError("--names must be true or false")
            return value
        if key == "label_prefix":
            if value is None:
                return None
            if not isinstance(value, str):
                raise argparse.ArgumentTypeError("--label-prefix must be a string")
            return label_prefix_value(value)
        if key == "title":
            if not isinstance(value, str):
                raise argparse.ArgumentTypeError("--title must be a string")
            return value
    except PaletteError as exc:
        parser.error(str(exc))
    except argparse.ArgumentTypeError as exc:
        parser.error(f"invalid preset value for {key}: {exc}")

    raise AssertionError(f"unhandled preset key: {key}")


def int_preset_value(key: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise argparse.ArgumentTypeError(
            f"--{key.replace('_', '-')} must be an integer"
        )
    return value


def float_preset_value(key: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise argparse.ArgumentTypeError(f"--{key.replace('_', '-')} must be a number")
    return float(value)


def relative_href(from_html_path: Path, target_path: Path) -> str:
    try:
        href = os.path.relpath(
            target_path.resolve(strict=False),
            start=from_html_path.parent.resolve(strict=False),
        )
    except ValueError:
        href = str(target_path)
    return Path(href).as_posix()


def gallery_main(argv: Sequence[str]) -> int:
    parser = build_gallery_parser()
    args = parser.parse_args(argv)

    try:
        written = create_gallery(
            Path(args.output_dir),
            include_index=not args.no_index,
            include_manifest=args.manifest,
            force=args.force,
            tags=args.tag,
        )
    except GalleryError as exc:
        print(f"swatch-story gallery: {exc}", file=sys.stderr)
        return 2

    print(
        f"Wrote sample fixture gallery to {Path(args.output_dir)} "
        f"({len(written)} files)"
    )
    return 0


def presets_main(argv: Sequence[str]) -> int:
    parser = build_presets_parser()
    args = parser.parse_args(argv)

    records = []
    for preset_path in args.preset_paths:
        preset = load_preset(parser, preset_path)
        keys = sorted(preset)
        records.append(
            {
                "display_path": preset_path,
                "path": str(Path(preset_path).resolve()),
                "valid": True,
                "keys": keys,
            }
        )

    print("Preset validation summary")
    for record in records:
        keys = ", ".join(record["keys"]) if record["keys"] else "none"
        print(f"- {record['display_path']}: valid; keys: {keys}")

    if args.json_path:
        report = {
            "schema": "swatch-story.presets",
            "version": 1,
            "presets": [
                {
                    "path": record["path"],
                    "valid": record["valid"],
                    "keys": record["keys"],
                }
                for record in records
            ],
        }
        Path(args.json_path).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return 0


def batch_main(argv: Sequence[str]) -> int:
    parser = build_batch_parser()
    args = parser.parse_args(argv)
    apply_preset(parser, args, argv, BATCH_PRESET_KEYS)
    if len(args.images) < 2:
        parser.error("at least two image paths are required")
    if not args.markdown_path and not args.html_path:
        parser.error("at least one of --markdown or --html is required")

    try:
        summaries = [
            summarize_image(
                Path(image),
                colors=args.colors,
                sample_step=args.sample_step,
                sample_limit=args.sample_limit,
                include_color_names=args.names,
                ignore_color=args.ignore_color,
                matte=args.matte,
                cluster_distance=args.cluster_distance,
                cluster_space=args.cluster_space,
                sort=args.sort,
            )
            for image in args.images
        ]
    except PaletteError as exc:
        print(f"swatch-story batch: {exc}", file=sys.stderr)
        return 2

    written = []
    if args.markdown_path:
        write_batch_markdown_report(
            summaries,
            args.markdown_path,
            title=args.title,
            precision=args.precision,
        )
        written.append(Path(args.markdown_path))
    if args.html_path:
        write_batch_html_report(
            summaries,
            args.html_path,
            title=args.title,
            precision=args.precision,
        )
        written.append(Path(args.html_path))

    destinations = ", ".join(str(path) for path in written)
    print(f"Wrote batch report for {len(summaries)} images to {destinations}")
    return 0


def baseline_main(argv: Sequence[str]) -> int:
    parser = build_baseline_parser()
    args = parser.parse_args(argv)
    apply_preset(parser, args, argv, BASELINE_PRESET_KEYS)
    if (
        not args.json_path
        and not args.markdown_path
        and not args.text_path
        and not args.html_path
    ):
        parser.error(
            "at least one of --json, --markdown, --text, or --html is required"
        )

    try:
        baseline_summary = summarize_image(
            Path(args.baseline_image),
            colors=args.colors,
            sample_step=args.sample_step,
            sample_limit=args.sample_limit,
            include_color_names=args.names,
            ignore_color=args.ignore_color,
            matte=args.matte,
            cluster_distance=args.cluster_distance,
            cluster_space=args.cluster_space,
            sort=args.sort,
        )
        candidate_summaries = [
            summarize_image(
                Path(image),
                colors=args.colors,
                sample_step=args.sample_step,
                sample_limit=args.sample_limit,
                include_color_names=args.names,
                ignore_color=args.ignore_color,
                matte=args.matte,
                cluster_distance=args.cluster_distance,
                cluster_space=args.cluster_space,
                sort=args.sort,
            )
            for image in args.candidate_images
        ]
    except PaletteError as exc:
        print(f"swatch-story baseline: {exc}", file=sys.stderr)
        return 2

    report = baseline_report(
        baseline_summary,
        candidate_summaries,
        title=args.title,
        min_delta_percent=args.min_delta_percent,
    )
    output_report = baseline_report_with_precision(report, args.precision)
    written = []
    if args.json_path:
        write_baseline_json(output_report, args.json_path)
        written.append(Path(args.json_path))
    if args.markdown_path:
        write_baseline_markdown_report(output_report, args.markdown_path)
        written.append(Path(args.markdown_path))
    if args.text_path:
        write_baseline_text_report(output_report, args.text_path)
        written.append(Path(args.text_path))
    if args.html_path:
        write_baseline_html_report(output_report, args.html_path)
        written.append(Path(args.html_path))

    destinations = ", ".join(str(path) for path in written)
    print(
        f"Wrote baseline report for {len(candidate_summaries)} candidates to "
        f"{destinations}"
    )
    return 0


def compare_main(argv: Sequence[str]) -> int:
    parser = build_compare_parser()
    args = parser.parse_args(argv)
    apply_preset(parser, args, argv, COMPARE_PRESET_KEYS)

    try:
        before_summary = summarize_image(
            Path(args.before_image),
            colors=args.colors,
            sample_step=args.sample_step,
            sample_limit=args.sample_limit,
            include_color_names=args.names,
            ignore_color=args.ignore_color,
            matte=args.matte,
            cluster_distance=args.cluster_distance,
            cluster_space=args.cluster_space,
            sort=args.sort,
        )
        after_summary = summarize_image(
            Path(args.after_image),
            colors=args.colors,
            sample_step=args.sample_step,
            sample_limit=args.sample_limit,
            include_color_names=args.names,
            ignore_color=args.ignore_color,
            matte=args.matte,
            cluster_distance=args.cluster_distance,
            cluster_space=args.cluster_space,
            sort=args.sort,
        )
    except PaletteError as exc:
        print(f"swatch-story: {exc}", file=sys.stderr)
        return 2

    report = compare_summaries(
        before_summary,
        after_summary,
        min_delta_percent=args.min_delta_percent,
    )
    output_report = compare_report_with_precision(report, args.precision)
    if args.json_path:
        write_compare_json(output_report, args.json_path)
    if args.csv_path:
        write_compare_csv_report(output_report, args.csv_path)
    if args.html_path:
        write_compare_html_report(output_report, args.html_path, title=args.title)
    if args.markdown_path:
        write_compare_markdown_report(
            output_report,
            args.markdown_path,
            title=args.title,
        )
    if args.text_path:
        write_compare_text_report(output_report, args.text_path, title=args.title)
    print(render_compare_text(output_report), end="")
    return 0


def baseline_report_with_precision(
    report: dict[str, Any], precision: int | None
) -> dict[str, Any]:
    if precision is None:
        return report
    rounded_report = deepcopy(report)
    for entry in rounded_report["baseline"]["palette"]:
        round_palette_entry(entry, precision)
    for candidate in rounded_report["candidates"]:
        for entry in candidate["source"]["palette"]:
            round_palette_entry(entry, precision)
        for entry in candidate["changed"]:
            for key in ("before_percent", "after_percent", "delta_percent"):
                entry[key] = round(float(entry[key]), precision)
        candidate["drift_score"] = round(float(candidate["drift_score"]), precision)
    return rounded_report


def compare_report_with_precision(
    report: dict[str, Any], precision: int | None
) -> dict[str, Any]:
    if precision is None:
        return report
    rounded_report = deepcopy(report)
    for side_key in ("before", "after"):
        for entry in rounded_report[side_key]["palette"]:
            round_palette_entry(entry, precision)
    for entry in rounded_report["changed"]:
        for key in ("before_percent", "after_percent", "delta_percent"):
            entry[key] = round(float(entry[key]), precision)
    rounded_report["drift_score"] = round(
        float(rounded_report["drift_score"]), precision
    )
    return rounded_report


def round_palette_entry(entry: dict[str, Any], precision: int) -> None:
    for key in (
        "percent",
        "luminance",
        "contrast_with_black",
        "contrast_with_white",
    ):
        entry[key] = round(float(entry[key]), precision)


def print_summary(summary: dict, *, precision: int | None = None) -> None:
    print(
        f"{summary['source']} ({summary['size']['width']}x{summary['size']['height']})"
    )
    for entry in summary["palette"]:
        name_hint = f" name:{entry['name']}" if "name" in entry else ""
        percent = (
            f"{entry['percent']:>6.2f}"
            if precision is None
            else f"{entry['percent']:>{precision + 4}.{precision}f}"
        )
        contrast_black = (
            str(entry["contrast_with_black"])
            if precision is None
            else f"{entry['contrast_with_black']:.{precision}f}"
        )
        contrast_white = (
            str(entry["contrast_with_white"])
            if precision is None
            else f"{entry['contrast_with_white']:.{precision}f}"
        )
        print(
            f"{entry['rank']:>2}. {entry['hex']} "
            f"{percent}% "
            f"{entry['label']}{name_hint} "
            f"contrast:black {contrast_black}:1 white {contrast_white}:1 "
            f"text:{entry['best_text_color']}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
