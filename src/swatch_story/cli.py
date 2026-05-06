from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from swatch_story.palette import PaletteError, summarize_image
from swatch_story.report import write_css_report, write_html_report, write_json_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swatch-story",
        description=(
            "Extract a local image color story as console, JSON, HTML, and CSS output."
        ),
    )
    parser.add_argument("image", help="Local image path")
    parser.add_argument("--colors", type=int, default=6, help="Palette size, 2-12")
    parser.add_argument("--json", dest="json_path", help="Write JSON report to PATH")
    parser.add_argument(
        "--html", dest="html_path", help="Write standalone HTML to PATH"
    )
    parser.add_argument(
        "--css", dest="css_path", help="Write CSS custom properties to PATH"
    )
    parser.add_argument(
        "--sample-step",
        type=int,
        default=None,
        help="Sample every N pixels. Defaults to an automatic value.",
    )
    parser.add_argument("--title", default="Swatch Story", help="HTML report title")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        summary = summarize_image(
            Path(args.image), colors=args.colors, sample_step=args.sample_step
        )
    except PaletteError as exc:
        print(f"swatch-story: {exc}", file=sys.stderr)
        return 2

    if args.json_path:
        write_json_report(summary, args.json_path)
    if args.html_path:
        write_html_report(summary, args.html_path, title=args.title)
    if args.css_path:
        write_css_report(summary, args.css_path)

    print_summary(summary)
    return 0


def print_summary(summary: dict) -> None:
    print(
        f"{summary['source']} ({summary['size']['width']}x{summary['size']['height']})"
    )
    for entry in summary["palette"]:
        print(
            f"{entry['rank']:>2}. {entry['hex']} "
            f"{entry['percent']:>6.2f}% "
            f"{entry['label']} text:{entry['best_text_color']}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
