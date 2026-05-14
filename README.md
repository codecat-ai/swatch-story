# swatch-story

[English](README.md) | [中文](README-zh.md) | [日本語](README-ja.md)


`swatch-story` is a local-first image utility that extracts a compact color story from an image and exports machine-readable JSON, UTF-8 CSV, CSS custom properties, portable Markdown, paste-friendly plain text, GIMP `.gpl` palettes, Adobe Swatch Exchange `.ase` palettes, and a standalone HTML report.

## Problem and Motivation

Screenshots, covers, posters, and teaching images often contain useful color information, but quick palette tools can be too web-service-oriented or only return raw hex values. `swatch-story` keeps images on your machine and adds proportions, luminance labels, and readable black/white text guidance so the output is useful in design notes, documentation, lessons, and small creative workflows.

## Features

- Deterministic palette extraction from local image files with Pillow.
- JSON output with source filename, source path, image size, extraction settings, color rank, hex, RGB, count, percentage, relative luminance, readable black/white text choice, and a lightness label.
- UTF-8 CSV output with stable columns for spreadsheet sorting, filtering, and lightweight data workflows.
- CSS custom property output with hex, RGB triplets, and readable text-color variables.
- Portable Markdown reports with palette metadata and a table for notes and docs.
- Plain-text palette sheets with source metadata, extraction settings, and one paste-friendly line per swatch for emails, tickets, and lesson notes.
- Deterministic GIMP `.gpl` palette output for design-tool interoperability.
- Deterministic Adobe Swatch Exchange `.ase` output with RGB swatches grouped by report title.
- Standalone HTML contact-sheet reports with image metadata, extraction settings, accessible swatch cards, escaped user-derived values, and contrast guidance for browser review or design critique.
- Compact console summaries for quick terminal use.
- Configurable automatic sampling with `--sample-limit`, while keeping deterministic `--sample-step` overrides for repeatable reviews.
- `--ignore-color HEX` excludes an exact RGB color such as a flat screenshot background before palette ranking, with percentages recalculated from the remaining sampled pixels.
- `--cluster-distance N` optionally groups visually nearby sampled RGB colors before ranking, using a small deterministic local distance and weighted-average representative colors.
- `--sort {frequency,luminance,hue}` keeps the default frequency ranking or reorders selected swatches from dark to light or by hue angle for designer review.
- `--precision N` formats report percentages and relative luminance values with 0 to 6 decimal places for JSON, CSV, Markdown, text, HTML, and terminal summaries while preserving existing defaults when omitted.
- Optional `--names` hints that map colors to a small built-in set of approximate common names such as red, teal, blue, brown, black, white, and gray.
- Palette comparison reports for two local images with dominant-color changes, shared, added, and removed palette colors, and a deterministic overlap-based drift score in terminal, JSON, or standalone HTML output.

## Installation

This project is not published to a package registry. Install it from a source checkout only:

```bash
git clone https://github.com/codecat-ai/swatch-story.git
cd swatch-story
python -m pip install -e ".[dev]"
```

## Quick Start

```bash
swatch-story image.png --colors 6 --json story.json --csv story.csv --css story.css --html story.html --markdown story.md --text story.txt --gpl story.gpl --ase story.ase --title "Launch Palette"
```

The command prints a terminal summary and, when requested, writes `story.json`, `story.csv`, `story.css`, `story.html`, `story.md`, `story.txt`, `story.gpl`, and `story.ase`.

## Examples

Create only a JSON report:

```bash
swatch-story poster.png --colors 5 --json poster-colors.json
```

Create a spreadsheet-friendly CSV report:

```bash
swatch-story poster.png --colors 5 --csv poster-colors.csv
```

Create a shareable local HTML report with a fixed sampling step:

```bash
swatch-story screenshot.png --colors 8 --sample-step 2 --html screenshot-story.html
```

Tune automatic sampling for a very large image without choosing a fixed step:

```bash
swatch-story mural.png --colors 8 --sample-limit 25000 --json mural-colors.json
```

Ignore a flat background color before ranking the palette:

```bash
swatch-story screenshot.png --colors 6 --ignore-color ffffff --json screenshot-colors.json
```

Group nearby sampled colors before ranking:

```bash
swatch-story photo.png --colors 6 --cluster-distance 12 --json photo-colors.json
```

Sort selected swatches from dark to light after extraction:

```bash
swatch-story poster.png --colors 6 --sort luminance --html poster-luminance.html
```

Sort selected chromatic swatches by hue angle, with grayscale colors after chromatic colors:

```bash
swatch-story poster.png --colors 6 --sort hue --json poster-hue.json
```

Round report percentages and relative luminance values for compact review output:

```bash
swatch-story poster.png --colors 6 --precision 1 --json poster-colors.json --markdown poster-colors.md --html poster-colors.html
```

Compare two local images and write JSON and HTML drift reports:

```bash
swatch-story compare before.png after.png --colors 6 --sample-step 1 --json palette-drift.json --html palette-drift.html
```

The compare command prints a concise terminal report with the before and after paths, dominant color for each image, shared colors, added colors, removed colors, and a drift score. The score is the percentage of selected palette HEX values that changed, calculated as `100 * (1 - shared / union)`, so `0%` means the selected palette HEX values are identical and `100%` means there is no overlap.

The compare HTML report is a standalone local file for browser review. It includes escaped before and after source names and paths, each side's dominant colors, shared colors, added colors, removed colors, clear `None` states for empty change lists, and the drift score. You can request `--json` and `--html` in the same compare command.

The HTML report is a browser-friendly contact sheet. It shows the image name and path, dimensions, requested color count, effective sampling step, cluster distance, sort mode, whether approximate names were included, a short summary, and one card per swatch with HEX, RGB, relative luminance, readable text color, and contrast guidance.

Create CSS custom properties for use in a stylesheet:

```bash
swatch-story poster.png --colors 5 --css poster-colors.css
```

Create a portable Markdown report for notes or docs:

```bash
swatch-story poster.png --colors 5 --markdown poster-colors.md --title "Poster Palette"
```

Create a plain-text palette sheet for pasting into emails, tickets, or lesson notes:

```bash
swatch-story poster.png --colors 5 --text poster-colors.txt --title "Poster Palette"
```

Create a GIMP palette for design tools:

```bash
swatch-story poster.png --colors 5 --gpl poster-colors.gpl --title "Poster Palette"
```

Create an Adobe Swatch Exchange palette for design tools:

```bash
swatch-story poster.png --colors 5 --ase poster-colors.ase --title "Poster Palette"
```

Include approximate common color-name hints in JSON, CSV, HTML, Markdown, text, GIMP and ASE palette labels, CSS comments, and the terminal summary:

```bash
swatch-story poster.png --colors 5 --names --json poster-colors.json --csv poster-colors.csv --markdown poster-colors.md
```

Example CSS output:

```css
/* Generated by swatch-story. */
:root {
  --swatch-story-color-1: #112233;
  --swatch-story-color-1-rgb: 17, 34, 51;
  --swatch-story-color-1-text: white;
}
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

JSON settings include `cluster_distance` and the selected sort mode, for example `"cluster_distance": 0` and `"sort": "frequency"`. When `--ignore-color` is used, JSON settings include the normalized lowercase value, for example `"ignore_color": "#ffffff"`. The ignored pixels are removed before optional clustering and ranking, so swatch percentages are based only on the remaining sampled pixels.

Example compare JSON output:

```json
{
  "before": {
    "source": "before.png",
    "source_path": "before.png",
    "dominant": "#112233"
  },
  "after": {
    "source": "after.png",
    "source_path": "after.png",
    "dominant": "#445566"
  },
  "shared": ["#eeeeee"],
  "added": ["#445566"],
  "removed": ["#112233"],
  "drift_score": 66.67
}
```

Example CSV output:

```csv
rank,hex,r,g,b,count,percent,luminance,best_text_color,label,name
1,#112233,17,34,51,120,32.43,0.015,white,dark,
```

Example plain-text output:

```text
Poster Palette

Source: poster.png
Image size: 1200 x 800 px
Settings: colors 2; sample step 1; sample limit 10000; cluster distance 0; sort frequency; ignored color none; names not included

Swatches:
1. #112233 | rgb(17, 34, 51) | 32.43% | dark | text white
2. #eeeeee | rgb(238, 238, 238) | 18.25% | light | text black
```

Example GIMP palette output:

```text
GIMP Palette
Name: Poster Palette
Columns: 2
# Generated by swatch-story.
 17  34  51 #112233
238 238 238 #eeeeee
```

With `--names`, palette entries include an extra approximate common-name hint:

```json
{
  "rank": 1,
  "hex": "#112233",
  "rgb": [17, 34, 51],
  "count": 120,
  "percent": 32.43,
  "luminance": 0.015,
  "best_text_color": "white",
  "label": "dark",
  "name": "black"
}
```

## Configuration

`swatch-story` is configured entirely through CLI options:

- `--colors N`: number of colors to report, from 2 to 12. Default: 6.
- `--json PATH`: write a JSON report.
- `--csv PATH`: write a UTF-8 CSV report with stable columns: `rank`, `hex`, `r`, `g`, `b`, `count`, `percent`, `luminance`, `best_text_color`, `label`, and `name`.
- `--css PATH`: write CSS custom properties.
- `--html PATH`: write a standalone HTML report.
- `--markdown PATH`: write a portable Markdown report.
- `--text PATH`: write a UTF-8 plain-text palette sheet with title, source filename, image size, extraction settings, and one line per swatch containing rank, hex, RGB triplet, percent, label, best text color, and optional name hint.
- `--gpl PATH`: write a deterministic GIMP `.gpl` palette.
- `--ase PATH`: write a deterministic Adobe Swatch Exchange `.ase` palette.
- `--sample-step N`: sample every N pixels. By default, small images use every pixel and larger images use a deterministic automatic step.
- `--sample-limit N`: target sampled pixels for the automatic step when `--sample-step` is omitted. Default: 10000. Must be 1 or greater. If `--sample-step` is provided, the fixed step controls pixel iteration; JSON settings still include the selected `sample_limit` and effective `sample_step`.
- `--ignore-color HEX`: exclude sampled pixels that exactly match a hex RGB color before palette ranking. Accepts `#rrggbb` or `rrggbb`, case-insensitive, and stores the normalized lowercase `#rrggbb` value in JSON/report settings. If every sampled pixel is ignored or the value is not valid hex RGB, the command exits with a clear error.
- `--cluster-distance N`: when greater than 0, group similar sampled RGB colors before palette ranking. The value must be from 0 to 255. Default: 0, which preserves the exact RGB bucket behavior. Cluster representatives are rounded weighted averages of member RGB values, weighted by sampled pixel counts.
- `--sort {frequency,luminance,hue}`: order the selected palette entries. `frequency` preserves the default ranking by sampled pixel count, `luminance` reorders swatches from dark to light, and `hue` orders chromatic swatches by HSV hue angle before grayscale or near-grayscale swatches. Reordered palettes are reranked from 1. Default: `frequency`.
- `--precision N`: format user-facing report percentages and relative luminance values with `N` decimal places, from 0 to 6. When omitted, output preserves the existing JSON numbers and report strings. The option applies to normal palette extraction JSON, CSV, Markdown, text, HTML, and terminal summaries; design-tool palette formats such as CSS, GIMP `.gpl`, and Adobe `.ase` keep their format-specific output.
- `--title TEXT`: title for HTML, Markdown, text, GIMP palette, and ASE output. Default: `Swatch Story`.
- `--names`: include deterministic, offline, approximate common color-name hints. The names come from a small built-in RGB reference set and are intended as human-friendly family hints, not exact color names.

`swatch-story compare BEFORE_IMAGE AFTER_IMAGE [options]` reuses `--colors`, `--sample-step`, `--sample-limit`, `--ignore-color`, `--cluster-distance`, `--sort`, and `--names`. For compare mode, `--json PATH` writes the deterministic comparison JSON report instead of the single-image report, and `--html PATH` writes a standalone HTML comparison report. Both outputs can be requested together.

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
- Optional perceptual color-space clustering based on a more formal color model such as CIELAB for closer visual grouping.
- Small sample fixture gallery for teaching palette extraction and report formats.
- Optional side-by-side palette preview thumbnails in HTML reports for quicker visual review.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md), add behavior-focused tests before changing behavior, and keep the README translations synchronized in meaning.

## License

MIT. See [LICENSE](LICENSE).

## AI-Assisted Maintenance

This project may use AI assistance for maintenance tasks. Maintainers review changes before release and do not intentionally copy code or text from other projects.
