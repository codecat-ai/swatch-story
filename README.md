# swatch-story

[English](README.md) | [中文](README-zh.md) | [日本語](README-ja.md)


`swatch-story` is a local-first image utility that extracts a compact color story from an image and exports machine-readable JSON, design-token JSON, UTF-8 CSV, CSS custom properties, portable Markdown, WCAG-oriented Markdown audits, paste-friendly plain text, standalone SVG swatch sheets, GIMP `.gpl` palettes, Adobe Swatch Exchange `.ase` palettes, and a standalone HTML report.

## Problem and Motivation

Screenshots, covers, posters, and teaching images often contain useful color information, but quick palette tools can be too web-service-oriented or only return raw hex values. `swatch-story` keeps images on your machine and adds proportions, stable token labels, and black/white contrast ratios so the output is useful in design notes, documentation, lessons, and small creative workflows.

## Features

- Deterministic palette extraction from local image files with Pillow.
- JSON output with stable `schema_version: 1`, source filename, source path, image size, extraction settings, color rank, hex, RGB, count, percentage, relative luminance, black and white text contrast ratios, readable text choice, and a stable token label.
- Design-token JSON output for the main image command, with Design Tokens Community Group schema metadata, stable color token keys, `$type: color`, `$value`, human-readable contrast guidance, and `extensions.swatchStory` metrics for token pipelines.
- UTF-8 CSV output with stable columns for spreadsheet sorting, filtering, and lightweight data workflows.
- CSS custom property output with hex, RGB triplets, black/white contrast ratios, and readable text-color variables.
- Portable Markdown reports with palette metadata and a table for notes and docs.
- WCAG-oriented Markdown audit reports that reuse each swatch's black/white contrast ratios, summarize normal and large text AA/AAA readiness, and recommend the stronger text color.
- Plain-text palette sheets with source metadata, extraction settings, and one paste-friendly line per swatch for emails, tickets, and lesson notes.
- Standalone SVG swatch sheets with source metadata, extraction settings, color blocks, HEX values, optional names, percentages, luminance, black/white contrast ratios, labels, and readable text-color guidance for docs and slides.
- Deterministic GIMP `.gpl` palette output for design-tool interoperability.
- Deterministic Adobe Swatch Exchange `.ase` output with RGB swatches grouped by report title.
- Standalone HTML contact-sheet reports with image metadata, extraction settings, accessible swatch cards, escaped user-derived values, and contrast guidance for browser review or design critique.
- Optional local sidecar thumbnails for HTML reports with `--html-thumbnail PATH`, linked from the report without embedding the source image as base64.
- Compact console summaries for quick terminal use.
- Configurable automatic sampling with `--sample-limit`, while keeping deterministic `--sample-step` overrides for repeatable reviews.
- `--ignore-color HEX` excludes an exact RGB color such as a flat screenshot background before palette ranking, with percentages recalculated from the remaining sampled pixels.
- `--matte HEX` composites transparent and semi-transparent pixels over a chosen background color before extraction, so icons and logos can be sampled as they appear on dark, light, or brand surfaces.
- `--cluster-distance N` optionally groups nearby sampled colors before ranking; `--cluster-space {rgb,lab}` keeps the existing deterministic RGB-ish default or uses local sRGB-to-CIELAB conversion with Euclidean Lab distance for perceptual grouping.
- `--sort {frequency,luminance,hue}` keeps the default frequency ranking or reorders selected swatches from dark to light or by hue angle for designer review.
- `--precision N` formats report percentages, relative luminance values, and contrast ratios with 0 to 6 decimal places for JSON, design-token JSON, CSV, Markdown, WCAG audit, text, SVG, HTML, and terminal summaries while preserving existing defaults when omitted.
- `--label-prefix PREFIX` replaces default `color-1`, `color-2` labels with design-token labels such as `brand-1`, `brand-2` in the main image command, including `--tokens` keys.
- Optional `--names` hints that map colors to a small built-in set of approximate common names such as red, teal, blue, brown, black, white, and gray.
- Palette comparison reports for two local images with dominant-color changes, compact side-by-side HTML palette preview strips, shared, added, and removed palette colors, and a deterministic overlap-based drift score in terminal, JSON, standalone HTML, portable Markdown, or plain-text output.
- Baseline drift reviews that compare one reference image against multiple candidates, rank candidates by drift score, and write deterministic JSON, Markdown, plain-text, and standalone HTML dashboard reports.
- Batch team-review reports that combine two or more local image audits into one deterministic Markdown and/or standalone HTML file with one section/card per image, dominant colors, palette rows, contrast guidance, escaped user-derived values, and shared extraction settings.
- Preset discovery for local JSON preset files, with deterministic terminal validation summaries and optional JSON reports for team review setup.
- Source-checkout sample fixture gallery generation with tiny deterministic PNGs, stable lesson-theme tags, an optional Markdown index, and an optional JSON manifest for teaching palette extraction and fixture assertions.

## Installation

This project is not published to a package registry. Install it from a source checkout only:

```bash
git clone https://github.com/codecat-ai/swatch-story.git
cd swatch-story
python -m pip install -e ".[dev]"
```

## Quick Start

```bash
swatch-story image.png --colors 6 --json story.json --tokens story.tokens.json --csv story.csv --css story.css --html story.html --markdown story.md --wcag-audit audit.md --text story.txt --svg story.svg --gpl story.gpl --ase story.ase --title "Launch Palette"
```

The command prints a terminal summary and, when requested, writes `story.json`, `story.tokens.json`, `story.csv`, `story.css`, `story.html`, `story.md`, `audit.md`, `story.txt`, `story.svg`, `story.gpl`, and `story.ase`.

Generate local teaching fixtures from the same source checkout:

```bash
swatch-story gallery demo-gallery
```

The gallery command writes tiny deterministic PNG files plus `demo-gallery/README.md` with example commands and tags for extracting palettes and reports from those samples. Add `--manifest` when lesson material or tests need `demo-gallery/manifest.json` with expected dominant colors, palette hex values, and stable lesson-theme tags.

Create a team-review report for several local images:

```bash
swatch-story batch hero.png card.png poster.png --colors 6 --markdown team-review.md --html team-review.html
```

Rank candidate images against a reference palette:

```bash
swatch-story baseline reference.png option-a.png option-b.png --colors 6 --markdown baseline-review.md --text baseline-review.txt --html baseline-review.html
```

## Examples

Generate only the sample PNG fixtures without the Markdown index:

```bash
swatch-story gallery demo-gallery --no-index
```

Generate PNG fixtures plus a machine-readable manifest without the Markdown index:

```bash
swatch-story gallery demo-gallery --manifest --no-index
```

Generate only samples that match every requested lesson tag:

```bash
swatch-story gallery demo-gallery --manifest --tag contrast --tag accessibility
```

Create only a JSON report:

```bash
swatch-story poster.png --colors 5 --json poster-colors.json
```

Extract a transparent logo as it appears on a dark matte:

```bash
swatch-story logo.png --colors 5 --matte 111827 --json logo-dark-colors.json
```

Create design-token JSON for a token pipeline:

```bash
swatch-story poster.png --colors 5 --tokens poster.tokens.json --title "Poster Palette"
```

Create a spreadsheet-friendly CSV report:

```bash
swatch-story poster.png --colors 5 --csv poster-colors.csv
```

Create a shareable local HTML report with a fixed sampling step:

```bash
swatch-story screenshot.png --colors 8 --sample-step 2 --html screenshot-story.html
```

Create a local HTML report with a small sidecar thumbnail for quick source review:

```bash
swatch-story screenshot.png --colors 8 --html reports/screenshot-story.html --html-thumbnail reports/assets/screenshot-thumb.png
```

Tune automatic sampling for a very large image without choosing a fixed step:

```bash
swatch-story mural.png --colors 8 --sample-limit 25000 --json mural-colors.json
```

Ignore a flat background color before ranking the palette:

```bash
swatch-story screenshot.png --colors 6 --ignore-color ffffff --json screenshot-colors.json
```

Composite transparent pixels over a brand background before ranking:

```bash
swatch-story icon.png --colors 4 --matte "#003366" --json icon-brand-colors.json
```

Group nearby sampled colors before ranking:

```bash
swatch-story photo.png --colors 6 --cluster-distance 12 --json photo-colors.json
```

Use perceptual Lab-space clustering when small RGB channel changes do not match visual similarity:

```bash
swatch-story photo.png --colors 6 --cluster-distance 5 --cluster-space lab --json photo-lab-colors.json
```

Lab clustering is most useful for screenshots, exported art, and design review sets where compression, antialiasing, or gradients create many RGB-adjacent pixels that should be treated as the same visual color. The selected `cluster_space` and `cluster_distance` are recorded in JSON and rendered report settings so compare, baseline, and batch reports remain reviewable later.

Sort selected swatches from dark to light after extraction:

```bash
swatch-story poster.png --colors 6 --sort luminance --html poster-luminance.html
```

Sort selected chromatic swatches by hue angle, with grayscale colors after chromatic colors:

```bash
swatch-story poster.png --colors 6 --sort hue --json poster-hue.json
```

Round report percentages, relative luminance values, and contrast ratios for compact review output:

```bash
swatch-story poster.png --colors 6 --precision 1 --json poster-colors.json --tokens poster.tokens.json --markdown poster-colors.md --svg poster-colors.svg --html poster-colors.html
```

Write a WCAG-oriented Markdown audit for black and white text readiness:

```bash
swatch-story poster.png --colors 5 --wcag-audit poster-wcag.md --title "Poster Palette"
```

Apply a design-token label prefix to generated reports:

```bash
swatch-story poster.png --colors 5 --label-prefix brand --tokens poster.tokens.json --json poster-colors.json --css poster-colors.css
```

Reuse a local JSON extraction preset while letting explicit CLI flags win:

```json
{
  "colors": 5,
  "sample_step": 1,
  "matte": "111827",
  "names": true,
  "precision": 1,
  "label_prefix": "brand",
  "title": "Poster Palette"
}
```

```bash
swatch-story poster.png --preset presets/poster.json --colors 6 --json poster-colors.json --tokens poster.tokens.json
```

Validate shared presets before a review session:

```bash
swatch-story presets presets/poster.json presets/baseline.json --json preset-validation.json
```

Compare two local images and write JSON, CSV, HTML, Markdown, and plain-text drift reports:

```bash
swatch-story compare before.png after.png --colors 6 --sample-step 1 --matte 111827 --min-delta-percent 2 --json palette-drift.json --csv palette-drift.csv --html palette-drift.html --markdown palette-drift.md --text palette-drift.txt
```

For perceptual clustering in a drift snapshot, use Lab clustering with the same extraction settings on both sides:

```bash
swatch-story compare before.png after.png --colors 6 --cluster-distance 5 --cluster-space lab --json palette-drift.json
```

The compare command prints a concise terminal report with the before and after paths, dominant color for each image, shared colors, added colors, removed colors, changed shared-color percentages, and a drift score. The score is the percentage of selected palette HEX values that changed, calculated as `100 * (1 - shared / union)`, so `0%` means the selected palette HEX values are identical and `100%` means there is no overlap. Use `--min-delta-percent N` to hide shared-color delta detail rows whose absolute percentage change is less than `N`; added and removed colors are still reported.

The compare CSV report is a deterministic UTF-8 table for spreadsheet palette drift review. The compare HTML report is a standalone local file for browser review with compact CSS-only side-by-side palette preview strips for each image. The compare Markdown report is a portable table for notes, issue comments, and design docs. The compare plain-text report is a deterministic UTF-8 drift sheet for emails, tickets, and review logs. These reports include safely represented before and after source names and paths, each side's dominant colors, shared colors, added colors, removed colors, filtered changed-color delta details, clear `None` states for empty change lists, and the drift score. You can request `--json`, `--csv`, `--html`, `--markdown`, and `--text` in the same compare command.

Compare one baseline image against several candidates and rank drift:

```bash
swatch-story baseline reference.png draft-a.png draft-b.png --colors 6 --sample-step 1 --names --title "Baseline Drift Review" --json baseline-drift.json --markdown baseline-drift.md --text baseline-drift.txt --html baseline-drift.html
```

Use the same Lab clustering settings for the baseline and every candidate when tiny RGB differences should not become separate drift colors:

```bash
swatch-story baseline reference.png draft-a.png draft-b.png --colors 6 --cluster-distance 5 --cluster-space lab --json baseline-drift.json
```

The baseline command requires one baseline image, at least one candidate image, and at least one of `--json PATH`, `--markdown PATH`, `--text PATH`, or `--html PATH`; all four outputs may be requested together. It reuses the compare drift logic for every candidate, keeps JSON candidates in input order with a rank and drift score, and sorts Markdown/text/HTML summaries by drift score descending. Baseline reports include baseline source metadata, candidate source metadata, shared colors, added colors, removed colors, filtered changed-color details, and escaped user-derived titles, names, and paths. The baseline HTML report is a standalone dashboard with deterministic inline CSS, metadata panels, a sortable-looking ranked candidate table, and visual swatches for shared, added, removed, and changed color lists.

Combine several local image audits into one team-review report:

```bash
swatch-story batch hero.png card.png poster.png --colors 6 --sample-step 1 --names --title "Campaign Palette Review" --markdown campaign-review.md --html campaign-review.html
```

For a compact team snapshot that groups visually close sampled colors across all inputs, add Lab clustering to the batch extraction settings:

```bash
swatch-story batch hero.png card.png poster.png --colors 6 --cluster-distance 5 --cluster-space lab --markdown campaign-review.md
```

The batch command requires at least two image paths and at least one of `--markdown PATH` or `--html PATH`; both outputs may be requested together. It reuses the same deterministic palette extraction settings for every image and writes one Markdown section or HTML card per source image with the source name/path, image size, dominant colors, palette rows/cards, and black/white text contrast guidance. User-derived titles, filenames, paths, labels, and names are escaped, and files are written as deterministic UTF-8.

Preset files are local JSON objects for sharing deterministic extraction defaults across commands. Accepted keys are `colors`, `sample_step`, `sample_limit`, `ignore_color`, `matte`, `cluster_distance`, `cluster_space`, `sort`, `names`, `precision`, `label_prefix`, `title`, and `min_delta_percent`. The main image command uses extraction settings plus `names`, `precision`, `label_prefix`, and `title`; `compare` and `baseline` use shared extraction settings plus `names`, `precision`, `title`, and `min_delta_percent`; `batch` uses shared extraction settings plus `names`, `precision`, and `title`. A flag typed on the command line always overrides the preset value. Presets must be local files; URLs, missing files, invalid JSON, non-object JSON, unknown keys, and invalid values fail before reports are written. Use `swatch-story presets PATH [PATH ...]` to validate one or more local presets without reading image files. The command prints each input path, `valid` status, and supported keys in sorted order, or `keys: none` for an empty preset. Add `--json PATH` to write a deterministic report after all presets validate successfully.

The HTML report is a browser-friendly contact sheet. It shows the image name and path, dimensions, requested color count, effective sampling step, cluster distance and space, sort mode, whether approximate names were included, a short summary, and one card per swatch with HEX, RGB, relative luminance, black/white contrast ratios, readable text color, and contrast guidance. Add `--html-thumbnail PATH` with `--html PATH` to generate a bounded local thumbnail from the source image and link it with a relative path where practical; the source image is not embedded as base64.

The SVG report is a standalone local swatch sheet for docs and slides. It shows the title, source filename, image dimensions, extraction settings, and one row per swatch with a color rectangle, HEX, optional approximate name, percent, luminance, black/white contrast ratios, label, and readable text color. User-derived title, source, labels, and names are XML-escaped, and the source image itself is not embedded.

The design-token JSON report is intended for design-token pipelines. It uses the extracted label as each `color` key, so `--label-prefix brand` produces keys such as `brand-1`; `--precision N` also rounds token percentages, luminance values, contrast ratios, and description text. The option is available on the main image command only, not `compare` or `gallery`.

The WCAG audit report is a deterministic UTF-8 Markdown file for review notes. It includes the title, source name and path, image size, extraction settings, WCAG AA/AAA thresholds for normal and large text, and one row per swatch showing black-text readiness, white-text readiness, the preferred text color, and a concise recommendation. User-derived Markdown table cells are escaped.

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

Create a standalone SVG swatch sheet for docs or slides:

```bash
swatch-story poster.png --colors 5 --svg poster-colors.svg --title "Poster Palette"
```

Create a GIMP palette for design tools:

```bash
swatch-story poster.png --colors 5 --gpl poster-colors.gpl --title "Poster Palette"
```

Create an Adobe Swatch Exchange palette for design tools:

```bash
swatch-story poster.png --colors 5 --ase poster-colors.ase --title "Poster Palette"
```

Include approximate common color-name hints in JSON, CSV, HTML, Markdown, text, SVG, GIMP and ASE palette labels, CSS comments, and the terminal summary:

```bash
swatch-story poster.png --colors 5 --names --json poster-colors.json --csv poster-colors.csv --markdown poster-colors.md
```

Example CSS output:

```css
/* Generated by swatch-story. */
:root {
  --swatch-story-color-1: #112233;
  --swatch-story-color-1-rgb: 17, 34, 51;
  --swatch-story-color-1-contrast-black: 1.3;
  --swatch-story-color-1-contrast-white: 16.15;
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
  "contrast_with_black": 1.3,
  "contrast_with_white": 16.15,
  "best_text_color": "white",
  "label": "color-1"
}
```

Contrast ratios use the WCAG formula `(lighter + 0.05) / (darker + 0.05)` from relative luminance, comparing each swatch against black luminance `0` and white luminance `1`. `best_text_color` is the higher-contrast option. JSON settings include `cluster_distance`, `cluster_space`, and the selected sort mode, for example `"cluster_distance": 0`, `"cluster_space": "rgb"`, and `"sort": "frequency"`. When `--ignore-color` is used, JSON settings include the normalized lowercase value, for example `"ignore_color": "#ffffff"`. The ignored pixels are removed before optional clustering and ranking, so swatch percentages are based only on the remaining sampled pixels. When `--matte` is used, JSON settings include the normalized lowercase value, for example `"matte": "#111827"`; the field is omitted when the default white matte is used.

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
  "changed": [
    {
      "hex": "#eeeeee",
      "before_percent": 20.0,
      "after_percent": 23.5,
      "delta_percent": 3.5
    }
  ],
  "drift_score": 66.67
}
```

Example compare plain-text output:

```text
Palette Drift Report

Before source name: before.png
Before source path: before.png
After source name: after.png
After source path: after.png
Before dominant colors: #112233, #eeeeee
After dominant colors: #445566, #eeeeee
Shared colors: #eeeeee
Added colors: #445566
Removed colors: #112233
Changed colors: #eeeeee (20.0% to 23.5%, +3.5%)
Drift score: 66.67%
```

Example CSV output:

```csv
rank,hex,r,g,b,count,percent,luminance,contrast_with_black,contrast_with_white,best_text_color,label,name
1,#112233,17,34,51,120,32.43,0.015,1.3,16.15,white,color-1,
```

Example plain-text output:

```text
Poster Palette

Source: poster.png
Image size: 1200 x 800 px
Settings: colors 2; sample step 1; sample limit 10000; cluster distance 0; cluster space rgb; sort frequency; ignored color none; names not included

Swatches:
1. #112233 | rgb(17, 34, 51) | 32.43% | color-1 | contrast black 1.3:1 white 16.15:1 | text white
2. #eeeeee | rgb(238, 238, 238) | 18.25% | color-2 | contrast black 18.1:1 white 1.16:1 | text black
```

Example GIMP palette output:

```text
GIMP Palette
Name: Poster Palette
Columns: 2
# Generated by swatch-story.
 17  34  51 color-1
238 238 238 color-2
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
  "contrast_with_black": 1.3,
  "contrast_with_white": 16.15,
  "best_text_color": "white",
  "label": "color-1",
  "name": "black"
}
```

## Configuration

`swatch-story` is configured entirely through CLI options:

- `--colors N`: number of colors to report, from 2 to 12. Default: 6.
- `--json PATH`: write a JSON report.
- `--tokens PATH`: write a deterministic design-token JSON report for import into token pipelines. The report includes `$schema`, `source`, `title`, and `color` tokens keyed by palette label with `$type`, `$value`, description text, and `extensions.swatchStory` metrics.
- `--csv PATH`: write a UTF-8 CSV report with stable columns: `rank`, `hex`, `r`, `g`, `b`, `count`, `percent`, `luminance`, `contrast_with_black`, `contrast_with_white`, `best_text_color`, `label`, and `name`.
- `--css PATH`: write CSS custom properties.
- `--html PATH`: write a standalone HTML report.
- `--html-thumbnail PATH`: write a small local sidecar thumbnail and link it from the HTML report. This option requires `--html PATH`; the thumbnail is bounded to 320 px on its longest side, preserves aspect ratio, creates parent directories as needed, and keeps image data local instead of embedding base64 in HTML.
- `--markdown PATH`: write a portable Markdown report.
- `--wcag-audit PATH`: write a deterministic UTF-8 Markdown audit with source metadata, extraction settings, WCAG normal/large text AA/AAA readiness against black and white text, preferred text color, and one recommendation per swatch.
- `--text PATH`: write a UTF-8 plain-text palette sheet with title, source filename, image size, extraction settings, and one line per swatch containing rank, hex, RGB triplet, percent, label, black/white contrast ratios, best text color, and optional name hint.
- `--svg PATH`: write a deterministic UTF-8 standalone SVG swatch sheet with title, source filename, image size, extraction settings, and one row per swatch containing a color rectangle, HEX, optional name hint, percent, luminance, black/white contrast ratios, label, and readable text color.
- `--gpl PATH`: write a deterministic GIMP `.gpl` palette.
- `--ase PATH`: write a deterministic Adobe Swatch Exchange `.ase` palette.
- `--sample-step N`: sample every N pixels. By default, small images use every pixel and larger images use a deterministic automatic step.
- `--sample-limit N`: target sampled pixels for the automatic step when `--sample-step` is omitted. Default: 10000. Must be 1 or greater. If `--sample-step` is provided, the fixed step controls pixel iteration; JSON settings still include the selected `sample_limit` and effective `sample_step`.
- `--ignore-color HEX`: exclude sampled pixels that exactly match a hex RGB color before palette ranking. Accepts `#rrggbb` or `rrggbb`, case-insensitive, and stores the normalized lowercase `#rrggbb` value in JSON/report settings. If every sampled pixel is ignored or the value is not valid hex RGB, the command exits with a clear error.
- `--matte HEX`: composite transparent or semi-transparent pixels over a hex RGB background before palette extraction. Accepts `#rrggbb` or `rrggbb`, case-insensitive. Default behavior remains white, and JSON settings include normalized `matte` only when this option is explicitly provided.
- `--cluster-distance N`: when greater than 0, group similar sampled colors before palette ranking. The value must be from 0 to 255. Default: 0, which preserves the exact RGB bucket behavior. Cluster representatives are rounded weighted averages of member RGB values, weighted by sampled pixel counts.
- `--cluster-space {rgb,lab}`: choose the distance space used by `--cluster-distance`. `rgb` is the default and preserves existing deterministic RGB-ish clustering. `lab` converts sRGB to XYZ and CIELAB with a D65 white point, then compares colors with Euclidean Lab distance. JSON and report settings always include the selected value, even when `--cluster-distance` is 0.
- `--sort {frequency,luminance,hue}`: order the selected palette entries. `frequency` preserves the default ranking by sampled pixel count, `luminance` reorders swatches from dark to light, and `hue` orders chromatic swatches by HSV hue angle before grayscale or near-grayscale swatches. Reordered palettes are reranked from 1. Default: `frequency`.
- `--precision N`: format user-facing report percentages, relative luminance values, and contrast ratios with `N` decimal places, from 0 to 6. When omitted, output preserves the existing JSON numbers and report strings. The option applies to normal palette extraction JSON, design-token JSON, CSV, Markdown, WCAG audit, text, SVG, HTML, and terminal summaries; design-tool palette formats such as CSS, GIMP `.gpl`, and Adobe `.ase` keep their format-specific output.
- `--label-prefix PREFIX`: replace default palette labels with `PREFIX-1`, `PREFIX-2`, and so on for the main image command. `PREFIX` must start with a lowercase letter and contain only lowercase letters, numbers, and hyphens. For example, `--label-prefix brand` writes labels such as `brand-1` into JSON, design-token JSON keys, CSV, CSS custom property names, Markdown, WCAG audit, text, HTML, SVG, GIMP `.gpl`, Adobe `.ase`, and terminal output. Compare and gallery commands do not use this option.
- `--preset PATH`: read reusable defaults from a local JSON preset before running the main image, `compare`, `baseline`, or `batch` command. Explicit CLI flags override preset values. The preset may contain `colors`, `sample_step`, `sample_limit`, `ignore_color`, `matte`, `cluster_distance`, `cluster_space`, `sort`, `names`, `precision`, `label_prefix`, `title`, and `min_delta_percent`; mode-specific unsupported keys are ignored rather than applied.
- `--title TEXT`: title for design-token JSON, HTML, Markdown, WCAG audit, text, SVG, GIMP palette, and ASE output. Default: `Swatch Story`.
- `--names`: include deterministic, offline, approximate common color-name hints. The names come from a small built-in RGB reference set and are intended as human-friendly family hints, not exact color names.

`swatch-story compare BEFORE_IMAGE AFTER_IMAGE [options]` reuses `--colors`, `--sample-step`, `--sample-limit`, `--ignore-color`, `--matte`, `--cluster-distance`, `--cluster-space`, `--sort`, and `--names`; the same matte is applied to both images. It also accepts `--min-delta-percent N`, where `N` is a float percentage of `0` or greater. For compare mode, `--json PATH` writes the deterministic comparison JSON report with root `schema_version: 1` instead of the single-image report, `--csv PATH` writes a deterministic UTF-8 comparison CSV with metadata plus filtered changed-color rows and unfiltered added/removed color rows, `--html PATH` writes a standalone HTML comparison report, `--markdown PATH` writes a portable Markdown comparison report, and `--text PATH` writes a UTF-8 plain-text drift report. These outputs can be requested together.

`swatch-story baseline BASELINE_IMAGE CANDIDATE_IMAGE [CANDIDATE_IMAGE ...] [options]` reuses `--colors`, `--sample-step`, `--sample-limit`, `--ignore-color`, `--matte`, `--cluster-distance`, `--cluster-space`, `--sort`, `--names`, `--precision`, `--title`, and `--min-delta-percent`. It requires at least one candidate image and at least one output path. `--json PATH` writes a deterministic baseline drift JSON report with root `schema_version: 1`, schema marker, version, baseline metadata, input-order candidates, ranks, drift scores, shared/added/removed colors, and changed-color details. `--markdown PATH` writes a ranked review with a summary table and candidate sections. `--text PATH` writes compact ranked log lines. `--html PATH` writes a standalone ranked dashboard with escaped metadata plus shared, added, removed, and changed color columns for browser review.

`swatch-story batch IMAGE IMAGE [IMAGE...] [options]` reuses `--colors`, `--sample-step`, `--sample-limit`, `--ignore-color`, `--matte`, `--cluster-distance`, `--cluster-space`, `--sort`, `--names`, `--precision`, and `--title` across every image. It requires at least two image paths and at least one output path. `--markdown PATH` writes a deterministic UTF-8 team-review Markdown report, and `--html PATH` writes a standalone HTML team-review report; both can be requested together. Batch mode does not use `--label-prefix`, `--tokens`, `--json`, `--csv`, `--css`, `--wcag-audit`, `--text`, `--svg`, `--gpl`, `--ase`, or `--html-thumbnail`.

`swatch-story gallery OUT_DIR [--manifest] [--no-index] [--force] [--tag TAG]...` writes the built-in sample fixture PNGs and, by default, a Markdown `README.md` gallery with source-checkout commands and readable sample tags. `--manifest` also writes a deterministic UTF-8 `manifest.json` containing schema version `1`, generator name, sample filenames, dimensions, stories, tags, expected dominant colors, and expected palette hex values. `--tag` may be repeated to generate only samples containing all requested tags; matching is case-insensitive, and unknown or empty-result filters fail before writing files. `--no-index` skips only `README.md`, so it can be combined with `--manifest`. The command refuses to overwrite existing gallery files, including `manifest.json`, unless `--force` is provided.

`swatch-story presets PATH [PATH ...] [--json PATH]` validates local JSON preset files with the same rules as `--preset` and does not read any image files. The terminal summary preserves input order, reports normalized supported keys in sorted order, and shows `keys: none` for presets with no supported keys. `--json PATH` writes schema marker `swatch-story.presets`, version `1`, normalized absolute preset paths, validity, and sorted keys only after every input preset validates.

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

The test suite builds tiny synthetic images and verifies palette proportions, contrast text choices, single-image, compare, baseline, and batch report rendering, design-token JSON output, preset discovery validation, gallery manifest content, escaping of user-derived report values, and CLI file output.

```bash
pytest -q
```

## Roadmap

swatch-story is alpha-stage but usable for local, deterministic palette extraction and review reports. After the 2026-05-18 release-readiness review, the project is moving from growth to maintenance cadence: every 2-4 weeks plus urgent bug, docs-truthfulness, dependency, or report-schema stability issues.

Now:
- Keep the upcoming release candidate stable: run the release checklist before tagging, watch for user-reported palette/report regressions, and avoid broad feature additions unless they support release confidence.

Next:
- Improve gallery samples only if they directly demonstrate release-critical workflows such as transparency, ignored backgrounds, or perceptual clustering.
- Keep report schema changes additive until a tagged release documents the current JSON shape.
- Revisit cadence after the next release tag or if real user feedback reveals a higher-value workflow gap.

Later:
- Consider optional machine-readable changelog metadata for release automation.
- Evaluate config-file support only if repeated CLI presets stop covering common workflows.

Release checklist:
- Run `ruff check .`, `ruff format --check .`, `pytest -q`, and `python -m build` in a clean local virtual environment.
- Verify `README.md`, `README-zh.md`, and `README-ja.md` describe the same install path, examples, roadmap posture, and MIT license note.
- Confirm `CHANGELOG.md` has an Unreleased entry for every user-visible CLI option, report format field, or output artifact change.
- Smoke-test representative single-image, compare, baseline, batch, and gallery commands with tiny local fixtures when the release changes extraction or report rendering.
- Do not add package-registry install commands unless a package has been explicitly published and verified.

Completion review:
- Completed: The 2026-05-18 release-readiness review lowered swatch-story to maintenance cadence because current user-facing workflows are broad enough for a release candidate and remaining items are release hygiene or evidence/examples rather than core feature growth.
- A roadmap item is complete only after tests, docs, translated README meaning, and release notes or changelog impact have been checked.
- Completed items should be removed from this README roadmap and, when substantial, archived in [ROADMAP.md](ROADMAP.md) or the changelog.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md), add behavior-focused tests before changing behavior, and keep the README translations synchronized in meaning.

## License

MIT. See [LICENSE](LICENSE).

## AI-Assisted Maintenance

This project may use AI assistance for maintenance tasks. Maintainers review changes before release and do not intentionally copy code or text from other projects.
