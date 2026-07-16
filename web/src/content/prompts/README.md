# OpenRadar Web V2 Prompt Content Pilot

This directory holds the canonical OpenRadar prompt records for the Web V2 pilot.

## Status

This is the **canonical Web V2 prompt-content pilot**. It is the editorial source for prompts that will eventually surface in the Web V2 `/prompt-kits` experience. It is **not** the runtime content of the production Streamlit application.

## Relationship to legacy content

- `prompts_data/prompts.json` (the legacy data file) is **untouched**. It still powers the Streamlit production UI.
- `prompts.py` and `app.py` are unchanged.
- Records here are written from the same conceptual starting points as the frozen legacy IDs, but every word is OpenRadar-authored. No vendor sample blocks, no product-specific syntax, no living-creator names.

## What lives here

- `types.ts` -- the TypeScript contract for a canonical prompt record.
- `pilot-batch-1.ts` -- the first five canonical records.
- `index.ts` -- barrel export for downstream consumers.
- `web/scripts/validate-prompt-content.mjs` -- dependency-free structural validator. Run with `npm run content:validate` from `web/`.

## What the records are

Drafts. Every record currently has:

- `sourceType: "openradar-original"`
- `authorship: "OpenRadar editorial"`
- `reviewStatus: "draft"`
- `reviewer: null`
- `lastReviewedAt: null`
- `contentVersion: 1`
- `safetyClass: "general"`
- `commercialUseAllowed: false`

Inclusion in this directory does **not** equal legal clearance, public publication, or commercial use. The wording has not been reviewed by an editor, a lawyer, or a trust-and-safety reviewer.

## Promotion requirements

A record can move out of `draft` only when all of the following are true:

1. An editor has read it end to end and filled in `reviewer` and `lastReviewedAt`.
2. The review notes have been recorded somewhere durable (likely a follow-up doc, not in this file).
3. `commercialUseAllowed` is flipped to `true` only after the wording has been cleared for commercial publication.
4. `reviewStatus` moves through `editorial-review` and (where relevant) `legal-review` before reaching `approved`.

Until then, treat every record here as a working draft and do not publish it externally.

## Frozen scope

The set of IDs that may appear in this pilot is frozen in `docs/content-os/prompt-pilot-scope-v1.md`. Batch 1 implements the first five:

- `code-pr-description`
- `code-review-staff`
- `write-customer-notification`
- `operate-incident-first-15-minutes`
- `design-frontend-page-skeleton`

Future batches must follow the same frozen scope document. The validator enforces the exact ID set for this batch.

## Validation

From the `web/` directory:

```sh
npm run content:validate
```

The validator checks:

- exactly five records
- the exact ID set above
- unique IDs and slugs
- allowed categories and difficulties
- every required field present and non-empty where it must be
- inputs is a non-empty structured list with snake_case `name` and non-empty `label` and `description`
- notes and antiPatterns are non-empty lists
- `reviewStatus` is `draft`
- `commercialUseAllowed` is `false`
- `reviewer` and `lastReviewedAt` are `null`
- `sourceType` is `openradar-original`
- no em dash in any user-facing field
- no forbidden vendor / product / service tokens in prompt bodies
- no duplicate prompt bodies
- no placeholder values such as `TODO`, `lorem ipsum`, or `TBD`

The validator is dependency-free: it reads the TypeScript file, strips the type annotations, and evaluates the `promptRecords` array as plain JavaScript. No TypeScript toolchain required at runtime.

## Editing rules

- No em dashes anywhere in user-facing content. Use a colon, two hyphens, or a sentence break instead.
- Variables in prompt bodies use `{snake_case}` placeholders and must be explained in the matching `inputs` entry.
- The expected output must describe what a correct response looks like, not what a generic response looks like.
- Notes explain why the prompt works, not what it does.
- Anti-patterns describe real failure modes the prompt is designed to avoid, not vague warnings.
- Tool-agnostic wording only. No model name, no framework name, no product name in the prompt body.