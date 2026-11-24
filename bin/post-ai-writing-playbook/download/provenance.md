# Original research materials

These paths are relative to the root of the original repository consulted when writing the acquisition specification. To run this package, use the [acquisition specification](download-spec.md).

| Original path | SHA-256 | Material consulted |
| --- | --- | --- |
| `bin/analytics/post-ai-writing/README.md` | `84316ba34679a263b488b69448157bb20a9b3517955a5d9210b936df9eddfd58` | Common Crawl index and five-record HTML retrieval procedure |
| `bin/analytics/post-ai-writing/count_dev.py` | `67b3a511d81f311e7552ce340a71fc1b0a2709430437c4dcb19c0fb321ef67f7` | File list, index filters, and full-set reconciliation |
| `bin/analytics/post-ai-writing/fetch_dev_html.py` | `f0155ae5f1fed2fc3b9bcb948c63b4ac69fbb96a57021912b6001ad6637776dc` | Earliest capture selection, byte ranges, and WARC and HTML verification |
| `bin/analytics/post-ai-writing/bulk_dev.py` | `471bfe97353d3bf98e7ba2d7a46b459d1489fb9cfb8456fd45d93f8d0617ce7b` | Frozen order, resumption, retries, and acquisition ledger |
| `bin/analytics/post-ai-writing/bulk-download.md` | `45ef407e331558a5b6749cebe15e8a999ac3be5cd59f54ac9dc0e99ecacaa5c8` | Expansion from 20,000 records to all candidates and the operating units |
| `bin/analytics/post-ai-writing/bulk_config.json` | `af0f972882950ea04169571873c884744b7430584246eafeb4a7641f3b75e37b` | Target crawl and historical candidate count |
| `bin/analytics/post-ai-writing/html_metadata.py` | `10bffcb7a0f5154f6f8fd429e0776bc04e0a8c1adcedc8c33b313855da9abf42` | Reading publication and modification dates from HTML |
| `bin/analytics/post-ai-writing/corpus-guide.md` | `4da940768771d96053d0e7e56ea111313794f0cb59396593d188421420a77853` | Final Common Crawl acquisition and extraction counts |
| `bin/analytics/post-ai-writing/collect_dev2026.py` | `352265919d5d9a56f850beed461523968e6ad605ecd98ed536a478f1935f4859` | Checking API listings, freezing the plan, and retrieving detail responses |
| `bin/analytics/post-ai-writing/DEV2026-取得手順.md` | `68b736c29fd63d690e837593028b9208993bb353c1ce4fe8abc8ab191bb11ed5` | Public API limits, acquisition, and resumption |
| `bin/analytics/post-ai-writing/PHASE2-analysis-plan.md` | `1bf3b3f3840cf46b25448ef470c7f8819ad955dac8215f847ed261ce7316b8e4` | UTC monthly scope and planned counts |
| `bin/analytics/post-ai-writing/PHASE2-corpus.md` | `f4f4241c7052314c54988a832004defc6af919800e13704ab106b13491d5b3b3` | Eligibility outcomes for all planned IDs and English-language counts |
| `bin/analytics/post-ai-writing/pyproject.toml` | `3cb78bbc38e7852c06a673f455b632eef030a3d9ef55f08cad3975b3fefc66ed` | Dependency bounds for the original acquisition environment |
| `bin/analytics/post-ai-writing/質疑応答と原稿ドラフト/handoff.md` | `285e44c388ba1e099eec6903b7b0348baaccf502566d143b4bde5252838efbcc` | Final scope and inclusion counts across both phases |
| `bin/analytics/post-ai-writing/phase2-research/session-qa-handoff-20261115-v1/handoff.md` | `67ebf0ba029a513fe8e518a1b263e3cb66cfd638da8eaa1e8a5c34b5ac9b3f67` | Monthly API plan and limits on interpretation |

## Historical counts

| Step | Recorded count |
| --- | --- |
| Common Crawl candidates | 43,240 candidates, with 43,233 successful acquisitions and 7 failures. |
| Body extraction from archived HTML | 43,228 articles, with 5 pages lacking a body region. |
| Phase 1 analysis corpus | 38,980 English-language DEV articles published from 2018 through 2025. The coverage for 2025 is partial. |
| DEV API plan | 1,000 per UTC month from January through October 2026, for 10,000 in total. |
| Phase 2 screening of the 2026 corpus | 8,942 English, 151 mixed, 69 unknown language, 662 non-English, 101 without a body, and 75 unavailable. |

These counts document the original study. Use each future run's own acceptance criteria. The Common Crawl candidates represent coverage in one crawl. New API results can vary with publication status, edits, and listing order. New runs identify Common Crawl candidates by a hash of the normalized path. Samples that originally used numeric IDs as seed inputs can change even when the HTML is identical.
