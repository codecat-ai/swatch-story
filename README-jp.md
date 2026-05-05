# swatch-story

[English](README.md) | [中文](README-zh.md) | [日本語](README-jp.md)


`swatch-story` は、画像からコンパクトな色のストーリーを抽出し、機械可読な JSON と単体で開ける HTML レポートを書き出すローカル優先の画像ユーティリティです。

## 課題と動機

スクリーンショット、カバー画像、ポスター、教材画像には有用な色の情報が含まれることがあります。しかし、手軽なパレットツールはオンラインサービス前提だったり、単なる HEX 値だけを返したりしがちです。`swatch-story` は画像をローカルに保ち、割合、輝度ラベル、読みやすい黒/白の文字色候補を加えることで、デザインメモ、ドキュメント、授業、小さな制作ワークフローで使いやすい出力を提供します。

## 機能

- Pillow を使い、ローカル画像ファイルから決定的にパレットを抽出します。
- JSON 出力には、元ファイル名、画像サイズ、色の順位、HEX、RGB、カウント、割合、相対輝度、読みやすい黒/白の文字色、明暗ラベルが含まれます。
- アクセシブルなスウォッチを含む単体 HTML レポートを生成し、レポートタイトルはエスケープされます。
- ターミナルで素早く確認できるコンパクトな要約を表示します。

## インストール

このプロジェクトはパッケージレジストリには公開されていません。GitHub からクローンしてローカルにインストールしてください。

```bash
git clone https://github.com/codecat-ai/swatch-story.git
cd swatch-story
python -m pip install -e ".[dev]"
```

## クイックスタート

```bash
swatch-story image.png --colors 6 --json story.json --html story.html --title "Launch Palette"
```

このコマンドはターミナル要約を表示し、指定された場合は `story.json` と `story.html` を書き出します。

## 例

JSON レポートだけを作成します。

```bash
swatch-story poster.png --colors 5 --json poster-colors.json
```

固定サンプリング間隔で共有しやすいローカル HTML レポートを作成します。

```bash
swatch-story screenshot.png --colors 8 --sample-step 2 --html screenshot-story.html
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

## 設定

`swatch-story` は CLI オプションだけで設定します。

- `--colors N`: レポートする色数です。2 から 12 まで指定できます。既定値は 6 です。
- `--json PATH`: JSON レポートを書き出します。
- `--html PATH`: 単体 HTML レポートを書き出します。
- `--sample-step N`: N ピクセルごとにサンプリングします。既定では、小さい画像は全ピクセルを使い、大きい画像は決定的な自動ステップを使います。
- `--title TEXT`: HTML レポートのタイトルです。既定値は `Swatch Story` です。

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

テストスイートは小さな合成画像を作成し、パレット割合、コントラストに基づく文字色、レポート描画、CLI のファイル出力を検証します。

```bash
pytest -q
```

## ロードマップ

- 一般的なパレット向けの任意の色名ヒント。
- CSS カスタムプロパティや Markdown テーブルなどの追加エクスポート形式。
- 教材やポートフォリオ向けの追加レポートレイアウト。
- 非常に大きな画像向けのサンプリング戦略改善。

## コントリビュート

コントリビューションを歓迎します。[CONTRIBUTING.md](CONTRIBUTING.md) を読み、振る舞いを変える前に振る舞い重視のテストを追加し、README 翻訳の意味を同期してください。

## ライセンス

MIT。詳しくは [LICENSE](LICENSE) を参照してください。

## AI 支援メンテナンス

このプロジェクトではメンテナンス作業に AI 支援を使う場合があります。メンテナーはリリース前に変更を確認し、他のプロジェクトのコードや文章を意図的にコピーしません。
