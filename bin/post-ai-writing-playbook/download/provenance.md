# 元の調査資料

次のパスは、取得仕様の作成時に参照した元リポジトリのルートからの相対パス。パッケージを実行するときは [取得仕様](download-spec.md) を使う。

| 元のパス | SHA-256 | 参照内容 |
| --- | --- | --- |
| `bin/analytics/post-ai-writing/README.md` | `84316ba34679a263b488b69448157bb20a9b3517955a5d9210b936df9eddfd58` | CC索引と5件のHTML取得手順 |
| `bin/analytics/post-ai-writing/count_dev.py` | `67b3a511d81f311e7552ce340a71fc1b0a2709430437c4dcb19c0fb321ef67f7` | ファイル一覧、索引のフィルタ、全件照合 |
| `bin/analytics/post-ai-writing/fetch_dev_html.py` | `f0155ae5f1fed2fc3b9bcb948c63b4ac69fbb96a57021912b6001ad6637776dc` | 最早保存記録、Range、WARC・HTML検証 |
| `bin/analytics/post-ai-writing/bulk_dev.py` | `471bfe97353d3bf98e7ba2d7a46b459d1489fb9cfb8456fd45d93f8d0617ce7b` | 固定順、再開、再試行、保存台帳 |
| `bin/analytics/post-ai-writing/bulk-download.md` | `45ef407e331558a5b6749cebe15e8a999ac3be5cd59f54ac9dc0e99ecacaa5c8` | 2万件から全候補への拡張、運用単位 |
| `bin/analytics/post-ai-writing/bulk_config.json` | `af0f972882950ea04169571873c884744b7430584246eafeb4a7641f3b75e37b` | 対象crawl、当時の候補数 |
| `bin/analytics/post-ai-writing/html_metadata.py` | `10bffcb7a0f5154f6f8fd429e0776bc04e0a8c1adcedc8c33b313855da9abf42` | HTMLの公開日と更新日の読取り |
| `bin/analytics/post-ai-writing/corpus-guide.md` | `4da940768771d96053d0e7e56ea111313794f0cb59396593d188421420a77853` | Common Crawlの取得・抽出の最終件数 |
| `bin/analytics/post-ai-writing/collect_dev2026.py` | `352265919d5d9a56f850beed461523968e6ad605ecd98ed536a478f1935f4859` | API一覧の確認、固定計画、個別取得 |
| `bin/analytics/post-ai-writing/DEV2026-取得手順.md` | `68b736c29fd63d690e837593028b9208993bb353c1ce4fe8abc8ab191bb11ed5` | 公開APIの上限、取得と再開手順 |
| `bin/analytics/post-ai-writing/PHASE2-analysis-plan.md` | `1bf3b3f3840cf46b25448ef470c7f8819ad955dac8215f847ed261ce7316b8e4` | UTCの月別対象と計画件数 |
| `bin/analytics/post-ai-writing/PHASE2-corpus.md` | `f4f4241c7052314c54988a832004defc6af919800e13704ab106b13491d5b3b3` | 全計画IDの採否と英語採用件数 |
| `bin/analytics/post-ai-writing/pyproject.toml` | `3cb78bbc38e7852c06a673f455b632eef030a3d9ef55f08cad3975b3fefc66ed` | 元の取得環境の依存範囲 |
| `bin/analytics/post-ai-writing/質疑応答と原稿ドラフト/handoff.md` | `285e44c388ba1e099eec6903b7b0348baaccf502566d143b4bde5252838efbcc` | 両Phaseの最終的な対象範囲と採用件数 |
| `bin/analytics/post-ai-writing/phase2-research/session-qa-handoff-20261115-v1/handoff.md` | `67ebf0ba029a513fe8e518a1b263e3cb66cfd638da8eaa1e8a5c34b5ac9b3f67` | APIの月別計画と解釈上の限界 |

## 当時の件数

| 工程 | 記録値 |
| --- | --- |
| Common Crawlの候補 | 43,240件。取得成功43,233件、取得失敗7件。 |
| 保存HTMLからの本文領域抽出 | 43,228件。本文領域なし5件。 |
| Phase 1の分析対象 | 2018〜2025年公開のDEV英語記事38,980件。2025年は部分年。 |
| DEV APIの計画 | 2026年のUTC1〜10月に各1,000件、計10,000件。 |
| Phase 2の2026年側の採否 | 英語8,942件、混在151件、言語不明69件、非英語662件、本文なし101件、取得不能75件。 |

各値は元の調査の記録であり、将来の実行の合格値には使わない。Common Crawl の候補は一つのクロールにおける収録範囲を表す。APIの新規取得結果には、掲載状態や編集と一覧順の変化が含まれる。新しい実行のCC候補IDは正規化パスのハッシュ。元の調査で数値IDをseedの入力に使った標本は、同じHTMLからでも選択が変わり得る。
