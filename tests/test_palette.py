from pathlib import Path

import pytest
from PIL import Image

from swatch_story.palette import (
    PaletteError,
    automatic_sample_step,
    best_text_color,
    common_color_name,
    extract_palette,
    summarize_image,
)


def save_blocks(path: Path, colors: list[tuple[int, int, int]]) -> None:
    image = Image.new("RGB", (len(colors), 1))
    image.putdata(colors)
    image.save(path)


def test_extract_palette_reports_dominant_colors_and_percentages(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "blocks.png"
    save_blocks(
        image_path,
        [
            (255, 0, 0),
            (255, 0, 0),
            (255, 0, 0),
            (0, 0, 255),
        ],
    )

    palette = extract_palette(image_path, colors=2, sample_step=1)

    assert [entry.hex for entry in palette] == ["#ff0000", "#0000ff"]
    assert [entry.count for entry in palette] == [3, 1]
    assert [entry.percent for entry in palette] == [75.0, 25.0]
    assert [entry.rank for entry in palette] == [1, 2]


def test_best_text_color_prefers_readable_foreground() -> None:
    assert best_text_color((10, 20, 30)) == "white"
    assert best_text_color((245, 240, 230)) == "black"


def test_common_color_name_maps_exact_and_nearby_colors() -> None:
    assert common_color_name((255, 0, 0)) == "red"
    assert common_color_name((250, 250, 250)) == "white"
    assert common_color_name((8, 12, 18)) == "black"
    assert common_color_name((20, 130, 130)) == "teal"
    assert common_color_name((112, 73, 35)) == "brown"


def test_automatic_sample_step_accepts_custom_sample_limit() -> None:
    assert automatic_sample_step(400, 400, sample_limit=40_000) == 2
    assert automatic_sample_step(100, 100, sample_limit=40_000) == 1


def test_invalid_color_count_raises_clean_error(tmp_path: Path) -> None:
    image_path = tmp_path / "one.png"
    save_blocks(image_path, [(0, 0, 0)])

    with pytest.raises(PaletteError, match="between 2 and 12"):
        extract_palette(image_path, colors=13)


def test_summarize_image_has_expected_json_shape(tmp_path: Path) -> None:
    image_path = tmp_path / "summary.png"
    save_blocks(image_path, [(0, 0, 0), (255, 255, 255)])

    summary = summarize_image(image_path, colors=2, sample_step=1)

    assert summary["source"] == "summary.png"
    assert summary["size"] == {"width": 2, "height": 1}
    assert summary["settings"]["sample_limit"] == 10_000
    assert summary["palette"][0].keys() == {
        "rank",
        "hex",
        "rgb",
        "count",
        "percent",
        "luminance",
        "best_text_color",
        "label",
    }


def test_summarize_image_can_include_optional_color_names(tmp_path: Path) -> None:
    image_path = tmp_path / "names.png"
    save_blocks(image_path, [(255, 0, 0), (0, 0, 255)])

    summary = summarize_image(
        image_path, colors=2, sample_step=1, include_color_names=True
    )

    assert [entry["name"] for entry in summary["palette"]] == ["blue", "red"]
