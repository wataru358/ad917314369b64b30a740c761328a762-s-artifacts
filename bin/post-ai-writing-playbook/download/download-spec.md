# 取得仕様

## 共通の保存と再開

対象期間、seed、プロファイル、小分け実行の上限はルートの `config.json` から読む。新しい実行では、この設定、対象ソース、取得コードの版、依存パッケージの版を `manifest.json` に記録する。保存済みの実行と照合できるよう、設定と入力ファイルの SHA-256 を残す。

各タスクは指定された `output_dir` に `report.md`、`summary.json`、`manifest.json`、`verification.json` を保存する。JSONL は1行1オブジェクトの UTF-8 とし、改行は LF を使う。ハッシュは保存バイト列の SHA-256、時刻は ISO 8601 とする。`manifest.json` に `task_id`、`run_id`、`attempt`、`scope`、凍結入力の識別子、ファイルの相対パス、バイト数、ハッシュを含める。多数のファイルは、同じ項目を持つ `raw-files.jsonl` から参照してよい。入力台帳のファイルパスは、そのタスクの `output_dir` を基準に解決する。

1. 台帳の作成と更新には出力先ごとの排他ロックを使う。ネットワーク処理の前にリクエストを記録し、受信した原データは一時ファイルへの書込みと原子的な移動で確定する。保存後に台帳の状態を更新する。
2. 1回の処理は `limits` の件数、受信ボディのバイト数、経過秒数、および同時実行数の上限内で進める。確認、再試行、リダイレクト拒否で消費したリクエストも数える。大きな応答は上限の残りを越えて読み込まない。応答の受信や待機で小分け実行の期限を越える場合は、その前に状態を確定して止める。終了理由と消費した予算を台帳に記録する。
3. 上限へ達したら状態を確定し、次の区切りで未処理分から再開する。`Retry-After` の秒数と HTTP 日付に対応し、指定期限を `not_before` に保存する。待機中は同じ取得先へリクエストせず、独立した工程を進める。
4. 再開前に入力ハッシュと確定済みの台帳を照合する。中断した処理は試行履歴に残し、検証済みの原データがあれば再利用する。ハッシュの不一致や確定記録の欠損は報告して復旧する。期間、候補集合、seed、プロファイルを変えるときは別の実行にする。
5. `verification.json` に検証範囲、読み戻した件数、独立検証の結果、失敗や対象外の理由を残す。後工程に渡す成果物のハッシュと照合結果をレシートに記す。`full` の試行で得た5件は途中の検証記録として保存する。

## D01の候補と保存位置を固定する

一覧は `https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/cc-index-table.paths.gz`。圧縮2 MiB、展開後8 MiBを上限とする。取得した gzip を `manifest.paths.gz` に保存する。空行を除き、`cc-index/table/cc-main/warc/crawl=CC-MAIN-2025-43/` 以下のキーだけを受け付ける。`subset=warc/` の直下にある `[A-Za-z0-9_.-]+\.parquet` だけを対象とする。`..` のパス要素や重複があれば拒否し、キーは昇順に固定する。各 Parquet は `https://data.commoncrawl.org/` にキーを連結して読む。

索引の `url_host_tld = 'to'`、`url_host_registered_domain = 'dev.to'`、`url_host_name = 'dev.to'`、`fetch_status = 200`、`content_mime_detected = 'text/html'` をすべて満たす行を数える。対象行のうち、`url_path` が `/[^/]+/[^/]+/?` に完全一致するものを候補とする。次の正規表現に一致するルートは除く。

```text
^/(t|tag|tags|api|search|settings|dashboard|admin|feed|pod|videos|comments|top|readinglist|organizations|series|badges)/
```

末尾の `/` を落とした `url_path` を候補の `path` とする。索引の `url_path` を使うため、URLのクエリとスキームは重複排除に影響しない。大小文字と文字エンコードは保存値のまま扱う。移転、転載、異なるslugは別候補として保持する。全ファイルを通じて `path` で重複を除き、`id = sha256(path.encode('utf-8')).hexdigest()` とする。

索引から `url`、`fetch_time`、`warc_filename`、`warc_record_offset`、`warc_record_length`、`content_languages` を残す。候補に複数の保存記録があるときは、UTCに正規化した `fetch_time`、`url`、`warc_filename`、`warc_record_offset` の順に昇順で比較し、先頭の1件を固定する。同順位の区別には索引キーを使う。元の `content_languages` は参考値として保存する。保存位置を収録と同時に確定できない構成では、候補が見つかった索引ファイルだけを同じ条件で再照会する。

必要列と範囲を絞って Parquet を読む。公式の DuckDB `httpfs` を使う場合は、元の実装で使った接続上限を目安にする。同時走査1、メモリ1 GiB、一時領域1 GiB、HTTPタイムアウト30秒。`httpfs` の内部転送量を数えられない場合は、各取得で受信上限を適用できる Range クライアントとローカルキャッシュを使う。たとえば、Parquet リーダーにシーク可能な HTTP Range ストリームを渡し、フッターと必要な行グループの列を読む。Range キャッシュにはキー、オブジェクト長、取得できた識別子、206で検証した範囲とハッシュを記録する。読み取りが1区切りに収まらない場合は、行グループの一時集計または範囲キャッシュから再開する。一覧と索引の取得に固定のバイト上限を設定していなかった当時の実装とは、この実行条件が異なる。

ファイル別の件数と候補の確定を同じトランザクションにする。最初の該当ファイルで `pilot.cc_records` 件の候補を検証する。足りなければ次のファイルへ進む。少数検証に使ったファイルと検証した候補を残す。一覧の全キーの処理が済んでから候補集合を確定する。未処理キーがあれば報告を部分集計とする。

| ファイル | 確定する項目 |
| --- | --- |
| `manifest.paths.gz` | 受信した圧縮一覧のバイト列。 |
| `index-files.jsonl` | 一覧にある全キーの `file_key`、処理状態、`html_captures`、`candidate_captures`、エラー、処理日時。未処理行の件数は `null`。 |
| `candidates.jsonl` | `path` 昇順。`id`、`path`、`url`、`index_file`、`index_captured_at`、`warc_filename`、`offset`、`length`、`index_languages`。 |
| `summary.json` | crawl、条件、圧縮一覧のハッシュ、全ファイル数、確定ファイル数、HTML保存件数、候補保存件数、重複排除後の候補数、`complete_index`、プロファイル。 |

## D02の指示範囲からWARCとHTMLを保存する

D01の `candidates.jsonl` を入力とする。D01のスコープ、ハッシュ、各IDの一意性を確かめる。固定順の作り方は、UTF-8の候補パスを昇順で並べ、Python 3.11 の `random.Random(42).shuffle` を適用する。seed は設定値を使う。`ordinal` は0から付ける。先頭 `pilot.cc_records` 件を試行して、WARC と HTML の照合を行ってから続きへ進む。

元の調査では先に2万件を取得し、残りを後から追加した。パス昇順の母集団から `random.Random(42).sample(paths, 20000)` を取り、その集合と補集合をそれぞれパス昇順から別々に `random.Random(42).shuffle` した。元のSQLiteでは、この順に挿入した行の数値IDを後工程で使った。今回のIDはD01のパスハッシュなので、同じHTMLでも記事IDをseedの入力に使う抽出標本は変わり得る。元の数値IDとパスの対応表が提供され、出所とハッシュを照合できた場合は `legacy_job_id` を任意項目として保存する。元の標本の一致を検証するには、その対応表、元の原データ、処理の版がそろう必要がある。

1. `url` は `http` または `https`、ホストは `dev.to`、末尾 `/` を除いたパスは候補と一致することを確認する。`warc_filename` は `crawl-data/CC-MAIN-2025-43/segments/` 以下の `.warc.gz`、許可文字は `[A-Za-z0-9_./-]`、`..` 要素なし。`offset` は非負整数、`length` は1以上8 MiB以下の整数。
2. `https://data.commoncrawl.org/<warc_filename>` に `Range: bytes=<offset>-<offset+length-1>`、`Accept-Encoding: identity` でリクエストする。リダイレクトを拒否する。外側の応答は HTTP 206 と `Content-Range: bytes <offset>-<end>/<total>` を必須とし、`total > end` と受信長 `length` を照合する。HTTP 200 の代替応答はボディを読む前に拒否する。
3. 1件ずつ取得し、直前の通信終了から3秒以上空ける。タイムアウトは30秒。圧縮WARCの受信が完了したらハッシュを記録して保存する。検証済みの同じWARCは再通信せず使う。
4. gzip 展開後32 MiB以内の、ただ1件の `response` レコードを読む。`WARC-Target-URI` は索引の `url` と完全一致させる。`WARC-Truncated` があれば失敗とする。内部HTTPは200かつ media type が `text/html`。HTTP圧縮は `identity`、`gzip`、`deflate` に対応し、転送形式もデコードする。展開した空でないHTMLは16 MiB以下とし、抽出や文字コード変換を加えずバイト列で保存する。ページ内の外部リソースは取得しない。
5. HTMLメタデータを別記録にする。JSON-LD の `@type` に `Article`、`BlogPosting`、`TechArticle`、`NewsArticle` のいずれかを持つノードの文字列 `datePublished` を集める。値が1種類なら採用。複数なら公開日は `null` として警告を残す。値がなければ `meta` の `article:published_time` を使う。公開年は解析できた公開日時から取得し、取得日時や更新日時で埋めない。`html_lang` は `<html lang>`、`modified_at` は対応する JSON-LD の `dateModified`。HTMLの宣言値は言語判定に使わない。

WARCとHTMLは `warc/<idの先頭2文字>/<id>.warc.gz` と `html/<idの先頭2文字>/<id>.html` に保存する。成功行には両方のパスと SHA-256 を持たせる。失敗でも検証を通った保存物があれば台帳に残す。

`429` または `Retry-After` 付きの失敗では送信を止める。タイムアウト、接続障害、408、429、500、502、503、504 は再試行対象。404、形式不一致、URL不一致、過大な保存位置などは理由付きで確定失敗にする。再試行は1区切りに同じ候補を1回まで、累積の処理開始は最大3回か `limits.retries + 1` の小さい方。下限待機は失敗回数ごとに60秒から倍増させ、独自の待機は1時間で頭打ちとする。サーバーの指定がそれより長い場合は指定を使う。連続5件の一時通信エラー、保存障害、権限エラーでは区切りを止める。復旧後は同じ候補を続け、失敗分の別候補への差し替えやライブ本文への変更は行わない。

| ファイル | 確定する項目 |
| --- | --- |
| `acquisitions.jsonl` | `ordinal` 順で1候補1行。D01の項目に `ordinal`、`status`、`attempt_count`、`range_http_status`、`original_http_status`、`html_file`、`html_sha256`、`html_bytes`、`warc_file`、`warc_sha256`、`warc_bytes`、`warc_record_id`、`warc_captured_at`、`saved_at`、`title`、`published_at`、`published_year`、`publication_source`、`modified_at`、`html_lang`、`failure_stage`、`failure_reason` を加える。利用できない値は `null`。 |
| `attempts.jsonl` | 候補ID、開始・終了日時、再試行状態、HTTP状態、キャッシュ利用、エラー、`next_retry_at`。 |
| `summary.json` | 計画数、処理済み数、成功・失敗・残件数、試行と待機の記録、取得対象のハッシュ。 |

`full` 完了時はD01の全IDとD02の `succeeded` または `failed` の全IDが一致する。全件失敗や通信停止中の残件は、範囲取得と入力の妥当性を確認できないため、取得完了として後工程へ渡さない。

## D03で2026年の各月1,000件を固定する

一覧は `GET https://dev.to/api/articles/latest?per_page=1000&page=<整数>`。個別応答は `GET https://dev.to/api/articles/<整数ID>`。`Accept: application/vnd.forem.api-v1+json` を指定する。対象ホストは `dev.to`、通信は HTTPS のみ。リダイレクトは拒否する。許可済みの資格情報が環境にあれば `api-key` ヘッダーに使う。値はコマンド引数、ログ、設定、成果物に書かない。応答に資格情報が混入していないことを確かめる。

1. 最初に一覧1ページ目の形を調べ、API が返した5つの有効IDで個別応答、保存、読戻しを確かめる。対象期間外のIDも接続確認に使える。確認専用の個別応答は計画の取得件数から外す。一覧1ページ目を条件どおりに検証して確定した場合は一覧走査で再利用できる。認証済みの深いページが利用可能かを確認するときは、1,001ページ目を確認専用として扱う。
2. 一覧は1ページ目から順に進め、1区切りの最大20ページと `limits` を併用する。200応答から空でない配列を読み、各行の `id` が1以上64ビット符号付き整数の最大値以下の整数であることを確かめる。タイムゾーン付きの `published_at` を UTC に変換する。マイクロ秒まで統一し、月は UTC に変換した後の日時から取得する。
3. `2026-01-01T00:00:00Z <= published_at < 2026-11-01T00:00:00Z` の行を保存する。`id` は最初に確定した期間内の行を使い、重複数と日時が食い違う行を記録する。対象期間より古い行が初めて出たページを最後まで保存し、ページ番号とその行の日時を下限到達の根拠にする。200以外、空配列、解析エラーから下限到達を推定しない。オフセットページング中に内容が動くため、下限まで確認できても網羅率は不明と記す。
4. 一覧に含まれる原JSONをそのまま保存する。ページ台帳、候補行、次ページ番号を同じトランザクションで確定する。当時の公開アクセスでは1,000ページが上限だった。実行時に制限へ達したら記録して止める。401、403、リダイレクトでは送信を止め、許可済みのアクセス経路と設定を確認する。回避手段で上限を越えない。
5. 下限到達の根拠と、UTC1〜10月の各月に1,000以上の一意なIDがあることを検証する。各月のIDを `sha256(f'{seed}:{id}'.encode('utf-8')).hexdigest()` の昇順で並べ、同順位では数値IDが小さいものを先にする。各月の先頭1,000件を採用し、1月から10月まで順に1件ずつ取り出す操作を1,000回繰り返す。位置は1始まり。候補不足を別月で埋めない。タグ、APIの言語属性、本文の長さで候補順を変えない。
6. `plan.jsonl` を書込み、一覧台帳と計画のハッシュを固定する。再開時も同じ `id`、月、位置を使う。計画の先頭5件の個別応答を先に読み、結果を確かめる。計画に対して保存した有効な応答は全量の取得分にも使う。続きは未処理から1区切り最大50件と `limits` の範囲で進める。
7. 個別HTTP 200では、応答の `id` が要求IDと一致することを確かめる。`body_html` と `body_markdown` は文字列または `null` を受け付ける。片方でも空白以外の文字を含めば `saved`、どちらも空、空白のみ、欠落、または `null` なら `empty`。JSONの元バイト列はどちらの状態でも保存する。`saved` では、フィールドをUTF-8で符号化した `body.html` と `body.md` も保存する。欠落または `null` の方は空のバイト列を使う。公開日時に変化があれば差を記録し、計画上の月を保つ。HTTP 404 は `not_found`、確定した他の取得失敗は `failed` とする。

DEV API のリクエストは1件ずつ、3秒以上の間隔で送る。タイムアウト30秒。通信障害、429、5xx は初回に加え `limits.retries` の範囲で再試行し、既定は合計4回。試行回数をページ番号または計画IDごとに記録する。待機は3秒、6秒、12秒と増やし、`Retry-After` が長ければ指定期限を使う。権限エラー、継続中のレート制限、連続5件の個別取得の一時障害、保存障害では区切りを止める。失敗した一覧ページは読み飛ばさず、根拠と再開条件を残す。個別取得の連続障害が復旧したら残件を続け、再試行上限に達した個別IDは理由付きで残す。全件で接続に失敗した場合は停止原因を解消してから再開する。保存済み原JSONのハッシュが一致していれば本文ファイルは原JSONから復元できる。API由来の本文は取得時の公開状態で、公開後の編集や削除により前回の実行と異なり得る。

| ファイル | 確定する項目 |
| --- | --- |
| `pages.jsonl` | ページ番号、要求URL、取得日時、HTTP状態、原JSONへの相対パスとハッシュ、行数、期間内行数、最小・最大日時、下限到達フラグ。 |
| `plan.jsonl` | `position`、`id`、`month`、UTCの `published_at`、`seed_rank`、初出ページと行番号、言語の参考値があれば `language_hint`。 |
| `responses.jsonl` | `plan.jsonl` の全IDに1行ずつ。`id`、`position`、`month`、`status`、`request_url`、`fetched_at`、`http_status`、`attempt_count`、`raw_file`、`raw_sha256`、`html_file`、`html_sha256`、`markdown_file`、`markdown_sha256`、`detail_published_at`、`failure_reason`。利用できない値は `null`。 |
| `requests.jsonl` | 確認、一覧、個別の役割、URL、開始・終了日時、HTTP状態、失敗理由、再試行、待機期限。記録ヘッダーは `Date`、`ETag`、`Content-Type`、`Retry-After`、レート制限情報などの許可リストに絞る。 |
| `summary.json` | 期間、seed、下限到達の証拠、ページ数、月別候補・計画・結果数、重複と食い違い、残件、取得時刻の範囲。 |

一覧原JSONは `raw/pages/<ページ番号>.json`、個別原JSONは `raw/details/<id>/<応答SHA-256>.json` に保存する。本文ファイルは `articles/<id>/<応答SHA-256>/` に置く。`manifest.json` のファイルハッシュと `pages.jsonl`、`responses.jsonl` の参照を照合する。`full` 完了時はUTC1〜10月が各1,000件、全10,000件の計画に対し、すべてのIDに確定した取得結果がある。本文の英語判定と抽出済み本文の作成は Phase 2のS02へ渡す。
