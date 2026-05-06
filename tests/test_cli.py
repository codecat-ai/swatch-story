import json
from pathlib import Path

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


def test_cli_rejects_invalid_color_count(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    exit_code = main([str(image_path), "--colors", "1"])

    assert exit_code == 2
    assert "between 2 and 12" in capsys.readouterr().err
