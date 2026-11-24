# A05 Author Voice and Direct Address

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Measure pronouns, contractions, connective expressions, and punctuation in P using a dictionary.

## Inputs

- T03 cohort
- T02 P units, sentences, tokens, and author IDs

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Freeze the bundled dictionary and scan P for word forms and phrases, including paragraph openings.
2. Summarize the share of articles using each form, density per 1,000 P words, conditional density, and zero-word status by year, period, and word-count band.
3. Audit interpretations of US, we, you, quotations, and contractions against fixed excerpts.
4. Check dictionary matches, denominators, cluster resampling, and plotted values against an independent implementation.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `voice-article.csv`
- `voice-annual.csv`
- `voice-contrasts.csv`
- `voice-audit.json`
- `voice.svg`

## Completion Criteria

- C01 Word-form counts for all articles, the share of articles using each form, and density denominators for all articles and articles using the form are reported separately.
- C02 Ambiguous pronouns and contractions are checked in blinded excerpts, and the dictionary is frozen before results are examined.
- C03 First-person singular and contraction rates per 1,000 P words can be mapped unambiguously to T02 IDs.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a05-settings.json](../references/a05-settings.json)

## Interpretation

- Treat matches for I as word-form counts. Use content evidence to assess personal experience.
- Interpret word-form matches as linguistic features. They provide no evidence of AI use on their own.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
