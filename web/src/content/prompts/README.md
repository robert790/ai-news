# OpenRadar Web V2 Prompt Content Pilot

This directory holds the canonical OpenRadar prompt records for the Web V2 pilot.

## Status

This is the **canonical Web V2 prompt-content pilot**. It is the editorial source for prompts that will eventually surface in the Web V2 `/prompt-kits` experience. It is **not** the runtime content of the production Streamlit application.

As of Pilot V1 owner authorization on 2026-07-16:

- All five Pilot V1 records are owner-approved (`reviewStatus: "approved"`, `commercialUseStatus: "cleared"`, `publicationEligibility: "prompt-kits"`).
- The records are eligible for future Prompt Kits integration. They are **not** yet wired into the public route; the wiring is a separate change.
- Professional prompts still require appropriate human review at use time, regardless of their approved eligibility.
- See `docs/content-os/prompt-pilot-owner-decisions-v1.md` for the durable owner-decision record (reviewer, timestamp, source SHA, packet SHA).

## Relationship to legacy content

- `prompts_data/prompts.json` (the legacy data file) is **untouched**. It still powers the Streamlit production UI.
- `prompts.py` and `app.py` are unchanged.
- Batch 1 records are rewrites of legacy Prompt Bible concepts under the same ID, with provenance recorded as a structured `internal-concept` reference on every record. Batch 2 records are not rewrites of legacy content in the same shape; they use OpenRadar-authored wording developed around frozen internal concept IDs, with the per-record exception noted under "Batch 2" below.

## What lives here

- `types.ts` -- the TypeScript contract for a canonical prompt record.
- `collections.ts` -- the canonical collection registry (`BUILDER_BENCH`, `EDITOR_DESK`, `OPERATOR_PLAYBOOK`, `STUDIO_FOUNDATION`, `RESEARCH_DESK`, `DECISION_ROOM`).
- `pilot-batch-1.ts` -- the first five canonical records. Exports `pilotBatch1Records`.
- `pilot-batch-2.ts` -- the next five canonical records, currently all `draft` and `pending`. Exports `pilotBatch2Records`.
- `index.ts` -- the **sole catalog source**. Imports every batch explicitly, exports `pilotBatch1Records`, `pilotBatch2Records`, and `promptRecords` (the complete catalog). There is no runtime file globbing; the catalog is a static import graph.
- `web/scripts/validate-prompt-content.mjs` -- the validator. Compiles the canonical index with the installed TypeScript compiler, emits to a temp directory, loads the emitted module with the normal Node loader, then runs the pure validation functions on the loaded catalog. Run with `npm run content:validate` from `web/`.
- `web/scripts/validate-prompt-content.lib.mjs` -- the pure validation functions. Exported so the negative-test suite can validate supplied record arrays directly, without subprocesses or fixture files.
- `web/scripts/validate-prompt-content.test.mjs` -- negative tests for the validator, run with `node --test`. Run with `npm run content:test` from `web/`.

## The canonical contract (v1)

### Identity

- `id` is lowercase kebab-case, immutable, and stable across the lifetime of the record.
- `slug` is the routing identity. In v1, `slug === id` is enforced.
- IDs and slugs are unique across the complete catalog.

### Provenance

- `sourceType` is one of `openradar-original`, `openradar-rewrite`, or `external-reference`.
- `sourceReferences` is a list of structured references, each with:
  - `kind` -- one of `internal-concept`, `public-framework`, `standard`, `paper`, `external-reference`.
  - `label` -- short, non-empty.
  - `url` -- optional; must be a non-empty valid http/https URL when present.
  - `note` -- optional; must be a non-empty string when present.
- Reference count rule per `sourceType`:
  - `openradar-rewrite`: at least one reference.
  - `external-reference`: at least one reference.
  - `openradar-original`: zero references, or exactly one `internal-concept` reference.
- All Batch 1 records are `openradar-rewrite` with a single `internal-concept` reference labelled `Legacy Prompt Bible concept: <record-id>` and a `note` stating the wording was rewritten from first principles.
- Batch 2 records do not all share this shape. See "Batch 2" below for the per-record provenance. The reference-count rule per `sourceType` still applies; the validator enforces it on every record regardless of batch.

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

There is no `legal-review` state. There is no inferred state. Post-draft states carry only the three fields above.

### Commercial use

`commercialUseStatus` is one of `"pending" | "cleared" | "restricted"`. Pilot V1 records are `cleared`.

### Publication eligibility

`publicationEligibility` is one of `"internal" | "prompt-kits"`.

- `internal` — not approved for public Prompt Kits integration.
- `prompt-kits` — owner-approved as eligible for future Prompt Kits integration.

Eligibility records owner approval only. It does **not** mean the record is currently wired into the public route.

Eligibility invariants:

- `publicationEligibility: "prompt-kits"` requires:
  - `reviewStatus: "approved"`.
  - `commercialUseStatus: "cleared"`.
  - non-empty `reviewer`.
  - valid `lastReviewedAt`.
- `draft`, `editor-reviewed`, or `rejected` records cannot use `"prompt-kits"`.
- A `rejected` record must use `"internal"`.

The validator enforces these invariants.

### Safety classification

`safetyClass` is one of `general`, `professional`, or `sensitive`.

### Collections

A record belongs to one or more registered collections. The registry lives in `collections.ts` and contains exactly:

- `builder-bench`
- `editor-desk`
- `operator-playbook`
- `studio-foundation`
- `research-desk`
- `decision-room`

The validator rejects any `collectionIds` value that is not in this registry.

### Input contract

Each declared input in `inputs`:

- `name` is lowercase snake_case, unique within the record.
- `label` and `description` are non-empty strings.
- `example` is an optional non-empty string when present.

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

`content:validate`:

- Type-checks the canonical index with the installed TypeScript compiler.
- Emits the canonical index graph to a temporary directory.
- Loads the emitted module via the normal Node loader (CommonJS, extension-less imports).
- Runs the pure validation functions on the loaded catalog.
- Cleans up the temporary output.

`content:test`:

- Imports the pure validation functions directly.
- Builds malformed record objects in memory.
- Asserts each malformed record fails for its intended reason.
- Does NOT spawn subprocesses or copy fixture files.

## Promotion requirements

A record can move out of `draft` only when all of the following are true:

1. An editor has read it end to end and filled in `reviewer` and `lastReviewedAt`.
2. The review notes have been recorded somewhere durable (likely a follow-up doc, not in this file).
3. `commercialUseStatus` is flipped to `cleared` only after the wording has been cleared for commercial publication.
4. `reviewStatus` moves through `editor-reviewed` before reaching `approved` or `rejected`.

Until then, treat every record here as a working draft and do not publish it externally.

## Disclaimer

Automated checks do not prove originality, factual correctness, editorial quality, or safe execution. Inclusion in this directory does **not** equal legal clearance, public publication, or commercial use. Batch 1 Pilot V1 wording has been editorially reviewed and approved. Batch 2 remains draft, commercially pending, internally eligible only, and not editorially approved. No automated or human check can prove factual correctness of a model response or guarantee safe execution of an operational action. Use the structure; do not rely on the prose for safety-critical decisions.

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

Future batches are added by importing the new batch file's record array into `index.ts` and spreading it into `promptRecords`. There is no globbing.

### Batch 2 (drafts, not yet eligible for Prompt Kits)

Batch 2 (`pilot-batch-2.ts`) adds the next five canonical records as drafts. They are not yet wired into the public selector and are not part of `PILOT_V1_LOCK_IDS` in `selectors.ts`. Each Batch 2 record carries:

- `reviewStatus: "draft"`, `reviewer: null`, `lastReviewedAt: null`.
- `commercialUseStatus: "pending"` and `publicationEligibility: "internal"`.
- `safetyClass: "professional"` and `contentVersion: 1`.
- `authorship: "OpenRadar editorial"`.

Every Batch 1 record is a rewrite of a legacy Prompt Bible concept under the same ID. Batch 2 records use OpenRadar-authored wording developed around frozen internal concept IDs unless a record explicitly identifies a public framework. Every record carries structured provenance appropriate to its source type.

All Batch 2 records remain draft, commercially pending, internally eligible only, and not editorially approved.

Concretely, four Batch 2 records are `openradar-original` with one `internal-concept` `sourceReferences` entry naming the frozen concept ID and noting that the wording was rewritten from first principles. `decide-pre-mortem` is `openradar-rewrite` with one `public-framework` reference for the named pre-mortem method; no URL is attached because none has been verified for inclusion. The pre-mortem wording was rewritten from first principles around that public framework name.

The AMBER Batch 2 records remain pending until owner and legal-trust review resolves attribution concerns.

Batch 2 IDs:

- `code-refactor-no-driveby` (builder-bench)
- `write-incident-postmortem` (operator-playbook)
- `research-source-triangulate` (research-desk)
- `decide-pre-mortem` (decision-room, openradar-rewrite)
- `operate-auto-rollback-conditions` (operator-playbook)

Batch 2 also extends the collection registry in `collections.ts` with `research-desk` and `decision-room`.