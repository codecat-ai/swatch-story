from swatch_story.compare import (
    compare_summaries,
    render_compare_html_report,
    render_compare_markdown_report,
    render_compare_text,
)


def summary(source: str, colors: list[str]) -> dict:
    return {
        "source": source,
        "source_path": f"fixtures/{source}",
        "palette": [
            {
                "rank": rank,
                "hex": color,
                "rgb": [rank, rank, rank],
                "count": 1,
                "percent": 50.0,
                "luminance": 0.1,
                "best_text_color": "white",
                "label": "dark",
            }
            for rank, color in enumerate(colors, start=1)
        ],
    }


def test_compare_summaries_reports_overlap_added_removed_and_drift() -> None:
    before = summary("before.png", ["#111111", "#222222", "#333333"])
    after = summary("after.png", ["#222222", "#333333", "#444444"])

    report = compare_summaries(before, after)

    assert report["before"]["source"] == "before.png"
    assert report["before"]["dominant"] == "#111111"
    assert report["after"]["source"] == "after.png"
    assert report["after"]["dominant"] == "#222222"
    assert report["shared"] == ["#222222", "#333333"]
    assert report["added"] == ["#444444"]
    assert report["removed"] == ["#111111"]
    assert report["drift_score"] == 50.0


def test_compare_summaries_uses_palette_order_for_added_and_removed() -> None:
    before = summary("before.png", ["#aaaaaa", "#111111", "#333333"])
    after = summary("after.png", ["#333333", "#bbbbbb", "#111111", "#cccccc"])

    report = compare_summaries(before, after)

    assert report["shared"] == ["#111111", "#333333"]
    assert report["added"] == ["#bbbbbb", "#cccccc"]
    assert report["removed"] == ["#aaaaaa"]
    assert report["drift_score"] == 60.0


def test_render_compare_text_is_concise_and_human_readable() -> None:
    report = compare_summaries(
        summary("before.png", ["#111111", "#222222"]),
        summary("after.png", ["#222222", "#333333"]),
    )

    text = render_compare_text(report)

    assert "Palette comparison: fixtures/before.png -> fixtures/after.png" in text
    assert "Before dominant: #111111" in text
    assert "After dominant: #222222" in text
    assert "Shared colors: #222222" in text
    assert "Added colors: #333333" in text
    assert "Removed colors: #111111" in text
    assert "Drift score: 66.67%" in text


def test_render_compare_html_report_contains_palette_drift_and_escapes_text() -> None:
    report = compare_summaries(
        summary('before"><script>.png', ["#111111", "#222222"]),
        summary("after & final.png", ["#222222", "#333333"]),
    )

    html = render_compare_html_report(report, title="<Drift & Review>")

    assert html.startswith("<!doctype html>\n")
    assert "&lt;Drift &amp; Review&gt;" in html
    assert "<Drift & Review>" not in html
    assert "before&quot;&gt;&lt;script&gt;.png" in html
    assert "fixtures/before&quot;&gt;&lt;script&gt;.png" in html
    assert "after &amp; final.png" in html
    assert "<script>" not in html
    assert "Before dominant</dt>" in html
    assert "#111111</dd>" in html
    assert "After dominant</dt>" in html
    assert "#222222</dd>" in html
    assert "Shared colors" in html
    assert "#222222" in html
    assert "Added colors" in html
    assert "#333333" in html
    assert "Removed colors" in html
    assert "#111111" in html
    assert "Drift score</dt>" in html
    assert "66.67%</dd>" in html


def test_render_compare_html_report_renders_empty_drift_lists_as_none() -> None:
    report = compare_summaries(
        summary("before.png", ["#111111", "#222222"]),
        summary("after.png", ["#111111", "#222222"]),
    )

    html = render_compare_html_report(report)

    assert "Added colors" in html
    assert "Removed colors" in html
    assert html.count(">None<") >= 2


def test_render_compare_markdown_report_contains_palette_drift() -> None:
    report = compare_summaries(
        summary("before.png", ["#111111", "#222222"]),
        summary("after.png", ["#222222", "#333333"]),
    )

    markdown = render_compare_markdown_report(report)

    assert markdown == (
        "# Palette Drift Report\n"
        "\n"
        "| Field | Value |\n"
        "| --- | --- |\n"
        "| Before source name | before.png |\n"
        "| Before source path | fixtures/before.png |\n"
        "| After source name | after.png |\n"
        "| After source path | fixtures/after.png |\n"
        "| Before dominant colors | `#111111`, `#222222` |\n"
        "| After dominant colors | `#222222`, `#333333` |\n"
        "| Shared colors | `#222222` |\n"
        "| Added colors | `#333333` |\n"
        "| Removed colors | `#111111` |\n"
        "| Drift score | 66.67% |\n"
        "\n"
    )


def test_render_compare_markdown_report_escapes_table_breaking_text() -> None:
    report = compare_summaries(
        summary("before|draft\none.png", ["#111111"]),
        summary("after|final\ntwo.png", ["#111111"]),
    )

    markdown = render_compare_markdown_report(report)

    assert "before\\|draft<br>one.png" in markdown
    assert "fixtures/before\\|draft<br>one.png" in markdown
    assert "after\\|final<br>two.png" in markdown
    assert "| Added colors | None |" in markdown
    assert "| Removed colors | None |" in markdown
