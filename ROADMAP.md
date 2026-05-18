# swatch-story Roadmap

[English](README.md) | [中文](README-zh.md) | [日本語](README-ja.md)

## Maturity and Cadence

swatch-story is alpha-stage but usable for local, deterministic palette extraction and review reports. The project follows a small-maintenance cadence: behavior changes should land with tests, documentation translations should stay synchronized in meaning, and the roadmap should be reviewed after each feature slice or before a release tag.

## Now

- Harden clustering documentation and examples with real fixture scenarios.
- Add schema-version notes for JSON-like outputs before downstream users depend on more fields.

## Next

- Add lightweight report fixture snapshots for Lab clustering in compare, baseline, and batch flows.
- Improve gallery samples so they cover transparency, ignored backgrounds, and perceptual clustering examples.

## Later

- Consider optional machine-readable changelog metadata for release automation.
- Evaluate config-file support only if repeated CLI presets stop covering common workflows.

## Maintenance Triggers

- Update this roadmap when a public CLI option, report field, or output format changes.
- Recheck README, README-zh, and README-ja together when behavior descriptions change.
- Add or revise tests before changing palette extraction, clustering, report rendering, or preset validation behavior.
- Review changelog impact before release tags or when downstream report consumers may need migration notes.

## Completion Review

- A roadmap item is complete only after tests, docs, translated README meaning, and release notes or changelog impact have been checked.
- Completed items should be removed from README roadmap summaries and either archived here with context or recorded in the changelog.
- Items that stay open across multiple feature slices should be split into smaller verifiable tasks.
