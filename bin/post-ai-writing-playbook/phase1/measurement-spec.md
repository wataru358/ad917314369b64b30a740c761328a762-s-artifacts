# Phase 1 measurement specification

## Cohort and dates

Each article has a unique `id` corresponding to the D02 normalized path. Use `article_id=id` throughout. Keep every candidate in the ledger. Mark failed acquisitions and missing body regions as unavailable. Keep articles at different paths even if their saved text is identical. Include articles of any word count. The original run used SQLite job IDs, and the new run uses path SHA-256 hashes. ID-seeded sampling and extraction order can change even when the HTML is identical. Reproducing historical frozen samples requires identical bytes, a verified mapping to historical IDs, the same dependency versions, and identical selection rules.

The main cohort consists of archived articles whose body text is classified as English and whose UTC publication year is 2018–2025. Use the publication timestamp to assign the year. Treat 2022 as a transition year and 2025 as a partial year in annual summaries. The original coverage extended partway through October, so mark October as a partial month and November and December as unobserved. Mark months as `coverage_unknown` if the bundled settings and acquisition logs cannot establish coverage. Keep fully covered months with zero articles distinct from unobserved months. The supplemental comparison uses January through September for years with complete coverage in those months.

Store publication, update, CC capture, and download timestamps in separate columns. Divide the difference between UTC publication and CC capture epoch seconds by 86,400 to calculate the delay in days. Record original values and sources for flags that indicate inconsistent update timing or future publication. Treat the archived body as the version observed at capture.

## Extraction and English classification

- T00 freezes the bundled [article_extraction.py](references/article_extraction.py) as `extract.py` and applies `extract_article` to the archived HTML. Pass the original HTTP Content-Type and charset when available from the WARC response headers. Flag missing provenance when defaulting to UTF-8. Prefer `#article-body`, then `.crayons-article__body`. Record multiple matches, unavailable acquisitions, and decoding failures. Use headers and other non-body content to collect metadata.
- Use the extractor's `prose_units` in source order with their original XPath. P is `paragraph`, L is `list_item`, U is the remaining `text`, and S includes all three. Count nested prose once. Exclude the HTML title, headings, code, quotations, tables, images, recognized tables of contents, and widgets from S. Track unsupported elements, code-like prose, and potential tables of contents as quality flags.
- T01 uses the bundled [language_rules.py](references/language_rules.py). Score full S, P, L, and contiguous, nonoverlapping, 1,200-code-point chunks of S across all 75 languages in Lingua 2.1.1. A confident result requires a top score of at least 0.70 and a margin of at least 0.30 over the runner-up. Save the original S SHA-256, regions, spans, scores, and automatic classifications. Provide evidence inputs as a mapping with article_id, prose_text, prose_sha256, extraction_status, and the expanded payload. Treat the scores as classifier scores.
- For nonempty S, assign `mixed` when confident English and non-English results coexist in P, L, or the chunks. Assign `unknown` when the full-S result lacks confidence. Flag mixed candidates as English-dominant when English is the highest-scoring language for S. Use language hints, country, and tags only as context. Limit manual overrides to documented examples whose full text was reviewed in blinded calibration or diagnostics, and keep the automatic classifications.

## Words, sentences, and structure

T02 freezes [segmentation.py](references/segmentation.py), [t02_structure.py](references/t02_structure.py), and [t02_features.py](references/t02_features.py). Resolve T02 dependencies in the bundled directory and use the extractor with the same hash as the T00 output extract.py. Save the units and owning blocks from `project(payload)`. Keep the original prose unit order distinct from the order of owning blocks reassembled by identical XPath. Represent unit-to-owner offset mappings as half-open ranges of Unicode code points. Segment sentences within owning blocks and allow them to map back to source units.

An ASCII letter sequence with internal single apostrophes or hyphens is a word. Both `don't` and `state-of-the-art` count as one word. Normalize curly apostrophes in the word form only. URLs, email addresses, numbers, `UTF-8`, `snake_case`, and Unicode words containing non-ASCII characters have separate token types. `Node.js` counts as two ASCII words. Preserve the original punctuation and offsets in the body.

Include abbreviations, quotation marks, consecutive punctuation, technical names with periods, decimal numbers, versions, `br`, and trailing fragments in sentence boundary regression checks. Detect boundaries within each source P owning block. Keep fragments without terminal punctuation. Use only P sentences with at least one ASCII word for M02 and M03. Keep separate P owning blocks independent.

Project bold character ranges onto the saved S. Merge consecutive bold characters across nested or adjacent tags. Break spans at plain characters and prose unit boundaries. Count spans that overlap an ASCII word. Count each bold word once even if several bold spans overlap it. Assign `projection_error` only to values affected by a failed DOM-to-S projection. Count L words separately from li elements. Allocate words in nested lists and p elements inside li once, to the nearest li. Heading H includes H1–H6 in the cleaned DOM. Save code C separately.

## Article-level metrics

| ID | Value | Validity and missingness |
| --- | --- | --- |
| M01 | P word count `W_P` | Articles without P have zero words. The primary comparison uses `log1p(W_P)`. |
| M02 | Mean length `μ` of P sentences with positive word counts | NA when no sentences qualify. |
| M03 | Population standard deviation `σ` of P sentence length divided by `μ` | NA with fewer than two qualifying sentences. Flag two to four as low n. |
| M04 | `1000 × comma count in P / W_P` | Exclude commas between digits. NA when `W_P=0`. |
| M05 | `W_L / (W_P + W_L + W_U)` | Zero when S has words and L has none. NA when the S word count is zero. |
| M06 | `1000 × bold span count in S / W_S` | Zero when S has words and no bold spans qualify. NA when the S word count is zero, with a separate reason for projection errors. |

Secondary metrics include median P owning-paragraph word count, H2+H3 density per 1,000 S words, share of bold words, the monotonic PCV transformation `(σ−μ)/(σ+μ)`, adjacent positive-word-count sentence length differences within P owning blocks, the share of single-sentence paragraphs, and punctuation prevalence and density. For MATTR, take the P word forms in article order, lowercase them, slide a 100-word window one word at a time, and average the share of unique words. Report the 50-word window separately. Mark articles shorter than the window as NA. Count emoji code-point candidates separately from rendered emoji. Pass the within-sentence comma spacing and the historical article-level approximation `W_P/(commas+1)` to A02 as separate measures.

Metric rows with states share the columns `article_id,metric_id,value,numerator,denominator,state,reason`. Use `ok` for a finite value or `NA` with a blank value and a reason. Distinguish no sentences, no ASCII words, one sentence, insufficient words for the window, structure projection failure, and missing inputs. M01 can have a value with a blank denominator because it has no defined denominator.

## Authors, tags, and strata

T02 uses [t02_metadata_v2.py](references/t02_metadata_v2.py) and [t02_metadata.py](references/t02_metadata.py) and rechecks the body HTML hash. Pass article_id, url, and html_sha256 to extract_metadata, using the encoding recorded by T00. Collect numeric personal IDs, coauthors, header links to people, JSON-LD Person entries, publication venues, and organizations separately. Preserve conflict, multiple, profile-only, and missing states. Treat only single stable numeric IDs as known authors and normalize them to `dev:user:<id>`. Use organization slugs only for organizations. Treat unobserved organization status as unknown.

First use [t02_classification.json](references/t02_classification.json) to assign exploratory article types and multiple topic cues from archived titles and tags. Assign the first matching topic by the priority order in [t02-strata-map.json](references/t02-strata-map.json). Use `unknown` for missing tags or no matching classification. Save the coarse article type separately, with calibration matches, totals, and limitations. Use only validated article types for primary composition adjustment. Treat unvalidated types as coarse cues or unknown in the requested exploratory analyses.

## Primary comparisons and intervals

Compute the article-weighted mean `m_y` of valid values within each UTC year, giving every article equal weight. The primary point difference is `(m_2023+m_2024)/2 − (m_2018+m_2019+m_2020+m_2021)/4`. Multiply M05 differences by 100 to obtain percentage points. Store the all-article point difference and the same-scale point difference restricted to articles with stable numeric author IDs in separate columns. Include yearly total n, valid metric n, counts by NA reason, the known-author share, and the number of known authors. Keep M01 means, medians, and quantiles on the original scale too.

To calculate an interval, sample known authors with replacement from the fixed population across all years. Draw as many authors as there are known authors and include all articles for each author as many times as that author was drawn. Recalculate the point difference on each draw. Use 2,000 replicates with seed 42 and linear quantiles at 2.5% and 97.5%. Resample author clusters jointly across years. If any comparison year has fewer than 30 valid known authors, report NA. When the known-author share falls below 90%, state that representativeness for the full cohort cannot be assessed. The interval population is limited to known authors at any coverage level. Keep runs with empty years or failed resamples as invalid and record valid replicate counts and failure reasons.

Use descriptive estimates and intervals for the primary comparisons. The default omits p-values and Holm correction. If explicitly run, report the methods, including the same prespecified family of six metrics, the two-sided centered author bootstrap approximation, and Holm correction. Use 1 for unavailable tests in the correction and display NA. Treat direction as undetermined when an interval crosses zero. Interpret these comparisons within the archived cohort. They do not establish AI use, causal effects, all-DEV patterns, writing quality, comprehension, or reading time.

## Downstream file contracts

`articles.jsonl` contains one row for each included article, with `article_id`, title, UTC publication, update, and capture timestamps, the body extraction hash, `units` and Unicode-offset `owners`, `headings`, `bold_spans`, ordered `dom_events`, quality flags, and `W_P/W_L/W_U/W_S`. Give each DOM event a kind, order, original XPath, and closest S word position. Events outside S, such as quotations, tables, code, and images, also carry positions and references.

`metadata.csv` contains article ID, `author_id`, `author_numeric_id`, `author_status`, `author_known`, `organization_id`, `organization_slug`, `organization_status`, `tags` as a JSON array, `tag_status`, `topic_primary`, `article_type`, dates, and provenance. `cohort.csv` contains every candidate ID, UTC publication timestamp and year, language state, inclusion decision, and any reason for exclusion. `coverage.csv` contains the UTC year-month grid, coverage states and their sources, and counts.
