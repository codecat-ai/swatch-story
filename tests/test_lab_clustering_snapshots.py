import json
from pathlib import Path

from PIL import Image

from swatch_story.cli import main


def write_pixels(path: Path, pixels: list[tuple[int, int, int]]) -> None:
    image = Image.new("RGB", (len(pixels), 1))
    image.putdata(pixels)
    image.save(path)


LAB_RED_CLUSTER = [(200, 0, 0), (200, 0, 0), (202, 4, 0)]
GREEN_CLUSTER = [(0, 128, 0), (0, 128, 0)]
BLUE_CLUSTER = [(0, 100, 200), (4, 102, 204)]


def test_compare_cli_json_snapshot_includes_lab_cluster_settings_and_drift(
    tmp_path: Path, capsys
) -> None:
    before_path = tmp_path / "before.png"
    after_path = tmp_path / "after.png"
    write_pixels(before_path, LAB_RED_CLUSTER + GREEN_CLUSTER)
    write_pixels(after_path, LAB_RED_CLUSTER + GREEN_CLUSTER + BLUE_CLUSTER)
    json_path = tmp_path / "compare.json"

    exit_code = main(
        [
            "compare",
            str(before_path),
            str(after_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--cluster-distance",
            "5",
            "--cluster-space",
            "lab",
            "--precision",
            "2",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["schema_version"] == 1
    assert report["before"]["settings"]["cluster_space"] == "lab"
    assert report["after"]["settings"]["cluster_distance"] == 5
    assert [entry["hex"] for entry in report["before"]["palette"]] == [
        "#c90100",
        "#008000",
    ]
    assert [entry["hex"] for entry in report["after"]["palette"]] == [
        "#c90100",
        "#008000",
        "#0265ca",
    ]
    assert report["added"] == ["#0265ca"]
    assert report["removed"] == []
    assert report["changed"] == [
        {
            "hex": "#c90100",
            "before_percent": 60.0,
            "after_percent": 42.86,
            "delta_percent": -17.14,
        },
        {
            "hex": "#008000",
            "before_percent": 40.0,
            "after_percent": 28.57,
            "delta_percent": -11.43,
        },
    ]
    assert report["drift_score"] == 33.33
    assert "Drift score: 33.33%" in capsys.readouterr().out


def test_baseline_cli_json_snapshot_keeps_lab_settings_per_candidate(
    tmp_path: Path, capsys
) -> None:
    baseline_path = tmp_path / "baseline.png"
    steady_path = tmp_path / "steady.png"
    shifted_path = tmp_path / "shifted.png"
    baseline_pixels = LAB_RED_CLUSTER + GREEN_CLUSTER
    write_pixels(baseline_path, baseline_pixels)
    write_pixels(steady_path, baseline_pixels)
    write_pixels(shifted_path, LAB_RED_CLUSTER + BLUE_CLUSTER)
    json_path = tmp_path / "baseline.json"

    exit_code = main(
        [
            "baseline",
            str(baseline_path),
            str(steady_path),
            str(shifted_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--cluster-distance",
            "5",
            "--cluster-space",
            "lab",
            "--precision",
            "1",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["schema_version"] == 1
    assert report["baseline"]["settings"]["cluster_space"] == "lab"
    assert report["baseline"]["palette"][0]["hex"] == "#c90100"
    assert [
        candidate["source"]["settings"]["cluster_distance"]
        for candidate in report["candidates"]
    ] == [5, 5]
    candidate_cluster_spaces = [
        candidate["source"]["settings"]["cluster_space"]
        for candidate in report["candidates"]
    ]
    assert candidate_cluster_spaces == [
        "lab",
        "lab",
    ]
    assert [candidate["source"]["source"] for candidate in report["candidates"]] == [
        "steady.png",
        "shifted.png",
    ]
    assert [candidate["drift_score"] for candidate in report["candidates"]] == [
        0.0,
        66.7,
    ]
    assert report["candidates"][1]["added"] == ["#0265ca"]
    assert report["candidates"][1]["removed"] == ["#008000"]
    assert "Wrote baseline report for 2 candidates" in capsys.readouterr().out


def test_batch_cli_markdown_snapshot_includes_lab_settings_and_representatives(
    tmp_path: Path, capsys
) -> None:
    first_path = tmp_path / "first.png"
    second_path = tmp_path / "second.png"
    write_pixels(first_path, LAB_RED_CLUSTER + GREEN_CLUSTER)
    write_pixels(second_path, BLUE_CLUSTER + GREEN_CLUSTER)
    markdown_path = tmp_path / "batch.md"

    exit_code = main(
        [
            "batch",
            str(first_path),
            str(second_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--cluster-distance",
            "5",
            "--cluster-space",
            "lab",
            "--precision",
            "1",
            "--markdown",
            str(markdown_path),
        ]
    )

    assert exit_code == 0
    markdown = markdown_path.read_text(encoding="utf-8")
    assert (
        "Settings: colors 3; sample step 1; sample limit 10000; "
        "cluster distance 5; cluster space lab; sort frequency;"
    ) in markdown
    assert "## first.png" in markdown
    assert "Dominant colors: `#c90100` 60.0%, `#008000` 40.0%" in markdown
    assert "| 1 | `#c90100` | `201, 1, 0` | 60.0% |" in markdown
    assert "## second.png" in markdown
    assert "Dominant colors: `#008000` 50.0%, `#0265ca` 50.0%" in markdown
    assert "| 2 | `#0265ca` | `2, 101, 202` | 50.0% |" in markdown
    assert "Wrote batch report for 2 images" in capsys.readouterr().out
