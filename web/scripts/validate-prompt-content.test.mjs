#!/usr/bin/env node
/**
 * Negative tests for the canonical prompt-content validator.
 *
 * These tests import the pure validation functions from
 * `validate-prompt-content.lib.mjs` and feed them in-memory record
 * arrays. They do NOT:
 *   - copy fixture files,
 *   - spawn subprocesses,
 *   - sandbox a directory,
 *   - duplicate any validator rule.
 *
 * Each test builds a malformed record, runs validateCatalog, and
 * asserts that the expected error substring appears in the result.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  validateCatalog,
  validateBatch1Lock,
  BATCH_1_LOCK_IDS,
} from "./validate-prompt-content.lib.mjs";

/**
 * A known-good base record. Tests override one or two fields to
 * introduce a single specific defect.
 */
function baseRecord(overrides = {}) {
  return {
    id: "good-record",
    slug: "good-record",
    title: "Good record",
    category: "code",
    difficulty: "beginner",
    audience: "Audience.",
    useCase: "Use case.",
    inputs: [
      {
        name: "input_a",
        label: "Input A",
        description: "Description A.",
      },
    ],
    prompt: ["Prompt body.", "", "Input A: {input_a}"].join("\n"),
    expectedOutput: "Expected output.",
    notes: [{ title: "Note title", body: "Note body." }],
    antiPatterns: [{ title: "Anti-pattern title", body: "Anti-pattern body." }],
    collectionIds: ["builder-bench"],
    sourceType: "openradar-rewrite",
    sourceReferences: [
      {
        kind: "internal-concept",
        label: "Internal concept",
      },
    ],
    authorship: "OpenRadar editorial",
    reviewStatus: "approved",
    reviewer: "Reviewer",
    lastReviewedAt: "2026-07-16T19:12:27Z",
    contentVersion: 1,
    safetyClass: "general",
    commercialUseStatus: "cleared",
    publicationEligibility: "prompt-kits",
    ...overrides,
  };
}

const REGISTRY = new Set(["builder-bench", "editor-desk", "operator-playbook", "studio-foundation"]);

function runWith(records) {
  return validateCatalog(records, {
    collectionIdSet: REGISTRY,
  });
}

function runLockWith(records) {
  return validateBatch1Lock(records, BATCH_1_LOCK_IDS);
}

function assertHasError(result, fragment) {
  assert.ok(
    result.errors.some((e) => e.includes(fragment)),
    `expected an error containing ${JSON.stringify(fragment)}, got: ${JSON.stringify(result.errors, null, 2)}`,
  );
}

function assertNoError(result, fragment) {
  assert.ok(
    !result.errors.some((e) => e.includes(fragment)),
    `expected no error containing ${JSON.stringify(fragment)}, got: ${JSON.stringify(result.errors, null, 2)}`,
  );
}

// ---------------- existing cases ----------------

test("negative: missing required field", () => {
  const r = runWith([baseRecord({ title: "" })]);
  assertHasError(r, "title");
  assertHasError(r, "must be a non-empty string");
});

test("negative: malformed input", () => {
  const r = runWith([
    baseRecord({
      inputs: [{ name: "Bad Name", label: "x", description: "x" }],
    }),
  ]);
  assertHasError(r, "snake_case");
});

test("negative: malformed source reference", () => {
  const r = runWith([
    baseRecord({
      sourceReferences: [{ kind: "totally-bogus", label: "x" }],
    }),
  ]);
  assertHasError(r, "kind");
});

test("negative: duplicate ID", () => {
  const a = baseRecord({ id: "dup-id", slug: "dup-id-a", title: "A" });
  const b = baseRecord({ id: "dup-id", slug: "dup-id-b", title: "B" });
  const r = runWith([a, b]);
  assertHasError(r, "Duplicate id");
});

test("negative: duplicate slug", () => {
  const a = baseRecord({ id: "slug-a", slug: "shared-slug", title: "A" });
  const b = baseRecord({ id: "slug-b", slug: "shared-slug", title: "B" });
  const r = runWith([a, b]);
  assertHasError(r, "Duplicate slug");
});

test("negative: invalid ID or slug format", () => {
  const r = runWith([baseRecord({ id: "Bad-ID", slug: "Bad-ID" })]);
  assertHasError(r, "lowercase kebab-case");
});

test("negative: slug not equal to ID", () => {
  const r = runWith([baseRecord({ id: "good-id", slug: "good-slug" })]);
  assertHasError(r, "must equal id");
});

test("negative: duplicate input names", () => {
  const r = runWith([
    baseRecord({
      inputs: [
        { name: "input_a", label: "A1", description: "D1" },
        { name: "input_a", label: "A2", description: "D2" },
      ],
    }),
  ]);
  assertHasError(r, "duplicate input name");
});

test("negative: declared input absent from prompt", () => {
  const r = runWith([
    baseRecord({
      inputs: [
        { name: "input_a", label: "A", description: "D" },
        { name: "input_b", label: "B", description: "D" },
      ],
      prompt: "Prompt body. {input_a}",
    }),
  ]);
  assertHasError(r, "does not appear as a");
});

test("negative: undeclared prompt placeholder", () => {
  const r = runWith([
    baseRecord({
      inputs: [{ name: "input_a", label: "A", description: "D" }],
      prompt: "Prompt body. {input_a} {undeclared_input}",
    }),
  ]);
  assertHasError(r, "has no matching declared input");
});

test("negative: invalid post-draft metadata", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "editor-reviewed",
      reviewer: "",
      lastReviewedAt: "2026-07-16T12:00:00Z",
      publicationEligibility: "internal",
    }),
  ]);
  assertHasError(r, "reviewer must be a non-empty string");
});

test("negative: invalid ISO timestamp", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "editor-reviewed",
      reviewer: "someone",
      lastReviewedAt: "not-a-real-date",
      publicationEligibility: "internal",
    }),
  ]);
  assertHasError(r, "lastReviewedAt must be a valid ISO-8601");
});

test("negative: invalid commercialUseStatus", () => {
  const r = runWith([
    baseRecord({ commercialUseStatus: "undecided-but-also-probably-fine" }),
  ]);
  assertHasError(r, "commercialUseStatus");
});

test("negative: unknown collection ID", () => {
  const r = runWith([
    baseRecord({ collectionIds: ["this-collection-is-not-registered"] }),
  ]);
  assertHasError(r, "is not in the registered collection registry");
});

test("negative: forbidden prompt-body token", () => {
  const r = runWith([
    baseRecord({ prompt: "Prompt body mentioning chatgpt for no reason." }),
  ]);
  assertHasError(r, "forbidden vendor/model/product phrase");
});

test("negative: em dash in a nested user-facing field", () => {
  const r = runWith([
    baseRecord({
      notes: [{ title: "Note", body: "Body with em dash \u2014 here." }],
    }),
  ]);
  assertHasError(r, "em or en dash");
});

test("negative: duplicate prompt body", () => {
  const sharedPrompt = "Shared prompt body. {input_a}";
  const a = baseRecord({ id: "shared-a", slug: "shared-a", title: "A", prompt: sharedPrompt });
  const b = baseRecord({ id: "shared-b", slug: "shared-b", title: "B", prompt: sharedPrompt });
  const r = runWith([a, b]);
  assertHasError(r, "Duplicate prompt body");
});

// ---------------- new cases ----------------

test("negative: openradar-rewrite with no source reference", () => {
  const r = runWith([baseRecord({ sourceReferences: [] })]);
  assertHasError(r, "sourceReferences must include at least one reference for openradar-rewrite");
});

test("negative: invalid draft reviewer/timestamp combination", () => {
  // reviewStatus: 'draft' must have reviewer: null and lastReviewedAt: null.
  const r = runWith([
    baseRecord({
      reviewStatus: "draft",
      reviewer: "should-be-null",
      lastReviewedAt: null,
      commercialUseStatus: "pending",
      publicationEligibility: "internal",
    }),
  ]);
  assertHasError(r, "reviewer must be null");
});

test("negative: incorrect Batch 1 ID set", () => {
  // The Batch 1 lock is enforced separately against pilotBatch1Records.
  // Drop one of the required Batch 1 IDs and add a non-canonical one.
  const records = BATCH_1_LOCK_IDS.slice(0, 4).map((id, idx) =>
    baseRecord({ id, slug: id, title: `Record ${idx}` }),
  );
  records.push(baseRecord({ id: "extra-not-in-batch-1", slug: "extra-not-in-batch-1", title: "Extra" }));
  const r = runLockWith(records);
  assertHasError(r, "Batch 1 lock");
  assertHasError(r, "missing expected ID 'design-frontend-page-skeleton'");
  assertHasError(r, "unexpected ID 'extra-not-in-batch-1'");
});

test("negative: Batch 1 lock with all five required IDs plus an extra valid record", () => {
  // The Batch 1 lock is enforced against the separately-exported
  // pilotBatch1Records. The required five IDs are present, but
  // pilotBatch1Records also contains one additional valid record.
  // The lock must fail specifically because of the unexpected extra ID.
  const records = BATCH_1_LOCK_IDS.map((id, idx) =>
    baseRecord({
      id,
      slug: id,
      title: `Batch 1 record ${idx}`,
      prompt: `Prompt body for ${id}.\n{input_a}`,
    }),
  );
  records.push(
    baseRecord({
      id: "extra-valid-record",
      slug: "extra-valid-record",
      title: "Extra valid record",
      prompt: "Extra valid record prompt body.\n{input_a}",
    }),
  );
  const r = runLockWith(records);
  assertHasError(r, "Batch 1 lock");
  assertHasError(r, "has 6 record(s); expected exactly 5");
  assertHasError(r, "unexpected ID 'extra-valid-record'");
});

test("negative: cross-record duplicate prompt bodies", () => {
  // Already covered by the existing 'duplicate prompt body' test, but
  // spelled out as a separate case for the cross-record axis.
  const a = baseRecord({ id: "cross-a", slug: "cross-a", title: "A", prompt: "Cross record prompt body. {input_a}" });
  const b = baseRecord({ id: "cross-b", slug: "cross-b", title: "B", prompt: "Cross record prompt body. {input_a}" });
  const r = runWith([a, b]);
  assertHasError(r, "Duplicate prompt body");
});

test("negative: null record", () => {
  const r = runWith([null]);
  assertHasError(r, "must be an object");
});

test("negative: malformed notes entry", () => {
  const r = runWith([
    baseRecord({ notes: [{ title: "", body: "body" }] }),
  ]);
  assertHasError(r, "notes[0]: title must be a non-empty string");
});

test("negative: malformed antiPatterns entry", () => {
  const r = runWith([
    baseRecord({ antiPatterns: [{ title: "title", body: "" }] }),
  ]);
  assertHasError(r, "antiPatterns[0]: body must be a non-empty string");
});

test("negative: empty optional source-reference URL", () => {
  const r = runWith([
    baseRecord({
      sourceReferences: [
        {
          kind: "internal-concept",
          label: "Internal concept",
          url: "",
        },
      ],
    }),
  ]);
  assertHasError(r, "url must be a non-empty string when present");
});

test("negative: empty optional source-reference note", () => {
  const r = runWith([
    baseRecord({
      sourceReferences: [
        {
          kind: "internal-concept",
          label: "Internal concept",
          note: "   ",
        },
      ],
    }),
  ]);
  assertHasError(r, "note must be a non-empty string when present");
});

// ---------------- publication eligibility cases ----------------

test("negative: publicationEligibility missing", () => {
  const { publicationEligibility, ...rest } = baseRecord();
  const r = runWith([rest]);
  assertHasError(r, "publicationEligibility");
});

test("negative: draft + prompt-kits fails", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "draft",
      reviewer: null,
      lastReviewedAt: null,
      commercialUseStatus: "pending",
      publicationEligibility: "prompt-kits",
    }),
  ]);
  assertHasError(r, "'prompt-kits'");
});

test("negative: editor-reviewed + prompt-kits fails", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "editor-reviewed",
      reviewer: "someone",
      lastReviewedAt: "2026-07-16T19:12:27Z",
      publicationEligibility: "prompt-kits",
    }),
  ]);
  assertHasError(r, "reviewStatus 'editor-reviewed' cannot be paired with publicationEligibility 'prompt-kits'");
});

test("negative: approved + pending + prompt-kits fails", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "approved",
      reviewer: "someone",
      lastReviewedAt: "2026-07-16T19:12:27Z",
      commercialUseStatus: "pending",
      publicationEligibility: "prompt-kits",
    }),
  ]);
  assertHasError(r, "'prompt-kits' requires commercialUseStatus 'cleared'");
});

test("negative: rejected + prompt-kits fails", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "rejected",
      reviewer: "someone",
      lastReviewedAt: "2026-07-16T19:12:27Z",
      commercialUseStatus: "cleared",
      publicationEligibility: "prompt-kits",
    }),
  ]);
  assertHasError(r, "publicationEligibility 'prompt-kits' requires reviewStatus 'approved'");
});

test("negative: rejected + not-internal fails", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "rejected",
      reviewer: "someone",
      lastReviewedAt: "2026-07-16T19:12:27Z",
      commercialUseStatus: "cleared",
      publicationEligibility: "prompt-kits",
    }),
  ]);
  assertHasError(r, "rejected record must use publicationEligibility 'internal'");
});

test("positive: approved + cleared + prompt-kits passes", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "approved",
      reviewer: "Robert Voicu",
      lastReviewedAt: "2026-07-16T19:12:27Z",
      commercialUseStatus: "cleared",
      publicationEligibility: "prompt-kits",
    }),
  ]);
  assertNoError(r, "publicationEligibility");
  assert.equal(r.errors.length, 0, JSON.stringify(r.errors, null, 2));
});

test("negative: approved + cleared + prompt-kits but reviewer empty fails", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "approved",
      reviewer: "",
      lastReviewedAt: "2026-07-16T19:12:27Z",
      commercialUseStatus: "cleared",
      publicationEligibility: "prompt-kits",
    }),
  ]);
  assertHasError(r, "'prompt-kits' requires a non-empty reviewer");
});

test("negative: approved + cleared + prompt-kits but lastReviewedAt invalid fails", () => {
  const r = runWith([
    baseRecord({
      reviewStatus: "approved",
      reviewer: "Robert Voicu",
      lastReviewedAt: "not-a-real-date",
      commercialUseStatus: "cleared",
      publicationEligibility: "prompt-kits",
    }),
  ]);
  assertHasError(r, "'prompt-kits' requires a valid lastReviewedAt");
});

// ---------------- sanity check ----------------

test("positive: full Batch 1 catalog passes", () => {
  // The Batch 1 lock is part of every catalog validation. A positive
  // test must feed in records that satisfy it.
  const records = BATCH_1_LOCK_IDS.map((id, idx) =>
    baseRecord({
      id,
      slug: id,
      title: `Batch 1 record ${idx}`,
      prompt: `Prompt body for ${id}.\n{input_a}`,
    }),
  );
  const r = runWith(records);
  assert.equal(r.errors.length, 0, JSON.stringify(r.errors, null, 2));
});