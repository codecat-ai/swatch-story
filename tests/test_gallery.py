import json
from pathlib import Path

import pytest
from PIL import Image

from swatch_story.gallery import (
    SAMPLE_FIXTURES,
    GalleryError,
    create_gallery,
    render_gallery_index,
    render_gallery_manifest,
)
from swatch_story.palette import summarize_image


def test_create_gallery_writes_deterministic_png_samples_and_index(
    tmp_path: Path,
) -> None:
    written = create_gallery(tmp_path)

    assert [path.name for path in written] == [
        "warm-blocks.png",
        "cool-stripes.png",
        "contrast-checker.png",
        "README.md",
    ]
    for sample in SAMPLE_FIXTURES:
        image_path = tmp_path / sample.filename
        assert image_path.exists()
        with Image.open(image_path) as image:
            assert image.size == sample.size
        summary = summarize_image(image_path, colors=3, sample_step=1)
        assert summary["palette"][0]["hex"] == sample.expected_dominant_hex
        assert [entry["hex"] for entry in summary["palette"]] == list(
            sample.expected_palette_hexes
        )


def test_create_gallery_can_skip_index(tmp_path: Path) -> None:
    written = create_gallery(tmp_path, include_index=False)

    assert [path.name for path in written] == [
        "warm-blocks.png",
        "cool-stripes.png",
        "contrast-checker.png",
    ]
    assert not (tmp_path / "README.md").exists()


def test_create_gallery_can_write_manifest_without_index(tmp_path: Path) -> None:
    written = create_gallery(tmp_path, include_index=False, include_manifest=True)

    assert [path.name for path in written] == [
        "warm-blocks.png",
        "cool-stripes.png",
        "contrast-checker.png",
        "manifest.json",
    ]
    assert not (tmp_path / "README.md").exists()
    manifest_path = tmp_path / "manifest.json"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    assert manifest_text.endswith("\n")
    assert json.loads(manifest_text) == json.loads(render_gallery_manifest())


def test_create_gallery_filters_samples_by_repeated_tags(tmp_path: Path) -> None:
    written = create_gallery(
        tmp_path,
        include_manifest=True,
        tags=["CONTRAST", "accessibility"],
    )

    assert [path.name for path in written] == [
        "contrast-checker.png",
        "README.md",
        "manifest.json",
    ]
    assert (tmp_path / "contrast-checker.png").exists()
    assert not (tmp_path / "warm-blocks.png").exists()
    assert not (tmp_path / "cool-stripes.png").exists()
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert [sample["filename"] for sample in manifest["samples"]] == [
        "contrast-checker.png"
    ]


def test_create_gallery_rejects_no_matching_tag_filter(tmp_path: Path) -> None:
    with pytest.raises(
        GalleryError,
        match="no gallery samples match tag filter: warm, accessibility",
    ):
        create_gallery(tmp_path, tags=["warm", "accessibility"])

    assert not any(tmp_path.iterdir())


def test_create_gallery_refuses_to_overwrite_existing_files(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)
    existing = tmp_path / SAMPLE_FIXTURES[0].filename
    existing.write_text("keep me", encoding="utf-8")

    with pytest.raises(GalleryError, match="already exists"):
        create_gallery(tmp_path)

    assert existing.read_text(encoding="utf-8") == "keep me"


def test_create_gallery_refuses_to_overwrite_existing_manifest(tmp_path: Path) -> None:
    existing = tmp_path / "manifest.json"
    existing.write_text("keep me", encoding="utf-8")

    with pytest.raises(GalleryError, match="manifest.json"):
        create_gallery(tmp_path, include_manifest=True)

    assert existing.read_text(encoding="utf-8") == "keep me"


def test_create_gallery_force_overwrites_existing_files(tmp_path: Path) -> None:
    existing = tmp_path / SAMPLE_FIXTURES[0].filename
    existing.write_text("replace me", encoding="utf-8")

    create_gallery(tmp_path, force=True)

    with Image.open(existing) as image:
        assert image.size == SAMPLE_FIXTURES[0].size


def test_render_gallery_index_includes_source_checkout_commands() -> None:
    markdown = render_gallery_index(Path("demo-gallery"))

    assert "# Swatch Story Sample Fixture Gallery" in markdown
    assert "- Tags: `warm`, `neutral`, `primary`" in markdown
    assert "- Tags: `contrast`, `accessibility`, `neutral`, `primary`" in markdown
    assert (
        "swatch-story demo-gallery/warm-blocks.png --colors 3 --sample-step 1"
        in markdown
    )
    assert "swatch-story demo-gallery/warm-blocks.png --colors 3 --markdown" in markdown
    assert "swatch-story compare demo-gallery/warm-blocks.png" in markdown
    assert "pip install" not in markdown


def test_render_gallery_manifest_is_stable_fixture_json() -> None:
    manifest = render_gallery_manifest()

    assert manifest.endswith("\n")
    assert json.loads(manifest) == {
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
            for sample in SAMPLE_FIXTURES
        ],
    }
