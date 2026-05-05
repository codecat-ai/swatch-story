# swatch-story

`swatch-story` is a local-first image utility that extracts a compact color story from an image and exports both machine-readable JSON and a standalone HTML report.

## Problem and Motivation

Screenshots, covers, posters, and teaching images often contain useful color information, but quick palette tools can be too web-service-oriented or only return raw hex values. `swatch-story` keeps images on your machine and adds proportions, luminance labels, and readable black/white text guidance so the output is useful in design notes, documentation, lessons, and small creative workflows.

## Features

- Deterministic palette extraction from local image files with Pillow.
- JSON output with source filename, image size, color rank, hex, RGB, count, percentage, relative luminance, readable black/white text choice, and a lightness label.
- Standalone HTML reports with accessible swatches and escaped report titles.
- Compact console summaries for quick terminal use.

## Installation

This project is not published to a package registry. Clone it from GitHub and install it locally:

```bash
git clone https://github.com/codecat-ai/swatch-story.git
cd swatch-story
python -m pip install -e ".[dev]"
```

## Quick Start

```bash
swatch-story image.png --colors 6 --json story.json --html story.html --title "Launch Palette"
```

The command prints a terminal summary and, when requested, writes `story.json` and `story.html`.

## Examples

Create only a JSON report:

```bash
swatch-story poster.png --colors 5 --json poster-colors.json
```

Create a shareable local HTML report with a fixed sampling step:

```bash
swatch-story screenshot.png --colors 8 --sample-step 2 --html screenshot-story.html
```

Example palette entry:

```json
{
  "rank": 1,
  "hex": "#112233",
  "rgb": [17, 34, 51],
  "count": 120,
  "percent": 32.43,
  "luminance": 0.015,
  "best_text_color": "white",
  "label": "dark"
}
```

## Configuration

`swatch-story` is configured entirely through CLI options:

- `--colors N`: number of colors to report, from 2 to 12. Default: 6.
- `--json PATH`: write a JSON report.
- `--html PATH`: write a standalone HTML report.
- `--sample-step N`: sample every N pixels. By default, small images use every pixel and larger images use a deterministic automatic step.
- `--title TEXT`: title for the HTML report. Default: `Swatch Story`.

The MVP does not read a config file and does not fetch remote images.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest -q
python -m build
```

## Testing

The test suite builds tiny synthetic images and verifies palette proportions, contrast text choices, report rendering, and CLI file output.

```bash
pytest -q
```

## Roadmap

- Optional color-name hints for common palettes.
- Additional export formats such as CSS custom properties or Markdown tables.
- More report layouts for teaching and portfolio use.
- Better sampling strategies for very large images.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md), add behavior-focused tests before changing behavior, and keep the README translations synchronized in meaning.

## License

MIT. See [LICENSE](LICENSE).

## AI-Assisted Maintenance

This project may use AI assistance for maintenance tasks. Maintainers review changes before release and do not intentionally copy code or text from other projects.
