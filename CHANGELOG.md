# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

- Documented a release-readiness review, maintenance cadence, and release checklist for tag preparation.
- Added lightweight Lab clustering snapshot coverage for compare, baseline, and batch report flows, plus synchronized README examples for when to use Lab clustering.
- Added root `schema_version: 1` metadata to deterministic JSON reports so downstream report consumers can track output shape changes.
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
