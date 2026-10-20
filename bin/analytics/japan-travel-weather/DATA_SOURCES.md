# Data sources and reproduction

The analysis uses public, aggregate observations and tourism statistics. Derived
CSV/Parquet files, tables, charts, and articles were extracted, joined, or calculated
by this project; they are not official publications or forecasts.

| Data | Official source | Reuse information |
| --- | --- | --- |
| Daily weather, 2016–2025; station catalog | [Japan Meteorological Agency](https://www.data.jma.go.jp/risk/obsdl/index.php) | [JMA terms](https://www.jma.go.jp/jma/kishou/info/coment.html): Public Data License 1.0, subject to stated exceptions; credit JMA and identify processing. |
| Monthly prefectural guest nights, 2023–2025 | [Japan Tourism Agency, Accommodation Survey](https://www.mlit.go.jp/kankocho/tokei_hakusyo/shukuhakutokei.html) | [Tourism Agency terms](https://www.mlit.go.jp/kankocho/site-policy.html): Public Data License 1.0, subject to stated exceptions; credit the agency and identify processing. |
| Municipal monthly tourism counts | [Hokkaido tourism survey](https://www.pref.hokkaido.lg.jp/kz/kkd/irikomi.html) | [Hokkaido site policy](https://www.pref.hokkaido.lg.jp/site-info/sitepolicy.html): CC BY unless otherwise indicated; third-party rights remain separate. |
| Kyoto City monthly visitor counts | [2024 report](https://www.city.kyoto.lg.jp/sankan/cmsfiles/contents/0000109/109809/R6honsatsu.pdf), [2025 report](https://www.city.kyoto.lg.jp/sankan/cmsfiles/contents/0000354/354593/honsatsu.pdf) | Only extracted numerical facts and project calculations are included. The reports themselves are omitted under the [city site policy](https://www.city.kyoto.lg.jp/main/site_policy/0000000005.html). See article notes about retrospective revisions and the research-only 2023 values. |
| Japanese national holidays | [Cabinet Office holiday calendar](https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html) | Source of holiday dates and names; the downloaded CSV and its provenance/hash are in `data/calendar/`. |

Source and reuse pages were checked on 2026-10-20. This repository does not grant a
new license over third-party material.

## Original report and workbook downloads

Original PDFs and Excel workbooks are intentionally ignored by Git. This avoids
redistributing full third-party reports and Office files containing author-machine
metadata, macros, or external links. Existing local originals are left unchanged.
Their expected names, sizes, and SHA-256 hashes are in
`data/original_downloads.sha256.json`.

For a fresh checkout, download the originals from the official pages above and
place them under these paths, relative to this directory:

- `data/accommodation/001750679.xlsx` — 2023 final annual Accommodation Survey.
- `data/accommodation/001905499.xlsx` — 2024 final annual Accommodation Survey.
- `data/accommodation/002010340.xlsx` — 2025 final annual Accommodation Survey.
- `data/tourism/hokkaido/hokkaido_tourism_fy2022_tables.xlsx` and
  `hokkaido_tourism_fy2023_tables.xlsx` — municipal/monthly tables for each fiscal year.
- `data/tourism/hokkaido/hokkaido_tourism_fy2024_tables.xlsm` and
  `hokkaido_tourism_fy2025_tables.xlsm` — municipal/monthly tables for each fiscal year.
  The loader reads cached values and does not execute macros.
- `data/tourism/kyoto/R6honsatsu.pdf` and `data/tourism/kyoto/honsatsu.pdf` —
  the two Kyoto reports linked above.

The four Hokkaido `*_report.pdf` files listed in the hash manifest are optional
reference material; the Hokkaido loader uses the workbooks.

Run `load_accommodation.py`, `load_hokkaido_tourism.py`, or
`load_kyoto_tourism.py` with `uv run python` from this directory to rebuild their
processed data. Verify downloaded hashes against the manifest if the original
edition is required; publishers may replace files.

## Verify the included results

From this directory:

```sh
uv run python verify_publication.py
```

This uses the included processed datasets and publication files; original PDFs
and workbooks are not needed. To rebuild publication outputs, install the root
Node dependencies with `npm install`, then run
`uv run python run_publication_review.py` here.
