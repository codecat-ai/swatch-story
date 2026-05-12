from swatch_story.compare import compare_summaries, render_compare_text


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
