# swatch-story Roadmap

[English](README.md) | [中文](README-zh.md) | [日本語](README-ja.md)

## Maturity and Cadence

swatch-story is alpha-stage but usable for local, deterministic palette extraction and review reports. The 2026-05-18 release-readiness review found the recent Lab clustering, schema-version, export, batch, baseline, and docs work cohesive enough to lower the project from growth to maintenance. Planned cadence is now every 2-4 weeks plus urgent bug, docs-truthfulness, dependency, or report-schema stability issues.

## Now

- Keep the upcoming release candidate stable: run the release checklist before tagging, watch for user-reported palette/report regressions, and avoid broad feature additions unless they support release confidence.

## Next

- Improve gallery samples only if they directly demonstrate release-critical workflows such as transparency, ignored backgrounds, or perceptual clustering.
- Keep report schema changes additive until a tagged release documents the current JSON shape.
- Revisit cadence after the next release tag or if real user feedback reveals a higher-value workflow gap.

## Later

- Consider optional machine-readable changelog metadata for release automation.
- Evaluate config-file support only if repeated CLI presets stop covering common workflows.

## Release Checklist

Before tagging a release:

- Run `ruff check .`, `ruff format --check .`, `pytest -q`, and `python -m build` in a clean local virtual environment.
- Verify `README.md`, `README-zh.md`, and `README-ja.md` describe the same install path, examples, roadmap posture, and MIT license note.
- Confirm `CHANGELOG.md` has an Unreleased entry for every user-visible CLI option, report format field, or output artifact change.
- Smoke-test representative single-image, compare, baseline, batch, and gallery commands with tiny local fixtures when the release changes extraction or report rendering.
- Do not add package-registry install commands unless a package has been explicitly published and verified.

## Maintenance Triggers

- Update this roadmap when a public CLI option, report field, or output format changes.
- Recheck README, README-zh, and README-ja together when behavior descriptions change.
- Add or revise tests before changing palette extraction, clustering, report rendering, or preset validation behavior.
- Review changelog impact before release tags or when downstream report consumers may need migration notes.

## Completion Review

- Completed: Lab clustering now has lightweight compare, baseline, and batch report fixture snapshots plus synchronized README examples.
- Completed: The 2026-05-18 release-readiness review lowered swatch-story to maintenance cadence because current user-facing workflows are broad enough for a release candidate and remaining items are release hygiene or evidence/examples rather than core feature growth.
- A roadmap item is complete only after tests, docs, translated README meaning, and release notes or changelog impact have been checked.
- Completed items should be removed from README roadmap summaries and either archived here with context or recorded in the changelog.
- Items that stay open across multiple feature slices should be split into smaller verifiable tasks.
