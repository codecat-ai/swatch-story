from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readmes_include_synchronized_lab_clustering_flow_examples() -> None:
    expected_commands = [
        (
            "swatch-story compare before.png after.png --colors 6 "
            "--cluster-distance 5 --cluster-space lab --json palette-drift.json"
        ),
        (
            "swatch-story baseline reference.png draft-a.png draft-b.png --colors 6 "
            "--cluster-distance 5 --cluster-space lab --json baseline-drift.json"
        ),
        (
            "swatch-story batch hero.png card.png poster.png --colors 6 "
            "--cluster-distance 5 --cluster-space lab --markdown campaign-review.md"
        ),
    ]
    for readme_name in ("README.md", "README-zh.md", "README-ja.md"):
        text = (ROOT / readme_name).read_text(encoding="utf-8")
        for command in expected_commands:
            assert command in text
