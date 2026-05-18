import json
import struct
import sys
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


def test_cli_rejects_html_thumbnail_without_html(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (255, 0, 0)).save(image_path)

    with pytest.raises(SystemExit) as exc_info:
        main([str(image_path), "--html-thumbnail", str(tmp_path / "thumb.png")])

    assert exc_info.value.code == 2
    assert "--html-thumbnail requires --html" in capsys.readouterr().err


def test_cli_writes_html_report_with_relative_thumbnail(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "source & image.png"
    Image.new("RGB", (80, 40), (17, 34, 51)).save(image_path)
    html_path = tmp_path / "reports" / "story.html"
    thumbnail_path = tmp_path / "reports" / "assets" / "source-thumb.png"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--html",
            str(html_path),
            "--html-thumbnail",
            str(thumbnail_path),
        ]
    )

    assert exit_code == 0
    with Image.open(thumbnail_path) as thumbnail:
        assert thumbnail.size == (80, 40)
    html = html_path.read_text(encoding="utf-8")
    assert '<section class="source-preview"' in html
    assert 'aria-label="Source image preview"' in html
    assert '<img src="assets/source-thumb.png"' in html
    assert "Thumbnail preview of source &amp; image.png" in html
    assert "#112233" in capsys.readouterr().out


def test_cli_writes_wcag_audit_report(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(17, 34, 51), (238, 238, 238)])
    image.save(image_path)
    audit_path = tmp_path / "nested" / "audit.md"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--title",
            "CLI Audit",
            "--wcag-audit",
            str(audit_path),
        ]
    )

    assert exit_code == 0
    audit = audit_path.read_text(encoding="utf-8")
    assert "# CLI Audit WCAG Audit" in audit
    assert "Source: `cli.png`" in audit
    assert "Settings: colors 2; sample step 1;" in audit
    assert "Thresholds: normal AA >= 4.5" in audit
    assert "| 1 | `#112233` | color-1 | white | No WCAG text pass |" in audit
    assert "| 2 | `#eeeeee` | color-2 | black |" in audit
    assert "#112233" in capsys.readouterr().out


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
    assert [entry["contrast_with_black"] for entry in summary["palette"]] == [5.3, 2.4]
    assert [entry["contrast_with_white"] for entry in summary["palette"]] == [4.0, 8.6]
    assert ",66.7,0.2,5.3,4.0," in csv_path.read_text(encoding="utf-8")
    assert "| 66.7% | 0.2 | black 5.3:1; white 4.0:1 |" in (
        markdown_path.read_text(encoding="utf-8")
    )
    assert "| 66.7% |" in text_path.read_text(encoding="utf-8")
    assert "contrast black 5.3:1 white 4.0:1" in text_path.read_text(encoding="utf-8")
    assert "<dd>66.7% of sampled pixels</dd>" in html_path.read_text(encoding="utf-8")
    console = capsys.readouterr().out
    assert "66.7%" in console
    assert "contrast:black 5.3:1 white 4.0:1" in console


def test_cli_writes_design_tokens_with_precision_and_label_prefix(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (3, 1))
    image.putdata([(255, 0, 0), (255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    tokens_path = tmp_path / "nested" / "tokens.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--precision",
            "1",
            "--label-prefix",
            "brand",
            "--tokens",
            str(tokens_path),
            "--title",
            "CLI Tokens",
        ]
    )

    assert exit_code == 0
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    assert tokens["source"] == "cli.png"
    assert tokens["title"] == "CLI Tokens"
    assert list(tokens["color"]) == ["brand-1", "brand-2"]
    first = tokens["color"]["brand-1"]
    assert first["$type"] == "color"
    assert first["$value"] == "#ff0000"
    assert first["description"] == (
        "Rank 1 color covering 66.7% of sampled pixels. "
        "Use black text for readable contrast."
    )
    assert first["extensions"]["swatchStory"]["percent"] == 66.7
    assert first["extensions"]["swatchStory"]["luminance"] == 0.2
    assert first["extensions"]["swatchStory"]["contrastWithBlack"] == 5.3
    assert first["extensions"]["swatchStory"]["contrastWithWhite"] == 4.0
    assert first["extensions"]["swatchStory"]["bestTextColor"] == "black"
    assert "brand-1" in capsys.readouterr().out


def test_cli_main_reads_preset_and_cli_colors_override_wins(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (3, 1))
    image.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    image.save(image_path)
    preset_path = tmp_path / "preset.json"
    preset_path.write_text(
        json.dumps(
            {
                "colors": 2,
                "sample_step": 1,
                "matte": "000000",
                "cluster_space": "lab",
                "names": True,
                "precision": 1,
                "label_prefix": "brand",
                "title": "Preset Story",
            }
        ),
        encoding="utf-8",
    )
    json_path = tmp_path / "story.json"
    tokens_path = tmp_path / "tokens.json"

    exit_code = main(
        [
            str(image_path),
            "--preset",
            str(preset_path),
            "--colors",
            "3",
            "--json",
            str(json_path),
            "--tokens",
            str(tokens_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert summary["settings"]["colors"] == 3
    assert summary["settings"]["sample_step"] == 1
    assert summary["settings"]["matte"] == "#000000"
    assert summary["settings"]["cluster_space"] == "lab"
    assert summary["settings"]["color_names"] is True
    assert [entry["label"] for entry in summary["palette"]] == [
        "brand-1",
        "brand-2",
        "brand-3",
    ]
    assert [entry["percent"] for entry in summary["palette"]] == [33.3, 33.3, 33.3]
    assert all("name" in entry for entry in summary["palette"])
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    assert tokens["title"] == "Preset Story"
    assert list(tokens["color"]) == ["brand-1", "brand-2", "brand-3"]
    assert "brand-1" in capsys.readouterr().out


def test_cli_main_reads_preset_when_called_from_sys_argv(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (2, 1), (255, 0, 0)).save(image_path)
    preset_path = tmp_path / "preset.json"
    preset_path.write_text(
        json.dumps({"colors": 2, "sample_step": 1}), encoding="utf-8"
    )
    json_path = tmp_path / "story.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "swatch-story",
            str(image_path),
            "--preset",
            str(preset_path),
            "--json",
            str(json_path),
        ],
    )

    exit_code = main()

    assert exit_code == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["settings"]["colors"] == 2
    assert "#ff0000" in capsys.readouterr().out


def test_cli_uses_default_design_token_labels(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    json_path = tmp_path / "story.json"
    css_path = tmp_path / "story.css"

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
    assert [entry["label"] for entry in summary["palette"]] == ["color-1", "color-2"]
    css = css_path.read_text(encoding="utf-8")
    assert "--swatch-story-color-1:" in css
    assert "--swatch-story-color-2:" in css
    console = capsys.readouterr().out
    assert "color-1" in console
    assert "color-2" in console


def test_cli_label_prefix_updates_all_label_outputs(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    json_path = tmp_path / "story.json"
    css_path = tmp_path / "story.css"
    csv_path = tmp_path / "story.csv"
    markdown_path = tmp_path / "story.md"
    text_path = tmp_path / "story.txt"
    html_path = tmp_path / "story.html"
    svg_path = tmp_path / "story.svg"
    gpl_path = tmp_path / "story.gpl"
    ase_path = tmp_path / "story.ase"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--label-prefix",
            "brand",
            "--json",
            str(json_path),
            "--css",
            str(css_path),
            "--csv",
            str(csv_path),
            "--markdown",
            str(markdown_path),
            "--text",
            str(text_path),
            "--html",
            str(html_path),
            "--svg",
            str(svg_path),
            "--gpl",
            str(gpl_path),
            "--ase",
            str(ase_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert [entry["label"] for entry in summary["palette"]] == ["brand-1", "brand-2"]
    assert "--swatch-story-brand-1:" in css_path.read_text(encoding="utf-8")
    assert ",brand-1," in csv_path.read_text(encoding="utf-8")
    assert "| brand-1 |" in markdown_path.read_text(encoding="utf-8")
    assert "| brand-1 |" in text_path.read_text(encoding="utf-8")
    assert "#1 - brand-1" in html_path.read_text(encoding="utf-8")
    assert "Label brand-1" in svg_path.read_text(encoding="utf-8")
    assert "brand-1" in gpl_path.read_text(encoding="utf-8")
    assert "brand-1" in _ase_strings(ase_path.read_bytes())
    console = capsys.readouterr().out
    assert "brand-1" in console
    assert "brand-2" in console


@pytest.mark.parametrize("prefix", ["", "Brand", "brand_name", "brand name", "brand!"])
def test_cli_rejects_invalid_label_prefix(tmp_path: Path, capsys, prefix: str) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    with pytest.raises(SystemExit) as exc_info:
        main([str(image_path), "--label-prefix", prefix])

    assert exc_info.value.code == 2
    error = capsys.readouterr().err
    assert "--label-prefix" in error
    assert "lowercase letters, numbers, and hyphens" in error


def test_cli_compare_does_not_accept_label_prefix(tmp_path: Path, capsys) -> None:
    before_path = tmp_path / "before.png"
    after_path = tmp_path / "after.png"
    Image.new("RGB", (1, 1), (255, 0, 0)).save(before_path)
    Image.new("RGB", (1, 1), (0, 0, 255)).save(after_path)

    with pytest.raises(SystemExit) as exc_info:
        main(["compare", str(before_path), str(after_path), "--label-prefix", "brand"])

    assert exc_info.value.code == 2
    assert "unrecognized arguments: --label-prefix brand" in capsys.readouterr().err


def test_cli_compare_does_not_accept_tokens(tmp_path: Path, capsys) -> None:
    before_path = tmp_path / "before.png"
    after_path = tmp_path / "after.png"
    Image.new("RGB", (1, 1), (255, 0, 0)).save(before_path)
    Image.new("RGB", (1, 1), (0, 0, 255)).save(after_path)

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "compare",
                str(before_path),
                str(after_path),
                "--tokens",
                str(tmp_path / "tokens.json"),
            ]
        )

    assert exc_info.value.code == 2
    assert "unrecognized arguments: --tokens" in capsys.readouterr().err


def test_cli_batch_requires_at_least_two_images(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "one.png"
    Image.new("RGB", (1, 1), (255, 0, 0)).save(image_path)

    with pytest.raises(SystemExit) as exc_info:
        main(["batch", str(image_path), "--markdown", str(tmp_path / "batch.md")])

    assert exc_info.value.code == 2
    assert "at least two image paths are required" in capsys.readouterr().err


def test_cli_batch_requires_an_output_path(tmp_path: Path, capsys) -> None:
    first_path = tmp_path / "one.png"
    second_path = tmp_path / "two.png"
    Image.new("RGB", (1, 1), (255, 0, 0)).save(first_path)
    Image.new("RGB", (1, 1), (0, 0, 255)).save(second_path)

    with pytest.raises(SystemExit) as exc_info:
        main(["batch", str(first_path), str(second_path)])

    assert exc_info.value.code == 2
    assert "at least one of --markdown or --html is required" in capsys.readouterr().err


def test_cli_batch_writes_markdown_and_html_reports(tmp_path: Path, capsys) -> None:
    first_path = tmp_path / "one <draft>.png"
    first = Image.new("RGB", (2, 1))
    first.putdata([(255, 0, 0), (0, 0, 255)])
    first.save(first_path)
    second_path = tmp_path / "two & final.png"
    Image.new("RGB", (1, 2), (17, 34, 51)).save(second_path)
    markdown_path = tmp_path / "reports" / "batch.md"
    html_path = tmp_path / "reports" / "batch.html"

    exit_code = main(
        [
            "batch",
            str(first_path),
            str(second_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--names",
            "--precision",
            "1",
            "--title",
            "Team <Review>",
            "--markdown",
            str(markdown_path),
            "--html",
            str(html_path),
        ]
    )

    assert exit_code == 0
    markdown = markdown_path.read_text(encoding="utf-8")
    assert markdown.startswith("# Team &lt;Review&gt;\n")
    assert "## one &lt;draft&gt;.png" in markdown
    assert "## two &amp; final.png" in markdown
    assert "Settings: colors 2; sample step 1;" in markdown
    assert "`#0000ff` 50.0%" in markdown
    assert "`#112233` 100.0%" in markdown
    assert "name:" not in markdown
    html = html_path.read_text(encoding="utf-8")
    assert "<h1>Team &lt;Review&gt;</h1>" in html
    assert "one &lt;draft&gt;.png" in html
    assert "two &amp; final.png" in html
    assert "#112233 100.0%" in html
    console = capsys.readouterr().out
    assert f"Wrote batch report for 2 images to {markdown_path}, {html_path}" in console


def test_cli_batch_reads_preset_and_cli_colors_override_wins(
    tmp_path: Path, capsys
) -> None:
    first_path = tmp_path / "one.png"
    second_path = tmp_path / "two.png"
    first = Image.new("RGB", (3, 1))
    first.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    first.save(first_path)
    second = Image.new("RGB", (3, 1))
    second.putdata([(17, 34, 51), (68, 85, 102), (119, 136, 153)])
    second.save(second_path)
    preset_path = tmp_path / "preset.json"
    preset_path.write_text(
        json.dumps(
            {
                "colors": 2,
                "sample_step": 1,
                "names": True,
                "precision": 1,
                "title": "Preset Batch",
            }
        ),
        encoding="utf-8",
    )
    markdown_path = tmp_path / "batch.md"

    exit_code = main(
        [
            "batch",
            str(first_path),
            str(second_path),
            "--preset",
            str(preset_path),
            "--colors",
            "3",
            "--markdown",
            str(markdown_path),
        ]
    )

    assert exit_code == 0
    markdown = markdown_path.read_text(encoding="utf-8")
    assert markdown.startswith("# Preset Batch\n")
    assert "Settings: colors 3; sample step 1;" in markdown
    assert "names included" in markdown
    assert "`#ff0000` 33.3%" in markdown
    assert "red" in markdown
    assert (
        f"Wrote batch report for 2 images to {markdown_path}" in capsys.readouterr().out
    )


def test_cli_baseline_requires_an_output_path(tmp_path: Path, capsys) -> None:
    baseline_path = tmp_path / "baseline.png"
    candidate_path = tmp_path / "candidate.png"
    Image.new("RGB", (1, 1), (255, 0, 0)).save(baseline_path)
    Image.new("RGB", (1, 1), (0, 0, 255)).save(candidate_path)

    with pytest.raises(SystemExit) as exc_info:
        main(["baseline", str(baseline_path), str(candidate_path)])

    assert exc_info.value.code == 2
    assert (
        "at least one of --json, --markdown, --text, or --html is required"
        in capsys.readouterr().err
    )


def test_cli_baseline_writes_json_markdown_and_text_reports(
    tmp_path: Path, capsys
) -> None:
    baseline_path = tmp_path / "baseline <ref>.png"
    baseline = Image.new("RGB", (3, 1))
    baseline.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    baseline.save(baseline_path)
    stable_path = tmp_path / "stable.png"
    stable = Image.new("RGB", (3, 1))
    stable.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    stable.save(stable_path)
    drifted_path = tmp_path / "drifted & final.png"
    drifted = Image.new("RGB", (3, 1))
    drifted.putdata([(0, 255, 0), (17, 34, 51), (68, 85, 102)])
    drifted.save(drifted_path)
    json_path = tmp_path / "reports" / "baseline.json"
    markdown_path = tmp_path / "reports" / "baseline.md"
    text_path = tmp_path / "reports" / "baseline.txt"

    exit_code = main(
        [
            "baseline",
            str(baseline_path),
            str(stable_path),
            str(drifted_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--precision",
            "1",
            "--title",
            "Baseline <Review>",
            "--json",
            str(json_path),
            "--markdown",
            str(markdown_path),
            "--text",
            str(text_path),
        ]
    )

    assert exit_code == 0
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["schema"] == "swatch-story.baseline"
    assert data["title"] == "Baseline <Review>"
    assert data["baseline"]["source"] == "baseline <ref>.png"
    assert [candidate["source"]["source"] for candidate in data["candidates"]] == [
        "stable.png",
        "drifted & final.png",
    ]
    assert [candidate["rank"] for candidate in data["candidates"]] == [2, 1]
    assert [candidate["drift_score"] for candidate in data["candidates"]] == [0.0, 80.0]
    markdown = markdown_path.read_text(encoding="utf-8")
    assert markdown.startswith("# Baseline &lt;Review&gt;\n")
    assert "baseline &lt;ref&gt;.png" in markdown
    assert "| 1 | drifted &amp; final.png |" in markdown
    text = text_path.read_text(encoding="utf-8")
    assert text.startswith("Baseline <Review>\n")
    assert "1. drifted & final.png | drift 80.0%" in text
    assert (
        f"Wrote baseline report for 2 candidates to {json_path}, {markdown_path}, "
        f"{text_path}" in capsys.readouterr().out
    )


def test_cli_baseline_writes_html_report(tmp_path: Path, capsys) -> None:
    baseline_path = tmp_path / "baseline <ref>.png"
    Image.new("RGB", (1, 1), (255, 0, 0)).save(baseline_path)
    candidate_path = tmp_path / "candidate & final.png"
    Image.new("RGB", (1, 1), (0, 0, 255)).save(candidate_path)
    html_path = tmp_path / "reports" / "baseline.html"

    exit_code = main(
        [
            "baseline",
            str(baseline_path),
            str(candidate_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--title",
            "Baseline <Review>",
            "--html",
            str(html_path),
        ]
    )

    assert exit_code == 0
    html = html_path.read_text(encoding="utf-8")
    assert html.startswith("<!doctype html>\n")
    assert "Baseline &lt;Review&gt;" in html
    assert "baseline &lt;ref&gt;.png" in html
    assert "candidate &amp; final.png" in html
    assert '<th scope="col" class="sortable">Rank</th>' in html
    assert 'style="background: #0000ff"' in html
    assert f"Wrote baseline report for 1 candidates to {html_path}" in (
        capsys.readouterr().out
    )


def _ase_strings(data: bytes) -> list[str]:
    assert data[:4] == b"ASEF"
    block_count = struct.unpack_from(">I", data, 8)[0]
    offset = 12
    strings = []
    for _ in range(block_count):
        _block_type, block_length = struct.unpack_from(">HI", data, offset)
        offset += 6
        block_end = offset + block_length
        if block_length >= 2:
            length = struct.unpack_from(">H", data, offset)[0]
            string_end = offset + 2 + (length * 2)
            if string_end <= block_end:
                strings.append(data[offset + 2 : string_end - 2].decode("utf-16-be"))
        offset = block_end
    return strings


def test_cli_writes_svg_report_with_names_title_and_precision(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli <story>.png"
    image = Image.new("RGB", (3, 1))
    image.putdata([(255, 0, 0), (255, 0, 0), (0, 0, 255)])
    image.save(image_path)
    svg_path = tmp_path / "nested" / "story.svg"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--names",
            "--precision",
            "1",
            "--title",
            "<CLI & Story>",
            "--svg",
            str(svg_path),
        ]
    )

    assert exit_code == 0
    svg = svg_path.read_text(encoding="utf-8")
    assert svg.startswith('<?xml version="1.0" encoding="UTF-8"?>\n')
    assert "&lt;CLI &amp; Story&gt;" in svg
    assert "cli &lt;story&gt;.png" in svg
    assert "names included" in svg
    assert "red" in svg
    assert "66.7%" in svg
    assert "0.2" in svg
    assert "#ff0000" in capsys.readouterr().out


def test_cli_rejects_invalid_precision_with_argparse(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    with pytest.raises(SystemExit) as exc_info:
        main([str(image_path), "--precision", "7"])

    assert exc_info.value.code == 2
    assert "--precision must be between 0 and 6" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("preset_content", "expected"),
    [
        ('{"colors": 2, "unexpected": true}', "unknown preset key: unexpected"),
        ("[]", "preset must be a JSON object"),
    ],
)
def test_cli_rejects_invalid_preset_before_writing_outputs(
    tmp_path: Path, capsys, preset_content: str, expected: str
) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)
    preset_path = tmp_path / "preset.json"
    preset_path.write_text(preset_content, encoding="utf-8")
    json_path = tmp_path / "story.json"

    with pytest.raises(SystemExit) as exc_info:
        main([str(image_path), "--preset", str(preset_path), "--json", str(json_path)])

    assert exc_info.value.code == 2
    assert expected in capsys.readouterr().err
    assert not json_path.exists()


@pytest.mark.parametrize(
    ("preset_path", "expected"),
    [
        ("https://example.com/preset.json", "preset path must be a local file"),
        ("missing.json", "preset file not found"),
    ],
)
def test_cli_rejects_non_local_or_missing_preset_before_writing_outputs(
    tmp_path: Path, capsys, preset_path: str, expected: str
) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)
    json_path = tmp_path / "story.json"

    with pytest.raises(SystemExit) as exc_info:
        main([str(image_path), "--preset", preset_path, "--json", str(json_path)])

    assert exc_info.value.code == 2
    assert expected in capsys.readouterr().err
    assert not json_path.exists()


def test_cli_presets_lists_valid_presets_in_input_order(tmp_path: Path, capsys) -> None:
    first_preset = tmp_path / "first.json"
    second_preset = tmp_path / "second.json"
    first_preset.write_text(
        json.dumps({"sort": "hue", "colors": 4, "names": True}),
        encoding="utf-8",
    )
    second_preset.write_text(
        json.dumps({"title": "Review", "sample_step": 2}),
        encoding="utf-8",
    )

    exit_code = main(["presets", str(first_preset), str(second_preset)])

    assert exit_code == 0
    assert capsys.readouterr().out == (
        "Preset validation summary\n"
        f"- {first_preset}: valid; keys: colors, names, sort\n"
        f"- {second_preset}: valid; keys: sample_step, title\n"
    )


def test_cli_presets_writes_json_report(tmp_path: Path, capsys) -> None:
    first_preset = tmp_path / "first.json"
    second_preset = tmp_path / "second.json"
    json_path = tmp_path / "presets-report.json"
    first_preset.write_text(json.dumps({"precision": 2}), encoding="utf-8")
    second_preset.write_text(
        json.dumps({"names": False, "colors": 3}), encoding="utf-8"
    )

    exit_code = main(
        ["presets", str(first_preset), str(second_preset), "--json", str(json_path)]
    )

    assert exit_code == 0
    assert "Preset validation summary" in capsys.readouterr().out
    assert json.loads(json_path.read_text(encoding="utf-8")) == {
        "schema": "swatch-story.presets",
        "version": 1,
        "presets": [
            {
                "path": str(first_preset.resolve()),
                "valid": True,
                "keys": ["precision"],
            },
            {
                "path": str(second_preset.resolve()),
                "valid": True,
                "keys": ["colors", "names"],
            },
        ],
    }


def test_cli_presets_reports_empty_object_with_no_keys(tmp_path: Path, capsys) -> None:
    preset_path = tmp_path / "empty.json"
    preset_path.write_text("{}", encoding="utf-8")

    exit_code = main(["presets", str(preset_path)])

    assert exit_code == 0
    assert capsys.readouterr().out == (
        f"Preset validation summary\n- {preset_path}: valid; keys: none\n"
    )


@pytest.mark.parametrize(
    ("preset_content", "expected"),
    [
        ("{", "invalid preset JSON"),
        ('{"unexpected": true}', "unknown preset key: unexpected"),
    ],
)
def test_cli_presets_rejects_invalid_file_before_writing_json(
    tmp_path: Path, capsys, preset_content: str, expected: str
) -> None:
    preset_path = tmp_path / "preset.json"
    preset_path.write_text(preset_content, encoding="utf-8")
    json_path = tmp_path / "presets-report.json"

    with pytest.raises(SystemExit) as exc_info:
        main(["presets", str(preset_path), "--json", str(json_path)])

    assert exc_info.value.code == 2
    assert expected in capsys.readouterr().err
    assert not json_path.exists()


def test_cli_presets_rejects_missing_file_before_writing_json(
    tmp_path: Path, capsys
) -> None:
    json_path = tmp_path / "presets-report.json"

    with pytest.raises(SystemExit) as exc_info:
        main(["presets", str(tmp_path / "missing.json"), "--json", str(json_path)])

    assert exc_info.value.code == 2
    assert "preset file not found" in capsys.readouterr().err
    assert not json_path.exists()


def test_cli_presets_reads_args_from_sys_argv(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    preset_path = tmp_path / "preset.json"
    preset_path.write_text(json.dumps({"colors": 3}), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["swatch-story", "presets", str(preset_path)])

    exit_code = main()

    assert exit_code == 0
    assert f"- {preset_path}: valid; keys: colors\n" in capsys.readouterr().out


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


def test_cli_gallery_writes_manifest_with_no_index(tmp_path: Path, capsys) -> None:
    gallery_dir = tmp_path / "gallery"

    exit_code = main(["gallery", str(gallery_dir), "--manifest", "--no-index"])

    assert exit_code == 0
    assert (gallery_dir / "warm-blocks.png").exists()
    assert (gallery_dir / "manifest.json").exists()
    assert not (gallery_dir / "README.md").exists()
    assert "4 files" in capsys.readouterr().out


def test_cli_gallery_filters_by_repeated_tags(tmp_path: Path, capsys) -> None:
    gallery_dir = tmp_path / "gallery"

    exit_code = main(
        [
            "gallery",
            str(gallery_dir),
            "--manifest",
            "--tag",
            "CONTRAST",
            "--tag",
            "accessibility",
        ]
    )

    assert exit_code == 0
    assert (gallery_dir / "contrast-checker.png").exists()
    assert not (gallery_dir / "warm-blocks.png").exists()
    manifest = json.loads((gallery_dir / "manifest.json").read_text(encoding="utf-8"))
    assert [sample["filename"] for sample in manifest["samples"]] == [
        "contrast-checker.png"
    ]
    index_text = (gallery_dir / "README.md").read_text(encoding="utf-8")
    assert "- Tags: `contrast`, `accessibility`, `neutral`, `primary`" in index_text
    assert "warm-blocks.png" not in index_text
    assert "cool-stripes.png" not in index_text
    assert "3 files" in capsys.readouterr().out


def test_cli_gallery_rejects_unknown_tag_before_writing(tmp_path: Path, capsys) -> None:
    gallery_dir = tmp_path / "gallery"

    exit_code = main(["gallery", str(gallery_dir), "--tag", "missing"])

    assert exit_code == 2
    assert (
        "swatch-story gallery: unknown gallery tag: missing" in capsys.readouterr().err
    )
    assert not gallery_dir.exists()


def test_cli_gallery_rejects_empty_tag_match_before_writing(
    tmp_path: Path, capsys
) -> None:
    gallery_dir = tmp_path / "gallery"

    exit_code = main(
        ["gallery", str(gallery_dir), "--tag", "warm", "--tag", "accessibility"]
    )

    assert exit_code == 2
    assert (
        "swatch-story gallery: no gallery samples match tag filter: warm, accessibility"
    ) in capsys.readouterr().err
    assert not gallery_dir.exists()


def test_cli_gallery_rejects_existing_files_without_force(
    tmp_path: Path, capsys
) -> None:
    gallery_dir = tmp_path / "gallery"
    gallery_dir.mkdir()
    (gallery_dir / "warm-blocks.png").write_text("existing", encoding="utf-8")

    exit_code = main(["gallery", str(gallery_dir)])

    assert exit_code == 2
    assert "already exists" in capsys.readouterr().err


def test_cli_gallery_rejects_existing_manifest_without_force(
    tmp_path: Path, capsys
) -> None:
    gallery_dir = tmp_path / "gallery"
    gallery_dir.mkdir()
    (gallery_dir / "manifest.json").write_text("existing", encoding="utf-8")

    exit_code = main(["gallery", str(gallery_dir), "--manifest"])

    assert exit_code == 2
    assert "manifest.json" in capsys.readouterr().err


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


def test_cli_compare_reads_preset_and_cli_min_delta_override_wins(
    tmp_path: Path, capsys
) -> None:
    before_path = tmp_path / "before.png"
    before = Image.new("RGB", (4, 1))
    before.putdata([(255, 0, 0), (255, 0, 0), (0, 0, 255), (0, 255, 0)])
    before.save(before_path)
    after_path = tmp_path / "after.png"
    after = Image.new("RGB", (4, 1))
    after.putdata([(255, 0, 0), (0, 0, 255), (0, 0, 255), (0, 255, 0)])
    after.save(after_path)
    preset_path = tmp_path / "preset.json"
    preset_path.write_text(
        json.dumps(
            {
                "colors": 3,
                "sample_step": 1,
                "names": True,
                "precision": 1,
                "title": "Preset Drift",
                "min_delta_percent": 40,
            }
        ),
        encoding="utf-8",
    )
    json_path = tmp_path / "compare.json"
    markdown_path = tmp_path / "compare.md"

    exit_code = main(
        [
            "compare",
            str(before_path),
            str(after_path),
            "--preset",
            str(preset_path),
            "--min-delta-percent",
            "20",
            "--json",
            str(json_path),
            "--markdown",
            str(markdown_path),
        ]
    )

    assert exit_code == 0
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["before"]["settings"]["colors"] == 3
    assert report["before"]["settings"]["sample_step"] == 1
    assert report["before"]["settings"]["color_names"] is True
    assert all("name" in entry for entry in report["before"]["palette"])
    assert report["changed"] == [
        {
            "hex": "#ff0000",
            "before_percent": 50.0,
            "after_percent": 25.0,
            "delta_percent": -25.0,
        },
        {
            "hex": "#0000ff",
            "before_percent": 25.0,
            "after_percent": 50.0,
            "delta_percent": 25.0,
        },
    ]
    markdown = markdown_path.read_text(encoding="utf-8")
    assert markdown.startswith("# Preset Drift\n")
    assert "25.0%" in markdown
    assert "Changed colors:" in capsys.readouterr().out


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


def test_cli_compare_writes_csv_and_still_prints_report(tmp_path: Path, capsys) -> None:
    before_path = tmp_path / "before.png"
    before = Image.new("RGB", (3, 1))
    before.putdata([(255, 0, 0), (0, 0, 255), (0, 255, 0)])
    before.save(before_path)
    after_path = tmp_path / "after.png"
    after = Image.new("RGB", (3, 1))
    after.putdata([(0, 0, 255), (0, 255, 0), (255, 255, 0)])
    after.save(after_path)
    csv_path = tmp_path / "nested" / "compare.csv"

    exit_code = main(
        [
            "compare",
            str(before_path),
            str(after_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--csv",
            str(csv_path),
        ]
    )

    assert exit_code == 0
    console = capsys.readouterr().out
    assert f"Palette comparison: {before_path} -> {after_path}" in console
    assert "Shared colors: #0000ff, #00ff00" in console
    assert "Added colors: #ffff00" in console
    assert "Removed colors: #ff0000" in console
    assert (
        "Changed colors: #0000ff (33.33% to 33.33%, 0.0%), "
        "#00ff00 (33.33% to 33.33%, 0.0%)"
    ) in console
    assert "Drift score: 50.0%" in console
    assert csv_path.read_text(encoding="utf-8") == (
        "section,field,value,category,hex,before_percent,after_percent,"
        "delta_percent\n"
        f"metadata,before_source,{before_path},,,,,\n"
        f"metadata,after_source,{after_path},,,,,\n"
        "metadata,drift_score,50.0,,,,,\n"
        "metadata,dominant_before_hex,#0000ff,,,,,\n"
        "metadata,dominant_after_hex,#0000ff,,,,,\n"
        "metadata,shared_count,2,,,,,\n"
        "metadata,added_count,1,,,,,\n"
        "metadata,removed_count,1,,,,,\n"
        "metadata,changed_count,2,,,,,\n"
        "color,,,changed,#0000ff,33.33,33.33,0.0\n"
        "color,,,changed,#00ff00,33.33,33.33,0.0\n"
        "color,,,added,#ffff00,,33.33,\n"
        "color,,,removed,#ff0000,33.33,,\n"
    )


def test_cli_compare_min_delta_percent_filters_changed_csv_rows(
    tmp_path: Path, capsys
) -> None:
    before_path = tmp_path / "before.png"
    before = Image.new("RGB", (10, 1))
    before.putdata([(255, 0, 0)] * 5 + [(0, 0, 255)] * 3 + [(0, 255, 0)] * 2)
    before.save(before_path)
    after_path = tmp_path / "after.png"
    after = Image.new("RGB", (10, 1))
    after.putdata([(255, 255, 0)] * 4 + [(0, 0, 255)] * 4 + [(0, 255, 0)] * 2)
    after.save(after_path)
    json_path = tmp_path / "compare.json"
    csv_path = tmp_path / "nested" / "compare.csv"

    exit_code = main(
        [
            "compare",
            str(before_path),
            str(after_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--min-delta-percent",
            "15",
            "--json",
            str(json_path),
            "--csv",
            str(csv_path),
        ]
    )

    assert exit_code == 0
    console = capsys.readouterr().out
    assert "Changed colors: none" in console
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["shared"] == ["#0000ff", "#00ff00"]
    assert report["added"] == ["#ffff00"]
    assert report["removed"] == ["#ff0000"]
    assert report["changed"] == []
    csv = csv_path.read_text(encoding="utf-8")
    assert "color,,,shared,#0000ff,30.0,40.0,10.0\n" not in csv
    assert "color,,,shared,#00ff00,20.0,20.0,0.0\n" not in csv
    assert "color,,,added,#ffff00,,40.0,\n" in csv
    assert "color,,,removed,#ff0000,50.0,,\n" in csv


def test_cli_compare_rejects_negative_min_delta_percent_with_argparse(
    tmp_path: Path, capsys
) -> None:
    before_path = tmp_path / "before.png"
    after_path = tmp_path / "after.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(before_path)
    Image.new("RGB", (1, 1), (0, 0, 0)).save(after_path)

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "compare",
                str(before_path),
                str(after_path),
                "--min-delta-percent",
                "-0.1",
            ]
        )

    assert exc_info.value.code == 2
    assert "--min-delta-percent must be 0 or greater" in capsys.readouterr().err


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


def test_cli_compare_uses_matte_for_both_images(tmp_path: Path, capsys) -> None:
    before_path = tmp_path / "before-transparent.png"
    before = Image.new("RGBA", (2, 1))
    before.putdata([(255, 0, 0, 128), (0, 0, 255, 0)])
    before.save(before_path)
    after_path = tmp_path / "after-transparent.png"
    after = Image.new("RGBA", (2, 1))
    after.putdata([(0, 255, 0, 128), (0, 0, 255, 0)])
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
            "--matte",
            "#000000",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["before"]["settings"]["matte"] == "#000000"
    assert report["after"]["settings"]["matte"] == "#000000"
    assert [entry["hex"] for entry in report["before"]["palette"]] == [
        "#000000",
        "#800000",
    ]
    assert [entry["hex"] for entry in report["after"]["palette"]] == [
        "#000000",
        "#008000",
    ]
    assert "Shared colors: #000000" in capsys.readouterr().out


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


def test_cli_matte_updates_transparent_palette_json_and_console(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli-matte.png"
    image = Image.new("RGBA", (2, 1))
    image.putdata([(255, 0, 0, 128), (0, 0, 255, 0)])
    image.save(image_path)
    json_path = tmp_path / "story.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "2",
            "--sample-step",
            "1",
            "--matte",
            "000000",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert summary["settings"]["matte"] == "#000000"
    assert [entry["hex"] for entry in summary["palette"]] == ["#000000", "#800000"]
    assert "#800000" in capsys.readouterr().out


def test_cli_rejects_invalid_matte_with_palette_error_style(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli-invalid-matte.png"
    Image.new("RGBA", (1, 1), (255, 0, 0, 128)).save(image_path)

    exit_code = main([str(image_path), "--matte", "#12345g"])

    assert exit_code == 2
    assert "swatch-story: --matte must be #rrggbb or rrggbb" in capsys.readouterr().err


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


def test_cli_cluster_space_lab_updates_palette_json_and_console(
    tmp_path: Path, capsys
) -> None:
    image_path = tmp_path / "cli-lab-cluster.png"
    image = Image.new("RGB", (4, 1))
    image.putdata(
        [
            (30, 80, 200),
            (30, 80, 200),
            (44, 77, 196),
            (255, 0, 0),
        ]
    )
    image.save(image_path)
    json_path = tmp_path / "story.json"

    exit_code = main(
        [
            str(image_path),
            "--colors",
            "3",
            "--sample-step",
            "1",
            "--cluster-distance",
            "5",
            "--cluster-space",
            "lab",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    assert summary["settings"]["cluster_distance"] == 5
    assert summary["settings"]["cluster_space"] == "lab"
    assert [entry["hex"] for entry in summary["palette"]] == ["#234fc7", "#ff0000"]
    assert "#234fc7" in capsys.readouterr().out


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


def test_cli_rejects_invalid_cluster_space_choice(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "cli.png"
    Image.new("RGB", (1, 1), (0, 0, 0)).save(image_path)

    with pytest.raises(SystemExit) as exc_info:
        main([str(image_path), "--cluster-space", "hsl"])

    assert exc_info.value.code == 2
    assert "invalid choice: 'hsl'" in capsys.readouterr().err


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
    assert (
        f"--swatch-story-color-1-contrast-black: {first['contrast_with_black']};"
    ) in css
    assert (
        f"--swatch-story-color-1-contrast-white: {first['contrast_with_white']};"
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
        lines[0] == "rank,hex,r,g,b,count,percent,luminance,contrast_with_black,"
        "contrast_with_white,best_text_color,label,name"
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
    assert "1,#0000ff,0,0,255,1,50.0,0.072,2.44,8.61,white,color-1,blue\n" in csv
    assert "2,#ff0000,255,0,0,1,50.0,0.213,5.26,3.99,black,color-2,red\n" in csv
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
    assert (
        "| Rank | Color | RGB | Percent | Luminance | Contrast | Text | Label |"
        in markdown
    )
    assert "black 5.26:1; white 3.99:1" in markdown
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
        "cluster distance 0; cluster space rgb; sort frequency; "
        "ignored color none; names included\n"
    ) in text
    assert (
        "1. #0000ff | rgb(0, 0, 255) | 50.0% | color-1 | "
        "contrast black 2.44:1 white 8.61:1 | text white | name blue"
    ) in text
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
        "  0   0 255 color-1 blue\n"
        "255   0   0 color-2 red\n"
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
    assert b"\x00c\x00o\x00l\x00o\x00r\x00-\x001\x00 \x00b\x00l\x00u\x00e" in data
    assert b"\x00c\x00o\x00l\x00o\x00r\x00-\x002\x00 \x00r\x00e\x00d" in data
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
