from __future__ import annotations

import colorsys
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from math import sqrt
from pathlib import Path
from typing import Any

MIN_COLORS = 2
MAX_COLORS = 12
DEFAULT_SAMPLE_LIMIT = 10_000
MIN_CLUSTER_DISTANCE = 0
MAX_CLUSTER_DISTANCE = 255
VALID_SORTS = ("frequency", "luminance", "hue")
HEX_RGB_PATTERN = re.compile(r"#?[0-9a-fA-F]{6}\Z")

COMMON_COLOR_NAMES: tuple[tuple[str, tuple[int, int, int]], ...] = (
    ("black", (0, 0, 0)),
    ("white", (255, 255, 255)),
    ("gray", (128, 128, 128)),
    ("red", (220, 20, 60)),
    ("orange", (255, 140, 0)),
    ("yellow", (255, 215, 0)),
    ("green", (34, 139, 34)),
    ("teal", (0, 128, 128)),
    ("cyan", (0, 188, 212)),
    ("blue", (30, 90, 200)),
    ("purple", (128, 0, 128)),
    ("pink", (255, 105, 180)),
    ("brown", (121, 85, 61)),
)


class PaletteError(ValueError):
    """Raised when palette extraction cannot continue with user input."""


@dataclass(frozen=True)
class PaletteEntry:
    rank: int
    rgb: tuple[int, int, int]
    count: int
    percent: float
    luminance: float
    best_text_color: str
    label: str

    @property
    def hex(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(*self.rgb)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "hex": self.hex,
            "rgb": list(self.rgb),
            "count": self.count,
            "percent": self.percent,
            "luminance": self.luminance,
            "best_text_color": self.best_text_color,
            "label": self.label,
        }


def validate_color_count(colors: int) -> None:
    if colors < MIN_COLORS or colors > MAX_COLORS:
        raise PaletteError(f"--colors must be between {MIN_COLORS} and {MAX_COLORS}")


def validate_sample_limit(sample_limit: int) -> None:
    if sample_limit < 1:
        raise PaletteError("--sample-limit must be 1 or greater")


def validate_cluster_distance(cluster_distance: int) -> None:
    if (
        cluster_distance < MIN_CLUSTER_DISTANCE
        or cluster_distance > MAX_CLUSTER_DISTANCE
    ):
        raise PaletteError(
            f"--cluster-distance must be between {MIN_CLUSTER_DISTANCE} "
            f"and {MAX_CLUSTER_DISTANCE}"
        )


def validate_sort(sort: str) -> None:
    if sort not in VALID_SORTS:
        choices = ", ".join(VALID_SORTS)
        raise PaletteError(f"sort must be one of: {choices}")


def normalize_ignore_color(ignore_color: str | None) -> str | None:
    if ignore_color is None:
        return None
    if not HEX_RGB_PATTERN.fullmatch(ignore_color):
        raise PaletteError("--ignore-color must be #rrggbb or rrggbb")
    value = ignore_color.lower()
    if not value.startswith("#"):
        value = f"#{value}"
    return value


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(value: int) -> float:
        normalized = value / 255
        if normalized <= 0.03928:
            return normalized / 12.92
        return ((normalized + 0.055) / 1.055) ** 2.4

    red, green, blue = (channel(value) for value in rgb)
    return round((0.2126 * red) + (0.7152 * green) + (0.0722 * blue), 3)


def contrast_ratio(
    first_rgb: tuple[int, int, int], second_rgb: tuple[int, int, int]
) -> float:
    first = relative_luminance(first_rgb)
    second = relative_luminance(second_rgb)
    light = max(first, second)
    dark = min(first, second)
    return (light + 0.05) / (dark + 0.05)


def best_text_color(rgb: tuple[int, int, int]) -> str:
    black_ratio = contrast_ratio(rgb, (0, 0, 0))
    white_ratio = contrast_ratio(rgb, (255, 255, 255))
    return "black" if black_ratio >= white_ratio else "white"


def lightness_label(luminance: float) -> str:
    if luminance < 0.25:
        return "dark"
    if luminance > 0.7:
        return "light"
    return "mid"


def common_color_name(rgb: tuple[int, int, int]) -> str:
    return min(
        COMMON_COLOR_NAMES,
        key=lambda named_color: rgb_distance(rgb, named_color[1]),
    )[0]


def rgb_distance(first: tuple[int, int, int], second: tuple[int, int, int]) -> int:
    return sum((first[index] - second[index]) ** 2 for index in range(3))


def automatic_sample_step(
    width: int, height: int, *, sample_limit: int = DEFAULT_SAMPLE_LIMIT
) -> int:
    validate_sample_limit(sample_limit)
    pixel_count = width * height
    if pixel_count <= sample_limit:
        return 1
    return max(1, int(sqrt(pixel_count / sample_limit)))


def quantized_key(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    # Five-bit buckets keep nearby colors together while preserving stable output.
    return tuple(channel // 8 for channel in rgb)


def average_rgb(values: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    total = len(values)
    return tuple(round(sum(rgb[index] for rgb in values) / total) for index in range(3))


@dataclass
class ColorCluster:
    rgb_totals: list[int]
    count: int

    @property
    def representative(self) -> tuple[int, int, int]:
        return tuple(round(total / self.count) for total in self.rgb_totals)

    def add(self, rgb: tuple[int, int, int], count: int) -> None:
        for index, channel in enumerate(rgb):
            self.rgb_totals[index] += channel * count
        self.count += count


def perceptualish_rgb_distance(
    first: tuple[int, int, int], second: tuple[int, int, int]
) -> float:
    red_delta = first[0] - second[0]
    green_delta = first[1] - second[1]
    blue_delta = first[2] - second[2]
    return sqrt(
        (red_delta * red_delta)
        + (2 * green_delta * green_delta)
        + (blue_delta * blue_delta)
    )


def cluster_color_counts(
    exact_counts: Counter[tuple[int, int, int]], cluster_distance: int
) -> list[tuple[tuple[int, int, int], int]]:
    clusters: list[ColorCluster] = []
    sorted_counts = sorted(exact_counts.items(), key=lambda item: (-item[1], item[0]))
    for rgb, count in sorted_counts:
        candidates = [
            (
                perceptualish_rgb_distance(rgb, cluster.representative),
                cluster.representative,
                index,
            )
            for index, cluster in enumerate(clusters)
        ]
        matching = [
            candidate for candidate in candidates if candidate[0] <= cluster_distance
        ]
        if matching:
            _distance, _representative, index = min(matching)
            clusters[index].add(rgb, count)
        else:
            clusters.append(
                ColorCluster(
                    rgb_totals=[channel * count for channel in rgb],
                    count=count,
                )
            )
    return [(cluster.representative, cluster.count) for cluster in clusters]


def extract_palette(
    image_path: str | Path,
    *,
    colors: int = 6,
    sample_step: int | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    ignore_color: str | None = None,
    cluster_distance: int = 0,
) -> list[PaletteEntry]:
    validate_color_count(colors)
    validate_sample_limit(sample_limit)
    validate_cluster_distance(cluster_distance)
    normalized_ignore_color = normalize_ignore_color(ignore_color)
    ignored_rgb = (
        hex_to_rgb(normalized_ignore_color)
        if normalized_ignore_color is not None
        else None
    )
    path = Path(image_path)
    if sample_step is not None and sample_step < 1:
        raise PaletteError("--sample-step must be 1 or greater")

    try:
        from PIL import Image, UnidentifiedImageError
    except ModuleNotFoundError as exc:
        raise PaletteError(
            "Pillow is required to read images. "
            "Install the project with the dev extras."
        ) from exc

    try:
        with Image.open(path) as image:
            rgba_image = image.convert("RGBA")
            width, height = rgba_image.size
            step = sample_step or automatic_sample_step(
                width, height, sample_limit=sample_limit
            )
            sampled = [
                composite_over_white(rgba_image.getpixel((x, y)))
                for y in range(0, height, step)
                for x in range(0, width, step)
            ]
    except FileNotFoundError as exc:
        raise PaletteError(f"image not found: {path}") from exc
    except UnidentifiedImageError as exc:
        raise PaletteError(f"unsupported or unreadable image: {path}") from exc

    if not sampled:
        raise PaletteError("image did not produce any sampled pixels")
    if ignored_rgb is not None:
        sampled = [rgb for rgb in sampled if rgb != ignored_rgb]
        if not sampled:
            raise PaletteError(
                f"all sampled pixels were ignored by --ignore-color "
                f"{normalized_ignore_color}"
            )

    return build_palette(sampled, colors, cluster_distance=cluster_distance)


def composite_over_white(rgba: tuple[int, int, int, int]) -> tuple[int, int, int]:
    red, green, blue, alpha = rgba
    if alpha == 255:
        return red, green, blue
    opacity = alpha / 255
    return tuple(
        round((channel * opacity) + (255 * (1 - opacity)))
        for channel in (red, green, blue)
    )


def build_palette(
    sampled: list[tuple[int, int, int]], colors: int, *, cluster_distance: int = 0
) -> list[PaletteEntry]:
    validate_cluster_distance(cluster_distance)
    exact_counts = Counter(sampled)
    if cluster_distance > 0:
        ranked = sorted(
            cluster_color_counts(exact_counts, cluster_distance),
            key=lambda item: (-item[1], item[0]),
        )
    elif len(exact_counts) <= colors:
        ranked = sorted(exact_counts.items(), key=lambda item: (-item[1], item[0]))
    else:
        buckets: dict[tuple[int, int, int], list[tuple[int, int, int]]] = defaultdict(
            list
        )
        for rgb in sampled:
            buckets[quantized_key(rgb)].append(rgb)
        ranked = sorted(
            ((average_rgb(values), len(values)) for values in buckets.values()),
            key=lambda item: (-item[1], item[0]),
        )

    total = len(sampled)
    entries = []
    for rank, (rgb, count) in enumerate(ranked[:colors], start=1):
        luminance = relative_luminance(rgb)
        entries.append(
            PaletteEntry(
                rank=rank,
                rgb=rgb,
                count=count,
                percent=round((count / total) * 100, 2),
                luminance=luminance,
                best_text_color=best_text_color(rgb),
                label=lightness_label(luminance),
            )
        )
    return entries


def sort_palette(entries: list[PaletteEntry], sort: str) -> list[PaletteEntry]:
    validate_sort(sort)
    if sort == "frequency":
        return entries
    if sort == "luminance":
        sorted_entries = sorted(entries, key=lambda entry: (entry.luminance, entry.rgb))
    else:
        sorted_entries = sorted(entries, key=hue_sort_key)
    return [
        replace(entry, rank=rank) for rank, entry in enumerate(sorted_entries, start=1)
    ]


def hue_sort_key(
    entry: PaletteEntry,
) -> tuple[bool, float, float, tuple[int, int, int]]:
    red, green, blue = (channel / 255 for channel in entry.rgb)
    hue, saturation, _value = colorsys.rgb_to_hsv(red, green, blue)
    is_grayscale = saturation <= 0.01
    return (is_grayscale, hue, entry.luminance, entry.rgb)


def summarize_image(
    image_path: str | Path,
    *,
    colors: int = 6,
    sample_step: int | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    include_color_names: bool = False,
    ignore_color: str | None = None,
    cluster_distance: int = 0,
    sort: str = "frequency",
) -> dict[str, Any]:
    validate_sample_limit(sample_limit)
    validate_cluster_distance(cluster_distance)
    validate_sort(sort)
    normalized_ignore_color = normalize_ignore_color(ignore_color)
    path = Path(image_path)
    try:
        from PIL import Image, UnidentifiedImageError
    except ModuleNotFoundError as exc:
        raise PaletteError(
            "Pillow is required to read images. "
            "Install the project with the dev extras."
        ) from exc

    try:
        with Image.open(path) as image:
            width, height = image.size
    except FileNotFoundError as exc:
        raise PaletteError(f"image not found: {path}") from exc
    except UnidentifiedImageError as exc:
        raise PaletteError(f"unsupported or unreadable image: {path}") from exc

    effective_sample_step = sample_step or automatic_sample_step(
        width, height, sample_limit=sample_limit
    )
    palette = extract_palette(
        path,
        colors=colors,
        sample_step=sample_step,
        sample_limit=sample_limit,
        ignore_color=normalized_ignore_color,
        cluster_distance=cluster_distance,
    )
    entries = [entry.to_dict() for entry in sort_palette(palette, sort)]
    if include_color_names:
        for entry in entries:
            entry["name"] = common_color_name(tuple(entry["rgb"]))
    settings = {
        "colors": colors,
        "sample_step": effective_sample_step,
        "sample_limit": sample_limit,
        "cluster_distance": cluster_distance,
        "sort": sort,
        "color_names": include_color_names,
    }
    if normalized_ignore_color is not None:
        settings["ignore_color"] = normalized_ignore_color
    return {
        "source": path.name,
        "source_path": str(path),
        "size": {"width": width, "height": height},
        "settings": settings,
        "palette": entries,
    }
