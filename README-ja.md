# swatch-story

[English](README.md) | [中文](README-zh.md) | [日本語](README-ja.md)


`swatch-story` は、画像からコンパクトな色のストーリーを抽出し、機械可読な JSON、UTF-8 CSV、CSS カスタムプロパティ、ポータブルな Markdown、貼り付けやすいプレーンテキスト、単体 SVG スウォッチシート、GIMP `.gpl` パレット、Adobe Swatch Exchange `.ase` パレット、単体で開ける HTML レポートを書き出すローカル優先の画像ユーティリティです。

## 課題と動機

スクリーンショット、カバー画像、ポスター、教材画像には有用な色の情報が含まれることがあります。しかし、手軽なパレットツールはオンラインサービス前提だったり、単なる HEX 値だけを返したりしがちです。`swatch-story` は画像をローカルに保ち、割合、輝度ラベル、読みやすい黒/白の文字色候補を加えることで、デザインメモ、ドキュメント、授業、小さな制作ワークフローで使いやすい出力を提供します。

## 機能

- Pillow を使い、ローカル画像ファイルから決定的にパレットを抽出します。
- JSON 出力には、元ファイル名、元ファイルパス、画像サイズ、抽出設定、色の順位、HEX、RGB、カウント、割合、相対輝度、読みやすい黒/白の文字色、明暗ラベルが含まれます。
- UTF-8 CSV 出力には、表計算ソフトでの並べ替え、絞り込み、軽量なデータ処理に使いやすい安定した列が含まれます。
- CSS カスタムプロパティ出力には、HEX、RGB の組、読みやすい文字色の変数が含まれます。
- ポータブルな Markdown レポートには、パレットのメタデータとメモやドキュメント向けの表が含まれます。
- プレーンテキストのパレットシートには、元ファイルのメタデータ、抽出設定、メール、チケット、授業メモに貼り付けやすいスウォッチごとの 1 行が含まれます。
- 単体 SVG スウォッチシートには、元ファイルのメタデータ、抽出設定、色ブロック、HEX 値、任意の名前、割合、輝度、ラベル、読みやすい文字色の指針が含まれ、ドキュメントやスライドに使いやすくなっています。
- デザインツールと連携しやすい、決定的な GIMP `.gpl` パレットを書き出します。
- レポートタイトルでグループ化した RGB スウォッチを含む、決定的な Adobe Swatch Exchange `.ase` を書き出します。
- 画像メタデータ、抽出設定、アクセシブルなスウォッチカード、エスケープ済みのユーザー由来値、ブラウザー確認やデザイン講評向けのコントラスト指針を含む、単体 HTML コンタクトシートレポートを生成します。
- ターミナルで素早く確認できるコンパクトな要約を表示します。
- `--sample-limit` で自動サンプリングの目標を設定でき、再現性のある確認向けには決定的な `--sample-step` の上書きも使えます。
- `--ignore-color HEX` により、フラットなスクリーンショット背景など、完全一致する RGB 色をパレット順位付けの前に除外し、残ったサンプリング済みピクセルから割合を再計算できます。
- `--cluster-distance N` により、順位付けの前に視覚的に近いサンプリング済み RGB 色を任意でグループ化できます。小さな決定的なローカル距離計算を使い、加重平均色を代表色にします。
- `--sort {frequency,luminance,hue}` により、既定の頻度順を保つか、抽出後の選択済みスウォッチを暗い順または色相角順に並べ替えてデザイン確認できます。
- `--precision N` により、JSON、CSV、Markdown、プレーンテキスト、SVG、HTML、ターミナル要約のレポート用割合と相対輝度を 0 から 6 桁の小数で整形できます。省略時は既存の既定出力を保ちます。
- 任意の `--names` ヒントにより、red、teal、blue、brown、black、white、gray などの小さな組み込み近似名セットへ色を対応付けます。
- 2 枚のローカル画像向けのパレット比較レポートで、主要色の変化、共有色、追加色、削除色、重なりに基づく決定的なドリフトスコアを、ターミナル、JSON、単体 HTML、ポータブル Markdown、プレーンテキストで確認できます。
- ソースチェックアウト内で、小さな決定的 PNG と任意の Markdown 索引を含むサンプル素材ギャラリーを生成し、パレット抽出とレポートコマンドの教材に使えます。

## インストール

このプロジェクトはパッケージレジストリには公開されていません。ソースチェックアウトからのみインストールしてください。

```bash
git clone https://github.com/codecat-ai/swatch-story.git
cd swatch-story
python -m pip install -e ".[dev]"
```

## クイックスタート

```bash
swatch-story image.png --colors 6 --json story.json --csv story.csv --css story.css --html story.html --markdown story.md --text story.txt --svg story.svg --gpl story.gpl --ase story.ase --title "Launch Palette"
```

このコマンドはターミナル要約を表示し、指定された場合は `story.json`、`story.csv`、`story.css`、`story.html`、`story.md`、`story.txt`、`story.svg`、`story.gpl`、`story.ase` を書き出します。

同じソースチェックアウトからローカル教材用素材を生成します。

```bash
swatch-story gallery demo-gallery
```

gallery コマンドは小さな決定的 PNG ファイルと `demo-gallery/README.md` を書き出します。README には、それらのサンプルからパレットやレポートを作るコマンドが含まれます。

## 例

Markdown 索引なしでサンプル PNG 素材だけを生成します。

```bash
swatch-story gallery demo-gallery --no-index
```

JSON レポートだけを作成します。

```bash
swatch-story poster.png --colors 5 --json poster-colors.json
```

表計算ソフトで扱いやすい CSV レポートを作成します。

```bash
swatch-story poster.png --colors 5 --csv poster-colors.csv
```

固定サンプリング間隔で共有しやすいローカル HTML レポートを作成します。

```bash
swatch-story screenshot.png --colors 8 --sample-step 2 --html screenshot-story.html
```

固定間隔を手動で選ばずに、非常に大きな画像の自動サンプリング目標を調整します。

```bash
swatch-story mural.png --colors 8 --sample-limit 25000 --json mural-colors.json
```

パレット順位付けの前にフラットな背景色を無視します。

```bash
swatch-story screenshot.png --colors 6 --ignore-color ffffff --json screenshot-colors.json
```

順位付けの前に近いサンプリング色をグループ化します。

```bash
swatch-story photo.png --colors 6 --cluster-distance 12 --json photo-colors.json
```

抽出後の選択済みスウォッチを暗い順に並べ替えます。

```bash
swatch-story poster.png --colors 6 --sort luminance --html poster-luminance.html
```

選択済みの有彩色スウォッチを色相角順に並べ、グレースケール色を有彩色の後に置きます。

```bash
swatch-story poster.png --colors 6 --sort hue --json poster-hue.json
```

コンパクトな確認出力向けに、レポートの割合と相対輝度を丸めます。

```bash
swatch-story poster.png --colors 6 --precision 1 --json poster-colors.json --markdown poster-colors.md --svg poster-colors.svg --html poster-colors.html
```

2 枚のローカル画像を比較し、JSON、CSV、HTML、Markdown、プレーンテキストのドリフトレポートを書き出します。

```bash
swatch-story compare before.png after.png --colors 6 --sample-step 1 --json palette-drift.json --csv palette-drift.csv --html palette-drift.html --markdown palette-drift.md --text palette-drift.txt
```

`compare` コマンドは、前後の画像パス、それぞれの主要色、共有色、追加色、削除色、ドリフトスコアを含む簡潔なターミナルレポートを表示します。スコアは選択済みパレットの HEX 値のうち変化した割合で、`100 * (1 - shared / union)` として計算します。`0%` は選択済みパレットの HEX 値が同一であること、`100%` は重なりがないことを意味します。

比較 CSV レポートは、スプレッドシートでパレットドリフトを確認するための決定的な UTF-8 表です。比較 HTML レポートは、ブラウザーで確認できる単体のローカルファイルです。比較 Markdown レポートは、メモ、Issue コメント、デザインドキュメントに向いたポータブルな表です。比較プレーンテキストレポートは、メール、チケット、レビューログ向けの決定的な UTF-8 ドリフトシートです。これらのレポートは、安全に表現された前後ソース名とパス、各側の主要色、共有色、追加色、削除色、空の変更リストに対する明確な `None` 状態、ドリフトスコアを含みます。同じ `compare` コマンドで `--json`、`--csv`、`--html`、`--markdown`、`--text` を同時に指定できます。

HTML レポートはブラウザーで確認しやすいコンタクトシートです。画像名とパス、サイズ、指定した色数、実際のサンプリング間隔、クラスタ距離、並べ替えモード、近似名の有無、短い要約を表示し、各スウォッチカードには HEX、RGB、相対輝度、読みやすい文字色、コントラスト指針が含まれます。

SVG レポートは、ドキュメントやスライド向けの単体ローカルスウォッチシートです。タイトル、元ファイル名、画像サイズ、抽出設定を表示し、各スウォッチ行には色の矩形、HEX、任意の近似名、割合、輝度、ラベル、読みやすい文字色が含まれます。ユーザー由来のタイトル、元ファイル名、ラベル、名前は XML エスケープされ、元画像自体は埋め込まれません。

スタイルシートで使える CSS カスタムプロパティを作成します。

```bash
swatch-story poster.png --colors 5 --css poster-colors.css
```

メモやドキュメント向けのポータブルな Markdown レポートを作成します。

```bash
swatch-story poster.png --colors 5 --markdown poster-colors.md --title "Poster Palette"
```

メール、チケット、授業メモに貼り付けやすいプレーンテキストのパレットシートを作成します。

```bash
swatch-story poster.png --colors 5 --text poster-colors.txt --title "Poster Palette"
```

ドキュメントやスライド向けの単体 SVG スウォッチシートを作成します。

```bash
swatch-story poster.png --colors 5 --svg poster-colors.svg --title "Poster Palette"
```

デザインツール向けの GIMP パレットを作成します。

```bash
swatch-story poster.png --colors 5 --gpl poster-colors.gpl --title "Poster Palette"
```

デザインツール向けの Adobe Swatch Exchange パレットを作成します。

```bash
swatch-story poster.png --colors 5 --ase poster-colors.ase --title "Poster Palette"
```

JSON、CSV、HTML、Markdown、プレーンテキスト、SVG、GIMP と ASE パレットのラベル、CSS コメント、ターミナル要約に近似的な一般色名ヒントを含めます。

```bash
swatch-story poster.png --colors 5 --names --json poster-colors.json --csv poster-colors.csv --markdown poster-colors.md
```

CSS 出力例：

```css
/* Generated by swatch-story. */
:root {
  --swatch-story-color-1: #112233;
  --swatch-story-color-1-rgb: 17, 34, 51;
  --swatch-story-color-1-text: white;
}
```

パレット項目の例：

```json
{
  "rank": 1,
  "hex": "#112233",
  "rgb": [17, 34, 51],
  "count": 120,
  "percent": 32.43,
  "luminance": 0.015,
  "best_text_color": "white",
  "label": "dark"
}
```

CSV 出力例：

```csv
rank,hex,r,g,b,count,percent,luminance,best_text_color,label,name
1,#112233,17,34,51,120,32.43,0.015,white,dark,
```

プレーンテキスト出力例：

```text
Poster Palette

Source: poster.png
Image size: 1200 x 800 px
Settings: colors 2; sample step 1; sample limit 10000; cluster distance 0; sort frequency; ignored color none; names not included

Swatches:
1. #112233 | rgb(17, 34, 51) | 32.43% | dark | text white
2. #eeeeee | rgb(238, 238, 238) | 18.25% | light | text black
```

GIMP パレット出力例：

```text
GIMP Palette
Name: Poster Palette
Columns: 2
# Generated by swatch-story.
 17  34  51 #112233
238 238 238 #eeeeee
```

`--names` を使うと、パレット項目には近似的な一般色名ヒントが追加されます。

```json
{
  "rank": 1,
  "hex": "#112233",
  "rgb": [17, 34, 51],
  "count": 120,
  "percent": 32.43,
  "luminance": 0.015,
  "best_text_color": "white",
  "label": "dark",
  "name": "black"
}
```

JSON 設定には `cluster_distance` と選択した並べ替えモード、例えば `"cluster_distance": 0` と `"sort": "frequency"` が含まれます。`--ignore-color` を使うと、JSON 設定には正規化された小文字の値、例えば `"ignore_color": "#ffffff"` が含まれます。無視されたピクセルは任意のクラスタリングと順位付けの前に除外されるため、スウォッチの割合は残ったサンプリング済みピクセルだけを基準に計算されます。

比較 JSON 出力例：

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
  "drift_score": 66.67
}
```

比較プレーンテキスト出力例：

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
Drift score: 66.67%
```

## 設定

`swatch-story` は CLI オプションだけで設定します。

- `--colors N`: レポートする色数です。2 から 12 まで指定できます。既定値は 6 です。
- `--json PATH`: JSON レポートを書き出します。
- `--csv PATH`: UTF-8 CSV レポートを書き出します。列は `rank`、`hex`、`r`、`g`、`b`、`count`、`percent`、`luminance`、`best_text_color`、`label`、`name` で安定しています。
- `--css PATH`: CSS カスタムプロパティを書き出します。
- `--html PATH`: 単体 HTML レポートを書き出します。
- `--markdown PATH`: ポータブルな Markdown レポートを書き出します。
- `--text PATH`: UTF-8 プレーンテキストのパレットシートを書き出します。タイトル、元ファイル名、画像サイズ、抽出設定、各スウォッチの順位、HEX、RGB の組、割合、ラベル、最適な文字色、任意の名前ヒントを含みます。
- `--svg PATH`: 決定的な UTF-8 単体 SVG スウォッチシートを書き出します。タイトル、元ファイル名、画像サイズ、抽出設定、各スウォッチ行の色矩形、HEX、任意の名前ヒント、割合、輝度、ラベル、読みやすい文字色を含みます。
- `--gpl PATH`: 決定的な GIMP `.gpl` パレットを書き出します。
- `--ase PATH`: 決定的な Adobe Swatch Exchange `.ase` パレットを書き出します。
- `--sample-step N`: N ピクセルごとにサンプリングします。既定では、小さい画像は全ピクセルを使い、大きい画像は決定的な自動ステップを使います。
- `--sample-limit N`: `--sample-step` が省略された場合に、自動ステップが目標とするサンプリング済みピクセル数を指定します。既定値は 10000 です。1 以上である必要があります。`--sample-step` が指定された場合、固定ステップがピクセル走査を制御しますが、JSON 設定には選択された `sample_limit` と実際の `sample_step` が含まれます。
- `--ignore-color HEX`: パレット順位付けの前に、十六進 RGB 色と完全一致するサンプリング済みピクセルを除外します。`#rrggbb` または `rrggbb` を受け付け、大文字小文字は区別しません。JSON/レポート設定には正規化された小文字の `#rrggbb` 値が保存されます。すべてのサンプリング済みピクセルが無視された場合、または値が有効な十六進 RGB でない場合、コマンドは明確なエラーで終了します。
- `--cluster-distance N`: 0 より大きい場合、パレット順位付けの前に似ているサンプリング済み RGB 色をグループ化します。値は 0 から 255 の範囲で指定します。既定値は 0 で、完全一致 RGB バケットの挙動を保ちます。クラスタの代表色は、サンプリング済みピクセル数で重み付けした RGB の丸め平均です。
- `--sort {frequency,luminance,hue}`: 選択済みパレット項目の順序を指定します。`frequency` はサンプリング済みピクセル数による既定の順位を保ち、`luminance` はスウォッチを暗い順から明るい順に並べ替え、`hue` は HSV 色相角順の有彩色スウォッチの後にグレースケールまたはほぼグレースケールのスウォッチを置きます。並べ替え後のパレットは 1 から順位を振り直します。既定値は `frequency` です。
- `--precision N`: ユーザー向けレポートの割合と相対輝度を `N` 桁の小数で整形します。範囲は 0 から 6 です。省略時は既存の JSON 数値とレポート文字列を保ちます。このオプションは通常のパレット抽出の JSON、CSV、Markdown、プレーンテキスト、SVG、HTML、ターミナル要約に適用されます。CSS、GIMP `.gpl`、Adobe `.ase` などのデザインツール向けパレット形式は、それぞれの形式固有の出力を保ちます。
- `--title TEXT`: HTML、Markdown、プレーンテキスト、SVG、GIMP パレット、ASE 出力のタイトルです。既定値は `Swatch Story` です。
- `--names`: 決定的でオフラインの近似的な一般色名ヒントを含めます。名前は小さな組み込み RGB 参照セットから選ばれ、人が読みやすい色系統のヒントを目的としており、厳密な色名ではありません。

`swatch-story compare BEFORE_IMAGE AFTER_IMAGE [options]` は、`--colors`、`--sample-step`、`--sample-limit`、`--ignore-color`、`--cluster-distance`、`--sort`、`--names` を再利用します。比較モードでは、`--json PATH` は単一画像レポートではなく、決定的な比較 JSON レポートを書き出し、`--csv PATH` はメタデータと共有/追加/削除色行を含む決定的な UTF-8 比較 CSV を書き出し、`--html PATH` は単体 HTML 比較レポートを書き出し、`--markdown PATH` はポータブルな Markdown 比較レポートを書き出し、`--text PATH` は UTF-8 プレーンテキストのドリフトレポートを書き出します。これらの出力は同時に指定できます。

`swatch-story gallery OUT_DIR [--no-index] [--force]` は、組み込みサンプル PNG 素材を書き出し、既定ではソースチェックアウト用コマンドを含む Markdown `README.md` gallery も生成します。`--force` がない限り、既存の gallery ファイルは上書きしません。

MVP は設定ファイルを読み込まず、リモート画像の取得もしません。

## 開発

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest -q
python -m build
```

## テスト

テストスイートは小さな合成画像を作り、パレット比率、コントラスト用テキスト色、レポート描画、CLI ファイル出力を検証します。

```bash
pytest -q
```

## ロードマップ
- CIELAB など、より正式な色モデルに基づく任意の知覚色空間クラスタリングで、視覚的なまとまりをさらに近づける。
- 生成された gallery 素材向けの任意 JSON マニフェストにより、教材が Markdown を再解析せずに期待される主要色を検証できるようにする。
- HTML レポートで任意の横並びパレットプレビューサムネイルを表示し、視覚確認を速くする。

## コントリビュート

コントリビューションを歓迎します。[CONTRIBUTING.md](CONTRIBUTING.md) を読み、振る舞いを変える前に振る舞い重視のテストを追加し、README 翻訳の意味を同期してください。

## ライセンス

MIT。詳しくは [LICENSE](LICENSE) を参照してください。

## AI 支援メンテナンス

このプロジェクトではメンテナンス作業に AI 支援を使う場合があります。メンテナーはリリース前に変更を確認し、他のプロジェクトのコードや文章を意図的にコピーしません。
