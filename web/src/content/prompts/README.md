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
- `collections.ts` -- the canonical collection registry (`BUILDER_BENCH`, `EDITOR_DESK`, `OPERATOR_PLAYBOOK`, `STUDIO_FOUNDATION`).
- `pilot-batch-1.ts` -- the first five canonical records.
- `__fixtures__/` -- negative-test fixtures used only by the validator tests. Not shipped in any production path.
- `index.ts` -- barrel export for downstream consumers.
- `web/scripts/validate-prompt-content.mjs` -- dependency-free structural validator. Built on the installed TypeScript compiler. Run with `npm run content:validate` from `web/`.
- `web/scripts/validate-prompt-content.test.mjs` -- negative tests for the validator. Run with `npm run content:test` from `web/`.

## The canonical contract (v1)

### Identity

- `id` is lowercase kebab-case, immutable, and stable across the lifetime of the record. It is the canonical identifier.
- `slug` is the routing identity. In v1, `slug === id` is enforced.
- IDs must be unique across all loaded batch files. Slugs must be unique across all loaded batch files.

### Provenance

- `sourceType` is one of `openradar-original`, `openradar-rewrite`, or `external-reference`.
- `sourceReferences` is a list of structured references, each with:
  - `kind` -- one of `internal-concept`, `public-framework`, `standard`, `paper`, `external-reference`.
  - `label` -- short, non-empty.
  - `url` -- optional; must be a valid http/https URL when present.
  - `note` -- optional; non-empty when present.
- Reference count rule per `sourceType`:
  - `openradar-original`: zero references, or exactly one `internal-concept` reference.
  - `openradar-rewrite`: at least one reference.
  - `external-reference`: at least one reference.

### Review metadata (discriminated union)

The record's review state is a discriminated union on `reviewStatus`:

```ts
| { reviewStatus: "draft"; reviewer: null; lastReviewedAt: null; }
| {
    reviewStatus: "editor-reviewed" | "approved" | "rejected";
    reviewer: string;            // non-empty
    lastReviewedAt: string;      // valid ISO-8601
  }
```

There is no `legal-review` state. There is no inferred state. The four allowed states are the four above.

Post-draft states carry only the three fields above (`reviewStatus`, `reviewer`, `lastReviewedAt`). No rejection reason. No cleared-for-X list. No extra payloads.

### Commercial use

`commercialUseStatus` is one of `"pending" | "cleared" | "restricted"`. All current records are `pending`. Promotion to `cleared` is a separate review gate and is not part of this contract.

### Safety classification

`safetyClass` is one of:

- `general` -- low-consequence productivity or creative work.
- `professional` -- software quality, customer communication, incidents, operations, or organizational decisions.
- `sensitive` -- regulated, safety-critical, high-impact, or abuse-prone.

### Collections

A record belongs to one or more registered collections. The registry is in `collections.ts` and contains exactly:

- `builder-bench`
- `editor-desk`
- `operator-playbook`
- `studio-foundation`

The validator rejects any `collectionIds` value that is not in this registry.

### Input contract

Each declared input in `inputs`:

- `name` is lowercase snake_case, unique within the record.
- `label` and `description` are non-empty strings.
- `example` is an optional string.

Placeholder contract:

- Every declared `name` must appear as `{name}` in the prompt body.
- Every `{name}` placeholder in the prompt body must have a matching declared input.
- The same placeholder may appear more than once.

### Em-dash policy

Em dashes (and en dashes, as a defensive fallback) are forbidden in any user-facing field, recursively:

- `title`, `audience`, `useCase`, `prompt`, `expectedOutput`.
- `inputs[].label`, `inputs[].description`, `inputs[].example`.
- `notes[].title`, `notes[].body`.
- `antiPatterns[].title`, `antiPatterns[].body`.
- `sourceReferences[].label`, `sourceReferences[].note`.

Use a colon, two hyphens, or a sentence break instead.

### Vendor / model / product guard

The validator hard-fails on unambiguous vendor, model, or product phrases in prompt bodies (`chatgpt`, `gpt-4`, `claude sonnet`, `gemini pro`, `github copilot`, `hugging face`, etc.). It does NOT hard-fail on ordinary words like `cursor`, `linear`, or `notion`. This guard does NOT prove neutrality, originality, or safe production use.

### What the validator does not do

The validator does not attempt to judge:

- generated verdict consistency inside a code review record;
- factual correctness of any prompt body;
- originality of the wording;
- quality of the editorial notes or anti-pattern prose.

## Validation and tests

From the `web/` directory:

```sh
npm run content:validate
npm run content:test
```

The validator:

- Type-checks the canonical index using the installed TypeScript compiler.
- Loads each batch file by transpiling it with the installed compiler and reading its `promptRecords` export.
- Cross-checks every record against the rules above.
- Enforces the exact five-ID Batch 1 set as a separate rule for `pilot-batch-1.ts`.

The negative tests:

- Use Node's built-in test runner (`node --test`).
- Run the validator in a sandbox against fixture batch files under `__fixtures__/`.
- Assert each fixture fails for its intended reason.
- Do NOT reimplement validator rules.

## Promotion requirements

A record can move out of `draft` only when all of the following are true:

1. An editor has read it end to end and filled in `reviewer` and `lastReviewedAt`.
2. The review notes have been recorded somewhere durable (likely a follow-up doc, not in this file).
3. `commercialUseStatus` is flipped to `cleared` only after the wording has been cleared for commercial publication.
4. `reviewStatus` moves through `editor-reviewed` before reaching `approved` or `rejected`.

Until then, treat every record here as a working draft and do not publish it externally.

## Disclaimer

Automated checks do not prove originality, legal clearance, editorial quality, or safe production use. Inclusion in this directory does **not** equal legal clearance, public publication, or commercial use. The wording has not been reviewed by an editor, a lawyer, or a trust-and-safety reviewer. Use the structure; do not rely on the prose.

## Editing rules

- No em dashes anywhere in user-facing content. Use a colon, two hyphens, or a sentence break instead.
- Variables in prompt bodies use `{snake_case}` placeholders and must be explained in the matching `inputs` entry.
- The expected output must describe what a correct response looks like, not what a generic response looks like.
- Notes explain why the prompt works, not what it does.
- Anti-patterns describe real failure modes the prompt is designed to avoid, not vague warnings.
- Tool-agnostic wording only. No model name, no framework name, no product name in the prompt body.

## Frozen scope

The set of IDs that may appear in this pilot is frozen in `docs/content-os/prompt-pilot-scope-v1.md`. Batch 1 implements the first five:

- `code-pr-description`
- `code-review-staff`
- `write-customer-notification`
- `operate-incident-first-15-minutes`
- `design-frontend-page-skeleton`

Future batches must follow the same frozen scope document. The validator enforces the exact ID set for this batch as a separate rule.