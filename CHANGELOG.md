# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

- Added `--ignore-color HEX` to exclude exact RGB matches before palette ranking, normalize accepted `#rrggbb`/`rrggbb` values in settings, recalculate percentages from remaining sampled pixels, and report clear errors for invalid or fully ignored samples.
- Added deterministic Adobe Swatch Exchange `.ase` palette export with `--ase PATH`, title-based groups, RGB swatches, and optional `--names` labels for common design-tool palette imports.
- Added deterministic GIMP `.gpl` palette export with `--gpl PATH`, whitespace-collapsed titles, and optional `--names` labels for design-tool interoperability.
- Added browser-review HTML contact-sheet reports with image path/name metadata, extraction settings, escaped user-derived values, swatch cards, and contrast guidance.
- Added optional `--names` color-name hints for JSON, HTML, Markdown, CSS comments, and console summaries using a small offline built-in common-color set.
- Added Markdown palette report rendering and `--markdown PATH` CLI output for notes and docs.

## 0.1.0 - 2026-05-05

- Initial local-first palette extraction CLI.
- Added JSON and standalone HTML report output.
- Added tests, CI, and project documentation.
