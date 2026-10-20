# Learning Python and DuckDB Through a Japan Travel Data Project

> Editorial draft, 19 October 2026. The companion travel article ranks weather results and shows lodging demand alongside them.

Kyoto in August exposed a problem with the travel score I was testing. None of its valid four-day periods met my weather conditions. Yet adding a lodging-demand penalty moved it from rank 47 to rank 19, using a coefficient of 20. Kyoto's weather result stayed at zero; other places lost more points.

That calculation was correct. The interpretation needed work.

This project compares 56 Japanese destinations across 12 months. I started it to learn Python and DuckDB with an AI tutor, using public data for an English travel article. The early workflow involved running small scripts and inspecting their output. As publication became more urgent, I asked Codex to implement and execute more of the remaining work while preserving code, outputs, and verification records. The repository contains both stages of that process.

## Four days made the question concrete

A monthly average temperature would not tell me whether a visitor could get four days without repeated rain or sustained heat. I chose a four-day period as the unit of evaluation.

The weather limits require daily maximum temperatures from 10°C to below 35°C, at most one day reaching 30°C, at most one day with at least 1 mm of precipitation, and no day with 30 mm or more. These thresholds describe a preference. They do not establish a universal measure of good travel weather.

The [Japan Meteorological Agency download service](https://www.data.jma.go.jp/risk/obsdl/index.php) supplied daily observations. After loading and checking the data, the consolidated Parquet file contained 204,568 rows: 56 destinations times 3,653 dates from 2016 through 2025.

Parquet gave the analysis scripts a typed table to read. I kept the downloaded CSVs separately so I could trace a value back to the source. DuckDB handled the table queries; Python handled file paths, downloads, checks, and orchestration.

## A four-row window needs a complete calendar

The SQL window in `analyze_weather_all56region.py` is:

```sql
WINDOW trip AS (
    PARTITION BY destination_id
    ORDER BY date
    ROWS BETWEEN CURRENT ROW AND 3 FOLLOWING
)
```

`PARTITION BY` keeps destinations separate. The frame includes the current row and the next three rows. It represents four consecutive days only because the script first checks duplicate keys, date boundaries, and the expected number of dates for each destination.

I kept dates with missing or poor-quality observations in the table. Deleting them before the window calculation could join observations from nonconsecutive days. The script then evaluates only periods with four usable temperature values and four usable precipitation values, all with quality code 8.

Each destination produces 3,650 complete periods. The final three dates of 2025 cannot start a complete period within the dataset. Other month and year boundaries remain in the analysis: a stay beginning on 31 December 2024 includes the first three days of 2025 and belongs to December.

I saved two percentages. `valid_trips_pct` measures data coverage. `matching_trips_pct` measures how often valid periods passed the weather limits. Treating invalid periods as weather failures would mix missing data with actual conditions.

## A prefecture is a different geographic unit from a destination

The [Japan Tourism Agency lodging tables](https://www.mlit.go.jp/kankocho/tokei_hakusyo/shukuhakutokei.html) cover prefectures. My weather table covers destinations, sometimes represented by a nearby observation station. Joining them required an explicit destination-to-prefecture relationship.

The combined table has 672 rows, one for each destination-month pair. Before saving it, the code checks the complete set of keys, the absence of unmatched lodging records, and agreement with every original weather column. A successful join alone does not establish that a prefecture describes every destination inside it.

For each prefecture and year, I calculated:

```text
monthly lodging ratio =
    (monthly guest nights / days in month)
    / (annual guest nights / days in year)

representative monthly ratio =
    mean of the 2023, 2024, and 2025 ratios
```

This accounts for February and leap years. Averaging the three annual ratios gives each year equal weight. Pooling the guest nights first would answer a different question by giving higher-volume years more influence.

A ratio of 1.2 means that daily overnight demand was 20% above that prefecture's annual daily average. It does not mean 20% more crowded than another prefecture. It also says nothing direct about room prices or availability.

## Regional comparisons changed the use of lodging data

I checked municipal tourism figures for six Hokkaido destinations and day-trip figures for Kyoto. The purpose was to test the national indicator's limitations, rather than collect a separate local dataset for all 56 destinations.

In August, Shari Town's three-year guest-night ratio was 1.935, compared with 1.313 for Hokkaido. Shari includes the Utoro area and other places. A single Hokkaido figure hides that difference in seasonal concentration. The source is the [prefecture's municipal tourism survey](https://www.pref.hokkaido.lg.jp/kz/kkd/irikomi.html).

Kyoto raised a different issue: day visitors can follow a different seasonal pattern from overnight guests. It also required version checks. The city announced [retrospective revisions](https://www.city.kyoto.lg.jp/sankan/page/0000355046.html) while leaving older publications unchanged. Matching 2024 monthly values across two editions did not prove that the older 2023 values had been revised. The travel draft therefore uses the 2024–2025 city comparison from the 2025 report and retains the 2023 values for research.

The article now shows lodging demand next to the weather result. The score experiments remain available in the analysis files.

## Coefficient sensitivity exposed the limits of a combined score

The experimental formula was:

```text
score = weather_match_percent
        - coefficient * max(lodging_ratio - 1, 0)
```

I compared coefficients of 0, 10, 20, and 30. Below-average lodging demand earned no bonus. Above-average demand incurred a penalty.

At coefficient 20, 273 of the 672 destination-month rows changed rank. Fifteen zero-weather rows improved their rank, and 53 scores became negative. The Kyoto example at the beginning belongs to this group.

Clamping the score to zero would remove negative numbers, but it would also create more ties and discard distinctions. A minimum weather threshold would introduce another preference to justify. Neither change establishes a defensible exchange rate between a percentage point of historical weather performance and a relative lodging-demand ratio.

The weather-only draft keeps the experimental scores out of the main table. Its ties use the existing percentages rounded to one decimal place, with ranks such as 1, 1, 3. These ranks describe the sample. Adjacent four-day periods overlap, so I cannot treat them as independent trials when discussing uncertainty.

## Calendar enrichment needed its own boundary checks

The [Cabinet Office holiday CSV](https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html) allowed a date-level addition without inventing another crowding score. The calendar code preserves the raw file and its SHA-256 hash, decodes its Japanese text, and checks date uniqueness.

For each four-day period, it records holidays, weekends, and the union of both. A Sunday holiday counts once in the union. Historical special cases, including moved holidays in 2020 and 2021, come from the published dates rather than a generic recurring rule.

The historical output uses the same 3,650 starts as the weather analysis. A separate planning calendar covers starts from 1 January 2026 through 28 December 2027. Starting later would require 2028 holiday data, which the source had not yet published at the time of this review. Absence from the available calendar must not silently become “not a holiday.”

## Verification should challenge the calculation

The publication verifier reads the daily Parquet data through DuckDB, then recomputes the four-day results with Python lists and comparisons. It does not reuse the SQL aggregation. It also recomputes lodging ratios from the monthly Parquet input, checks calendar boundaries, and verifies ranks and article table rows.

This check starts at the processed daily and monthly inputs; it does not independently re-download and parse every original weather or lodging file. Earlier loading checks and retained sources remain part of the evidence. Passing arithmetic checks cannot establish that the chosen thresholds predict future weather or represent every traveler's preferences.

The execution runner records each command, exit code, log, and file hash. It also checks that the pre-existing analysis files remain unchanged. To reproduce this publication stage from the saved inputs:

```bash
cd bin/analytics/japan-travel-weather
uv run python run_publication_review.py
```

The saved holiday source supports an offline rerun. `build_trip_calendar.py --download` performs an explicit refresh when needed; it is separate from the normal reproduction command.

I can follow the article's numbers back through the join, the monthly ratios, the four-day periods, and the retained source files. I can also identify the editorial choices behind the results: the weather limits, the ranking policy, and the claims the article makes from those numbers.
