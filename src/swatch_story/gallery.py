from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


class GalleryError(ValueError):
    """Raised when sample gallery files cannot be written safely."""


@dataclass(frozen=True)
class SampleFixture:
    name: str
    filename: str
    story: str
    size: tuple[int, int]
    tags: tuple[str, ...]
    pixels: tuple[tuple[int, int, int], ...]
    expected_dominant_hex: str
    expected_palette_hexes: tuple[str, ...]


SAMPLE_FIXTURES: tuple[SampleFixture, ...] = (
    SampleFixture(
        name="Warm Blocks",
        filename="warm-blocks.png",
        story="Warm teaching blocks with coral, amber, and deep brown.",
        size=(4, 4),
        tags=("warm", "neutral", "primary"),
        pixels=(
            *((220, 72, 52),) * 8,
            *((245, 166, 35),) * 5,
            *((90, 48, 35),) * 3,
        ),
        expected_dominant_hex="#dc4834",
        expected_palette_hexes=("#dc4834", "#f5a623", "#5a3023"),
    ),
    SampleFixture(
        name="Cool Stripes",
        filename="cool-stripes.png",
        story="Cool horizontal stripes with teal, blue, and pale ice.",
        size=(3, 6),
        tags=("cool", "gradient", "primary"),
        pixels=(
            *((0, 128, 128),) * 9,
            *((30, 90, 200),) * 6,
            *((210, 238, 242),) * 3,
        ),
        expected_dominant_hex="#008080",
        expected_palette_hexes=("#008080", "#1e5ac8", "#d2eef2"),
    ),
    SampleFixture(
        name="Contrast Checker",
        filename="contrast-checker.png",
        story="High contrast checker with black, white, and signal yellow.",
        size=(4, 4),
        tags=("contrast", "accessibility", "neutral", "primary"),
        pixels=(
            *((0, 0, 0),) * 7,
            *((255, 255, 255),) * 6,
            *((255, 215, 0),) * 3,
        ),
        expected_dominant_hex="#000000",
        expected_palette_hexes=("#000000", "#ffffff", "#ffd700"),
    ),
)


def _samples_for_tags(
    tags: list[str] | tuple[str, ...] | None,
) -> tuple[SampleFixture, ...]:
    if not tags:
        return SAMPLE_FIXTURES

    requested_tags = tuple(tag.lower() for tag in tags)
    known_tags = {tag for sample in SAMPLE_FIXTURES for tag in sample.tags}
    for tag in requested_tags:
        if tag not in known_tags:
            raise GalleryError(f"unknown gallery tag: {tag}")

    filtered_samples = tuple(
        sample
        for sample in SAMPLE_FIXTURES
        if all(tag in sample.tags for tag in requested_tags)
    )
    if not filtered_samples:
        raise GalleryError(
            "no gallery samples match tag filter: " + ", ".join(requested_tags)
        )
    return filtered_samples


def create_gallery(
    output_dir: str | Path,
    *,
    include_index: bool = True,
    include_manifest: bool = False,
    force: bool = False,
    tags: list[str] | tuple[str, ...] | None = None,
) -> list[Path]:
    target_dir = Path(output_dir)
    samples = _samples_for_tags(tags)
    paths = [target_dir / sample.filename for sample in samples]
    if include_index:
        paths.append(target_dir / "README.md")
    if include_manifest:
        paths.append(target_dir / "manifest.json")

    existing = [path for path in paths if path.exists()]
    if existing and not force:
        names = ", ".join(str(path) for path in existing)
        raise GalleryError(
            f"gallery file already exists: {names}. Use --force to replace them."
        )

    target_dir.mkdir(parents=True, exist_ok=True)
    for sample in samples:
        image = Image.new("RGB", sample.size)
        image.putdata(sample.pixels)
        image.save(target_dir / sample.filename)
    if include_index:
        (target_dir / "README.md").write_text(
            render_gallery_index(target_dir, samples=samples),
            encoding="utf-8",
        )
    if include_manifest:
        (target_dir / "manifest.json").write_text(
            render_gallery_manifest(samples=samples),
            encoding="utf-8",
        )
    return paths


def render_gallery_manifest(
    samples: tuple[SampleFixture, ...] = SAMPLE_FIXTURES,
) -> str:
    manifest = {
        "schema_version": 1,
        "generator": "swatch-story",
        "samples": [
            {
                "name": sample.name,
                "filename": sample.filename,
                "story": sample.story,
                "width": sample.size[0],
                "height": sample.size[1],
                "tags": list(sample.tags),
                "expected_dominant_hex": sample.expected_dominant_hex,
                "expected_palette_hexes": list(sample.expected_palette_hexes),
            }
            for sample in samples
        ],
    }
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def render_gallery_index(
    output_dir: str | Path,
    *,
    samples: tuple[SampleFixture, ...] = SAMPLE_FIXTURES,
) -> str:
    gallery_path = Path(output_dir)
    lines = [
        "# Swatch Story Sample Fixture Gallery",
        "",
        "This directory contains deterministic tiny PNG fixtures for learning "
        "palette extraction and report formats from a source checkout.",
        "",
        "## Samples",
        "",
    ]
    for sample in samples:
        sample_path = gallery_path / sample.filename
        lines.extend(
            [
                f"### {sample.name}",
                "",
                f"- File: `{sample_path.as_posix()}`",
                f"- Size: `{sample.size[0]}x{sample.size[1]}`",
                f"- Expected dominant color: `{sample.expected_dominant_hex}`",
                f"- Expected palette: `{', '.join(sample.expected_palette_hexes)}`",
                f"- Tags: {', '.join(f'`{tag}`' for tag in sample.tags)}",
                f"- Story: {sample.story}",
                "",
            ]
        )

    first_sample = samples[0]
    first_path = (gallery_path / first_sample.filename).as_posix()
    first_stem = Path(first_sample.filename).stem
    lines.extend(
        [
            "## Try The CLI",
            "",
            "Generate this gallery from a source checkout:",
            "",
            "```bash",
            f"swatch-story gallery {gallery_path.as_posix()}",
            "```",
            "",
            "Print a terminal palette summary:",
            "",
            "```bash",
            f"swatch-story {first_path} --colors 3 --sample-step 1",
            "```",
            "",
            "Write Markdown and HTML reports next to the fixtures:",
            "",
            "```bash",
            f"swatch-story {first_path} --colors 3 --markdown "
            f"{gallery_path.as_posix()}/{first_stem}.md --html "
            f"{gallery_path.as_posix()}/{first_stem}.html",
            "```",
            "",
        ]
    )
    if len(samples) >= 2:
        second_path = (gallery_path / samples[1].filename).as_posix()
        compare_report_path = f"{gallery_path.as_posix()}/sample-compare.md"
        lines.extend(
            [
                "Compare two sample palette stories:",
                "",
                "```bash",
                f"swatch-story compare {first_path} {second_path} --colors 3 "
                f"--sample-step 1 --markdown {compare_report_path}",
                "```",
                "",
            ]
        )
    return "\n".join(lines)
