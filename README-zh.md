# swatch-story

[English](README.md) | [中文](README-zh.md) | [日本語](README-ja.md)


`swatch-story` 是一个本地优先的图像工具，可以从图片中提取简洁的色彩故事，并导出机器可读的 JSON、设计令牌 JSON、UTF-8 CSV、CSS 自定义属性、便携 Markdown、面向 WCAG 的 Markdown 审计、便于粘贴的纯文本、独立 SVG 色块单页、GIMP `.gpl` 调色板、Adobe Swatch Exchange `.ase` 调色板和独立 HTML 报告。

## 问题与动机

截图、封面、海报和教学图片里常常包含有用的色彩信息，但快速调色板工具有时偏向在线服务，或者只返回原始十六进制颜色。`swatch-story` 会把图片留在本机，并补充占比、稳定的令牌标签、黑/白文字对比度，让输出更适合设计笔记、文档、课程和小型创作流程。

## 功能

- 使用 Pillow 从本地图像文件中进行确定性的调色板提取。
- JSON 输出包含源文件名、源文件路径、图像尺寸、提取设置、颜色排名、十六进制颜色、RGB、数量、占比、相对亮度、黑/白文字对比度、可读文字选择以及稳定的令牌标签。
- 主图像命令可输出设计令牌 JSON，包含 Design Tokens Community Group schema 元数据、稳定的颜色令牌键、`$type: color`、`$value`、可读对比度说明，以及适合令牌流水线使用的 `extensions.swatchStory` 指标。
- UTF-8 CSV 输出提供稳定列，便于在电子表格中排序、筛选，也适合轻量数据流程。
- CSS 自定义属性输出包含十六进制颜色、RGB 三元组、黑/白对比度和可读文字颜色变量。
- 便携 Markdown 报告包含调色板元数据和适合笔记、文档使用的表格。
- 面向 WCAG 的 Markdown 审计报告会复用每个色块的黑/白对比度，总结普通文本和大号文本的 AA/AAA 准备度，并推荐对比度更高的文字颜色。
- 纯文本调色板单页包含源文件元数据、提取设置，以及每个色块一行的易粘贴内容，适合邮件、工单和课程笔记。
- 独立 SVG 色块单页包含源文件元数据、提取设置、色块、HEX 值、可选名称、占比、亮度、黑/白对比度、标签和可读文字颜色建议，适合文档和幻灯片。
- 确定性的 GIMP `.gpl` 调色板输出，便于与设计工具互操作。
- 确定性的 Adobe Swatch Exchange `.ase` 输出，按报告标题分组 RGB 色块。
- 独立 HTML 联系表报告包含图像元数据、提取设置、可访问的色块卡片、已转义的用户来源值，以及适合在浏览器审阅或设计评审中使用的对比度建议。
- HTML 报告可通过 `--html-thumbnail PATH` 生成本地旁路缩略图并从报告链接，不会把源图片以 base64 嵌入 HTML。
- 在终端中输出紧凑摘要，便于快速查看。
- 通过 `--sample-limit` 配置自动采样目标，同时保留确定性的 `--sample-step` 覆盖，方便可重复审阅。
- `--ignore-color HEX` 会在调色板排名前排除精确匹配的 RGB 颜色，例如平面截图背景，并基于剩余采样像素重新计算占比。
- `--matte HEX` 会在提取前把透明和半透明像素合成到指定背景色上，方便按深色、浅色或品牌底色上的实际外观采样图标和 logo。
- `--cluster-distance N` 可在排名前选择性地把视觉上接近的采样 RGB 颜色分组，使用小型、确定性的本地距离计算，并用加权平均颜色作为代表色。
- `--sort {frequency,luminance,hue}` 保留默认的频率排名，或在提取后把已选色块按从暗到亮、或按色相角度重新排序，方便设计师审阅。
- `--precision N` 可把 JSON、设计令牌 JSON、CSV、Markdown、WCAG 审计、纯文本、SVG、HTML 和终端摘要中的报告占比、相对亮度和对比度格式化为 0 到 6 位小数；省略时保持现有默认输出。
- `--label-prefix PREFIX` 会在主图像命令中把默认的 `color-1`、`color-2` 标签替换为 `brand-1`、`brand-2` 这样的设计令牌标签，也会影响 `--tokens` 的键名。
- 可选的 `--names` 提示会把颜色映射到一小组内置的近似常见名称，例如 red、teal、blue、brown、black、white 和 gray。
- 两张本地图像的调色板对比报告，包含主色变化、紧凑的 HTML 并排调色板预览条、共有颜色、新增颜色、移除颜色，以及基于重叠度的确定性漂移分数，并可输出到终端、JSON、独立 HTML、便携 Markdown 或纯文本。
- 批量团队审阅报告可把两张或更多本地图像审计合并为一个确定性的 Markdown 和/或独立 HTML 文件；每张图片都有一个章节/卡片，包含主色、调色板行、对比度建议、已转义的用户来源值和共享提取设置。
- 源码检出环境中的示例素材库生成，可以写入小型确定性 PNG、稳定的课程主题标签、可选 Markdown 索引和可选 JSON 清单，用于教学调色板提取和素材断言。

## 安装

本项目尚未发布到包注册表。只能从源码检出安装：

```bash
git clone https://github.com/codecat-ai/swatch-story.git
cd swatch-story
python -m pip install -e ".[dev]"
```

## 快速开始

```bash
swatch-story image.png --colors 6 --json story.json --tokens story.tokens.json --csv story.csv --css story.css --html story.html --markdown story.md --wcag-audit audit.md --text story.txt --svg story.svg --gpl story.gpl --ase story.ase --title "Launch Palette"
```

该命令会打印终端摘要，并在需要时写入 `story.json`、`story.tokens.json`、`story.csv`、`story.css`、`story.html`、`story.md`、`audit.md`、`story.txt`、`story.svg`、`story.gpl` 和 `story.ase`。

从同一个源码检出生成本地教学素材：

```bash
swatch-story gallery demo-gallery
```

gallery 命令会写入小型确定性 PNG 文件，并生成 `demo-gallery/README.md`，其中包含针对这些示例提取调色板和报告的命令及标签。当课程材料或测试需要包含预期主色、调色板十六进制值和稳定课程主题标签的 `demo-gallery/manifest.json` 时，可以添加 `--manifest`。

为多张本地图像创建团队审阅报告：

```bash
swatch-story batch hero.png card.png poster.png --colors 6 --markdown team-review.md --html team-review.html
```

## 示例

只生成示例 PNG 素材，不生成 Markdown 索引：

```bash
swatch-story gallery demo-gallery --no-index
```

生成 PNG 素材和机器可读清单，但不生成 Markdown 索引：

```bash
swatch-story gallery demo-gallery --manifest --no-index
```

只生成匹配所有请求课程标签的示例：

```bash
swatch-story gallery demo-gallery --manifest --tag contrast --tag accessibility
```

只创建 JSON 报告：

```bash
swatch-story poster.png --colors 5 --json poster-colors.json
```

按深色底色上的实际外观提取透明 logo：

```bash
swatch-story logo.png --colors 5 --matte 111827 --json logo-dark-colors.json
```

为令牌流水线创建设计令牌 JSON：

```bash
swatch-story poster.png --colors 5 --tokens poster.tokens.json --title "Poster Palette"
```

创建适合电子表格使用的 CSV 报告：

```bash
swatch-story poster.png --colors 5 --csv poster-colors.csv
```

使用固定采样步长创建可分享的本地 HTML 报告：

```bash
swatch-story screenshot.png --colors 8 --sample-step 2 --html screenshot-story.html
```

创建带有小型旁路缩略图的本地 HTML 报告，方便快速审阅来源视觉效果：

```bash
swatch-story screenshot.png --colors 8 --html reports/screenshot-story.html --html-thumbnail reports/assets/screenshot-thumb.png
```

为超大图片调整自动采样目标，而不手动选择固定步长：

```bash
swatch-story mural.png --colors 8 --sample-limit 25000 --json mural-colors.json
```

在调色板排名前忽略平面背景色：

```bash
swatch-story screenshot.png --colors 6 --ignore-color ffffff --json screenshot-colors.json
```

排名前把透明像素合成到品牌背景色上：

```bash
swatch-story icon.png --colors 4 --matte "#003366" --json icon-brand-colors.json
```

在排名前把接近的采样颜色分组：

```bash
swatch-story photo.png --colors 6 --cluster-distance 12 --json photo-colors.json
```

在提取后把已选色块按从暗到亮排序：

```bash
swatch-story poster.png --colors 6 --sort luminance --html poster-luminance.html
```

把已选的彩色色块按色相角度排序，并把灰阶颜色放在彩色之后：

```bash
swatch-story poster.png --colors 6 --sort hue --json poster-hue.json
```

为紧凑审阅输出舍入报告占比、相对亮度和对比度：

```bash
swatch-story poster.png --colors 6 --precision 1 --json poster-colors.json --tokens poster.tokens.json --markdown poster-colors.md --svg poster-colors.svg --html poster-colors.html
```

写入面向 WCAG 的 Markdown 审计，用于检查黑/白文字可用性：

```bash
swatch-story poster.png --colors 5 --wcag-audit poster-wcag.md --title "Poster Palette"
```

为生成的报告应用设计令牌标签前缀：

```bash
swatch-story poster.png --colors 5 --label-prefix brand --tokens poster.tokens.json --json poster-colors.json --css poster-colors.css
```

对比两张本地图像，并写入 JSON、CSV、HTML、Markdown 和纯文本漂移报告：

```bash
swatch-story compare before.png after.png --colors 6 --sample-step 1 --matte 111827 --min-delta-percent 2 --json palette-drift.json --csv palette-drift.csv --html palette-drift.html --markdown palette-drift.md --text palette-drift.txt
```

`compare` 命令会打印简洁的终端报告，包含前后图片路径、两张图各自的主色、共有颜色、新增颜色、移除颜色、共有颜色占比变化和漂移分数。分数表示已选调色板 HEX 值中发生变化的比例，计算方式为 `100 * (1 - shared / union)`；`0%` 表示已选调色板 HEX 值完全相同，`100%` 表示没有重叠。使用 `--min-delta-percent N` 可以隐藏绝对占比变化小于 `N` 的共有颜色明细行；新增和移除颜色仍会报告。

对比 CSV 报告是用于电子表格调色板漂移审阅的确定性 UTF-8 表格。对比 HTML 报告是可在浏览器中审阅的独立本地文件，并为每张图片提供紧凑的 CSS-only 并排调色板预览条。对比 Markdown 报告是适合笔记、议题评论和设计文档的便携表格。对比纯文本报告是确定性的 UTF-8 漂移单页，适合邮件、工单和审阅日志。这些报告都会包含安全表示的前后图片名称和路径、两侧各自的主色、共有颜色、新增颜色、移除颜色、过滤后的颜色变化明细、空变化列表的清晰 `None` 状态，以及漂移分数。你可以在同一个 `compare` 命令中同时请求 `--json`、`--csv`、`--html`、`--markdown` 和 `--text`。

把多张本地图像审计合并为一个团队审阅报告：

```bash
swatch-story batch hero.png card.png poster.png --colors 6 --sample-step 1 --names --title "Campaign Palette Review" --markdown campaign-review.md --html campaign-review.html
```

`batch` 命令要求至少两个图像路径，并且至少提供 `--markdown PATH` 或 `--html PATH` 之一；两个输出可以同时请求。它会对每张图片复用相同的确定性调色板提取设置，并为每个来源图像写入一个 Markdown 章节或 HTML 卡片，包含来源名称/路径、图像尺寸、主色、调色板行/卡片，以及黑/白文字对比度建议。用户来源的标题、文件名、路径、标签和名称都会被转义，文件以确定性 UTF-8 写入。

HTML 报告是适合浏览器查看的联系表。它会显示图像名称和路径、尺寸、请求的颜色数量、实际采样步长、聚类距离、排序模式、是否包含近似名称、简短摘要，以及每个色块的卡片；卡片包含 HEX、RGB、相对亮度、黑/白对比度、可读文字颜色和对比度建议。把 `--html-thumbnail PATH` 与 `--html PATH` 一起使用时，会从源图片生成一个有尺寸上限的本地缩略图，并尽量用相对路径链接；源图片不会以 base64 嵌入。

SVG 报告是适合文档和幻灯片的独立本地色块单页。它会显示标题、源文件名、图像尺寸、提取设置，以及每个色块一行的颜色矩形、HEX、可选近似名称、占比、亮度、黑/白对比度、标签和可读文字颜色。用户来源的标题、源文件名、标签和名称都会进行 XML 转义，并且不会嵌入源图片本身。

设计令牌 JSON 报告面向设计令牌流水线。它使用提取出的标签作为每个 `color` 键，因此 `--label-prefix brand` 会生成 `brand-1` 等键；`--precision N` 也会舍入令牌中的占比、亮度、对比度和说明文本。该选项只适用于主图像命令，不适用于 `compare` 或 `gallery`。

WCAG 审计报告是适合审阅笔记的确定性 UTF-8 Markdown 文件。它包含标题、源文件名和路径、图像尺寸、提取设置、普通文本和大号文本的 WCAG AA/AAA 阈值，以及每个色块一行的黑色文字准备度、白色文字准备度、推荐文字颜色和简短建议。用户来源的 Markdown 表格单元格会被转义。

创建可在样式表中使用的 CSS 自定义属性：

```bash
swatch-story poster.png --colors 5 --css poster-colors.css
```

为笔记或文档创建便携 Markdown 报告：

```bash
swatch-story poster.png --colors 5 --markdown poster-colors.md --title "Poster Palette"
```

创建便于粘贴到邮件、工单或课程笔记的纯文本调色板单页：

```bash
swatch-story poster.png --colors 5 --text poster-colors.txt --title "Poster Palette"
```

创建适合文档或幻灯片的独立 SVG 色块单页：

```bash
swatch-story poster.png --colors 5 --svg poster-colors.svg --title "Poster Palette"
```

创建可用于设计工具的 GIMP 调色板：

```bash
swatch-story poster.png --colors 5 --gpl poster-colors.gpl --title "Poster Palette"
```

创建可用于设计工具的 Adobe Swatch Exchange 调色板：

```bash
swatch-story poster.png --colors 5 --ase poster-colors.ase --title "Poster Palette"
```

在 JSON、CSV、HTML、Markdown、纯文本、SVG、GIMP 和 ASE 调色板标签、CSS 注释和终端摘要中包含近似常见颜色名称提示：

```bash
swatch-story poster.png --colors 5 --names --json poster-colors.json --csv poster-colors.csv --markdown poster-colors.md
```

CSS 输出示例：

```css
/* Generated by swatch-story. */
:root {
  --swatch-story-color-1: #112233;
  --swatch-story-color-1-rgb: 17, 34, 51;
  --swatch-story-color-1-contrast-black: 1.3;
  --swatch-story-color-1-contrast-white: 16.15;
  --swatch-story-color-1-text: white;
}
```

示例调色板条目：

```json
{
  "rank": 1,
  "hex": "#112233",
  "rgb": [17, 34, 51],
  "count": 120,
  "percent": 32.43,
  "luminance": 0.015,
  "contrast_with_black": 1.3,
  "contrast_with_white": 16.15,
  "best_text_color": "white",
  "label": "color-1"
}
```

对比度使用基于相对亮度的 WCAG 公式 `(lighter + 0.05) / (darker + 0.05)`，把每个色块分别与黑色亮度 `0` 和白色亮度 `1` 比较。`best_text_color` 是对比度更高的选项。

CSV 输出示例：

```csv
rank,hex,r,g,b,count,percent,luminance,contrast_with_black,contrast_with_white,best_text_color,label,name
1,#112233,17,34,51,120,32.43,0.015,1.3,16.15,white,color-1,
```

纯文本输出示例：

```text
Poster Palette

Source: poster.png
Image size: 1200 x 800 px
Settings: colors 2; sample step 1; sample limit 10000; cluster distance 0; sort frequency; ignored color none; names not included

Swatches:
1. #112233 | rgb(17, 34, 51) | 32.43% | color-1 | contrast black 1.3:1 white 16.15:1 | text white
2. #eeeeee | rgb(238, 238, 238) | 18.25% | color-2 | contrast black 18.1:1 white 1.16:1 | text black
```

GIMP 调色板输出示例：

```text
GIMP Palette
Name: Poster Palette
Columns: 2
# Generated by swatch-story.
 17  34  51 color-1
238 238 238 color-2
```

使用 `--names` 时，调色板条目会包含额外的近似常见名称提示：

```json
{
  "rank": 1,
  "hex": "#112233",
  "rgb": [17, 34, 51],
  "count": 120,
  "percent": 32.43,
  "luminance": 0.015,
  "contrast_with_black": 1.3,
  "contrast_with_white": 16.15,
  "best_text_color": "white",
  "label": "color-1",
  "name": "black"
}
```

JSON 设置会包含 `cluster_distance` 和所选排序模式，例如 `"cluster_distance": 0` 和 `"sort": "frequency"`。使用 `--ignore-color` 时，JSON 设置会包含规范化的小写值，例如 `"ignore_color": "#ffffff"`。被忽略的像素会在可选聚类和排名前移除，因此色块占比只基于剩余采样像素计算。使用 `--matte` 时，JSON 设置会包含规范化的小写值，例如 `"matte": "#111827"`；使用默认白色底色时不会写入该字段。

对比 JSON 输出示例：

```json
{
  "before": {
    "source": "before.png",
    "source_path": "before.png",
    "dominant": "#112233"
  },
  "after": {
    "source": "after.png",
    "source_path": "after.png",
    "dominant": "#445566"
  },
  "shared": ["#eeeeee"],
  "added": ["#445566"],
  "removed": ["#112233"],
  "changed": [
    {
      "hex": "#eeeeee",
      "before_percent": 20.0,
      "after_percent": 23.5,
      "delta_percent": 3.5
    }
  ],
  "drift_score": 66.67
}
```

对比纯文本输出示例：

```text
Palette Drift Report

Before source name: before.png
Before source path: before.png
After source name: after.png
After source path: after.png
Before dominant colors: #112233, #eeeeee
After dominant colors: #445566, #eeeeee
Shared colors: #eeeeee
Added colors: #445566
Removed colors: #112233
Changed colors: #eeeeee (20.0% to 23.5%, +3.5%)
Drift score: 66.67%
```

## 配置

`swatch-story` 完全通过 CLI 选项配置：

- `--colors N`：报告的颜色数量，范围为 2 到 12。默认值：6。
- `--json PATH`：写入 JSON 报告。
- `--tokens PATH`：写入确定性的设计令牌 JSON 报告，便于导入令牌流水线。报告包含 `$schema`、`source`、`title`，以及按调色板标签作为键的 `color` 令牌，每个令牌包含 `$type`、`$value`、说明文本和 `extensions.swatchStory` 指标。
- `--csv PATH`：写入 UTF-8 CSV 报告，包含稳定列：`rank`、`hex`、`r`、`g`、`b`、`count`、`percent`、`luminance`、`contrast_with_black`、`contrast_with_white`、`best_text_color`、`label` 和 `name`。
- `--css PATH`：写入 CSS 自定义属性。
- `--html PATH`：写入独立 HTML 报告。
- `--html-thumbnail PATH`：写入小型本地旁路缩略图，并从 HTML 报告链接。该选项要求同时提供 `--html PATH`；缩略图最长边限制为 320 px，保持宽高比，按需创建父目录，并把图片数据留在本地而不是以 base64 嵌入 HTML。
- `--markdown PATH`：写入便携 Markdown 报告。
- `--wcag-audit PATH`：写入确定性的 UTF-8 Markdown 审计，包含源元数据、提取设置、针对黑/白文字的 WCAG 普通/大号文本 AA/AAA 准备度、推荐文字颜色，以及每个色块的一条建议。
- `--text PATH`：写入 UTF-8 纯文本调色板单页，包含标题、源文件名、图像尺寸、提取设置，以及每个色块一行的排名、十六进制颜色、RGB 三元组、占比、标签、黑/白对比度、最佳文字颜色和可选名称提示。
- `--svg PATH`：写入确定性的 UTF-8 独立 SVG 色块单页，包含标题、源文件名、图像尺寸、提取设置，以及每个色块一行的颜色矩形、HEX、可选名称提示、占比、亮度、黑/白对比度、标签和可读文字颜色。
- `--gpl PATH`：写入确定性的 GIMP `.gpl` 调色板。
- `--ase PATH`：写入确定性的 Adobe Swatch Exchange `.ase` 调色板。
- `--sample-step N`：每隔 N 个像素采样一次。默认情况下，小图使用每个像素，大图使用确定性的自动步长。
- `--sample-limit N`：在未提供 `--sample-step` 时，设置自动步长的目标采样像素数。默认值：10000。必须大于等于 1。如果提供了 `--sample-step`，固定步长会控制像素迭代；JSON 设置仍会包含所选的 `sample_limit` 和实际的 `sample_step`。
- `--ignore-color HEX`：在调色板排名前排除与某个十六进制 RGB 颜色完全匹配的采样像素。接受 `#rrggbb` 或 `rrggbb`，不区分大小写，并在 JSON/报告设置中存储规范化的小写 `#rrggbb` 值。如果所有采样像素都被忽略，或该值不是有效的十六进制 RGB，命令会以清晰错误退出。
- `--matte HEX`：在提取调色板前，把透明或半透明像素合成到十六进制 RGB 背景色上。接受 `#rrggbb` 或 `rrggbb`，不区分大小写。默认行为仍是白色底色，只有显式提供该选项时，JSON 设置才会包含规范化的 `matte`。
- `--cluster-distance N`：当值大于 0 时，在调色板排名前把相似的采样 RGB 颜色分组。取值必须在 0 到 255 之间。默认值为 0，保留精确 RGB 分桶行为。聚类代表色是按采样像素数量加权后的 RGB 四舍五入平均值。
- `--sort {frequency,luminance,hue}`：设置已选调色板条目的顺序。`frequency` 保留按采样像素数量排名的默认顺序，`luminance` 将色块从暗到亮重新排序，`hue` 先按 HSV 色相角度排列彩色色块，再放置灰阶或近灰阶色块。重新排序后的调色板会从 1 重新编号。默认值：`frequency`。
- `--precision N`：把面向用户的报告占比、相对亮度和对比度格式化为 `N` 位小数，范围为 0 到 6。省略时会保留现有 JSON 数字和报告字符串。该选项适用于普通调色板提取的 JSON、设计令牌 JSON、CSV、Markdown、WCAG 审计、纯文本、SVG、HTML 和终端摘要；CSS、GIMP `.gpl`、Adobe `.ase` 等设计工具调色板格式会保留各自的格式化输出。
- `--label-prefix PREFIX`：在主图像命令中把默认调色板标签替换为 `PREFIX-1`、`PREFIX-2` 等形式。`PREFIX` 必须以小写字母开头，并且只能包含小写字母、数字和连字符。例如，`--label-prefix brand` 会把 `brand-1` 写入 JSON、设计令牌 JSON 键、CSV、CSS 自定义属性名、Markdown、WCAG 审计、纯文本、HTML、SVG、GIMP `.gpl`、Adobe `.ase` 和终端输出。compare 和 gallery 命令不使用此选项。
- `--title TEXT`：设计令牌 JSON、HTML、Markdown、WCAG 审计、纯文本、SVG、GIMP 调色板和 ASE 输出标题。默认值：`Swatch Story`。
- `--names`：包含确定性、离线、近似的常见颜色名称提示。这些名称来自一小组内置 RGB 参考值，适合作为方便阅读的颜色家族提示，而不是精确颜色命名。

`swatch-story compare BEFORE_IMAGE AFTER_IMAGE [options]` 会复用 `--colors`、`--sample-step`、`--sample-limit`、`--ignore-color`、`--matte`、`--cluster-distance`、`--sort` 和 `--names`；同一个 matte 会应用到两张图片。它也接受 `--min-delta-percent N`，其中 `N` 是 `0` 或更大的浮点百分比。在对比模式下，`--json PATH` 会写入确定性的对比 JSON 报告，而不是单图报告；`--csv PATH` 会写入确定性的 UTF-8 对比 CSV，包含元数据、过滤后的颜色变化行以及不过滤的新增/移除颜色行；`--html PATH` 会写入独立 HTML 对比报告；`--markdown PATH` 会写入便携 Markdown 对比报告；`--text PATH` 会写入 UTF-8 纯文本漂移报告。这些输出可以同时请求。

`swatch-story batch IMAGE IMAGE [IMAGE...] [options]` 会在每张图片上复用 `--colors`、`--sample-step`、`--sample-limit`、`--ignore-color`、`--matte`、`--cluster-distance`、`--sort`、`--names`、`--precision` 和 `--title`。它要求至少两个图像路径和至少一个输出路径。`--markdown PATH` 会写入确定性的 UTF-8 团队审阅 Markdown 报告，`--html PATH` 会写入独立 HTML 团队审阅报告；两者可以同时请求。批量模式不使用 `--label-prefix`、`--tokens`、`--json`、`--csv`、`--css`、`--wcag-audit`、`--text`、`--svg`、`--gpl`、`--ase` 或 `--html-thumbnail`。

`swatch-story gallery OUT_DIR [--manifest] [--no-index] [--force] [--tag TAG]...` 会写入内置示例 PNG 素材，并默认生成包含源码检出命令和可读示例标签的 Markdown `README.md` gallery。`--manifest` 还会写入确定性的 UTF-8 `manifest.json`，其中包含 schema 版本 `1`、生成器名称、示例文件名、尺寸、故事、标签、预期主色和预期调色板十六进制值。`--tag` 可以重复使用，只生成包含所有请求标签的示例；匹配不区分大小写，未知标签或无匹配结果会在写入文件前失败。`--no-index` 只跳过 `README.md`，因此可以与 `--manifest` 组合使用。除非提供 `--force`，否则该命令会拒绝覆盖已有 gallery 文件，包括 `manifest.json`。

MVP 不读取配置文件，也不会获取远程图片。

## 开发

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest -q
python -m build
```

## 测试

测试套件会构建小型合成图像，并验证调色板占比、对比度文字选择、单图/对比/批量报告渲染、设计令牌 JSON 输出、gallery 清单内容、用户来源报告值的转义和 CLI 文件输出。

```bash
pytest -q
```

## 路线图
- 基于更正式色彩模型（如 CIELAB）的可选感知色彩空间聚类，让视觉分组更接近人眼感受。
- 可选的调色板预设文件，用于在团队和项目之间保存可复用的提取设置。
- 可选的基准到批量漂移审阅，用一张参考图像对比一组候选图像。

## 贡献

欢迎贡献。请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，在改变行为前添加面向行为的测试，并保持 README 翻译含义同步。

## 许可证

MIT。参见 [LICENSE](LICENSE)。

## AI 辅助维护

本项目可能使用 AI 辅助进行维护任务。维护者会在发布前审查变更，并且不会有意复制其他项目的代码或文本。
