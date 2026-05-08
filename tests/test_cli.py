import json
import struct
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
