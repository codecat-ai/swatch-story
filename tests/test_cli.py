import json
import struct
from pathlib import Path

import pytest
from PIL import Image

from swatch_story.cli import main


def test_cli_writes_json_html_and_prints_summary(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    json_path = tmp_path / "story.json"
    html_path = tmp_path / "story.html"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--json",
            str(json_path),
            "--html",
            str(html_path),
            "--title",
            "CLI Story",
        ]
    )

    assert exit_code == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["source"] == "cli.png"
    assert "CLI Story" in html_path.read_text(encoding="utf-8")
    assert "#ff0000" in capsys.readouterr().out


def test_cli_precision_formats_palette_reports(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (3, 1))
    image.putdata([(255, 0, 0), (255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    json_path = tmp_path / "story.json"
    csv_path = tmp_path / "story.csv"
    markdown_path = tmp_path / "story.md"
    text_path = tmp_path / "story.txt"
    html_path = tmp_path / "story.html"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--precision",
            "1",
            "--json",
            str(json_path),
            "--csv",
            str(csv_path),
            "--markdown",
            str(markdown_path),
            "--text",
            str(text_path),
            "--html",
            str(html_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert [entry["percent"] for entry in summary["palette"]] == [66.7, 33.3]
    assert [entry["luminance"] for entry in summary["palette"]] == [0.2, 0.1]
    assert ",66.7,0.2," in csv_path.read_text(encoding="utf-8")
    assert "| 66.7% | 0.2 |" in markdown_path.read_text(encoding="utf-8")
    assert "| 66.7% |" in text_path.read_text(encoding="utf-8")
    assert "<dd>66.7% of sampled pixels</dd>" in html_path.read_text(encoding="utf-8")
    assert "66.7%" in capsys.readouterr().out


def test_cli_rejects_invalid_precision_with_argparse(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    with pytest.raises(SystemExit) as exc_info:
        main([str(image_path), "--precision", "7"])

    assert exc_info.value.code == 2
    assert "--precision must be between 0 and 6" in capsys.readouterr().err


def test_cli_gallery_writes_samples_and_index(tmp_path: Path, capsys) -> None:
    gallery_dir = tmp_path / "gallery"

    exit_code = main(["gallery", str(gallery_dir)])

    assert exit_code == 0
    assert (gallery_dir / "warm-blocks.png").exists()
    assert (gallery_dir / "cool-stripes.png").exists()
    assert (gallery_dir / "contrast-checker.png").exists()
    assert "swatch-story gallery" in (gallery_dir / "README.md").read_text(
        encoding="utf-8"
    )
    assert f"Wrote sample fixture gallery to {gallery_dir}" in capsys.readouterr().out


def test_cli_gallery_respects_no_index(tmp_path: Path, capsys) -> None:
    gallery_dir = tmp_path / "gallery"

    exit_code = main(["gallery", str(gallery_dir), "--no-index"])

    assert exit_code == 0
    assert (gallery_dir / "warm-blocks.png").exists()
    assert not (gallery_dir / "README.md").exists()
    assert "3 files" in capsys.readouterr().out


def test_cli_gallery_rejects_existing_files_without_force(
    tmp_path: Path, capsys
) -> None:
    gallery_dir = tmp_path / "gallery"
    gallery_dir.mkdir()
    (gallery_dir / "warm-blocks.png").write_text("existing", encoding="utf-8")

    exit_code = main(["gallery", str(gallery_dir)])

    assert exit_code == 2
    assert "already exists" in capsys.readouterr().err


def test_cli_gallery_force_overwrites_existing_files(tmp_path: Path, capsys) -> None:
    gallery_dir = tmp_path / "gallery"
    gallery_dir.mkdir()
    existing = gallery_dir / "warm-blocks.png"
    existing.write_text("existing", encoding="utf-8")

    exit_code = main(["gallery", str(gallery_dir), "--force"])

    assert exit_code == 0
    with Image.open(existing) as image:
        assert image.size == (4, 4)
    assert "4 files" in capsys.readouterr().out


def test_cli_compare_prints_report_and_writes_json(tmp_path: Path, capsys) -> None:
    before_path = tmp_path / "before.png"
    before = Image.new("RGB", (3, 1))
    before.putdata([(255, 0, 0), (0, 0, 255), (0, 255, 0)])
    before.save(before_path)
    after_path = tmp_path / "after.png"
    after = Image.new("RGB", (3, 1))
    after.putdata([(0, 0, 255), (0, 255, 0), (255, 255, 0)])
    after.save(after_path)
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
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    console = capsys.readouterr().out
    assert f"Palette comparison: {before_path} -> {after_path}" in console
    assert "Before dominant: #0000ff" in console
    assert "After dominant: #0000ff" in console
    assert "Shared colors: #0000ff, #00ff00" in console
    assert "Added colors: #ffff00" in console
    assert "Removed colors: #ff0000" in console
    assert "Drift score: 50.0%" in console
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["before"]["source_path"] == str(before_path)
    assert report["after"]["source_path"] == str(after_path)
    assert report["shared"] == ["#0000ff", "#00ff00"]
    assert report["added"] == ["#ffff00"]
    assert report["removed"] == ["#ff0000"]
    assert report["drift_score"] == 50.0


def test_cli_compare_writes_html_and_json_reports(tmp_path: Path, capsys) -> None:
    before_path = tmp_path / "before <one>.png"
    before = Image.new("RGB", (3, 1))
    before.putdata([(255, 0, 0), (0, 0, 255), (0, 255, 0)])
    before.save(before_path)
    after_path = tmp_path / "after & two.png"
    after = Image.new("RGB", (3, 1))
    after.putdata([(0, 0, 255), (0, 255, 0), (255, 255, 0)])
    after.save(after_path)
    json_path = tmp_path / "compare.json"
    html_path = tmp_path / "nested" / "compare.html"

    exit_code = main(
        [
            "compare",
            str(before_path),
            str(after_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--json",
            str(json_path),
            "--html",
            str(html_path),
        ]
    )

    assert exit_code == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["drift_score"] == 50.0
    html = html_path.read_text(encoding="utf-8")
    assert "Palette Drift Report" in html
    assert "before &lt;one&gt;.png" in html
    assert "after &amp; two.png" in html
    assert "Before dominant</dt>" in html
    assert "After dominant</dt>" in html
    assert "Shared colors" in html
    assert "#0000ff" in html
    assert "Added colors" in html
    assert "#ffff00" in html
    assert "Removed colors" in html
    assert "#ff0000" in html
    assert "Drift score</dt>" in html
    assert "50.0%</dd>" in html
    assert "Drift score: 50.0%" in capsys.readouterr().out


def test_cli_compare_writes_markdown_and_json_reports(tmp_path: Path, capsys) -> None:
    before_path = tmp_path / "before.png"
    before = Image.new("RGB", (3, 1))
    before.putdata([(255, 0, 0), (0, 0, 255), (0, 255, 0)])
    before.save(before_path)
    after_path = tmp_path / "after.png"
    after = Image.new("RGB", (3, 1))
    after.putdata([(0, 0, 255), (0, 255, 0), (255, 255, 0)])
    after.save(after_path)
    json_path = tmp_path / "compare.json"
    markdown_path = tmp_path / "nested" / "compare.md"

    exit_code = main(
        [
            "compare",
            str(before_path),
            str(after_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--json",
            str(json_path),
            "--markdown",
            str(markdown_path),
        ]
    )

    assert exit_code == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["drift_score"] == 50.0
    markdown = markdown_path.read_text(encoding="utf-8")
    assert markdown.startswith("# Palette Drift Report\n")
    assert f"| Before source path | {before_path} |" in markdown
    assert f"| After source path | {after_path} |" in markdown
    assert "| Before dominant colors | `#0000ff`, `#00ff00`, `#ff0000` |" in markdown
    assert "| After dominant colors | `#0000ff`, `#00ff00`, `#ffff00` |" in markdown
    assert "| Shared colors | `#0000ff`, `#00ff00` |" in markdown
    assert "| Added colors | `#ffff00` |" in markdown
    assert "| Removed colors | `#ff0000` |" in markdown
    assert "| Drift score | 50.0% |" in markdown
    assert "Drift score: 50.0%" in capsys.readouterr().out


def test_cli_compare_writes_text_markdown_and_json_reports(
    tmp_path: Path, capsys
) -> None:
    before_path = tmp_path / "before\none.png"
    before = Image.new("RGB", (3, 1))
    before.putdata([(255, 0, 0), (0, 0, 255), (0, 255, 0)])
    before.save(before_path)
    after_path = tmp_path / "after\ttwo.png"
    after = Image.new("RGB", (3, 1))
    after.putdata([(0, 0, 255), (0, 255, 0), (255, 255, 0)])
    after.save(after_path)
    json_path = tmp_path / "compare.json"
    markdown_path = tmp_path / "nested" / "compare.md"
    text_path = tmp_path / "nested" / "compare.txt"

    exit_code = main(
        [
            "compare",
            str(before_path),
            str(after_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--json",
            str(json_path),
            "--markdown",
            str(markdown_path),
            "--text",
            str(text_path),
        ]
    )

    assert exit_code == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["drift_score"] == 50.0
    assert markdown_path.read_text(encoding="utf-8").startswith(
        "# Palette Drift Report\n"
    )
    text = text_path.read_text(encoding="utf-8")
    assert text.startswith("Palette Drift Report\n")
    assert f"Before source path: {tmp_path}/before one.png\n" in text
    assert f"After source path: {tmp_path}/after two.png\n" in text
    assert "Before dominant colors: #0000ff, #00ff00, #ff0000\n" in text
    assert "After dominant colors: #0000ff, #00ff00, #ffff00\n" in text
    assert "Shared colors: #0000ff, #00ff00\n" in text
    assert "Added colors: #ffff00\n" in text
    assert "Removed colors: #ff0000\n" in text
    assert "Drift score: 50.0%\n" in text
    assert "Drift score: 50.0%" in capsys.readouterr().out


def test_cli_compare_uses_existing_palette_options(tmp_path: Path, capsys) -> None:
    before_path = tmp_path / "before.png"
    before = Image.new("RGB", (4, 1))
    before.putdata([(255, 255, 255), (255, 0, 0), (0, 0, 255), (0, 0, 255)])
    before.save(before_path)
    after_path = tmp_path / "after.png"
    after = Image.new("RGB", (4, 1))
    after.putdata([(255, 255, 255), (0, 0, 255), (0, 128, 128), (0, 128, 128)])
    after.save(after_path)
    json_path = tmp_path / "compare.json"

    exit_code = main(
        [
            "compare",
            str(before_path),
            str(after_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--ignore-color",
            "ffffff",
            "--sort",
            "hue",
            "--names",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["before"]["settings"]["ignore_color"] == "#ffffff"
    assert report["before"]["settings"]["sort"] == "hue"
    assert report["before"]["palette"][0]["name"] == "red"
    assert report["after"]["palette"][0]["name"] == "teal"
    assert "Added colors: #008080" in capsys.readouterr().out


def test_cli_compare_returns_palette_error_exit_code(tmp_path: Path, capsys) -> None:
    before_path = tmp_path / "missing.png"
    after_path = tmp_path / "after.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(after_path)

    exit_code = main(["compare", str(before_path), str(after_path)])

    assert exit_code == 2
    assert "swatch-story: image not found:" in capsys.readouterr().err


def test_cli_html_report_includes_settings_and_names(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli <story>.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    html_path = tmp_path / "nested" / "story.html"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--html",
            str(html_path),
            "--names",
        ]
    )

    assert exit_code == 0
    html = html_path.read_text(encoding="utf-8")
    assert "cli &lt;story&gt;.png" in html
    assert str(image_path).replace("<", "&lt;").replace(">", "&gt;") in html
    assert "Requested colors</dt>" in html
    assert "2</dd>" in html
    assert "Sample step</dt>" in html
    assert "Every 1 pixel</dd>" in html
    assert "Color names</dt>" in html
    assert "Included</dd>" in html
    assert "Common name" in html
    assert "#ff0000" in capsys.readouterr().out


def test_cli_names_flag_adds_json_and_console_name_hints(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    json_path = tmp_path / "story.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--json",
            str(json_path),
            "--names",
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert [entry["name"] for entry in summary["palette"]] == ["blue", "red"]
    assert "blue" in capsys.readouterr().out


def test_cli_ignore_color_updates_palette_json_and_console(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli-ignore.png"
    image = Image.new("RGB", (4, 1))
    image.putdata([(255, 255, 255), (255, 255, 255), (255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    json_path = tmp_path / "story.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--ignore-color",
            "FFFFFF",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert summary["settings"]["ignore_color"] == "#ffffff"
    assert [entry["hex"] for entry in summary["palette"]] == ["#0000ff", "#ff0000"]
    assert [entry["percent"] for entry in summary["palette"]] == [50.0, 50.0]
    console = capsys.readouterr().out
    assert "#ffffff" not in console
    assert "#0000ff" in console


def test_cli_cluster_distance_updates_palette_json_and_console(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli-cluster.png"
    image = Image.new("RGB", (4, 1))
    image.putdata(
        [
            (100, 100, 100),
            (100, 100, 100),
            (104, 101, 100),
            (20, 20, 20),
        ]
    )
    image.save(image_path)
    json_path = tmp_path / "story.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--cluster-distance",
            "8",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert summary["settings"]["cluster_distance"] == 8
    assert [entry["hex"] for entry in summary["palette"]] == ["#656464", "#141414"]
    assert [entry["count"] for entry in summary["palette"]] == [3, 1]
    assert "#656464" in capsys.readouterr().out


def test_cli_sort_luminance_updates_json_and_console_order(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli-sort.png"
    image = Image.new("RGB", (7, 1))
    image.putdata(
        [
            (255, 0, 0),
            (255, 0, 0),
            (255, 0, 0),
            (0, 0, 255),
            (0, 0, 255),
            (255, 255, 255),
            (0, 0, 0),
        ]
    )
    image.save(image_path)
    json_path = tmp_path / "story.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "4",
            "--sample-step",
            "1",
            "--sort",
            "luminance",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert summary["settings"]["sort"] == "luminance"
    assert [entry["hex"] for entry in summary["palette"]] == [
        "#000000",
        "#0000ff",
        "#ff0000",
        "#ffffff",
    ]
    console_lines = capsys.readouterr().out.splitlines()
    assert " 1. #000000" in console_lines[1]
    assert " 4. #ffffff" in console_lines[4]


def test_cli_rejects_invalid_sort_choice(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    with pytest.raises(SystemExit) as exc_info:
        main([str(image_path), "--sort", "brightness"])

    assert exc_info.value.code == 2
    assert "invalid choice: 'brightness'" in capsys.readouterr().err


def test_cli_rejects_invalid_cluster_distance_with_argparse(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    with pytest.raises(SystemExit) as exc_info:
        main([str(image_path), "--cluster-distance", "256"])

    assert exc_info.value.code == 2
    assert "--cluster-distance must be between 0 and 255" in capsys.readouterr().err


def test_cli_default_json_omits_color_name_hints(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    json_path = tmp_path / "story.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert "name" not in summary["palette"][0]
    assert "name" not in summary["palette"][1]
    assert "blue" not in capsys.readouterr().out


def test_cli_sample_limit_controls_automatic_sample_step(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "large.png"
    Image.new("RGB", (400, 400), (0, 0, 0)).save(image_path)
    json_path = tmp_path / "story.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-limit",
            "40000",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    settings = json.loads(json_path.read_text(encoding="utf-8"))["settings"]
    assert settings["sample_limit"] == 40_000
    assert settings["sample_step"] == 2
    assert "#000000" in capsys.readouterr().out


def test_cli_sample_step_takes_precedence_over_sample_limit(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "large.png"
    Image.new("RGB", (400, 400), (0, 0, 0)).save(image_path)
    json_path = tmp_path / "story.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "5",
            "--sample-limit",
            "40000",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    settings = json.loads(json_path.read_text(encoding="utf-8"))["settings"]
    assert settings["sample_limit"] == 40_000
    assert settings["sample_step"] == 5
    assert "#000000" in capsys.readouterr().out


def test_cli_writes_css_custom_properties(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    json_path = tmp_path / "story.json"
    css_path = tmp_path / "nested" / "story.css"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--json",
            str(json_path),
            "--css",
            str(css_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    css = css_path.read_text(encoding="utf-8")
    first = summary["palette"][0]
    second = summary["palette"][1]
    assert f"--swatch-story-color-1: {first['hex']};" in css
    assert (
        f"--swatch-story-color-1-rgb: "
        f"{first['rgb'][0]}, {first['rgb'][1]}, {first['rgb'][2]};"
    ) in css
    assert f"--swatch-story-color-1-text: {first['best_text_color']};" in css
    assert f"--swatch-story-color-2: {second['hex']};" in css
    assert first["hex"] in capsys.readouterr().out


def test_cli_writes_csv_report_with_blank_names_by_default(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    csv_path = tmp_path / "nested" / "story.csv"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--csv",
            str(csv_path),
        ]
    )

    assert exit_code == 0
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert (
        lines[0] == "rank,hex,r,g,b,count,percent,luminance,best_text_color,label,name"
    )
    assert lines[1].endswith(",")
    assert lines[2].endswith(",")
    assert "#ff0000" in capsys.readouterr().out


def test_cli_writes_csv_report_with_names(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    csv_path = tmp_path / "nested" / "story.csv"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--csv",
            str(csv_path),
            "--names",
        ]
    )

    assert exit_code == 0
    csv = csv_path.read_text(encoding="utf-8")
    assert "1,#0000ff,0,0,255,1,50.0,0.072,white,dark,blue\n" in csv
    assert "2,#ff0000,255,0,0,1,50.0,0.213,black,dark,red\n" in csv
    assert "#ff0000" in capsys.readouterr().out


def test_cli_writes_markdown_report(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    markdown_path = tmp_path / "nested" / "story.md"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--markdown",
            str(markdown_path),
            "--title",
            "CLI Story",
        ]
    )

    assert exit_code == 0
    markdown = markdown_path.read_text(encoding="utf-8")
    assert markdown.startswith("# CLI Story\n")
    assert "| Rank | Color | RGB | Percent | Luminance | Text | Label |" in markdown
    assert "#ff0000" in markdown
    assert "#ff0000" in capsys.readouterr().out


def test_cli_writes_text_report_and_prints_summary(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    text_path = tmp_path / "nested" / "story.txt"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--text",
            str(text_path),
            "--title",
            "CLI\nStory",
            "--names",
        ]
    )

    assert exit_code == 0
    text = text_path.read_text(encoding="utf-8")
    assert text.startswith("CLI Story\n")
    assert "Source: cli.png\n" in text
    assert (
        "Settings: colors 2; sample step 1; sample limit 10000; "
        "cluster distance 0; sort frequency; ignored color none; names included\n"
    ) in text
    assert "1. #0000ff | rgb(0, 0, 255) | 50.0% | dark | text white | name blue" in text
    assert "#ff0000" in capsys.readouterr().out


def test_cli_writes_gpl_palette_with_names_and_collapsed_title(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    gpl_path = tmp_path / "nested" / "story.gpl"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--gpl",
            str(gpl_path),
            "--title",
            "CLI\nStory\tPalette",
            "--names",
        ]
    )

    assert exit_code == 0
    assert gpl_path.read_text(encoding="utf-8") == (
        "GIMP Palette\n"
        "Name: CLI Story Palette\n"
        "Columns: 2\n"
        "# Generated by swatch-story.\n"
        "  0   0 255 #0000ff blue\n"
        "255   0   0 #ff0000 red\n"
    )
    assert "#ff0000" in capsys.readouterr().out


def test_cli_writes_ase_palette_with_names_and_title(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    ase_path = tmp_path / "nested" / "story.ase"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--ase",
            str(ase_path),
            "--title",
            "CLI\nStory\tPalette",
            "--names",
        ]
    )

    assert exit_code == 0
    data = ase_path.read_bytes()
    assert data[:4] == b"ASEF"
    assert struct.unpack_from(">HHI", data, 4) == (1, 0, 4)
    assert b"\x00C\x00L\x00I\x00 \x00S\x00t\x00o\x00r\x00y\x00 \x00P" in data
    assert b"\x00#\x000\x000\x000\x000\x00f\x00f\x00 \x00b\x00l\x00u\x00e" in data
    assert b"\x00#\x00f\x00f\x000\x000\x000\x000\x00 \x00r\x00e\x00d" in data
    assert "#ff0000" in capsys.readouterr().out


def test_cli_rejects_invalid_color_count(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    exit_code = main([str(image_path), "--colors", "1"])

    assert exit_code == 2
    assert "between 2 and 12" in capsys.readouterr().err


def test_cli_rejects_invalid_sample_limit(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    exit_code = main([str(image_path), "--sample-limit", "0"])

    assert exit_code == 2
    assert "--sample-limit must be 1 or greater" in capsys.readouterr().err


def test_cli_rejects_invalid_ignore_color(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    exit_code = main([str(image_path), "--ignore-color", "#12345z"])

    assert exit_code == 2
    assert "--ignore-color must be #rrggbb or rrggbb" in capsys.readouterr().err
