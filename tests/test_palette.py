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


def test_extract_palette_default_cluster_distance_keeps_exact_rgb_behavior(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "exact.png"
    save_blocks(
        image_path,
        [
            (100, 100, 100),
            (100, 100, 100),
            (104, 101, 100),
            (20, 20, 20),
        ],
    )

    palette = extract_palette(image_path, colors=3, sample_step=1)

    assert [entry.rgb for entry in palette] == [
        (100, 100, 100),
        (20, 20, 20),
        (104, 101, 100),
    ]
    assert [entry.count for entry in palette] == [2, 1, 1]


def test_extract_palette_clusters_nearby_colors_when_distance_permits(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "cluster.png"
    save_blocks(
        image_path,
        [
            (100, 100, 100),
            (100, 100, 100),
            (104, 101, 100),
            (20, 20, 20),
        ],
    )

    palette = extract_palette(image_path, colors=2, sample_step=1, cluster_distance=8)

    assert [entry.rgb for entry in palette] == [(101, 100, 100), (20, 20, 20)]
    assert [entry.count for entry in palette] == [3, 1]
    assert [entry.percent for entry in palette] == [75.0, 25.0]


def test_extract_palette_does_not_cluster_below_threshold(tmp_path: Path) -> None:
    image_path = tmp_path / "below-threshold.png"
    save_blocks(
        image_path,
        [
            (100, 100, 100),
            (100, 100, 100),
            (104, 101, 100),
            (20, 20, 20),
        ],
    )

    palette = extract_palette(image_path, colors=3, sample_step=1, cluster_distance=3)

    assert [entry.rgb for entry in palette] == [
        (100, 100, 100),
        (20, 20, 20),
        (104, 101, 100),
    ]
    assert [entry.count for entry in palette] == [2, 1, 1]


def test_extract_palette_ignores_exact_hex_before_ranking(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "background.png"
    save_blocks(
        image_path,
        [
            (255, 255, 255),
            (255, 255, 255),
            (255, 0, 0),
            (0, 0, 255),
            (0, 0, 255),
        ],
    )

    palette = extract_palette(
        image_path, colors=2, sample_step=1, ignore_color="#ffffff"
    )

    assert [entry.hex for entry in palette] == ["#0000ff", "#ff0000"]
    assert [entry.count for entry in palette] == [2, 1]
    assert [entry.percent for entry in palette] == [66.67, 33.33]


def test_extract_palette_ignores_exact_hex_before_clustering(tmp_path: Path) -> None:
    image_path = tmp_path / "ignore-before-cluster.png"
    save_blocks(
        image_path,
        [
            (255, 255, 255),
            (250, 250, 250),
            (250, 250, 250),
            (10, 10, 10),
        ],
    )

    palette = extract_palette(
        image_path,
        colors=2,
        sample_step=1,
        ignore_color="#ffffff",
        cluster_distance=12,
    )

    assert [entry.rgb for entry in palette] == [(250, 250, 250), (10, 10, 10)]
    assert [entry.count for entry in palette] == [2, 1]
    assert [entry.percent for entry in palette] == [66.67, 33.33]


def test_extract_palette_accepts_case_insensitive_ignore_color_without_hash(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "case.png"
    save_blocks(image_path, [(170, 187, 204), (0, 0, 0), (0, 0, 0)])

    palette = extract_palette(
        image_path, colors=2, sample_step=1, ignore_color="AABBCC"
    )

    assert [entry.hex for entry in palette] == ["#000000"]
    assert [entry.percent for entry in palette] == [100.0]


def test_extract_palette_raises_when_ignore_color_removes_all_samples(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "empty.png"
    save_blocks(image_path, [(255, 255, 255), (255, 255, 255)])

    with pytest.raises(PaletteError, match="all sampled pixels were ignored"):
        extract_palette(image_path, colors=2, sample_step=1, ignore_color="ffffff")


def test_extract_palette_rejects_invalid_ignore_color(tmp_path: Path) -> None:
    image_path = tmp_path / "invalid.png"
    save_blocks(image_path, [(0, 0, 0), (255, 255, 255)])

    with pytest.raises(PaletteError, match="--ignore-color must be"):
        extract_palette(image_path, colors=2, sample_step=1, ignore_color="#ffffgg")


def test_extract_palette_rejects_invalid_cluster_distance(tmp_path: Path) -> None:
    image_path = tmp_path / "invalid-cluster.png"
    save_blocks(image_path, [(0, 0, 0), (255, 255, 255)])

    with pytest.raises(
        PaletteError, match="--cluster-distance must be between 0 and 255"
    ):
        extract_palette(image_path, colors=2, sample_step=1, cluster_distance=256)


def test_best_text_color_prefers_readable_foreground() -> None:
    assert best_text_color((10, 20, 30)) == "white"
    assert best_text_color((245, 240, 230)) == "black"


def test_palette_entries_include_black_and_white_contrast_ratios(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "contrast.png"
    save_blocks(image_path, [(0, 0, 0), (255, 255, 255)])

    summary = summarize_image(image_path, colors=2, sample_step=1, sort="luminance")

    dark, light = summary["palette"]
    assert dark["luminance"] == 0.0
    assert dark["contrast_with_black"] == 1.0
    assert dark["contrast_with_white"] == 21.0
    assert dark["best_text_color"] == "white"
    assert light["luminance"] == 1.0
    assert light["contrast_with_black"] == 21.0
    assert light["contrast_with_white"] == 1.0
    assert light["best_text_color"] == "black"


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
    assert summary["settings"]["sort"] == "frequency"
    assert summary["settings"]["cluster_distance"] == 0
    assert summary["palette"][0].keys() == {
        "rank",
        "hex",
        "rgb",
        "count",
        "percent",
        "luminance",
        "contrast_with_black",
        "contrast_with_white",
        "best_text_color",
        "label",
    }


def test_summarize_image_normalizes_ignore_color_in_settings(tmp_path: Path) -> None:
    image_path = tmp_path / "summary-ignore.png"
    save_blocks(image_path, [(170, 187, 204), (0, 0, 0), (255, 255, 255)])

    summary = summarize_image(
        image_path, colors=2, sample_step=1, ignore_color="AABBCC"
    )

    assert summary["settings"]["ignore_color"] == "#aabbcc"
    assert [entry["hex"] for entry in summary["palette"]] == ["#000000", "#ffffff"]


def test_summarize_image_frequency_sort_preserves_existing_ranking(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "frequency.png"
    save_blocks(
        image_path,
        [
            (255, 0, 0),
            (255, 0, 0),
            (255, 0, 0),
            (0, 0, 255),
            (0, 0, 255),
            (255, 255, 255),
            (0, 0, 0),
        ],
    )

    summary = summarize_image(image_path, colors=4, sample_step=1, sort="frequency")

    assert [entry["hex"] for entry in summary["palette"]] == [
        "#ff0000",
        "#0000ff",
        "#000000",
        "#ffffff",
    ]
    assert [entry["rank"] for entry in summary["palette"]] == [1, 2, 3, 4]


def test_summarize_image_luminance_sort_orders_dark_to_light_and_reranks(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "luminance.png"
    save_blocks(
        image_path,
        [
            (255, 0, 0),
            (255, 0, 0),
            (255, 0, 0),
            (0, 0, 255),
            (0, 0, 255),
            (255, 255, 255),
            (0, 0, 0),
        ],
    )

    summary = summarize_image(image_path, colors=4, sample_step=1, sort="luminance")

    assert summary["settings"]["sort"] == "luminance"
    assert [entry["hex"] for entry in summary["palette"]] == [
        "#000000",
        "#0000ff",
        "#ff0000",
        "#ffffff",
    ]
    assert [entry["rank"] for entry in summary["palette"]] == [1, 2, 3, 4]
    assert [entry["count"] for entry in summary["palette"]] == [1, 2, 3, 1]


def test_summarize_image_hue_sort_orders_chromatic_before_grayscale_and_reranks(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "hue.png"
    save_blocks(
        image_path,
        [
            (128, 128, 128),
            (128, 128, 128),
            (128, 128, 128),
            (0, 0, 255),
            (0, 0, 255),
            (255, 0, 0),
            (255, 255, 0),
            (0, 255, 0),
            (64, 64, 64),
        ],
    )

    summary = summarize_image(image_path, colors=6, sample_step=1, sort="hue")

    assert summary["settings"]["sort"] == "hue"
    assert [entry["hex"] for entry in summary["palette"]] == [
        "#ff0000",
        "#ffff00",
        "#00ff00",
        "#0000ff",
        "#404040",
        "#808080",
    ]
    assert [entry["rank"] for entry in summary["palette"]] == [1, 2, 3, 4, 5, 6]


def test_summarize_image_rejects_invalid_sort_value(tmp_path: Path) -> None:
    image_path = tmp_path / "sort-error.png"
    save_blocks(image_path, [(0, 0, 0), (255, 255, 255)])

    with pytest.raises(PaletteError, match="sort must be one of"):
        summarize_image(image_path, colors=2, sample_step=1, sort="brightness")


def test_summarize_image_can_include_optional_color_names(tmp_path: Path) -> None:
    image_path = tmp_path / "names.png"
    save_blocks(image_path, [(255, 0, 0), (0, 0, 255)])

    summary = summarize_image(
        image_path, colors=2, sample_step=1, include_color_names=True
    )

    assert [entry["name"] for entry in summary["palette"]] == ["blue", "red"]


def test_summarize_image_clustered_palette_keeps_sort_and_names(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "cluster-summary.png"
    save_blocks(
        image_path,
        [
            (250, 0, 0),
            (250, 0, 0),
            (255, 4, 0),
            (0, 0, 250),
            (0, 0, 255),
        ],
    )

    summary = summarize_image(
        image_path,
        colors=2,
        sample_step=1,
        cluster_distance=8,
        include_color_names=True,
        sort="hue",
    )

    assert summary["settings"]["cluster_distance"] == 8
    assert [entry["hex"] for entry in summary["palette"]] == ["#fc0100", "#0000fc"]
    assert [entry["count"] for entry in summary["palette"]] == [3, 2]
    assert [entry["percent"] for entry in summary["palette"]] == [60.0, 40.0]
    assert [entry["name"] for entry in summary["palette"]] == ["red", "blue"]
