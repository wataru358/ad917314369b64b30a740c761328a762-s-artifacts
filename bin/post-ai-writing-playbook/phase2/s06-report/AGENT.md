# P2-S06 Compile the comparisons and four supplementary materials

Read the [root rules](../../AGENT.md) and [branch rules](../AGENT.md) before starting this task.

## Objective

Link numbers, figures, examples, and claims to the underlying comparisons so readers can verify the scope and limitations.

## Inputs

- S05's 18 decisions, fixed sensitivities, evidence-index, and independent checks
- S04 comparisons, candidates, yearly and monthly tables, stored article values, and X02 assessments
- S03 cohort and saved tags

Resolve upstream files using the upstream output_dir and manifest returned by workflow.py. Use paths resolved from the current run instead of absolute paths from earlier conversations.

## Steps

1. Copy S05's permissible wording to an 18-row claim ledger and link the values and evidence. Provide entry points for the 11 questions. Let readers find the cohort, distribution, yearly results, sensitivities, and X02 E/G combinations through the text, figures, and tables.
2. Preserve all fixed candidate rows, F/R/A comparisons by condition, yearly and monthly tables, and necessary examples with sources. Base the classifications on sealed D contexts. Quote only what is needed and avoid presenting examples as AI authorship judgments.
3. Build four resources from saved values for the nine comparison conditions, M05/M06 prevalence and amount among users, yearly general explanatory expressions, and saved tag composition. Keep full tables and summaries separately. Index each table's checks, source rows, and rerun commands.
4. Make the cohort periods, denominators, points versus percentage points, reasons for NA, and remaining differences in acquisition, measurement, and composition easy to find. Independently check chart values, year axes, descriptions, search, and links.
5. If the November 23 supplement is explicitly requested, save formatting by tag and the fixed 24-article HTML presence check in separate derived files. Preserve original data, main calculations, candidates, and formal decisions.

## Required outputs

Save all outputs under the output_dir returned by start.
- `report.md`
- `manifest.json`
- `verification.json`
- `claim-ledger.json`
- `materials-index.json`
- `index.html`
- `conditions.tsv`
- `structure-periods.tsv`
- `yearly-vocabulary.tsv`
- `tag-periods.tsv`

## Completion criteria

- C01 Retain the 18 decisions and all fixed candidates. Index prose, tables, figures, and examples with denominators and sources, and link them to the saved comparisons.
- C02 Build the four November 16 resources under the fixed conditions. Independently verify row counts, cohorts, missingness, units, and saved values.
- C03 Show the product of article prevalence and the mean among positive articles, the years without observations, tag missingness, and the definition of AI tags.
- C04 Verify HTML rendering, search, and links on the actual output. Record any areas that could not be verified and whether the optional November 23 work was performed.

Before completion, have a separate reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then apply the receipt with workflow.py finish from the root. Completion requires the full work after the pilot.

## Fixed reference rules

- [supplements.md](../supplements.md)
- [comparisons.md](../comparisons.md)
- [phase2-handoff.md](../phase2-handoff.md)

## Interpretation

- The comparison uses a fixed observed corpus. Treat topic and AI authorship as unknown when the only evidence is a missing tag, and avoid treating the whole corpus as classified technical articles.
- The supplementary materials describe the fixed observed corpus. Purchasing, publication, final manuscript approval, and measurement accuracy are outside their scope.

See [phase2-handoff.md](phase2-handoff.md) for the handoff and [status.json](status.json) for status.
