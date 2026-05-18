# swatch-story

[English](README.md) | [中文](README-zh.md) | [日本語](README-ja.md)


`swatch-story` は、画像からコンパクトな色のストーリーを抽出し、機械可読な JSON、デザイントークン JSON、UTF-8 CSV、CSS カスタムプロパティ、ポータブルな Markdown、WCAG 監査 Markdown、貼り付けやすいプレーンテキスト、単体 SVG スウォッチシート、GIMP `.gpl` パレット、Adobe Swatch Exchange `.ase` パレット、単体で開ける HTML レポートを書き出すローカル優先の画像ユーティリティです。

## 課題と動機

スクリーンショット、カバー画像、ポスター、教材画像には有用な色の情報が含まれることがあります。しかし、手軽なパレットツールはオンラインサービス前提だったり、単なる HEX 値だけを返したりしがちです。`swatch-story` は画像をローカルに保ち、割合、安定したトークンラベル、黒/白文字のコントラスト比を加えることで、デザインメモ、ドキュメント、授業、小さな制作ワークフローで使いやすい出力を提供します。

## 機能

- Pillow を使い、ローカル画像ファイルから決定的にパレットを抽出します。
- JSON 出力には、安定した `schema_version: 1`、ソースファイル名、ソースパス、画像サイズ、抽出設定、色の順位、HEX、RGB、カウント、割合、相対輝度、黒/白テキストとのコントラスト比、読みやすいテキスト色、安定したトークンラベルが含まれます。
- メイン画像コマンドでは、Design Tokens Community Group schema メタデータ、安定した色トークンキー、`$type: color`、`$value`、読みやすいコントラスト指針、トークンパイプライン向けの `extensions.swatchStory` 指標を含むデザイントークン JSON を書き出せます。
- UTF-8 CSV 出力には、表計算ソフトでの並べ替え、絞り込み、軽量なデータ処理に使いやすい安定した列が含まれます。
- CSS カスタムプロパティ出力には、HEX、RGB の組、黒/白のコントラスト比、読みやすい文字色の変数が含まれます。
- ポータブルな Markdown レポートには、パレットのメタデータとメモやドキュメント向けの表が含まれます。
- WCAG 監査 Markdown には、通常文字と大きな文字の AA/AAA しきい値、黒/白文字の準備度、推奨文字色、スウォッチごとの簡潔な推奨事項が含まれます。
- プレーンテキストのパレットシートには、元ファイルのメタデータ、抽出設定、メール、チケット、授業メモに貼り付けやすいスウォッチごとの 1 行が含まれます。
- 単体 SVG スウォッチシートには、元ファイルのメタデータ、抽出設定、色ブロック、HEX 値、任意の名前、割合、輝度、黒/白のコントラスト比、ラベル、読みやすい文字色の指針が含まれ、ドキュメントやスライドに使いやすくなっています。
- デザインツールと連携しやすい、決定的な GIMP `.gpl` パレットを書き出します。
- レポートタイトルでグループ化した RGB スウォッチを含む、決定的な Adobe Swatch Exchange `.ase` を書き出します。
- 画像メタデータ、抽出設定、アクセシブルなスウォッチカード、エスケープ済みのユーザー由来値、ブラウザー確認やデザイン講評向けのコントラスト指針を含む、単体 HTML コンタクトシートレポートを生成します。
- HTML レポートでは `--html-thumbnail PATH` によりローカルのサイドカーサムネイルを生成してリンクでき、元画像を base64 として HTML に埋め込みません。
- ターミナルで素早く確認できるコンパクトな要約を表示します。
- `--sample-limit` で自動サンプリングの目標を設定でき、再現性のある確認向けには決定的な `--sample-step` の上書きも使えます。
- `--ignore-color HEX` により、フラットなスクリーンショット背景など、完全一致する RGB 色をパレット順位付けの前に除外し、残ったサンプリング済みピクセルから割合を再計算できます。
- `--matte HEX` により、透明または半透明ピクセルを指定した背景色に合成してから抽出でき、暗い面、明るい面、ブランド背景上での見え方に合わせてアイコンやロゴをサンプリングできます。
- `--cluster-distance N` により、順位付けの前に近いサンプリング色を任意でグループ化できます。`--cluster-space {rgb,lab}` は既存の決定的な RGB-ish 既定値を保つか、ローカルの sRGB から CIELAB への変換と Lab ユークリッド距離による知覚的なグループ化を使います。
- `--sort {frequency,luminance,hue}` により、既定の頻度順を保つか、抽出後の選択済みスウォッチを暗い順または色相角順に並べ替えてデザイン確認できます。
- `--precision N` により、JSON、デザイントークン JSON、CSV、Markdown、WCAG 監査、プレーンテキスト、SVG、HTML、ターミナル要約のレポート用割合、相対輝度、コントラスト比を 0 から 6 桁の小数で整形できます。省略時は既存の既定出力を保ちます。
- `--label-prefix PREFIX` により、メイン画像コマンドの既定ラベル `color-1`、`color-2` を、`brand-1`、`brand-2` のようなデザイントークンラベルに置き換えられ、`--tokens` のキーにも反映されます。
- `--preset PATH` により、メイン画像、`compare`、`baseline`、`batch` コマンドで再利用できるローカル JSON 抽出プリセットを読み込み、明示した CLI フラグでプリセット値を上書きできます。
- 任意の `--names` ヒントにより、red、teal、blue、brown、black、white、gray などの小さな組み込み近似名セットへ色を対応付けます。
- 2 枚のローカル画像向けのパレット比較レポートで、主要色の変化、コンパクトな HTML 横並びパレットプレビュー、共有色、追加色、削除色、重なりに基づく決定的なドリフトスコアを、ターミナル、JSON、単体 HTML、ポータブル Markdown、プレーンテキストで確認できます。
- ベースラインドリフトレビューでは、1 枚の参照画像を複数の候補画像と比較し、ドリフトスコアで順位付けし、決定的な JSON、Markdown、プレーンテキスト、単体 HTML ダッシュボードレポートを書き出せます。
- 2 枚以上のローカル画像監査を、画像ごとのセクション/カード、主要色、パレット行、コントラスト指針、エスケープ済みユーザー由来値、共通抽出設定を含む決定的な Markdown または単体 HTML のチームレビューレポートにまとめられます。
- ローカル JSON プリセット検出により、チームレビュー準備向けの決定的なターミナル検証要約と任意の JSON レポートを作成できます。
- ソースチェックアウト内で、小さな決定的 PNG、安定した授業テーマタグ、任意の Markdown 索引、任意の JSON マニフェストを含むサンプル素材ギャラリーを生成し、パレット抽出の教材や素材の検証に使えます。

## インストール

このプロジェクトはパッケージレジストリには公開されていません。ソースチェックアウトからのみインストールしてください。

```bash
git clone https://github.com/codecat-ai/swatch-story.git
cd swatch-story
python -m pip install -e ".[dev]"
```

## クイックスタート

```bash
swatch-story image.png --colors 6 --json story.json --tokens story.tokens.json --csv story.csv --css story.css --html story.html --markdown story.md --wcag-audit story-audit.md --text story.txt --svg story.svg --gpl story.gpl --ase story.ase --title "Launch Palette"
```

このコマンドはターミナル要約を表示し、指定された場合は `story.json`、`story.tokens.json`、`story.csv`、`story.css`、`story.html`、`story.md`、`story-audit.md`、`story.txt`、`story.svg`、`story.gpl`、`story.ase` を書き出します。

同じソースチェックアウトからローカル教材用素材を生成します。

```bash
swatch-story gallery demo-gallery
```

gallery コマンドは小さな決定的 PNG ファイルと `demo-gallery/README.md` を書き出します。README には、それらのサンプルからパレットやレポートを作るコマンドとタグが含まれます。教材やテストで期待される主要色、パレット HEX 値、安定した授業テーマタグを含む `demo-gallery/manifest.json` が必要な場合は、`--manifest` を追加します。

複数のローカル画像向けにチームレビューレポートを作成します。

```bash
swatch-story batch hero.png card.png poster.png --colors 6 --markdown team-review.md --html team-review.html
```

参照パレットに対して候補画像を順位付けします。

```bash
swatch-story baseline reference.png option-a.png option-b.png --colors 6 --markdown baseline-review.md --text baseline-review.txt --html baseline-review.html
```

## 例

Markdown 索引なしでサンプル PNG 素材だけを生成します。

```bash
swatch-story gallery demo-gallery --no-index
```

Markdown 索引なしで、PNG 素材と機械可読マニフェストを生成します。

```bash
swatch-story gallery demo-gallery --manifest --no-index
```

要求した授業タグをすべて含むサンプルだけを生成します。

```bash
swatch-story gallery demo-gallery --manifest --tag contrast --tag accessibility
```

JSON レポートだけを作成します。

```bash
swatch-story poster.png --colors 5 --json poster-colors.json
```

暗いマット上での見え方として透明ロゴを抽出します。

```bash
swatch-story logo.png --colors 5 --matte 111827 --json logo-dark-colors.json
```

トークンパイプライン向けのデザイントークン JSON を作成します。

```bash
swatch-story poster.png --colors 5 --tokens poster.tokens.json --title "Poster Palette"
```

表計算ソフトで扱いやすい CSV レポートを作成します。

```bash
swatch-story poster.png --colors 5 --csv poster-colors.csv
```

固定サンプリング間隔で共有しやすいローカル HTML レポートを作成します。

```bash
swatch-story screenshot.png --colors 8 --sample-step 2 --html screenshot-story.html
```

元画像を素早く確認するための小さなサイドカーサムネイル付きローカル HTML レポートを作成します。

```bash
swatch-story screenshot.png --colors 8 --html reports/screenshot-story.html --html-thumbnail reports/assets/screenshot-thumb.png
```

固定間隔を手動で選ばずに、非常に大きな画像の自動サンプリング目標を調整します。

```bash
swatch-story mural.png --colors 8 --sample-limit 25000 --json mural-colors.json
```

パレット順位付けの前にフラットな背景色を無視します。

```bash
swatch-story screenshot.png --colors 6 --ignore-color ffffff --json screenshot-colors.json
```

順位付けの前に透明ピクセルをブランド背景色へ合成します。

```bash
swatch-story icon.png --colors 4 --matte "#003366" --json icon-brand-colors.json
```

順位付けの前に近いサンプリング色をグループ化します。

```bash
swatch-story photo.png --colors 6 --cluster-distance 12 --json photo-colors.json
```

RGB チャンネル差と見た目の近さが一致しにくい場合は、知覚的な Lab 空間クラスタリングを使います。

```bash
swatch-story photo.png --colors 6 --cluster-distance 5 --cluster-space lab --json photo-lab-colors.json
```

Lab クラスタリングは、圧縮、アンチエイリアス、グラデーションによって RGB は少し違っても同じ視覚色として扱いたいピクセルが多いスクリーンショット、書き出した artwork、デザインレビュー用画像に向いています。選択した `cluster_space` と `cluster_distance` は JSON とレンダリング済みレポート設定に記録されるため、compare、baseline、batch レポートを後から確認できます。

抽出後の選択済みスウォッチを暗い順に並べ替えます。

```bash
swatch-story poster.png --colors 6 --sort luminance --html poster-luminance.html
```

選択済みの有彩色スウォッチを色相角順に並べ、グレースケール色を有彩色の後に置きます。

```bash
swatch-story poster.png --colors 6 --sort hue --json poster-hue.json
```

コンパクトな確認出力向けに、レポートの割合、相対輝度、コントラスト比を丸めます。

```bash
swatch-story poster.png --colors 6 --precision 1 --json poster-colors.json --tokens poster.tokens.json --markdown poster-colors.md --svg poster-colors.svg --html poster-colors.html
```

生成レポートにデザイントークン用のラベル接頭辞を適用します。

```bash
swatch-story poster.png --colors 5 --label-prefix brand --tokens poster.tokens.json --json poster-colors.json --css poster-colors.css
```

明示した CLI フラグを優先しながら、ローカル JSON 抽出プリセットを再利用します。

```json
{
  "colors": 5,
  "sample_step": 1,
  "matte": "111827",
  "names": true,
  "precision": 1,
  "label_prefix": "brand",
  "title": "Poster Palette"
}
```

```bash
swatch-story poster.png --preset presets/poster.json --colors 6 --json poster-colors.json --tokens poster.tokens.json
```

レビューセッション前に共有プリセットを検証します。

```bash
swatch-story presets presets/poster.json presets/baseline.json --json preset-validation.json
```

2 枚のローカル画像を比較し、JSON、CSV、HTML、Markdown、プレーンテキストのドリフトレポートを書き出します。

```bash
swatch-story compare before.png after.png --colors 6 --sample-step 1 --matte 111827 --min-delta-percent 2 --json palette-drift.json --csv palette-drift.csv --html palette-drift.html --markdown palette-drift.md --text palette-drift.txt
```

ドリフトスナップショットで知覚的クラスタリングを使う場合は、両側に同じ Lab 抽出設定を適用します。

```bash
swatch-story compare before.png after.png --colors 6 --cluster-distance 5 --cluster-space lab --json palette-drift.json
```

`compare` コマンドは、前後の画像パス、それぞれの主要色、共有色、追加色、削除色、共有色の割合変化、ドリフトスコアを含む簡潔なターミナルレポートを表示します。スコアは選択済みパレットの HEX 値のうち変化した割合で、`100 * (1 - shared / union)` として計算します。`0%` は選択済みパレットの HEX 値が同一であること、`100%` は重なりがないことを意味します。`--min-delta-percent N` を使うと、絶対値で `N` 未満の割合変化しかない共有色の詳細行を非表示にできます。追加色と削除色は引き続き表示されます。

比較 CSV レポートは、スプレッドシートでパレットドリフトを確認するための決定的な UTF-8 表です。比較 HTML レポートは、各画像にコンパクトな CSS-only 横並びパレットプレビューを含む、ブラウザーで確認できる単体のローカルファイルです。比較 Markdown レポートは、メモ、Issue コメント、デザインドキュメントに向いたポータブルな表です。比較プレーンテキストレポートは、メール、チケット、レビューログ向けの決定的な UTF-8 ドリフトシートです。これらのレポートは、安全に表現された前後ソース名とパス、各側の主要色、共有色、追加色、削除色、フィルター済みの色変化詳細、空の変更リストに対する明確な `None` 状態、ドリフトスコアを含みます。同じ `compare` コマンドで `--json`、`--csv`、`--html`、`--markdown`、`--text` を同時に指定できます。

1 枚のベースライン画像を複数の候補画像と比較し、ドリフトで順位付けします。

```bash
swatch-story baseline reference.png draft-a.png draft-b.png --colors 6 --sample-step 1 --names --title "Baseline Drift Review" --json baseline-drift.json --markdown baseline-drift.md --text baseline-drift.txt --html baseline-drift.html
```

小さな RGB 差を別々のドリフト色として扱いたくない場合は、ベースラインとすべての候補に同じ Lab クラスタリング設定を使います。

```bash
swatch-story baseline reference.png draft-a.png draft-b.png --colors 6 --cluster-distance 5 --cluster-space lab --json baseline-drift.json
```

`baseline` コマンドには、1 枚のベースライン画像、少なくとも 1 枚の候補画像、そして `--json PATH`、`--markdown PATH`、`--text PATH`、`--html PATH` の少なくとも 1 つが必要です。4 つの出力は同時に指定できます。各候補に `compare` と同じドリフトロジックを使い、JSON では候補を入力順に保ちながら順位とドリフトスコアを含め、Markdown/テキスト/HTML の要約はドリフトスコア降順で並べます。ベースラインレポートには、ベースラインのソースメタデータ、候補のソースメタデータ、共有色、追加色、削除色、フィルター済みの色変化詳細、エスケープ済みのユーザー由来タイトル、名前、パスが含まれます。ベースライン HTML レポートは単体ダッシュボードで、決定的なインライン CSS、メタデータパネル、並べ替え可能に見える候補順位表、共有/追加/削除/変化色リストの視覚的なスウォッチを含みます。

複数のローカル画像監査を 1 つのチームレビューレポートにまとめます。

```bash
swatch-story batch hero.png card.png poster.png --colors 6 --sample-step 1 --names --title "Campaign Palette Review" --markdown campaign-review.md --html campaign-review.html
```

すべての入力で見た目の近いサンプリング色をまとめるコンパクトなチームスナップショットには、batch 抽出設定に Lab クラスタリングを追加します。

```bash
swatch-story batch hero.png card.png poster.png --colors 6 --cluster-distance 5 --cluster-space lab --markdown campaign-review.md
```

`batch` コマンドには少なくとも 2 つの画像パスと、`--markdown PATH` または `--html PATH` の少なくとも一方が必要です。両方の出力を同時に指定できます。すべての画像に同じ決定的なパレット抽出設定を適用し、各ソース画像についてソース名/パス、画像サイズ、主要色、パレット行/カード、黒/白文字のコントラスト指針を含む Markdown セクションまたは HTML カードを書き出します。ユーザー由来のタイトル、ファイル名、パス、ラベル、名前はエスケープされ、ファイルは決定的な UTF-8 として書き込まれます。

プリセットファイルは、コマンド間で決定的な抽出既定値を共有するためのローカル JSON オブジェクトです。使用できるキーは `colors`、`sample_step`、`sample_limit`、`ignore_color`、`matte`、`cluster_distance`、`cluster_space`、`sort`、`names`、`precision`、`label_prefix`、`title`、`min_delta_percent` です。メイン画像コマンドは抽出設定に加えて `names`、`precision`、`label_prefix`、`title` を使い、`compare` と `baseline` は共通抽出設定に加えて `names`、`precision`、`title`、`min_delta_percent` を使い、`batch` は共通抽出設定に加えて `names`、`precision`、`title` を使います。コマンドラインで入力したフラグは常にプリセット値を上書きします。プリセットはローカルファイルである必要があり、URL、存在しないファイル、不正な JSON、オブジェクト以外の JSON、不明なキー、不正な値はレポートを書き出す前に失敗します。`swatch-story presets PATH [PATH ...]` を使うと、画像ファイルを読まずに 1 つ以上のローカルプリセットを検証できます。このコマンドは各入力パス、`valid` ステータス、ソート済みの対応キーを表示し、空のプリセットでは `keys: none` と表示します。`--json PATH` を追加すると、すべてのプリセットが検証に成功した後で決定的なレポートを書き出します。

HTML レポートはブラウザーで確認しやすいコンタクトシートです。画像名とパス、サイズ、指定した色数、実際のサンプリング間隔、クラスタ距離と空間、並べ替えモード、近似名の有無、短い要約を表示し、各スウォッチカードには HEX、RGB、相対輝度、黒/白のコントラスト比、読みやすい文字色、コントラスト指針が含まれます。`--html PATH` と一緒に `--html-thumbnail PATH` を指定すると、元画像から上限付きのローカルサムネイルを生成し、可能な場合は相対パスでリンクします。元画像は base64 として埋め込まれません。

SVG レポートは、ドキュメントやスライド向けの単体ローカルスウォッチシートです。タイトル、元ファイル名、画像サイズ、抽出設定を表示し、各スウォッチ行には色の矩形、HEX、任意の近似名、割合、輝度、黒/白のコントラスト比、ラベル、読みやすい文字色が含まれます。ユーザー由来のタイトル、元ファイル名、ラベル、名前は XML エスケープされ、元画像自体は埋め込まれません。

デザイントークン JSON レポートは、デザイントークンパイプライン向けです。抽出されたラベルを各 `color` キーとして使うため、`--label-prefix brand` は `brand-1` などのキーを生成します。`--precision N` はトークン内の割合、輝度、コントラスト比、説明文も丸めます。このオプションはメイン画像コマンドだけで使え、`compare` や `gallery` では使えません。

スタイルシートで使える CSS カスタムプロパティを作成します。

```bash
swatch-story poster.png --colors 5 --css poster-colors.css
```

メモやドキュメント向けのポータブルな Markdown レポートを作成します。

```bash
swatch-story poster.png --colors 5 --markdown poster-colors.md --title "Poster Palette"
```

黒/白文字との WCAG 読みやすさ監査を作成します。

```bash
swatch-story poster.png --colors 5 --wcag-audit poster-audit.md --title "Poster Palette"
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
  --swatch-story-color-1-contrast-black: 1.3;
  --swatch-story-color-1-contrast-white: 16.15;
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
  "contrast_with_black": 1.3,
  "contrast_with_white": 16.15,
  "best_text_color": "white",
  "label": "color-1"
}
```

コントラスト比は、相対輝度に基づく WCAG の式 `(lighter + 0.05) / (darker + 0.05)` を使い、各スウォッチを黒の輝度 `0` と白の輝度 `1` に対して比較します。`best_text_color` は、より高いコントラストの選択肢です。

CSV 出力例：

```csv
rank,hex,r,g,b,count,percent,luminance,contrast_with_black,contrast_with_white,best_text_color,label,name
1,#112233,17,34,51,120,32.43,0.015,1.3,16.15,white,color-1,
```

プレーンテキスト出力例：

```text
Poster Palette

Source: poster.png
Image size: 1200 x 800 px
Settings: colors 2; sample step 1; sample limit 10000; cluster distance 0; cluster space rgb; sort frequency; ignored color none; names not included

Swatches:
1. #112233 | rgb(17, 34, 51) | 32.43% | color-1 | contrast black 1.3:1 white 16.15:1 | text white
2. #eeeeee | rgb(238, 238, 238) | 18.25% | color-2 | contrast black 18.1:1 white 1.16:1 | text black
```

GIMP パレット出力例：

```text
GIMP Palette
Name: Poster Palette
Columns: 2
# Generated by swatch-story.
 17  34  51 color-1
238 238 238 color-2
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
  "contrast_with_black": 1.3,
  "contrast_with_white": 16.15,
  "best_text_color": "white",
  "label": "color-1",
  "name": "black"
}
```

JSON 設定には `cluster_distance`、`cluster_space`、選択した並べ替えモード、例えば `"cluster_distance": 0`、`"cluster_space": "rgb"`、`"sort": "frequency"` が含まれます。`--ignore-color` を使うと、JSON 設定には正規化された小文字の値、例えば `"ignore_color": "#ffffff"` が含まれます。無視されたピクセルは任意のクラスタリングと順位付けの前に除外されるため、スウォッチの割合は残ったサンプリング済みピクセルだけを基準に計算されます。`--matte` を使うと、JSON 設定には正規化された小文字の値、例えば `"matte": "#111827"` が含まれます。既定の白いマットを使う場合、このフィールドは省略されます。

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
Changed colors: #eeeeee (20.0% to 23.5%, +3.5%)
Drift score: 66.67%
```

## 設定

`swatch-story` は CLI オプションだけで設定します。

- `--colors N`: レポートする色数です。2 から 12 まで指定できます。既定値は 6 です。
- `--json PATH`: JSON レポートを書き出します。
- `--tokens PATH`: トークンパイプラインに取り込める決定的なデザイントークン JSON レポートを書き出します。レポートには `$schema`、`source`、`title`、パレットラベルをキーにした `color` トークンが含まれ、各トークンには `$type`、`$value`、説明文、`extensions.swatchStory` 指標が入ります。
- `--csv PATH`: UTF-8 CSV レポートを書き出します。列は `rank`、`hex`、`r`、`g`、`b`、`count`、`percent`、`luminance`、`contrast_with_black`、`contrast_with_white`、`best_text_color`、`label`、`name` で安定しています。
- `--css PATH`: CSS カスタムプロパティを書き出します。
- `--html PATH`: 単体 HTML レポートを書き出します。
- `--html-thumbnail PATH`: 小さなローカルサイドカーサムネイルを書き出し、HTML レポートからリンクします。このオプションには `--html PATH` が必要です。サムネイルは長辺 320 px 以内に収まり、縦横比を維持し、必要に応じて親ディレクトリを作成し、画像データを base64 で HTML に埋め込まずローカルに保ちます。
- `--markdown PATH`: ポータブルな Markdown レポートを書き出します。
- `--wcag-audit PATH`: 決定的な UTF-8 Markdown 監査を書き出します。元データ、抽出設定、黒/白文字に対する通常/大きな文字の WCAG AA/AAA 準備度、推奨文字色、スウォッチごとの推奨事項を含みます。
- `--text PATH`: UTF-8 プレーンテキストのパレットシートを書き出します。タイトル、元ファイル名、画像サイズ、抽出設定、各スウォッチの順位、HEX、RGB の組、割合、ラベル、黒/白のコントラスト比、最適な文字色、任意の名前ヒントを含みます。
- `--svg PATH`: 決定的な UTF-8 単体 SVG スウォッチシートを書き出します。タイトル、元ファイル名、画像サイズ、抽出設定、各スウォッチ行の色矩形、HEX、任意の名前ヒント、割合、輝度、黒/白のコントラスト比、ラベル、読みやすい文字色を含みます。
- `--gpl PATH`: 決定的な GIMP `.gpl` パレットを書き出します。
- `--ase PATH`: 決定的な Adobe Swatch Exchange `.ase` パレットを書き出します。
- `--sample-step N`: N ピクセルごとにサンプリングします。既定では、小さい画像は全ピクセルを使い、大きい画像は決定的な自動ステップを使います。
- `--sample-limit N`: `--sample-step` が省略された場合に、自動ステップが目標とするサンプリング済みピクセル数を指定します。既定値は 10000 です。1 以上である必要があります。`--sample-step` が指定された場合、固定ステップがピクセル走査を制御しますが、JSON 設定には選択された `sample_limit` と実際の `sample_step` が含まれます。
- `--ignore-color HEX`: パレット順位付けの前に、十六進 RGB 色と完全一致するサンプリング済みピクセルを除外します。`#rrggbb` または `rrggbb` を受け付け、大文字小文字は区別しません。JSON/レポート設定には正規化された小文字の `#rrggbb` 値が保存されます。すべてのサンプリング済みピクセルが無視された場合、または値が有効な十六進 RGB でない場合、コマンドは明確なエラーで終了します。
- `--matte HEX`: パレット抽出の前に、透明または半透明ピクセルを十六進 RGB 背景色に合成します。`#rrggbb` または `rrggbb` を受け付け、大文字小文字は区別しません。既定の挙動は白いマットのままで、このオプションを明示した場合だけ JSON 設定に正規化された `matte` が含まれます。
- `--cluster-distance N`: 0 より大きい場合、パレット順位付けの前に似ているサンプリング色をグループ化します。値は 0 から 255 の範囲で指定します。既定値は 0 で、完全一致 RGB バケットの挙動を保ちます。クラスタの代表色は、サンプリング済みピクセル数で重み付けした RGB の丸め平均です。
- `--cluster-space {rgb,lab}`: `--cluster-distance` が使う距離空間を選びます。`rgb` は既定値で、既存の決定的な RGB-ish クラスタリングを保ちます。`lab` は D65 白色点で sRGB を XYZ と CIELAB に変換し、Lab ユークリッド距離で色を比較します。`--cluster-distance` が 0 の場合でも、JSON とレポート設定には選択値が常に含まれます。
- `--sort {frequency,luminance,hue}`: 選択済みパレット項目の順序を指定します。`frequency` はサンプリング済みピクセル数による既定の順位を保ち、`luminance` はスウォッチを暗い順から明るい順に並べ替え、`hue` は HSV 色相角順の有彩色スウォッチの後にグレースケールまたはほぼグレースケールのスウォッチを置きます。並べ替え後のパレットは 1 から順位を振り直します。既定値は `frequency` です。
- `--precision N`: ユーザー向けレポートの割合、相対輝度、コントラスト比を `N` 桁の小数で整形します。範囲は 0 から 6 です。省略時は既存の JSON 数値とレポート文字列を保ちます。このオプションは通常のパレット抽出の JSON、デザイントークン JSON、CSV、Markdown、WCAG 監査、プレーンテキスト、SVG、HTML、ターミナル要約に適用されます。CSS、GIMP `.gpl`、Adobe `.ase` などのデザインツール向けパレット形式は、それぞれの形式固有の出力を保ちます。
- `--label-prefix PREFIX`: メイン画像コマンドで既定のパレットラベルを `PREFIX-1`、`PREFIX-2` のように置き換えます。`PREFIX` は小文字で始まり、小文字、数字、ハイフンだけを含められます。例えば `--label-prefix brand` は、JSON、デザイントークン JSON キー、CSV、CSS カスタムプロパティ名、Markdown、WCAG 監査、プレーンテキスト、HTML、SVG、GIMP `.gpl`、Adobe `.ase`、ターミナル出力に `brand-1` のようなラベルを書き出します。compare と gallery コマンドではこのオプションは使いません。
- `--preset PATH`: メイン画像、`compare`、`baseline`、`batch` コマンドの実行前に、再利用できる既定値をローカル JSON プリセットから読み込みます。明示した CLI フラグはプリセット値を上書きします。プリセットには `colors`、`sample_step`、`sample_limit`、`ignore_color`、`matte`、`cluster_distance`、`cluster_space`、`sort`、`names`、`precision`、`label_prefix`、`title`、`min_delta_percent` を含められます。モードで使わないキーは適用されません。
- `--title TEXT`: デザイントークン JSON、HTML、Markdown、WCAG 監査、プレーンテキスト、SVG、GIMP パレット、ASE 出力のタイトルです。既定値は `Swatch Story` です。
- `--names`: 決定的でオフラインの近似的な一般色名ヒントを含めます。名前は小さな組み込み RGB 参照セットから選ばれ、人が読みやすい色系統のヒントを目的としており、厳密な色名ではありません。

`swatch-story compare BEFORE_IMAGE AFTER_IMAGE [options]` は、`--colors`、`--sample-step`、`--sample-limit`、`--ignore-color`、`--matte`、`--cluster-distance`、`--cluster-space`、`--sort`、`--names` を再利用します。同じ matte が両方の画像に適用されます。さらに `--min-delta-percent N` を指定できます。`N` は `0` 以上の浮動小数点パーセントです。比較モードでは、`--json PATH` は単一画像レポートではなく、ルートの `schema_version: 1` を含む決定的な比較 JSON レポートを書き出し、`--csv PATH` はメタデータ、フィルター済みの色変化行、フィルターされない追加/削除色行を含む決定的な UTF-8 比較 CSV を書き出し、`--html PATH` は単体 HTML 比較レポートを書き出し、`--markdown PATH` はポータブルな Markdown 比較レポートを書き出し、`--text PATH` は UTF-8 プレーンテキストのドリフトレポートを書き出します。これらの出力は同時に指定できます。

`swatch-story baseline BASELINE_IMAGE CANDIDATE_IMAGE [CANDIDATE_IMAGE ...] [options]` は、`--colors`、`--sample-step`、`--sample-limit`、`--ignore-color`、`--matte`、`--cluster-distance`、`--cluster-space`、`--sort`、`--names`、`--precision`、`--title`、`--min-delta-percent` を再利用します。少なくとも 1 枚の候補画像と少なくとも 1 つの出力パスが必要です。`--json PATH` は、ルートの `schema_version: 1`、schema マーカー、version、ベースラインメタデータ、入力順の候補、順位、ドリフトスコア、共有/追加/削除色、色変化詳細を含む決定的なベースラインドリフト JSON レポートを書き出します。`--markdown PATH` は、要約表と候補ごとのセクションを含む順位付きレビューを書き出します。`--text PATH` は、コンパクトな順位付きログ行を書き出します。`--html PATH` は、エスケープ済みメタデータと共有/追加/削除/変化色の列を含む、ブラウザー確認用の独立した順位付きダッシュボードを書き出します。

`swatch-story batch IMAGE IMAGE [IMAGE...] [options]` は、すべての画像で `--colors`、`--sample-step`、`--sample-limit`、`--ignore-color`、`--matte`、`--cluster-distance`、`--cluster-space`、`--sort`、`--names`、`--precision`、`--title` を再利用します。少なくとも 2 つの画像パスと少なくとも 1 つの出力パスが必要です。`--markdown PATH` は決定的な UTF-8 のチームレビュー Markdown レポートを書き出し、`--html PATH` は単体 HTML チームレビューレポートを書き出します。両方を同時に指定できます。batch モードでは `--label-prefix`、`--tokens`、`--json`、`--csv`、`--css`、`--wcag-audit`、`--text`、`--svg`、`--gpl`、`--ase`、`--html-thumbnail` は使いません。

`swatch-story gallery OUT_DIR [--manifest] [--no-index] [--force] [--tag TAG]...` は、組み込みサンプル PNG 素材を書き出し、既定ではソースチェックアウト用コマンドと読みやすいサンプルタグを含む Markdown `README.md` gallery も生成します。`--manifest` は、schema version `1`、generator 名、サンプルファイル名、寸法、ストーリー、タグ、期待される主要色、期待されるパレット HEX 値を含む決定的な UTF-8 `manifest.json` も書き出します。`--tag` は繰り返し指定でき、要求したタグをすべて含むサンプルだけを生成します。照合は大文字小文字を区別せず、不明なタグや一致しないフィルターはファイルを書き出す前に失敗します。`--no-index` は `README.md` だけを省略するため、`--manifest` と組み合わせられます。`--force` がない限り、`manifest.json` を含む既存の gallery ファイルは上書きしません。

`swatch-story presets PATH [PATH ...] [--json PATH]` は、`--preset` と同じルールでローカル JSON プリセットファイルを検証し、画像ファイルは読みません。ターミナル要約は入力順を保ち、対応キーをソートして表示し、対応キーがないプリセットには `keys: none` を表示します。`--json PATH` は、すべての入力プリセットが検証に成功した場合にだけ、schema マーカー `swatch-story.presets`、version `1`、正規化された絶対プリセットパス、有効性、ソート済みキーを書き出します。

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

テストスイートは小さな合成画像を作り、パレット比率、コントラスト用テキスト色、単一画像/比較/ベースライン/batch レポート描画、デザイントークン JSON 出力、プリセット検出検証、gallery マニフェスト内容、ユーザー由来レポート値のエスケープ、CLI ファイル出力を検証します。

```bash
pytest -q
```

## ロードマップ

swatch-story は alpha 段階ですが、ローカルで決定的なパレット抽出とレビューレポートには利用できます。2026-05-18 のリリース準備レビューを受け、プロジェクトは成長サイクルから保守サイクルへ移行します。通常は 2-4 週間ごとに確認し、緊急のバグ、ドキュメントの正確性、依存関係、レポート schema 安定性の問題があれば対応します。

Now:
- 次のリリース候補を安定させます。タグ付け前にリリースチェックリストを実行し、ユーザー報告のパレット/レポート回帰を監視し、リリース信頼性を高めるもの以外の大きな機能追加は避けます。

Next:
- 透明度、無視する背景、知覚的クラスタリングなど、リリース上重要なワークフローを直接示す場合にのみギャラリーサンプルを改善します。
- タグ付きリリースで現在の JSON 形状を記録するまでは、レポート schema の変更を追加的なものに保ちます。
- 次のリリースタグ後、または実際のユーザー feedback がより価値の高いワークフロー不足を示した場合に、サイクルを再確認します。

Later:
- リリース自動化向けの任意の機械可読 changelog メタデータを検討します。
- 繰り返し使う CLI プリセットで一般的なワークフローを十分に覆えなくなった場合にのみ、設定ファイル対応を検討します。

リリースチェックリスト:
- クリーンなローカル仮想環境で `ruff check .`、`ruff format --check .`、`pytest -q`、`python -m build` を実行します。
- `README.md`、`README-zh.md`、`README-ja.md` が同じインストール手順、例、ロードマップ姿勢、MIT ライセンス注記を説明していることを確認します。
- ユーザーに見える CLI オプション、レポート形式フィールド、出力アーティファクトの変更ごとに、`CHANGELOG.md` の Unreleased 条目があることを確認します。
- リリースが抽出やレポート描画を変える場合は、小さなローカルフィクスチャで代表的な単一画像、比較、ベースライン、batch、gallery コマンドを smoke test します。
- パッケージが明示的に公開され検証されていない限り、パッケージレジストリのインストールコマンドは追加しません。

完了レビュー:
- 完了: 2026-05-18 のリリース準備レビューで swatch-story を保守サイクルへ下げました。現在のユーザー向けワークフローはリリース候補として十分に広く、残る項目は中核的な機能成長ではなくリリース衛生や例示です。
- ロードマップ項目は、テスト、ドキュメント、翻訳 README の意味、リリースノートまたは changelog への影響を確認してから完了とします。
- 完了した項目は README のロードマップから削除し、内容が大きい場合は [ROADMAP.md](ROADMAP.md) または changelog に記録します。

## コントリビュート

コントリビューションを歓迎します。[CONTRIBUTING.md](CONTRIBUTING.md) を読み、振る舞いを変える前に振る舞い重視のテストを追加し、README 翻訳の意味を同期してください。

## ライセンス

MIT。詳しくは [LICENSE](LICENSE) を参照してください。

## AI 支援メンテナンス

このプロジェクトではメンテナンス作業に AI 支援を使う場合があります。メンテナーはリリース前に変更を確認し、他のプロジェクトのコードや文章を意図的にコピーしません。
