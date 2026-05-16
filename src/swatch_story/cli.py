from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path

from swatch_story.compare import (
    compare_summaries,
    render_compare_text,
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
    MIN_CLUSTER_DISTANCE,
    VALID_SORTS,
    PaletteError,
    summarize_image,
)
from swatch_story.report import (
    write_ase_report,
    write_css_report,
    write_csv_report,
    write_gpl_report,
    write_html_report,
    write_json_report,
    write_markdown_report,
    write_svg_report,
    write_text_report,
    write_tokens_report,
)

LABEL_PREFIX_PATTERN = re.compile(r"[a-z][a-z0-9-]*\Z")


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
        "--css", dest="css_path", help="Write CSS custom properties to PATH"
    )
    parser.add_argument(
        "--markdown", dest="markdown_path", help="Write Markdown report to PATH"
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


def add_palette_options(parser: argparse.ArgumentParser) -> None:
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

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        summary = summarize_image(
            Path(args.image),
            colors=args.colors,
            sample_step=args.sample_step,
            sample_limit=args.sample_limit,
            include_color_names=args.names,
            ignore_color=args.ignore_color,
            cluster_distance=args.cluster_distance,
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
        write_html_report(
            summary,
            args.html_path,
            title=args.title,
            precision=args.precision,
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


def compare_main(argv: Sequence[str]) -> int:
    parser = build_compare_parser()
    args = parser.parse_args(argv)

    try:
        before_summary = summarize_image(
            Path(args.before_image),
            colors=args.colors,
            sample_step=args.sample_step,
            sample_limit=args.sample_limit,
            include_color_names=args.names,
            ignore_color=args.ignore_color,
            cluster_distance=args.cluster_distance,
            sort=args.sort,
        )
        after_summary = summarize_image(
            Path(args.after_image),
            colors=args.colors,
            sample_step=args.sample_step,
            sample_limit=args.sample_limit,
            include_color_names=args.names,
            ignore_color=args.ignore_color,
            cluster_distance=args.cluster_distance,
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
    if args.json_path:
        write_compare_json(report, args.json_path)
    if args.csv_path:
        write_compare_csv_report(report, args.csv_path)
    if args.html_path:
        write_compare_html_report(report, args.html_path)
    if args.markdown_path:
        write_compare_markdown_report(report, args.markdown_path)
    if args.text_path:
        write_compare_text_report(report, args.text_path)
    print(render_compare_text(report), end="")
    return 0


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
