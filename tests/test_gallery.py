from pathlib import Path

import pytest
from PIL import Image

from swatch_story.gallery import (
    SAMPLE_FIXTURES,
    GalleryError,
    create_gallery,
    render_gallery_index,
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


def test_create_gallery_refuses_to_overwrite_existing_files(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)
    existing = tmp_path / SAMPLE_FIXTURES[0].filename
    existing.write_text("keep me", encoding="utf-8")

    with pytest.raises(GalleryError, match="already exists"):
        create_gallery(tmp_path)

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
    assert (
        "swatch-story demo-gallery/warm-blocks.png --colors 3 --sample-step 1"
        in markdown
    )
    assert (
        "swatch-story demo-gallery/cool-stripes.png --colors 3 --markdown" in markdown
    )
    assert "swatch-story compare demo-gallery/warm-blocks.png" in markdown
    assert "pip install" not in markdown
