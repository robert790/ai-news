#!/usr/bin/env node
/**
 * Pilot V1 wiring tests for the Web V2 /prompt-kits selector.
 *
 * These tests import the pure selector from
 * `web/src/content/prompts/selectors.ts` and exercise it against:
 *   - in-memory record arrays (for negative cases),
 *   - the live canonical catalog loaded through the TypeScript
 *     compiler + CommonJS emit (for positive cases), using the same
 *     pipeline that the canonical validator uses, so the wiring is
 *     exercised against the real source of truth.
 *
 * Run via `npm run content:test` (which uses `node --test`).
 *
 * This suite is intentionally narrower than the canonical validator
 * suite. It covers only the exact-five fail-closed contract, the
 * five-field eligibility predicate, professional-safety mapping,
 * copy-source equals canonical prompt body, and a live-catalog
 * smoke check.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

import ts from "typescript";

const __dirname = dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = resolve(__dirname, "..");
const INDEX_PATH = resolve(
  WEB_ROOT,
  "src",
  "content",
  "prompts",
  "index.ts",
);
const SELECTORS_PATH = resolve(
  WEB_ROOT,
  "src",
  "content",
  "prompts",
  "selectors.ts",
);

/**
 * Compile and emit the selector module to a temp directory and load
 * the emitted CJS through the normal Node loader. Mirrors the
 * canonical validator pipeline so the test exercises the actual
 * source of truth.
 */
function loadSelectors() {
  const program = ts.createProgram([SELECTORS_PATH], {
    noEmit: false,
    strict: true,
    module: ts.ModuleKind.CommonJS,
    moduleResolution: ts.ModuleResolutionKind.Node10,
    target: ts.ScriptTarget.ES2022,
    skipLibCheck: true,
    esModuleInterop: true,
    allowSyntheticDefaultImports: true,
  });
  const diag = ts.getPreEmitDiagnostics(program);
  if (diag.length > 0) {
    const messages = diag
      .map((d) => ts.flattenDiagnosticMessageText(d.messageText, "\n"))
      .join("\n");
    throw new Error(`Selector compile failed: ${messages}`);
  }
  const tmp = mkdtempSync(join(tmpdir(), "openradar-selectors-"));
  try {
    const emit = ts.createProgram([SELECTORS_PATH], {
      noEmit: false,
      strict: true,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.Node10,
      target: ts.ScriptTarget.ES2022,
      skipLibCheck: true,
      esModuleInterop: true,
      allowSyntheticDefaultImports: true,
      outDir: tmp,
      rootDir: WEB_ROOT,
    });
    const result = emit.emit();
    const emitDiags = ts.getPreEmitDiagnostics(emit).concat(result.diagnostics);
    if (emitDiags.length > 0) {
      throw new Error(
        "Selector emit failed: " +
          emitDiags.map((d) => ts.flattenDiagnosticMessageText(d.messageText, "\n")).join("\n"),
      );
    }
    const emittedPath = join(tmp, "src", "content", "prompts", "selectors.js");
    const req = createRequire(import.meta.url);
    return req(emittedPath);
  } finally {
    process.on("exit", () => {
      try {
        rmSync(tmp, { recursive: true, force: true });
      } catch {
        // best-effort
      }
    });
  }
}

const selectors = loadSelectors();
const {
  PILOT_V1_LOCK_IDS,
  PROFESSIONAL_SAFETY_NOTICES,
  PromptKitsPilotV1UnavailableError,
  isPilotV1LockId,
  isPromptKitsEligible,
  professionalSafetyNoticeFor,
  selectPromptKitsPilotV1,
} = selectors;

/**
 * Build a known-good Batch 1 record. Mirrors the in-test fixture
 * used by the canonical validator negative tests, but matches the
 * canonical Batch 1 ids one-to-one.
 */
function baseRecord(overrides = {}) {
  return {
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Pull request description that reads like a change record",
    category: "code",
    difficulty: "beginner",
    audience: "Engineers opening pull requests.",
    useCase: "When you are about to open a pull request.",
    inputs: [
      {
        name: "change_summary",
        label: "Change summary",
        description: "What changed.",
      },
    ],
    prompt: "Prompt body. {change_summary}",
    expectedOutput: "Expected output.",
    notes: [{ title: "Note", body: "Note body." }],
    antiPatterns: [{ title: "Anti", body: "Anti body." }],
    collectionIds: ["builder-bench"],
    sourceType: "openradar-rewrite",
    sourceReferences: [
      {
        kind: "internal-concept",
        label: "Legacy concept",
      },
    ],
    authorship: "OpenRadar editorial",
    reviewStatus: "approved",
    reviewer: "Robert Voicu",
    lastReviewedAt: "2026-07-16T19:12:27Z",
    contentVersion: 1,
    safetyClass: "general",
    commercialUseStatus: "cleared",
    publicationEligibility: "prompt-kits",
    ...overrides,
  };
}

/**
 * Build the five canonical Batch 1 records with one input each.
 * The default difficulty / safetyClass matches the canonical
 * source: code-pr-description and design-frontend-page-skeleton
 * are general; the other three are professional.
 */
function canonicalBatch1() {
  return [
    baseRecord({
      id: "code-pr-description",
      slug: "code-pr-description",
      title: "Pull request description",
      safetyClass: "general",
      collectionIds: ["builder-bench"],
      difficulty: "beginner",
      category: "code",
    }),
    baseRecord({
      id: "code-review-staff",
      slug: "code-review-staff",
      title: "Staff-level code review",
      safetyClass: "professional",
      collectionIds: ["builder-bench"],
      difficulty: "advanced",
      category: "code",
    }),
    baseRecord({
      id: "write-customer-notification",
      slug: "write-customer-notification",
      title: "Customer notification",
      safetyClass: "professional",
      collectionIds: ["editor-desk"],
      difficulty: "advanced",
      category: "write",
    }),
    baseRecord({
      id: "operate-incident-first-15-minutes",
      slug: "operate-incident-first-15-minutes",
      title: "Incident first 15 minutes",
      safetyClass: "professional",
      collectionIds: ["operator-playbook"],
      difficulty: "advanced",
      category: "operate",
    }),
    baseRecord({
      id: "design-frontend-page-skeleton",
      slug: "design-frontend-page-skeleton",
      title: "Frontend page skeleton",
      safetyClass: "general",
      collectionIds: ["studio-foundation"],
      difficulty: "intermediate",
      category: "design",
    }),
  ];
}

// ---------------- Eligibility predicate ----------------

test("eligibility: draft record is rejected", () => {
  const r = baseRecord({
    id: "draft-1",
    slug: "draft-1",
    title: "Draft",
    reviewStatus: "draft",
    reviewer: null,
    lastReviewedAt: null,
    commercialUseStatus: "cleared",
    publicationEligibility: "prompt-kits",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: editor-reviewed record is rejected", () => {
  const r = baseRecord({
    id: "editor-1",
    slug: "editor-1",
    title: "Editor-reviewed",
    reviewStatus: "editor-reviewed",
    reviewer: "Someone",
    lastReviewedAt: "2026-07-16T12:00:00Z",
    publicationEligibility: "prompt-kits",
    commercialUseStatus: "cleared",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: pending commercialUseStatus is rejected", () => {
  const r = baseRecord({
    id: "pending-1",
    slug: "pending-1",
    title: "Pending",
    commercialUseStatus: "pending",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: restricted commercialUseStatus is rejected", () => {
  const r = baseRecord({
    id: "restricted-1",
    slug: "restricted-1",
    title: "Restricted",
    commercialUseStatus: "restricted",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: rejected reviewStatus is rejected", () => {
  const r = baseRecord({
    id: "rejected-1",
    slug: "rejected-1",
    title: "Rejected",
    reviewStatus: "rejected",
    publicationEligibility: "internal",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: internal publicationEligibility is rejected", () => {
  const r = baseRecord({
    id: "internal-1",
    slug: "internal-1",
    title: "Internal",
    publicationEligibility: "internal",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: empty reviewer is rejected", () => {
  const r = baseRecord({
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Empty reviewer",
    reviewer: "",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: whitespace-only reviewer is rejected", () => {
  const r = baseRecord({
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Whitespace reviewer",
    reviewer: "   ",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: null reviewer is rejected", () => {
  const r = baseRecord({
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Null reviewer",
    reviewer: null,
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: missing reviewer is rejected", () => {
  const r = baseRecord({
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Missing reviewer",
  });
  // delete the reviewer field entirely
  delete r.reviewer;
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: empty lastReviewedAt is rejected", () => {
  const r = baseRecord({
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Empty timestamp",
    lastReviewedAt: "",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: null lastReviewedAt is rejected", () => {
  const r = baseRecord({
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Null timestamp",
    lastReviewedAt: null,
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: missing lastReviewedAt is rejected", () => {
  const r = baseRecord({
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Missing timestamp",
  });
  delete r.lastReviewedAt;
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: invalid lastReviewedAt is rejected", () => {
  const r = baseRecord({
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Invalid timestamp",
    lastReviewedAt: "not-a-real-date",
  });
  assert.equal(isPromptKitsEligible(r), false);
});

test("eligibility: approved + cleared + prompt-kits + valid reviewer + valid lastReviewedAt passes", () => {
  const r = baseRecord({});
  assert.equal(isPromptKitsEligible(r), true);
});

test("eligibility: non-object inputs are rejected", () => {
  assert.equal(isPromptKitsEligible(null), false);
  assert.equal(isPromptKitsEligible("string"), false);
  assert.equal(isPromptKitsEligible(42), false);
});

// ---------------- Lock intersection ----------------

test("lock: only canonical Batch 1 ids are accepted", () => {
  assert.equal(isPilotV1LockId("code-pr-description"), true);
  assert.equal(isPilotV1LockId("code-review-staff"), true);
  assert.equal(isPilotV1LockId("write-customer-notification"), true);
  assert.equal(isPilotV1LockId("operate-incident-first-15-minutes"), true);
  assert.equal(isPilotV1LockId("design-frontend-page-skeleton"), true);
  // Batch 2-style ids are explicitly rejected even when they pass
  // the eligibility triple.
  assert.equal(isPilotV1LockId("write-release-notes"), false);
  assert.equal(isPilotV1LockId(""), false);
  assert.equal(isPilotV1LockId(null), false);
  assert.equal(isPilotV1LockId(undefined), false);
});

test("selector: pilot lock is exactly five ids", () => {
  assert.equal(PILOT_V1_LOCK_IDS.length, 5);
});

// ---------------- Exact-five positive behavior ----------------

test("selector: returns exactly 5 records from canonical Batch 1", () => {
  const records = canonicalBatch1();
  const out = selectPromptKitsPilotV1(records);
  assert.equal(out.length, 5);
});

test("selector: returns records in canonical Batch 1 lock order", () => {
  // Feed records in REVERSE canonical order. The selector must
  // still emit them in canonical order, ignoring input order.
  const records = [...canonicalBatch1()].reverse();
  const out = selectPromptKitsPilotV1(records);
  assert.deepEqual(
    out.map((r) => r.id),
    [
      "code-pr-description",
      "code-review-staff",
      "write-customer-notification",
      "operate-incident-first-15-minutes",
      "design-frontend-page-skeleton",
    ],
  );
});

test("selector: drops records that pass eligibility but are not in the lock", () => {
  // A non-lock record that is otherwise eligible must be ignored;
  // the result must still be the canonical five.
  const records = [
    ...canonicalBatch1(),
    baseRecord({
      id: "write-release-notes",
      slug: "write-release-notes",
      title: "Release notes",
      collectionIds: ["editor-desk"],
      category: "write",
      difficulty: "beginner",
      safetyClass: "general",
    }),
  ];
  const out = selectPromptKitsPilotV1(records);
  assert.equal(out.length, 5);
  assert.equal(
    out.some((r) => r.id === "write-release-notes"),
    false,
    "non-lock id was unexpectedly surfaced",
  );
});

// ---------------- Exact-five fail-closed negatives ----------------

test("selector: throws when promptRecords is not an array", () => {
  assert.throws(
    () => selectPromptKitsPilotV1(null),
    (err) => err instanceof PromptKitsPilotV1UnavailableError,
  );
  assert.throws(
    () => selectPromptKitsPilotV1("not-an-array"),
    (err) => err instanceof PromptKitsPilotV1UnavailableError,
  );
  assert.throws(
    () => selectPromptKitsPilotV1({}),
    (err) => err instanceof PromptKitsPilotV1UnavailableError,
  );
});

test("selector: throws on empty catalog", () => {
  assert.throws(
    () => selectPromptKitsPilotV1([]),
    (err) => err instanceof PromptKitsPilotV1UnavailableError,
  );
});

test("selector: throws when only ineligible records are present", () => {
  const records = [
    baseRecord({
      id: "draft-1",
      slug: "draft-1",
      title: "Draft",
      reviewStatus: "draft",
      reviewer: null,
      lastReviewedAt: null,
      commercialUseStatus: "pending",
      publicationEligibility: "internal",
    }),
  ];
  assert.throws(
    () => selectPromptKitsPilotV1(records),
    (err) => err instanceof PromptKitsPilotV1UnavailableError,
  );
});

test("selector: throws when only non-lock ids are present", () => {
  const records = [
    baseRecord({
      id: "write-release-notes",
      slug: "write-release-notes",
      title: "Release notes",
      collectionIds: ["editor-desk"],
      category: "write",
      difficulty: "beginner",
      safetyClass: "general",
    }),
  ];
  assert.throws(
    () => selectPromptKitsPilotV1(records),
    (err) => err instanceof PromptKitsPilotV1UnavailableError,
  );
});

test("selector: throws on duplicate lock ids in the catalog", () => {
  const records = [
    ...canonicalBatch1(),
    baseRecord({
      id: "code-pr-description",
      slug: "code-pr-description-dup",
      title: "Duplicate of code-pr-description",
      collectionIds: ["builder-bench"],
      category: "code",
      difficulty: "beginner",
      safetyClass: "general",
    }),
  ];
  let thrown = null;
  try {
    selectPromptKitsPilotV1(records);
  } catch (err) {
    thrown = err;
  }
  assert.ok(thrown instanceof PromptKitsPilotV1UnavailableError);
  assert.ok(
    String(thrown.message).includes("duplicate lock id"),
    `expected duplicate-id error, got: ${thrown.message}`,
  );
  assert.ok(
    String(thrown.message).includes("code-pr-description"),
    `expected error to mention the duplicate id, got: ${thrown.message}`,
  );
});

test("selector: throws when any required lock id is missing", () => {
  // Remove the last required id and verify the diagnostic lists
  // exactly the missing ids.
  const records = canonicalBatch1().filter(
    (r) => r.id !== "design-frontend-page-skeleton",
  );
  let thrown = null;
  try {
    selectPromptKitsPilotV1(records);
  } catch (err) {
    thrown = err;
  }
  assert.ok(thrown instanceof PromptKitsPilotV1UnavailableError);
  assert.ok(
    String(thrown.message).includes("missing required lock id"),
    `expected missing-id error, got: ${thrown.message}`,
  );
  assert.ok(
    String(thrown.message).includes("design-frontend-page-skeleton"),
    `expected error to name the missing id, got: ${thrown.message}`,
  );
});

test("selector: throws when more than one required lock id is missing", () => {
  // Remove TWO required ids; the error must name both.
  const records = canonicalBatch1().filter(
    (r) =>
      r.id !== "design-frontend-page-skeleton" &&
      r.id !== "operate-incident-first-15-minutes",
  );
  let thrown = null;
  try {
    selectPromptKitsPilotV1(records);
  } catch (err) {
    thrown = err;
  }
  assert.ok(thrown instanceof PromptKitsPilotV1UnavailableError);
  const msg = String(thrown.message);
  assert.ok(msg.includes("design-frontend-page-skeleton"));
  assert.ok(msg.includes("operate-incident-first-15-minutes"));
});

test("selector: throws when removing each individual required record (one-by-one)", () => {
  // For each of the five lock ids, run a four-of-five fixture and
  // assert the selector fails closed with that id in the message.
  for (const missingId of PILOT_V1_LOCK_IDS) {
    const records = canonicalBatch1().filter((r) => r.id !== missingId);
    let thrown = null;
    try {
      selectPromptKitsPilotV1(records);
    } catch (err) {
      thrown = err;
    }
    assert.ok(
      thrown instanceof PromptKitsPilotV1UnavailableError,
      `expected throw when removing ${missingId}`,
    );
    assert.ok(
      String(thrown.message).includes(missingId),
      `expected error to name ${missingId}, got: ${thrown.message}`,
    );
  }
});

test("selector: throws when any required record is changed to an ineligible state", () => {
  // For each lock id, mutate that record into an ineligible state
  // and assert the selector fails closed.
  const cases = [
    { id: "code-pr-description", mutate: (r) => ({ ...r, reviewStatus: "draft" }) },
    { id: "code-review-staff", mutate: (r) => ({ ...r, commercialUseStatus: "pending" }) },
    { id: "write-customer-notification", mutate: (r) => ({ ...r, publicationEligibility: "internal" }) },
    { id: "operate-incident-first-15-minutes", mutate: (r) => ({ ...r, reviewer: "" }) },
    { id: "design-frontend-page-skeleton", mutate: (r) => ({ ...r, lastReviewedAt: "bogus" }) },
  ];
  for (const { id, mutate } of cases) {
    const records = canonicalBatch1().map((r) =>
      r.id === id ? mutate(r) : r,
    );
    let thrown = null;
    try {
      selectPromptKitsPilotV1(records);
    } catch (err) {
      thrown = err;
    }
    assert.ok(
      thrown instanceof PromptKitsPilotV1UnavailableError,
      `expected throw when ${id} is ineligible`,
    );
    assert.ok(
      String(thrown.message).includes("ineligible"),
      `expected ineligible error, got: ${thrown.message}`,
    );
    assert.ok(
      String(thrown.message).includes(id),
      `expected error to name ${id}, got: ${thrown.message}`,
    );
  }
});

test("selector: throws when a required record has an empty reviewer", () => {
  const records = canonicalBatch1().map((r) =>
    r.id === "code-pr-description" ? { ...r, reviewer: "" } : r,
  );
  let thrown = null;
  try {
    selectPromptKitsPilotV1(records);
  } catch (err) {
    thrown = err;
  }
  assert.ok(thrown instanceof PromptKitsPilotV1UnavailableError);
  assert.ok(String(thrown.message).includes("reviewer"));
  assert.ok(String(thrown.message).includes("code-pr-description"));
});

test("selector: throws when a required record has a missing reviewer", () => {
  const records = canonicalBatch1().map((r) => {
    if (r.id !== "code-pr-description") return r;
    const { reviewer, ...rest } = r;
    return rest;
  });
  let thrown = null;
  try {
    selectPromptKitsPilotV1(records);
  } catch (err) {
    thrown = err;
  }
  assert.ok(thrown instanceof PromptKitsPilotV1UnavailableError);
  assert.ok(String(thrown.message).includes("reviewer"));
});

test("selector: throws when a required record has a null lastReviewedAt", () => {
  const records = canonicalBatch1().map((r) =>
    r.id === "code-pr-description"
      ? { ...r, lastReviewedAt: null }
      : r,
  );
  let thrown = null;
  try {
    selectPromptKitsPilotV1(records);
  } catch (err) {
    thrown = err;
  }
  assert.ok(thrown instanceof PromptKitsPilotV1UnavailableError);
  assert.ok(String(thrown.message).includes("lastReviewedAt"));
});

test("selector: throws when a required record has a missing lastReviewedAt", () => {
  const records = canonicalBatch1().map((r) => {
    if (r.id !== "code-pr-description") return r;
    const { lastReviewedAt, ...rest } = r;
    return rest;
  });
  let thrown = null;
  try {
    selectPromptKitsPilotV1(records);
  } catch (err) {
    thrown = err;
  }
  assert.ok(thrown instanceof PromptKitsPilotV1UnavailableError);
  assert.ok(String(thrown.message).includes("lastReviewedAt"));
});

test("selector: throws when a required record has an invalid lastReviewedAt", () => {
  const records = canonicalBatch1().map((r) =>
    r.id === "code-pr-description"
      ? { ...r, lastReviewedAt: "not-a-real-date" }
      : r,
  );
  let thrown = null;
  try {
    selectPromptKitsPilotV1(records);
  } catch (err) {
    thrown = err;
  }
  assert.ok(thrown instanceof PromptKitsPilotV1UnavailableError);
  assert.ok(String(thrown.message).includes("lastReviewedAt"));
});

test("selector: returns canonical PromptRecord objects unchanged", () => {
  const records = canonicalBatch1();
  const out = selectPromptKitsPilotV1(records);
  // Each returned record must be the EXACT same object reference
  // (no shallow copy / no metadata mutation).
  for (const rec of records) {
    const matched = out.find((r) => r.id === rec.id);
    assert.ok(matched, `selector dropped canonical record ${rec.id}`);
    assert.equal(matched, rec);
  }
});

// ---------------- Copy source = canonical prompt body ----------------

test("copy: every record's selected prompt equals its canonical prompt body", () => {
  // The page's Copy action writes `kit.prompt` directly. This test
  // pins that the selector returns the canonical prompt body
  // unchanged — i.e. the route's copy source equals the canonical
  // record's `prompt` field.
  const records = canonicalBatch1();
  for (const rec of records) {
    const out = selectPromptKitsPilotV1(records);
    const matched = out.find((r) => r.id === rec.id);
    assert.ok(matched, `selector dropped canonical record ${rec.id}`);
    assert.equal(matched.prompt, rec.prompt);
    // No placeholders were substituted by the selector.
    const placeholders = rec.prompt.match(/\{[a-z][a-z0-9_]*\}/g) ?? [];
    for (const ph of placeholders) {
      assert.ok(
        matched.prompt.includes(ph),
        `placeholder ${ph} was modified by the selector`,
      );
    }
  }
});

// ---------------- Safety notice mapping ----------------

test("safety: identifies exactly the three professional prompts that need a notice", () => {
  const records = canonicalBatch1();
  const noticeIds = records
    .map((r) => ({ id: r.id, notice: professionalSafetyNoticeFor(r) }))
    .filter((entry) => entry.notice !== null)
    .map((entry) => entry.id);
  assert.deepEqual(noticeIds, [
    "code-review-staff",
    "write-customer-notification",
    "operate-incident-first-15-minutes",
  ]);
});

test("safety: code-review-staff notice text is verbatim per spec", () => {
  const r = baseRecord({
    id: "code-review-staff",
    slug: "code-review-staff",
    title: "Staff-level code review",
    safetyClass: "professional",
  });
  assert.equal(
    professionalSafetyNoticeFor(r),
    "Human review is required before acting on consequential review findings.",
  );
});

test("safety: write-customer-notification notice text is verbatim per spec", () => {
  const r = baseRecord({
    id: "write-customer-notification",
    slug: "write-customer-notification",
    title: "Customer notification",
    safetyClass: "professional",
  });
  assert.equal(
    professionalSafetyNoticeFor(r),
    "Human review is required before customer delivery.",
  );
});

test("safety: operate-incident-first-15-minutes notice text is verbatim per spec", () => {
  const r = baseRecord({
    id: "operate-incident-first-15-minutes",
    slug: "operate-incident-first-15-minutes",
    title: "Incident first 15 minutes",
    safetyClass: "professional",
  });
  assert.equal(
    professionalSafetyNoticeFor(r),
    "Operational recommendations remain proposals until approved by an authorized responder.",
  );
});

test("safety: general records return null (no banner)", () => {
  const r1 = baseRecord({
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "PR description",
    safetyClass: "general",
  });
  const r2 = baseRecord({
    id: "design-frontend-page-skeleton",
    slug: "design-frontend-page-skeleton",
    title: "Page skeleton",
    safetyClass: "general",
  });
  assert.equal(professionalSafetyNoticeFor(r1), null);
  assert.equal(professionalSafetyNoticeFor(r2), null);
});

test("safety: notice map is frozen and keyed by the three required ids", () => {
  assert.equal(Object.isFrozen(PROFESSIONAL_SAFETY_NOTICES), true);
  for (const id of [
    "code-review-staff",
    "write-customer-notification",
    "operate-incident-first-15-minutes",
  ]) {
    assert.ok(
      Object.prototype.hasOwnProperty.call(PROFESSIONAL_SAFETY_NOTICES, id),
      `PROFESSIONAL_SAFETY_NOTICES missing required id '${id}'`,
    );
  }
});

// ---------------- Live canonical catalog (TS compile + emit) ----------------

/**
 * Compile the canonical index graph with the installed TypeScript
 * compiler, emit to a temp directory, and load the emitted module
 * through the normal Node loader. Mirrors the canonical validator's
 * pipeline so the wiring is exercised against the real source of
 * truth, not a hand-built fixture.
 */
async function loadCanonicalCatalog() {
  const program = ts.createProgram([INDEX_PATH], {
    noEmit: false,
    strict: true,
    module: ts.ModuleKind.CommonJS,
    moduleResolution: ts.ModuleResolutionKind.Node10,
    target: ts.ScriptTarget.ES2022,
    skipLibCheck: true,
    jsx: ts.JsxEmit.Preserve,
    esModuleInterop: true,
    allowSyntheticDefaultImports: true,
  });
  const diag = ts.getPreEmitDiagnostics(program);
  if (diag.length > 0) {
    const messages = diag
      .map((d) => ts.flattenDiagnosticMessageText(d.messageText, "\n"))
      .join("\n");
    throw new Error(`Canonical catalog compile failed: ${messages}`);
  }
  const tmp = mkdtempSync(join(tmpdir(), "openradar-pilot-v1-"));
  try {
    const emit = ts.createProgram([INDEX_PATH], {
      noEmit: false,
      strict: true,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.Node10,
      target: ts.ScriptTarget.ES2022,
      skipLibCheck: true,
      jsx: ts.JsxEmit.Preserve,
      esModuleInterop: true,
      allowSyntheticDefaultImports: true,
      outDir: tmp,
      rootDir: WEB_ROOT,
    });
    const result = emit.emit();
    const emitDiags = ts.getPreEmitDiagnostics(emit).concat(result.diagnostics);
    if (emitDiags.length > 0) {
      throw new Error(
        "Canonical catalog emit failed: " +
          emitDiags.map((d) => ts.flattenDiagnosticMessageText(d.messageText, "\n")).join("\n"),
      );
    }
    const emittedIndexPath = join(
      tmp,
      "src",
      "content",
      "prompts",
      "index.js",
    );
    const req = createRequire(import.meta.url);
    const mod = req(emittedIndexPath);
    if (!Array.isArray(mod.promptRecords)) {
      throw new Error("Canonical catalog did not export promptRecords");
    }
    return mod.promptRecords;
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

test("live catalog: returns exactly the five canonical Pilot V1 records", async () => {
  const catalog = await loadCanonicalCatalog();
  const out = selectPromptKitsPilotV1(catalog);
  assert.equal(out.length, 5);
});

test("live catalog: returns records in canonical lock order", async () => {
  const catalog = await loadCanonicalCatalog();
  const out = selectPromptKitsPilotV1(catalog);
  assert.deepEqual(
    out.map((r) => r.id),
    [
      "code-pr-description",
      "code-review-staff",
      "write-customer-notification",
      "operate-incident-first-15-minutes",
      "design-frontend-page-skeleton",
    ],
  );
});

test("live catalog: every returned record passes the five-field eligibility predicate", async () => {
  const catalog = await loadCanonicalCatalog();
  const out = selectPromptKitsPilotV1(catalog);
  for (const rec of out) {
    assert.equal(isPromptKitsEligible(rec), true, `in live catalog: ${rec.id}`);
    assert.equal(rec.reviewStatus, "approved");
    assert.equal(rec.commercialUseStatus, "cleared");
    assert.equal(rec.publicationEligibility, "prompt-kits");
    assert.ok(
      typeof rec.reviewer === "string" && rec.reviewer.length > 0,
      `${rec.id}: reviewer must be a non-empty string`,
    );
    assert.ok(
      typeof rec.lastReviewedAt === "string" && rec.lastReviewedAt.length > 0,
      `${rec.id}: lastReviewedAt must be a non-empty string`,
    );
  }
});

test("live catalog: exactly three records have a human-review notice", async () => {
  const catalog = await loadCanonicalCatalog();
  const out = selectPromptKitsPilotV1(catalog);
  const noticeCount = out.filter(
    (r) => professionalSafetyNoticeFor(r) !== null,
  ).length;
  assert.equal(noticeCount, 3);
});

// ---------------- Batch 2 invariants ----------------

const BATCH_2_IDS = Object.freeze([
  "code-refactor-no-driveby",
  "write-incident-postmortem",
  "research-source-triangulate",
  "decide-pre-mortem",
  "operate-auto-rollback-conditions",
]);

test("live catalog: complete catalog has exactly 10 records (Batch 1 + Batch 2)", async () => {
  const catalog = await loadCanonicalCatalog();
  assert.equal(catalog.length, 10);
});

test("live catalog: canonical catalog exposes Batch 1 and Batch 2 separately", async () => {
  const mod = loadCatalogExports();
  assert.equal(mod.pilotBatch1Records.length, 5);
  assert.equal(mod.pilotBatch2Records.length, 5);
  assert.equal(
    [...mod.pilotBatch2Records.map((r) => r.id)].sort().join(","),
    [...BATCH_2_IDS].sort().join(","),
  );
});

test("live catalog: Batch 2 IDs are absent from the public Prompt Kits selector", async () => {
  const catalog = await loadCanonicalCatalog();
  const out = selectPromptKitsPilotV1(catalog);
  const outIds = new Set(out.map((r) => r.id));
  for (const id of BATCH_2_IDS) {
    assert.equal(
      outIds.has(id),
      false,
      `Batch 2 id '${id}' leaked into the public selector`,
    );
  }
});

test("live catalog: public Prompt Kits selector still returns exactly 5 records", async () => {
  const catalog = await loadCanonicalCatalog();
  const out = selectPromptKitsPilotV1(catalog);
  assert.equal(out.length, 5);
});

test("live catalog: public Prompt Kits IDs and order are unchanged after Batch 2", async () => {
  const catalog = await loadCanonicalCatalog();
  const out = selectPromptKitsPilotV1(catalog);
  assert.deepEqual(
    out.map((r) => r.id),
    [
      "code-pr-description",
      "code-review-staff",
      "write-customer-notification",
      "operate-incident-first-15-minutes",
      "design-frontend-page-skeleton",
    ],
  );
});

test("live catalog: every Batch 2 record is draft, pending, and internally-eligible only", async () => {
  const mod = loadCatalogExports();
  for (const rec of mod.pilotBatch2Records) {
    assert.equal(rec.reviewStatus, "draft", `${rec.id}: reviewStatus must be 'draft'`);
    assert.equal(rec.reviewer, null, `${rec.id}: reviewer must be null when draft`);
    assert.equal(
      rec.lastReviewedAt,
      null,
      `${rec.id}: lastReviewedAt must be null when draft`,
    );
    assert.equal(
      rec.commercialUseStatus,
      "pending",
      `${rec.id}: commercialUseStatus must be 'pending'`,
    );
    assert.equal(
      rec.publicationEligibility,
      "internal",
      `${rec.id}: publicationEligibility must be 'internal'`,
    );
    assert.equal(
      rec.authorship,
      "OpenRadar editorial",
      `${rec.id}: authorship must be 'OpenRadar editorial'`,
    );
    assert.equal(
      rec.contentVersion,
      1,
      `${rec.id}: contentVersion must be 1`,
    );
    assert.equal(
      rec.safetyClass,
      "professional",
      `${rec.id}: safetyClass must be 'professional'`,
    );
    // Provenance: every Batch 2 record carries exactly one source reference.
    assert.equal(
      rec.sourceReferences.length,
      1,
      `${rec.id}: sourceReferences must be exactly one entry`,
    );
    // Four records are openradar-original with an internal-concept
    // reference. decide-pre-mortem is openradar-rewrite with a
    // public-framework reference for the named pre-mortem method,
    // per the Batch 2 corrections; no URL is attached.
    if (rec.id === "decide-pre-mortem") {
      assert.equal(
        rec.sourceType,
        "openradar-rewrite",
        `${rec.id}: sourceType must be 'openradar-rewrite'`,
      );
      assert.equal(
        rec.sourceReferences[0].kind,
        "public-framework",
        `${rec.id}: sourceReference kind must be 'public-framework'`,
      );
      assert.equal(
        rec.sourceReferences[0].url,
        undefined,
        `${rec.id}: sourceReference must not carry an unverified URL`,
      );
    } else {
      assert.equal(
        rec.sourceType,
        "openradar-original",
        `${rec.id}: sourceType must be 'openradar-original'`,
      );
      assert.equal(
        rec.sourceReferences[0].kind,
        "internal-concept",
        `${rec.id}: sourceReference kind must be 'internal-concept'`,
      );
    }
  }
});

test("live catalog: decide-pre-mortem carries a public-framework reference with no URL", async () => {
  const mod = loadCatalogExports();
  const rec = mod.pilotBatch2Records.find((r) => r.id === "decide-pre-mortem");
  assert.ok(rec, "decide-pre-mortem must exist in the canonical catalog");
  assert.equal(rec.sourceType, "openradar-rewrite");
  assert.equal(rec.sourceReferences.length, 1);
  assert.equal(rec.sourceReferences[0].kind, "public-framework");
  // Truthful label/note; no fabricated URL.
  assert.ok(
    typeof rec.sourceReferences[0].label === "string" &&
      rec.sourceReferences[0].label.trim().length > 0,
    "decide-pre-mortem public-framework label must be a non-empty string",
  );
  assert.equal(
    rec.sourceReferences[0].url,
    undefined,
    "decide-pre-mortem public-framework must not carry an unverified URL",
  );
});

test("live catalog: no Batch 2 record passes the public eligibility predicate", async () => {
  const mod = loadCatalogExports();
  for (const rec of mod.pilotBatch2Records) {
    assert.equal(
      isPromptKitsEligible(rec),
      false,
      `Batch 2 record '${rec.id}' must not be Prompt Kits eligible`,
    );
  }
});

/**
 * Compile the canonical index and load the emitted CJS module so the
 * Batch 2 invariant tests can read the separately-exported
 * pilotBatch1Records and pilotBatch2Records. Mirrors the
 * loadCanonicalCatalog() helper but additionally captures the
 * pilotBatch2Records export.
 */
function loadCatalogExports() {
  const program = ts.createProgram([INDEX_PATH], {
    noEmit: false,
    strict: true,
    module: ts.ModuleKind.CommonJS,
    moduleResolution: ts.ModuleResolutionKind.Node10,
    target: ts.ScriptTarget.ES2022,
    skipLibCheck: true,
    jsx: ts.JsxEmit.Preserve,
    esModuleInterop: true,
    allowSyntheticDefaultImports: true,
  });
  const diag = ts.getPreEmitDiagnostics(program);
  if (diag.length > 0) {
    const messages = diag
      .map((d) => ts.flattenDiagnosticMessageText(d.messageText, "\n"))
      .join("\n");
    throw new Error(`Canonical catalog compile failed: ${messages}`);
  }
  const tmp = mkdtempSync(join(tmpdir(), "openradar-batch2-exports-"));
  try {
    const emit = ts.createProgram([INDEX_PATH], {
      noEmit: false,
      strict: true,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.Node10,
      target: ts.ScriptTarget.ES2022,
      skipLibCheck: true,
      jsx: ts.JsxEmit.Preserve,
      esModuleInterop: true,
      allowSyntheticDefaultImports: true,
      outDir: tmp,
      rootDir: WEB_ROOT,
    });
    const result = emit.emit();
    const emitDiags = ts.getPreEmitDiagnostics(emit).concat(result.diagnostics);
    if (emitDiags.length > 0) {
      throw new Error(
        "Canonical catalog emit failed: " +
          emitDiags.map((d) => ts.flattenDiagnosticMessageText(d.messageText, "\n")).join("\n"),
      );
    }
    const emittedIndexPath = join(
      tmp,
      "src",
      "content",
      "prompts",
      "index.js",
    );
    const req = createRequire(import.meta.url);
    const mod = req(emittedIndexPath);
    if (!Array.isArray(mod.pilotBatch1Records)) {
      throw new Error("Canonical catalog did not export pilotBatch1Records");
    }
    if (!Array.isArray(mod.pilotBatch2Records)) {
      throw new Error("Canonical catalog did not export pilotBatch2Records");
    }
    return mod;
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}