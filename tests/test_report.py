import json
import struct
from pathlib import Path

import pytest
from PIL import Image

import swatch_story.report as report
from swatch_story.report import (
    render_ase_report,
    render_batch_html_report,
    render_batch_markdown_report,
    render_csv_report,
    render_gpl_report,
    render_html_report,
    render_markdown_report,
    render_svg_report,
    render_text_report,
    render_wcag_audit_report,
    write_ase_report,
    write_batch_html_report,
    write_batch_markdown_report,
    write_css_report,
    write_csv_report,
    write_gpl_report,
    write_html_report,
    write_html_thumbnail,
    write_json_report,
    write_markdown_report,
    write_svg_report,
    write_text_report,
    write_wcag_audit_report,
)


def sample_summary() -> dict:
    return {
        "source": "sample.png",
        "source_path": "fixtures/sample.png",
        "size": {"width": 2, "height": 1},
        "settings": {
            "colors": 2,
            "sample_step": 1,
            "cluster_distance": 0,
            "cluster_space": "rgb",
            "color_names": False,
        },
        "palette": [
            {
                "rank": 1,
                "hex": "#112233",
                "rgb": [17, 34, 51],
                "count": 1,
                "percent": 50.0,
                "luminance": 0.015,
                "contrast_with_black": 1.3,
                "contrast_with_white": 16.15,
                "best_text_color": "white",
                "label": "color-1",
            },
            {
                "rank": 2,
                "hex": "#eeeeee",
                "rgb": [238, 238, 238],
                "count": 1,
                "percent": 50.0,
                "luminance": 0.855,
                "contrast_with_black": 18.1,
                "contrast_with_white": 1.16,
                "best_text_color": "black",
                "label": "color-2",
            },
        ],
    }


def named_summary() -> dict:
    summary = sample_summary()
    summary["settings"]["color_names"] = True
    summary["palette"][0]["name"] = "blue"
    summary["palette"][1]["name"] = "gray"
    return summary


def second_sample_summary() -> dict:
    summary = sample_summary()
    summary["source"] = "second | sample <draft>.png"
    summary["source_path"] = "fixtures/second | sample <draft>.png"
    summary["size"] = {"width": 1, "height": 2}
    summary["palette"] = [
        {
            "rank": 1,
            "hex": "#ff0000",
            "rgb": [255, 0, 0],
            "count": 2,
            "percent": 100.0,
            "luminance": 0.213,
            "contrast_with_black": 5.26,
            "contrast_with_white": 4.0,
            "best_text_color": "black",
            "label": "color-1",
        }
    ]
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
    assert first_name == "color-1 blue"
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
    assert second_name == "color-2 gray"
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
    assert swatch_name == "color-1 steel blue ink"
    assert fallback_name == "color-2"


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


def test_write_json_report_adds_stable_schema_version_without_mutating_input(
    tmp_path: Path,
) -> None:
    output = tmp_path / "story.json"
    summary = sample_summary()

    write_json_report(summary, output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert "schema_version" not in summary


def test_write_json_report_applies_requested_precision(tmp_path: Path) -> None:
    output = tmp_path / "story.json"

    write_json_report(sample_summary(), output, precision=2)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["palette"][0]["percent"] == 50.0
    assert data["palette"][0]["luminance"] == 0.01
    assert data["palette"][0]["contrast_with_black"] == 1.3
    assert data["palette"][0]["contrast_with_white"] == 16.15
    assert data["palette"][1]["luminance"] == 0.85
    assert data["palette"][1]["contrast_with_black"] == 18.1
    assert data["palette"][1]["contrast_with_white"] == 1.16


def test_write_tokens_report_creates_design_token_json(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "tokens.json"

    report.write_tokens_report(sample_summary(), output, title="Product Palette")

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data == {
        "$schema": "https://design-tokens.github.io/community-group/format/",
        "source": "sample.png",
        "title": "Product Palette",
        "color": {
            "color-1": {
                "$type": "color",
                "$value": "#112233",
                "description": (
                    "Rank 1 color covering 50.0% of sampled pixels. "
                    "Use white text for readable contrast."
                ),
                "extensions": {
                    "swatchStory": {
                        "rank": 1,
                        "rgb": [17, 34, 51],
                        "percent": 50.0,
                        "luminance": 0.015,
                        "contrastWithBlack": 1.3,
                        "contrastWithWhite": 16.15,
                        "bestTextColor": "white",
                    }
                },
            },
            "color-2": {
                "$type": "color",
                "$value": "#eeeeee",
                "description": (
                    "Rank 2 color covering 50.0% of sampled pixels. "
                    "Use black text for readable contrast."
                ),
                "extensions": {
                    "swatchStory": {
                        "rank": 2,
                        "rgb": [238, 238, 238],
                        "percent": 50.0,
                        "luminance": 0.855,
                        "contrastWithBlack": 18.1,
                        "contrastWithWhite": 1.16,
                        "bestTextColor": "black",
                    }
                },
            },
        },
    }


def test_write_tokens_report_applies_requested_precision(tmp_path: Path) -> None:
    output = tmp_path / "tokens.json"

    report.write_tokens_report(sample_summary(), output, precision=1)

    tokens = json.loads(output.read_text(encoding="utf-8"))["color"]
    first = tokens["color-1"]
    assert first["description"] == (
        "Rank 1 color covering 50.0% of sampled pixels. "
        "Use white text for readable contrast."
    )
    assert first["extensions"]["swatchStory"]["luminance"] == 0.0
    assert first["extensions"]["swatchStory"]["contrastWithWhite"] == 16.1
    assert tokens["color-2"]["extensions"]["swatchStory"]["luminance"] == 0.9


def test_csv_report_renders_stable_table_with_blank_missing_names() -> None:
    summary = sample_summary()
    summary["palette"][0]["label"] = "dark, cool"
    summary["palette"][1]["name"] = "pale gray"

    assert render_csv_report(summary) == (
        "rank,hex,r,g,b,count,percent,luminance,contrast_with_black,"
        "contrast_with_white,best_text_color,label,name\r\n"
        '1,#112233,17,34,51,1,50.0,0.015,1.3,16.15,white,"dark, cool",\r\n'
        "2,#eeeeee,238,238,238,1,50.0,0.855,18.1,1.16,black,color-2,pale gray\r\n"
    )


def test_csv_report_applies_requested_precision() -> None:
    assert render_csv_report(sample_summary(), precision=1) == (
        "rank,hex,r,g,b,count,percent,luminance,contrast_with_black,"
        "contrast_with_white,best_text_color,label,name\r\n"
        "1,#112233,17,34,51,1,50.0,0.0,1.3,16.1,white,color-1,\r\n"
        "2,#eeeeee,238,238,238,1,50.0,0.9,18.1,1.2,black,color-2,\r\n"
    )


def test_write_csv_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "story.csv"

    write_csv_report(named_summary(), output)

    assert output.read_text(encoding="utf-8") == (
        "rank,hex,r,g,b,count,percent,luminance,contrast_with_black,"
        "contrast_with_white,best_text_color,label,name\n"
        "1,#112233,17,34,51,1,50.0,0.015,1.3,16.15,white,color-1,blue\n"
        "2,#eeeeee,238,238,238,1,50.0,0.855,18.1,1.16,black,color-2,gray\n"
    )


def test_svg_report_renders_standalone_swatch_sheet_with_metadata() -> None:
    svg = render_svg_report(named_summary(), title="Palette Story", precision=1)

    assert svg.startswith('<?xml version="1.0" encoding="UTF-8"?>\n')
    assert svg.endswith("\n")
    assert '<svg xmlns="http://www.w3.org/2000/svg"' in svg
    assert '<title id="title">Palette Story</title>' in svg
    assert '<desc id="desc">Palette swatch sheet for sample.png</desc>' in svg
    assert "Source: sample.png" in svg
    assert "Image: 2 x 1 px" in svg
    assert (
        "Settings: colors 2; sample step 1; sample limit unknown; "
        "cluster distance 0; cluster space rgb; sort frequency; "
        "ignored color none; names included"
    ) in svg
    assert 'fill="#112233"' in svg
    assert 'fill="#eeeeee"' in svg
    assert "#112233" in svg
    assert "blue" in svg
    assert "50.0%" in svg
    assert "Luminance 0.0" in svg
    assert "Contrast black 1.3:1; white 16.1:1" in svg
    assert "Label color-1" in svg
    assert "Text white" in svg


def test_svg_report_escapes_user_derived_text_without_embedding_source() -> None:
    summary = sample_summary()
    summary["source"] = 'sample"><script>.png'
    summary["source_path"] = "fixtures/<sample&story>.png"
    summary["palette"][0]["name"] = "<blue & steel>"
    summary["palette"][0]["label"] = "<dark>"

    svg = render_svg_report(summary, title="<Palette & Story>")

    assert "&lt;Palette &amp; Story&gt;" in svg
    assert "sample&quot;&gt;&lt;script&gt;.png" in svg
    assert "fixtures/&lt;sample&amp;story&gt;.png" not in svg
    assert "&lt;blue &amp; steel&gt;" in svg
    assert "Label &lt;dark&gt;" in svg
    assert "<script>" not in svg
    assert "<image" not in svg
    assert "href=" not in svg


def test_write_svg_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "story.svg"

    write_svg_report(sample_summary(), output, title="Palette Story")

    svg = output.read_text(encoding="utf-8")
    assert svg.startswith('<?xml version="1.0" encoding="UTF-8"?>\n')
    assert '<title id="title">Palette Story</title>' in svg


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
    assert "Cluster distance</dt>" in html
    assert "0</dd>" in html
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
    assert "Black contrast</dt>" in html
    assert "White contrast</dt>" in html
    assert "WCAG AA for normal text" in html
    assert "Relative luminance</dt>" in html


def test_html_report_applies_requested_precision() -> None:
    html = render_html_report(sample_summary(), precision=2)

    assert "<dd>50.00% of sampled pixels</dd>" in html
    assert "<dd>0.01</dd>" in html
    assert "<dd>1.30:1</dd>" in html
    assert "<dd>16.15:1</dd>" in html
    assert "<dd>0.85</dd>" in html


def test_html_report_includes_color_names_only_when_present() -> None:
    unnamed_html = render_html_report(sample_summary())
    named_html = render_html_report(named_summary())

    assert "Common name" not in unnamed_html
    assert "Common name</dt>" in named_html
    assert "blue</dd>" in named_html
    assert "gray</dd>" in named_html


def test_html_report_includes_escaped_thumbnail_preview() -> None:
    html = render_html_report(
        sample_summary(),
        thumbnail_href='thumbs/source "one&two<.png',
    )

    assert '<section class="source-preview"' in html
    assert 'aria-label="Source image preview"' in html
    assert "Source preview</h2>" in html
    assert (
        '<img src="thumbs/source &quot;one&amp;two&lt;.png" '
        'alt="Thumbnail preview of sample.png"'
    ) in html
    assert 'src="thumbs/source "one&two<.png"' not in html
    assert "<.png" not in html


def test_write_html_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "story.html"

    write_html_report(sample_summary(), output, title="Palette Story")

    assert output.read_text(encoding="utf-8").startswith("<!doctype html>\n")


def test_write_html_report_uses_thumbnail_href(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "story.html"

    write_html_report(
        sample_summary(),
        output,
        title="Palette Story",
        thumbnail_href="../thumbs/story-thumb.png",
    )

    html = output.read_text(encoding="utf-8")
    assert '<img src="../thumbs/story-thumb.png"' in html
    assert "Thumbnail preview of sample.png" in html


def test_batch_html_report_combines_images_with_escaped_cards() -> None:
    first = sample_summary()
    first["source"] = 'sample"><script>.png'
    first["source_path"] = "fixtures/<sample&story>.png"
    first["palette"][0]["name"] = "<blue & steel>"

    html = render_batch_html_report(
        [first, second_sample_summary()],
        title="<Team & Review>",
        precision=1,
    )

    assert html.startswith("<!doctype html>\n")
    assert "<title>&lt;Team &amp; Review&gt;</title>" in html
    assert "<h1>&lt;Team &amp; Review&gt;</h1>" in html
    assert "2 audited images" in html
    assert "sample&quot;&gt;&lt;script&gt;.png" in html
    assert "fixtures/&lt;sample&amp;story&gt;.png" in html
    assert "&lt;blue &amp; steel&gt;" in html
    assert "second | sample &lt;draft&gt;.png" in html
    assert "Dominant colors</dt>" in html
    assert "#ff0000 100.0%" in html
    assert "Use black text; contrast black 5.3:1; white 4.0:1" in html
    assert "<script>" not in html
    assert "<Team & Review>" not in html


def test_write_batch_html_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "batch.html"

    write_batch_html_report(
        [sample_summary(), second_sample_summary()],
        output,
        title="Team Review",
    )

    assert output.read_text(encoding="utf-8").startswith("<!doctype html>\n")


def test_write_html_thumbnail_preserves_aspect_ratio_and_bounds(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "source.png"
    Image.new("RGB", (640, 160), (17, 34, 51)).save(image_path)
    thumbnail_path = tmp_path / "nested" / "thumb.png"

    write_html_thumbnail(image_path, thumbnail_path, max_dimension=320)

    with Image.open(thumbnail_path) as thumbnail:
        assert thumbnail.size == (320, 80)
        assert thumbnail.mode == "RGB"


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
        "  --swatch-story-color-1-contrast-black: 1.3;\n"
        "  --swatch-story-color-1-contrast-white: 16.15;\n"
        "  --swatch-story-color-1-text: white;\n"
        "  --swatch-story-color-2: #eeeeee;\n"
        "  --swatch-story-color-2-rgb: 238, 238, 238;\n"
        "  --swatch-story-color-2-contrast-black: 18.1;\n"
        "  --swatch-story-color-2-contrast-white: 1.16;\n"
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
        " 17  34  51 color-1 blue\n"
        "238 238 238 color-2 gray\n"
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
        "Colors: 2  \n"
        "Cluster distance: 0  \n"
        "Cluster space: rgb\n"
        "\n"
        "| Rank | Color | RGB | Percent | Luminance | Contrast | Text | Label |\n"
        "| ---: | --- | --- | ---: | ---: | --- | --- | --- |\n"
        "| 1 | `#112233` | `17, 34, 51` | 50.0% | 0.015 | "
        "black 1.3:1; white 16.15:1 | white | color-1 |\n"
        "| 2 | `#eeeeee` | `238, 238, 238` | 50.0% | 0.855 | "
        "black 18.1:1; white 1.16:1 | black | color-2 |\n"
        "\n"
    )


def test_markdown_report_applies_requested_precision() -> None:
    markdown = render_markdown_report(sample_summary(), precision=0)

    assert (
        "| 1 | `#112233` | `17, 34, 51` | 50% | 0 | "
        "black 1:1; white 16:1 | white | color-1 |"
    ) in markdown
    assert (
        "| 2 | `#eeeeee` | `238, 238, 238` | 50% | 1 | "
        "black 18:1; white 1:1 | black | color-2 |"
    ) in markdown


def test_markdown_report_includes_color_names_only_when_present() -> None:
    unnamed_markdown = render_markdown_report(sample_summary())
    named_markdown = render_markdown_report(named_summary())

    assert "| Rank | Color | RGB | Percent | Luminance | Contrast | Text | Label |" in (
        unnamed_markdown
    )
    assert (
        "| Rank | Color | Name | RGB | Percent | Luminance | Contrast | Text | Label |"
        in (named_markdown)
    )
    assert "| 1 | `#112233` | blue | `17, 34, 51` |" in named_markdown


def test_write_markdown_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "story.md"

    write_markdown_report(sample_summary(), output, title="Palette Story")

    assert output.read_text(encoding="utf-8").startswith("# Palette Story\n")


def test_batch_markdown_report_combines_images_with_escaped_metadata() -> None:
    first = sample_summary()
    first["source"] = "sample <one>.png"
    first["source_path"] = "fixtures/sample <one>.png"

    markdown = render_batch_markdown_report(
        [first, second_sample_summary()],
        title="Team <Palette> Review",
        precision=1,
    )

    assert markdown.startswith("# Team &lt;Palette&gt; Review\n")
    assert "Images: 2" in markdown
    assert (
        "Settings: colors 2; sample step 1; sample limit unknown; "
        "cluster distance 0; cluster space rgb; sort frequency; "
        "ignored color none; names not included"
    ) in markdown
    assert "## sample &lt;one&gt;.png" in markdown
    assert "Source path: `fixtures/sample &lt;one&gt;.png`" in markdown
    assert "Dominant colors: `#112233` 50.0%, `#eeeeee` 50.0%" in markdown
    assert "### second \\| sample &lt;draft&gt;.png" not in markdown
    assert "## second \\| sample &lt;draft&gt;.png" in markdown
    assert "| 1 | `#ff0000` | `255, 0, 0` | 100.0% | 0.2 |" in markdown
    assert "Use black text; contrast black 5.3:1; white 4.0:1" in markdown
    assert "<script>" not in markdown


def test_write_batch_markdown_report_creates_parent_directories(
    tmp_path: Path,
) -> None:
    output = tmp_path / "nested" / "batch.md"

    write_batch_markdown_report(
        [sample_summary(), second_sample_summary()],
        output,
        title="Team Review",
    )

    assert output.read_text(encoding="utf-8").startswith("# Team Review\n")


def test_text_report_renders_paste_friendly_palette_sheet() -> None:
    summary = named_summary()
    summary["settings"]["ignore_color"] = "#ffffff"

    text = render_text_report(summary, title="  Palette\nStory\tExport  ")

    assert text == (
        "Palette Story Export\n"
        "\n"
        "Source: sample.png\n"
        "Image size: 2 x 1 px\n"
        "Settings: colors 2; sample step 1; sample limit unknown; "
        "cluster distance 0; cluster space rgb; sort frequency; "
        "ignored color #ffffff; names included\n"
        "\n"
        "Swatches:\n"
        "1. #112233 | rgb(17, 34, 51) | 50.0% | color-1 | "
        "contrast black 1.3:1 white 16.15:1 | text white | name blue\n"
        "2. #eeeeee | rgb(238, 238, 238) | 50.0% | color-2 | "
        "contrast black 18.1:1 white 1.16:1 | text black | name gray\n"
    )


def test_text_report_applies_requested_precision() -> None:
    text = render_text_report(sample_summary(), precision=2)

    assert (
        "1. #112233 | rgb(17, 34, 51) | 50.00% | color-1 | "
        "contrast black 1.30:1 white 16.15:1 | text white\n"
    ) in text
    assert (
        "2. #eeeeee | rgb(238, 238, 238) | 50.00% | color-2 | "
        "contrast black 18.10:1 white 1.16:1 | text black\n"
    ) in text


def test_text_report_sanitizes_multiline_title_source_label_and_names() -> None:
    summary = named_summary()
    summary["source"] = "sample\nstory.png"
    summary["palette"][0]["label"] = "dark\ncool\tink"
    summary["palette"][0]["name"] = "steel\nblue\tink"

    text = render_text_report(summary, title="Title\nName")

    assert text.startswith("Title Name\n")
    assert "Source: sample story.png\n" in text
    assert (
        "1. #112233 | rgb(17, 34, 51) | 50.0% | dark cool ink | "
        "contrast black 1.3:1 white 16.15:1 | text white | name steel blue ink\n"
    ) in text


def test_write_text_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "story.txt"

    write_text_report(sample_summary(), output, title="Palette Story")

    assert output.read_text(encoding="utf-8").startswith("Palette Story\n")


def test_wcag_audit_report_renders_thresholds_and_recommendations() -> None:
    audit = render_wcag_audit_report(sample_summary(), title="Palette Audit")

    assert audit == (
        "# Palette Audit WCAG Audit\n"
        "\n"
        "Source: `sample.png`  \n"
        "Source path: `fixtures/sample.png`  \n"
        "Image size: 2 x 1 px  \n"
        "Settings: colors 2; sample step 1; sample limit unknown; "
        "cluster distance 0; cluster space rgb; sort frequency; "
        "ignored color none; names not included\n"
        "\n"
        "Thresholds: normal AA >= 4.5, large AA >= 3.0, "
        "normal AAA >= 7.0, large AAA >= 4.5.\n"
        "\n"
        "| Rank | Color | Label | Preferred text | Black text readiness | "
        "White text readiness | Recommendation |\n"
        "| ---: | --- | --- | --- | --- | --- | --- |\n"
        "| 1 | `#112233` | color-1 | white | No WCAG text pass | "
        "AA normal, AA large, AAA normal, AAA large | "
        "Use white text; passes AA normal, AA large, AAA normal, AAA large. |\n"
        "| 2 | `#eeeeee` | color-2 | black | "
        "AA normal, AA large, AAA normal, AAA large | No WCAG text pass | "
        "Use black text; passes AA normal, AA large, AAA normal, AAA large. |\n"
        "\n"
    )


def test_wcag_audit_report_escapes_user_derived_markdown_cells() -> None:
    summary = sample_summary()
    summary["source"] = "source|name\nnext.png"
    summary["source_path"] = "fixtures/<source|name>.png"
    summary["palette"][0]["label"] = "brand|ink"
    summary["palette"][0]["name"] = "blue|steel"

    audit = render_wcag_audit_report(summary, title="Audit | <Story>")

    assert "# Audit \\| &lt;Story&gt; WCAG Audit" in audit
    assert "Source: `source\\|name<br>next.png`" in audit
    assert "Source path: `fixtures/&lt;source\\|name&gt;.png`" in audit
    assert "| 1 | `#112233` | brand\\|ink, blue\\|steel | white |" in audit
    assert "| brand|ink, blue|steel |" not in audit


def test_write_wcag_audit_report_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "audit.md"

    write_wcag_audit_report(sample_summary(), output, title="Palette Audit")

    assert output.read_text(encoding="utf-8").startswith("# Palette Audit WCAG Audit\n")
