# Draft calibration rubric for material that fulfills the title

This draft covers only the 32 blinded A07 calibration cases. It becomes frozen after independent review by the parent task.

## Inputs and decision order

Read the title alone and identify one promise. Freeze that decision before reading the body. If the title supports two or more interpretations, choose “no specific promise or unclear” and set the content state to `undeterminable`. Then read the archived body in DOM order and find the first concrete material that fulfills the promise. Consider only the archived text, excluding external pages, videos, and text within images.

| Title promise | What counts as the first material | Calibration examples |
| --- | --- | --- |
| Operation or implementation | A concrete action, setting, command, or implementation detail the reader can use | GET request in 7, Fuse setup in 23, console operation in 32 |
| Troubleshooting | A concrete check, change, or recovery action for the problem | Procfile check in 10 |
| Comparison or selection | A criterion or result specific to an option. For a two-way comparison, include both sides. | Function uses in 2, discount rates in 5, difference between two events in 16 |
| Experience or opinion | A firsthand event or observation, or a concrete example supporting a claim | Member count in 9, views in 17, development experience in 29 |
| No specific promise or unclear | The title leaves the type of material ambiguous | 1, 4, 21, 24, 25, 27 |

A product name with a brief description can leave it unclear whether the title promises experience, a design explanation, or an operation. In 6, classify “Blockchatting: A Peer-to-Peer Messaging dApp” as undeterminable using the title alone, regardless of “I have built” in the body. “From CMS To Contextual Editing” could promise migration instructions or a conceptual explanation, so 18 is also undeterminable. “Getting better at team communication” could promise experience or advice, so 21 is undeterminable.

## Content states

| State | Condition |
| --- | --- |
| `matched` | The first matching material can be identified in the archived body. Record the excerpt and position. |
| `no_material` | The promise is clear and the archived body lacks matching material. |
| `undeterminable` | The title promise or matching passage cannot be determined unambiguously. |
| `inapplicable` | The archived item is outside the article evaluation scope. |

Exclude greetings, previews, tables of contents, and lists of names found only in headings. Treat references to related external articles as references alone. Assign `no_material` to the archived bodies for 12 and 13 even though implementation details may appear elsewhere. Assign `inapplicable` to the metadata-like advertisement in 28 and the weekly newsletter in 31.

For an operation or implementation, start at the first minimal, concrete approach tied to the subject. In 26, “I use compose function” counts because it describes a concrete approach using function composition. The correctness or sufficiency of details in the later `asyncCompose` code is outside this first-occurrence judgment.

The label captures where the material first appears. Record that readers may infer year or author from dates, proper names, and product versions even in blinded packets. Correctness, sufficiency, quality, and reader satisfaction are outside the rating.

## Save positions

Use the saved S word sequence and record each half-open range `[start,end)` from the first qualifying token through the last in `S_word_ranges`, in order. Keep exact token boundaries instead of rounding to the start of a source unit or sentence, a heading, or a transition. Preserve distinct ranges when material spans several source units. `S_start` and `S_end` give the outer bounds and allow gaps, as shown by `[109,122)` and `[159,185)` in 16. Preserve existing source units, tokens, and S word counts.

Use a separate body-character range and adjacent S boundary for material outside S. For the command in 18, retain body-character range `[965,1027)` and adjacent S boundary 131 as a counterexample where the classification is indeterminate. In 23, save body-character range `[434,462)` for the sudo line and adjacent S boundary 65 separately from the prose spans `[44,59)` and `[59,65)`. The blinded packets lack raw DOM node locators. Record them as code candidates based on how the body appears and wait for DOM verification before assigning `code_block`. Quote the original `body_context_text`. In 15, quote only the sentence about the event, excluding the heading.

Leave S position missing for `no_material`, `undeterminable`, and `inapplicable`. A true position of `0` words and a numerical value of `0` with a unit both count as observations. When S has zero words, use NA for the ratio and retain a computable preceding S count of 0 when applicable.

## Machine-generated candidates

Identify code blocks and inline code separately. Look for number-and-unit expressions and candidate constraints or prerequisites in every saved P/L/U prose unit. Calibration packets covered `paragraph` and `list_item` kinds. Match numeric ranges before single values, preserving `20-30 minutes` in full. Allow only `registered` as the intervening word in `70,000 registered members`. Reject substring matches in `2GB3`, `2GB_foo`, `20-30 minutesXYZ`, and `20-30 minutes3`. Reject candidates that overlap a saved URL token span. Treat `0ms` as a valid candidate.

Save the start of every DOM `ol` as auxiliary structural data. Record a separate `numbered_procedure_candidate` when a direct `li` child has the frozen Step-plus-number prefix or at least two of the first three children start with imperative verbs from the frozen dictionary. Both cues identify machine-generated candidates. The numbered list of functions in 2 and the list of providers in 5 illustrate numbering alone. Save the candidate dictionary separately as a draft based on the 32 calibration cases. Keep it fixed after opening the 128 evaluation cases or full-cohort results.
