#!/usr/bin/env node
/**
 * Pilot V1 wiring tests for the Web V2 /prompt-kits selector.
 *
 * These tests import the pure selector from
 * `web/src/content/prompts/selectors.mjs` and exercise it against:
 *   - in-memory record arrays (for negative cases),
 *   - the live canonical catalog loaded through the TypeScript
 *     compiler + CommonJS emit (for positive cases), using the same
 *     pipeline that the canonical validator uses, so the wiring is
 *     exercised against the real source of truth.
 *
 * Run via `npm run content:test` (which uses `node --test`).
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
    // Keep the dir alive for the duration of the process; only clean
    // up on process exit. The test process is short-lived, so this
    // is fine.
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

// ---------------- Eligibility ----------------

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

test("eligibility: approved + cleared + prompt-kits passes", () => {
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

// ---------------- Exact-five + canonical order ----------------

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

test("selector: duplicates are deduplicated by id", () => {
  const records = [...canonicalBatch1(), ...canonicalBatch1()];
  const out = selectPromptKitsPilotV1(records);
  assert.equal(out.length, 5);
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

test("selector: throws PilotV1UnavailableError on empty catalog", () => {
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

test("selector: tolerates a partial lock (missing ids are omitted, not thrown)", () => {
  // If the catalog has 4 of 5 lock ids, the selector still
  // returns the 4 it can find. Throwing is reserved for the
  // zero-eligible case.
  const records = canonicalBatch1().filter(
    (r) => r.id !== "design-frontend-page-skeleton",
  );
  const out = selectPromptKitsPilotV1(records);
  assert.equal(out.length, 4);
  assert.equal(
    out.some((r) => r.id === "design-frontend-page-skeleton"),
    false,
  );
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

test("safety: professional record with an unmapped id returns null", () => {
  const r = baseRecord({
    id: "write-release-notes",
    slug: "write-release-notes",
    title: "Release notes",
    safetyClass: "professional",
  });
  assert.equal(professionalSafetyNoticeFor(r), null);
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

test("live catalog: every returned record has safetyClass and copyable prompt body", async () => {
  const catalog = await loadCanonicalCatalog();
  const out = selectPromptKitsPilotV1(catalog);
  for (const rec of out) {
    assert.equal(typeof rec.prompt, "string");
    assert.ok(rec.prompt.length > 0, `empty prompt for ${rec.id}`);
    assert.equal(rec.reviewStatus, "approved");
    assert.equal(rec.commercialUseStatus, "cleared");
    assert.equal(rec.publicationEligibility, "prompt-kits");
    assert.ok(
      ["general", "professional", "sensitive"].includes(rec.safetyClass),
      `unexpected safetyClass for ${rec.id}: ${rec.safetyClass}`,
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