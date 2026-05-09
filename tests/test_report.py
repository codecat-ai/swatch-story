import json
import struct
from pathlib import Path

import pytest

from swatch_story.report import (
    render_ase_report,
    render_csv_report,
    render_gpl_report,
    render_html_report,
    render_markdown_report,
    write_ase_report,
    write_css_report,
    write_csv_report,
    write_gpl_report,
    write_html_report,
    write_json_report,
    write_markdown_report,
)


def sample_summary() -> dict:
    return {
        "source": "sample.png",
        "source_path": "fixtures/sample.png",
        "size": {"width": 2, "height": 1},
        "settings": {"colors": 2, "sample_step": 1, "color_names": False},
        "palette": [
            {
                "rank": 1,
                "hex": "#112233",
                "rgb": [17, 34, 51],
                "count": 1,
                "percent": 50.0,
                "luminance": 0.015,
                "best_text_color": "white",
                "label": "dark",
            },
            {
                "rank": 2,
                "hex": "#eeeeee",
                "rgb": [238, 238, 238],
                "count": 1,
                "percent": 50.0,
                "luminance": 0.855,
                "best_text_color": "black",
                "label": "light",
            },
        ],
    }


def named_summary() -> dict:
    summary = sample_summary()
    summary["settings"]["color_names"] = True
    summary["palette"][0]["name"] = "blue"
    summary["palette"][1]["name"] = "gray"
    return summary


def parse_ase_string(data: bytes, offset: int) -> tuple[str, int]:
    length = struct.unpack_from(">H", data, offset)[0]
    offset += 2
    raw = data[offset : offset + (length * 2)]
    offset += length * 2
    return raw[:-2].decode("utf-16-be"), offset


def parse_ase_blocks(data: bytes) -> list[tuple[int, bytes]]:
    assert data[:4] == b"ASEF"
    assert struct.unpack_from(">HH", data, 4) == (1, 0)
    block_count = struct.unpack_from(">I", data, 8)[0]
    offset = 12
    blocks = []
    for _ in range(block_count):
        block_type, block_length = struct.unpack_from(">HI", data, offset)
        offset += 6
        block_data = data[offset : offset + block_length]
        offset += block_length
        blocks.append((block_type, block_data))
    assert offset == len(data)
    return blocks


def test_ase_report_renders_deterministic_rgb_group() -> None:
    ase = render_ase_report(named_summary(), title="  Palette\nStory\tExport  ")

    assert ase == render_ase_report(named_summary(), title="Palette Story Export")
    blocks = parse_ase_blocks(ase)
    assert [block_type for block_type, _ in blocks] == [0xC001, 0x0001, 0x0001, 0xC002]

    group_name, offset = parse_ase_string(blocks[0][1], 0)
    assert group_name == "Palette Story Export"
    assert offset == len(blocks[0][1])

    first_name, offset = parse_ase_string(blocks[1][1], 0)
    assert first_name == "#112233 blue"
    assert blocks[1][1][offset : offset + 4] == b"RGB "
    assert blocks[1][1][offset + 4 : offset + 16] == struct.pack(
        ">fff", 17 / 255, 34 / 255, 51 / 255
    )
    red, green, blue = struct.unpack_from(">fff", blocks[1][1], offset + 4)
    assert red == pytest.approx(17 / 255)
    assert green == pytest.approx(34 / 255)
    assert blue == pytest.approx(51 / 255)
    assert struct.unpack_from(">H", blocks[1][1], offset + 16)[0] == 0

    second_name, offset = parse_ase_string(blocks[2][1], 0)
    assert second_name == "#eeeeee gray"
    assert blocks[2][1][offset : offset + 4] == b"RGB "
    assert blocks[2][1][offset + 4 : offset + 16] == struct.pack(
        ">fff", 238 / 255, 238 / 255, 238 / 255
    )
    red, green, blue = struct.unpack_from(">fff", blocks[2][1], offset + 4)
    assert red == pytest.approx(238 / 255)
    assert green == pytest.approx(238 / 255)
    assert blue == pytest.approx(238 / 255)
    assert struct.unpack_from(">H", blocks[2][1], offset + 16)[0] == 0
    assert blocks[3][1] == b""


def test_ase_report_sanitizes_single_line_names() -> None:
    summary = sample_summary()
    summary["palette"][0]["name"] = "steel\nblue\tink"

    blocks = parse_ase_blocks(render_ase_report(summary, title="Title\nName"))

    group_name, _ = parse_ase_string(blocks[0][1], 0)
    swatch_name, _ = parse_ase_string(blocks[1][1], 0)
    fallback_name, _ = parse_ase_string(blocks[2][1], 0)
    assert group_name == "Title Name"
    assert swatch_name == "#112233 steel blue ink"
    assert fallback_name == "#eeeeee"


def test_write_ase_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "palette.ase"

    write_ase_report(sample_summary(), output, title="Palette Story")

    assert output.read_bytes().startswith(b"ASEF\x00\x01\x00\x00")


def test_write_json_report_creates_readable_json(tmp_path: Path) -> None:
    output = tmp_path / "story.json"

    write_json_report(sample_summary(), output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["source"] == "sample.png"
    assert data["palette"][0]["hex"] == "#112233"


def test_csv_report_renders_stable_table_with_blank_missing_names() -> None:
    summary = sample_summary()
    summary["palette"][0]["label"] = "dark, cool"
    summary["palette"][1]["name"] = "pale gray"

    assert render_csv_report(summary) == (
        "rank,hex,r,g,b,count,percent,luminance,best_text_color,label,name\r\n"
        '1,#112233,17,34,51,1,50.0,0.015,white,"dark, cool",\r\n'
        "2,#eeeeee,238,238,238,1,50.0,0.855,black,light,pale gray\r\n"
    )


def test_write_csv_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "story.csv"

    write_csv_report(named_summary(), output)

    assert output.read_text(encoding="utf-8") == (
        "rank,hex,r,g,b,count,percent,luminance,best_text_color,label,name\n"
        "1,#112233,17,34,51,1,50.0,0.015,white,dark,blue\n"
        "2,#eeeeee,238,238,238,1,50.0,0.855,black,light,gray\n"
    )


def test_html_report_escapes_title_and_contains_swatches() -> None:
    html = render_html_report(sample_summary(), title="<Palette & Story>")

    assert "&lt;Palette &amp; Story&gt;" in html
    assert "<Palette & Story>" not in html
    assert "#112233" in html
    assert "background: #112233" in html
    assert "color: white" in html


def test_html_report_renders_contact_sheet_review_metadata() -> None:
    html = render_html_report(named_summary(), title="Palette Review")

    assert "<h1>Palette Review</h1>" in html
    assert "Image name</dt>" in html
    assert "sample.png</dd>" in html
    assert "Image path</dt>" in html
    assert "fixtures/sample.png</dd>" in html
    assert "Requested colors</dt>" in html
    assert "2</dd>" in html
    assert "Sample step</dt>" in html
    assert "Every 1 pixel</dd>" in html
    assert "Color names</dt>" in html
    assert "Included</dd>" in html
    assert "Ignored color</dt>" not in html
    assert "2 swatches" in html
    assert "dominant color is #112233" in html


def test_html_report_includes_ignored_color_when_configured() -> None:
    summary = sample_summary()
    summary["settings"]["ignore_color"] = "#ffffff"

    html = render_html_report(summary)

    assert "Ignored color</dt>" in html
    assert "#ffffff</dd>" in html


def test_html_report_escapes_user_derived_metadata_and_names() -> None:
    summary = sample_summary()
    summary["source"] = 'sample"><script>.png'
    summary["source_path"] = "fixtures/<sample&story>.png"
    summary["palette"][0]["name"] = "<blue & steel>"
    summary["palette"][0]["label"] = "<dark>"

    html = render_html_report(summary, title="<Palette & Story>")

    assert "&lt;Palette &amp; Story&gt;" in html
    assert "sample&quot;&gt;&lt;script&gt;.png" in html
    assert "fixtures/&lt;sample&amp;story&gt;.png" in html
    assert "&lt;blue &amp; steel&gt;" in html
    assert "&lt;dark&gt;" in html
    assert "<script>" not in html
    assert "<blue & steel>" not in html


def test_html_report_cards_include_contrast_guidance() -> None:
    html = render_html_report(sample_summary())

    assert "Best readable text</dt>" in html
    assert "Use white text" in html
    assert "Use black text" in html
    assert "Contrast ratio</dt>" in html
    assert "WCAG AA for normal text" in html
    assert "Relative luminance</dt>" in html


def test_html_report_includes_color_names_only_when_present() -> None:
    unnamed_html = render_html_report(sample_summary())
    named_html = render_html_report(named_summary())

    assert "Common name" not in unnamed_html
    assert "Common name</dt>" in named_html
    assert "blue</dd>" in named_html
    assert "gray</dd>" in named_html


def test_write_html_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "story.html"

    write_html_report(sample_summary(), output, title="Palette Story")

    assert output.read_text(encoding="utf-8").startswith("<!doctype html>\n")


def test_write_css_report_creates_deterministic_custom_properties(
    tmp_path: Path,
) -> None:
    output = tmp_path / "nested" / "palette.css"

    write_css_report(sample_summary(), output)

    assert output.read_text(encoding="utf-8") == (
        "/* Generated by swatch-story. */\n"
        ":root {\n"
        "  --swatch-story-color-1: #112233;\n"
        "  --swatch-story-color-1-rgb: 17, 34, 51;\n"
        "  --swatch-story-color-1-text: white;\n"
        "  --swatch-story-color-2: #eeeeee;\n"
        "  --swatch-story-color-2-rgb: 238, 238, 238;\n"
        "  --swatch-story-color-2-text: black;\n"
        "}\n"
    )


def test_gpl_report_renders_deterministic_gimp_palette() -> None:
    gpl = render_gpl_report(named_summary(), title="  Palette\nStory\tExport  ")

    assert gpl == (
        "GIMP Palette\n"
        "Name: Palette Story Export\n"
        "Columns: 2\n"
        "# Generated by swatch-story.\n"
        " 17  34  51 #112233 blue\n"
        "238 238 238 #eeeeee gray\n"
    )


def test_write_gpl_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "palette.gpl"

    write_gpl_report(sample_summary(), output, title="Palette Story")

    assert output.read_text(encoding="utf-8").startswith("GIMP Palette\n")


def test_markdown_report_renders_portable_palette_table() -> None:
    markdown = render_markdown_report(sample_summary(), title="Palette <Story>")

    assert markdown == (
        "# Palette &lt;Story&gt;\n"
        "\n"
        "Source: `sample.png`  \n"
        "Size: 2 x 1 px  \n"
        "Colors: 2\n"
        "\n"
        "| Rank | Color | RGB | Percent | Luminance | Text | Label |\n"
        "| ---: | --- | --- | ---: | ---: | --- | --- |\n"
        "| 1 | `#112233` | `17, 34, 51` | 50.0% | 0.015 | white | dark |\n"
        "| 2 | `#eeeeee` | `238, 238, 238` | 50.0% | 0.855 | black | light |\n"
        "\n"
    )


def test_markdown_report_includes_color_names_only_when_present() -> None:
    unnamed_markdown = render_markdown_report(sample_summary())
    named_markdown = render_markdown_report(named_summary())

    assert "| Rank | Color | RGB | Percent | Luminance | Text | Label |" in (
        unnamed_markdown
    )
    assert "| Rank | Color | Name | RGB | Percent | Luminance | Text | Label |" in (
        named_markdown
    )
    assert "| 1 | `#112233` | blue | `17, 34, 51` |" in named_markdown


def test_write_markdown_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "story.md"

    write_markdown_report(sample_summary(), output, title="Palette Story")

    assert output.read_text(encoding="utf-8").startswith("# Palette Story\n")
