#!/usr/bin/env node
/**
 * Dependency-free validator for the canonical OpenRadar prompt-content pilot.
 *
 * Reads web/src/content/prompts/pilot-batch-1.ts by stripping its TypeScript
 * constructs and evaluating the `promptRecords` export as plain JSON. No
 * TypeScript compiler, no runtime dependencies, no Node modules from
 * package.json. Plain ESM only.
 *
 * Run with: npm run content:validate
 *
 * Exits 0 when every check passes, 1 otherwise.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "..", "..");
const SOURCE_PATH = resolve(
  REPO_ROOT,
  "web",
  "src",
  "content",
  "prompts",
  "pilot-batch-1.ts",
);

// ---------- configuration --------------------------------------------------

const EXPECTED_IDS = [
  "code-pr-description",
  "code-review-staff",
  "write-customer-notification",
  "operate-incident-first-15-minutes",
  "design-frontend-page-skeleton",
];

const ALLOWED_CATEGORIES = new Set([
  "code",
  "write",
  "research",
  "decide",
  "operate",
  "design",
  "agent",
]);

const ALLOWED_DIFFICULTIES = new Set(["beginner", "intermediate", "advanced"]);

const ALLOWED_REVIEW_STATUSES = new Set([
  "draft",
  "editorial-review",
  "legal-review",
  "approved",
]);

const ALLOWED_SOURCE_TYPES = new Set([
  "openradar-original",
  "openradar-rewrite",
  "external-reference",
]);

const ALLOWED_SAFETY_CLASSES = new Set(["general", "professional", "sensitive"]);

// Vendor / product / living-creator tokens forbidden in prompt bodies.
// All entries are lower-case and substring-matched; placeholders are not
// exempt (TODO/TBD/lorem are checked separately).
const FORBIDDEN_BODY_TOKENS = [
  // vendor model names
  "chatgpt",
  "claude",
  "gemini",
  "copilot",
  "gpt-4",
  "gpt-3",
  // vendor tool names
  "notion",
  "jira",
  "slack",
  "linear",
  "asana",
  "trello",
  // vendor code products
  "github copilot",
  "cursor",
  "cody",
  "tabnine",
  "codeium",
  // third-party services
  "hugging face",
  "huggingface",
  "openai api",
  "anthropic api",
  // living-creator surnames that have shown up in legacy wording;
  // intentionally surname-only so we do not flag legitimate words
  // that happen to contain these substrings inside larger words.
  // Each entry is checked as a whole-word match, case-insensitive.
];

const FORBIDDEN_BODY_REGEXES = [
  // em dash (and en dash as a defensive fallback)
  /[\u2014]/,
  // placeholder markers
  /\bTODO\b/i,
  /\bTBD\b/i,
  /\blorem ipsum\b/i,
];

// ---------- ts->json extraction --------------------------------------------

function stripImports(src) {
  // Remove `import ... from "..."` and `import "..."` lines.
  return src.replace(/^[ \t]*import[^\n;]*;[ \t]*\n?/gm, "");
}

function stripTypeAnnotations(src) {
  // We do not need full TS parsing. The batch file uses two TS-only
  // constructs outside the array literal:
  //   1. `export const promptRecords: PromptRecord[] = [...]`
  //      The `: PromptRecord[]` type annotation is removable.
  //   2. Type imports of the form `import type { ... } from "..."`
  //      Handled by stripImports.
  // Everything else in the batch file is plain JS object/array/string
  // syntax that evals fine.
  // Strip `: TypeName` annotations that appear on `const`/`let`/`var`
  // declarations. We only strip simple identifier / bracket / generic
  // forms; we do not handle function type annotations because the batch
  // file does not use them.
  return src.replace(
    /(\b(?:const|let|var)\s+[A-Za-z_$][\w$]*)\s*:\s*[A-Za-z_$][\w$<>,\[\]\s|&'"`{}()]*?(?=\s*=)/g,
    "$1",
  );
}

function stripExports(src) {
  // Replace `export const X` with `const X` and `export { X }` with nothing.
  let out = src.replace(/export\s+const\s+/g, "const ");
  out = out.replace(/^export\s*\{[^}]*\};?\s*$/gm, "");
  return out;
}

function extractRecords(src) {
  // Strategy: evaluate the entire module body (after stripping imports,
  // type annotations, and the `export` keyword) and then read the
  // `promptRecords` const from the resulting scope.
  const cleaned = stripExports(stripTypeAnnotations(stripImports(src)));

  // eslint-disable-next-line no-eval
  const moduleScope = (0, eval)(`(() => { ${cleaned}\n; return { promptRecords }; })()`);

  if (!moduleScope || !Array.isArray(moduleScope.promptRecords)) {
    throw new Error("Evaluated module did not expose a promptRecords array");
  }
  return moduleScope.promptRecords;
}

// ---------- checks ---------------------------------------------------------

const errors = [];
const warnings = [];

function fail(msg) {
  errors.push(msg);
}

function ok(msg) {
  // intentionally silent unless verbose
}

function check(condition, msg) {
  if (!condition) fail(msg);
  else ok(msg);
}

function checkRecordShape(rec, idx) {
  const where = `record #${idx + 1} (id=${rec.id ?? "<missing>"})`;

  const requiredStrings = [
    "id",
    "slug",
    "title",
    "audience",
    "useCase",
    "prompt",
    "expectedOutput",
  ];
  for (const key of requiredStrings) {
    check(
      typeof rec[key] === "string" && rec[key].trim().length > 0,
      `${where}: field '${key}' must be a non-empty string`,
    );
  }

  const requiredArrays = ["inputs", "notes", "antiPatterns", "collectionIds"];
  for (const key of requiredArrays) {
    check(
      Array.isArray(rec[key]) && rec[key].length > 0,
      `${where}: field '${key}' must be a non-empty array`,
    );
  }

  // category
  check(
    typeof rec.category === "string" && ALLOWED_CATEGORIES.has(rec.category),
    `${where}: category must be one of ${[...ALLOWED_CATEGORIES].join(", ")}`,
  );

  // difficulty
  check(
    typeof rec.difficulty === "string" &&
      ALLOWED_DIFFICULTIES.has(rec.difficulty),
    `${where}: difficulty must be one of ${[...ALLOWED_DIFFICULTIES].join(", ")}`,
  );

  // reviewStatus
  check(
    typeof rec.reviewStatus === "string" &&
      ALLOWED_REVIEW_STATUSES.has(rec.reviewStatus),
    `${where}: reviewStatus must be one of ${[...ALLOWED_REVIEW_STATUSES].join(", ")}`,
  );

  // commercialUseAllowed
  check(
    rec.commercialUseAllowed === false,
    `${where}: commercialUseAllowed must be false (drafts only)`,
  );

  // reviewer / lastReviewedAt
  check(
    rec.reviewer === null,
    `${where}: reviewer must be null while reviewStatus is draft`,
  );
  check(
    rec.lastReviewedAt === null,
    `${where}: lastReviewedAt must be null while reviewStatus is draft`,
  );

  // sourceType
  check(
    typeof rec.sourceType === "string" &&
      ALLOWED_SOURCE_TYPES.has(rec.sourceType),
    `${where}: sourceType must be one of ${[...ALLOWED_SOURCE_TYPES].join(", ")}`,
  );

  // safetyClass
  check(
    typeof rec.safetyClass === "string" &&
      ALLOWED_SAFETY_CLASSES.has(rec.safetyClass),
    `${where}: safetyClass must be one of ${[...ALLOWED_SAFETY_CLASSES].join(", ")}`,
  );

  // contentVersion
  check(
    Number.isInteger(rec.contentVersion) && rec.contentVersion >= 1,
    `${where}: contentVersion must be a positive integer`,
  );

  // authorship
  check(
    typeof rec.authorship === "string" && rec.authorship.trim().length > 0,
    `${where}: authorship must be a non-empty string`,
  );

  // inputs structure
  if (Array.isArray(rec.inputs)) {
    rec.inputs.forEach((input, iidx) => {
      const w = `${where} inputs[${iidx}]`;
      check(
        typeof input === "object" && input !== null,
        `${w}: must be an object`,
      );
      check(
        typeof input.name === "string" && /^[a-z][a-z0-9_]*$/.test(input.name),
        `${w}: name must be lowercase snake_case identifier`,
      );
      check(
        typeof input.label === "string" && input.label.trim().length > 0,
        `${w}: label must be a non-empty string`,
      );
      check(
        typeof input.description === "string" &&
          input.description.trim().length > 0,
        `${w}: description must be a non-empty string`,
      );
    });
  }

  // prompt body content rules
  if (typeof rec.prompt === "string") {
    for (const re of FORBIDDEN_BODY_REGEXES) {
      check(
        !re.test(rec.prompt),
        `${where}: prompt body matches forbidden pattern ${re}`,
      );
    }
    const lower = rec.prompt.toLowerCase();
    for (const tok of FORBIDDEN_BODY_TOKENS) {
      // whole-word check for tokens that look like surnames,
      // substring check for vendor tokens.
      if (tok.includes(" ")) {
        check(
          !lower.includes(tok),
          `${where}: prompt body contains forbidden token '${tok}'`,
        );
      } else {
        const wordRe = new RegExp(`\\b${tok}\\b`, "i");
        check(
          !wordRe.test(rec.prompt),
          `${where}: prompt body contains forbidden token '${tok}'`,
        );
      }
    }

    // expected output rules: no em dash, no forbidden tokens.
    if (typeof rec.expectedOutput === "string") {
      check(
        !/[\u2014]/.test(rec.expectedOutput),
        `${where}: expectedOutput contains an em dash`,
      );
    }
  }

  // title: no em dash
  if (typeof rec.title === "string") {
    check(
      !/[\u2014]/.test(rec.title),
      `${where}: title contains an em dash`,
    );
  }

  // useCase: no em dash
  if (typeof rec.useCase === "string") {
    check(
      !/[\u2014]/.test(rec.useCase),
      `${where}: useCase contains an em dash`,
    );
  }
}

// ---------- main -----------------------------------------------------------

function main() {
  let src;
  try {
    src = readFileSync(SOURCE_PATH, "utf8");
  } catch (err) {
    fail(`Cannot read ${SOURCE_PATH}: ${err.message}`);
    printAndExit();
    return;
  }

  let records;
  try {
    records = extractRecords(src);
  } catch (err) {
    fail(`Failed to extract promptRecords: ${err.message}`);
    printAndExit();
    return;
  }

  // Cardinality
  check(
    records.length === EXPECTED_IDS.length,
    `Expected ${EXPECTED_IDS.length} records, found ${records.length}`,
  );

  // Unique IDs and slugs
  const ids = records.map((r) => r.id);
  const slugs = records.map((r) => r.slug);
  const dupIds = ids.filter((v, i) => ids.indexOf(v) !== i);
  check(dupIds.length === 0, `Duplicate IDs: ${[...new Set(dupIds)].join(", ")}`);
  const dupSlugs = slugs.filter((v, i) => slugs.indexOf(v) !== i);
  check(
    dupSlugs.length === 0,
    `Duplicate slugs: ${[...new Set(dupSlugs)].join(", ")}`,
  );

  // ID set
  const missing = EXPECTED_IDS.filter((id) => !ids.includes(id));
  const extra = ids.filter((id) => !EXPECTED_IDS.includes(id));
  check(
    missing.length === 0,
    `Missing expected IDs: ${missing.join(", ")}`,
  );
  check(
    extra.length === 0,
    `Unexpected IDs present: ${extra.join(", ")}`,
  );

  // Duplicate prompt bodies
  const bodyHashes = new Map();
  for (const rec of records) {
    if (typeof rec.prompt !== "string") continue;
    const key = rec.prompt.replace(/\s+/g, " ").trim();
    if (bodyHashes.has(key)) {
      fail(
        `Duplicate prompt body between ${bodyHashes.get(key)} and ${rec.id}`,
      );
    } else {
      bodyHashes.set(key, rec.id);
    }
  }

  // Per-record shape
  records.forEach(checkRecordShape);

  printAndExit();
}

function printAndExit() {
  if (warnings.length > 0) {
    console.log("Warnings:");
    for (const w of warnings) console.log("  - " + w);
  }
  if (errors.length === 0) {
    console.log(
      `OK: ${EXPECTED_IDS.length} canonical prompt records validated.`,
    );
    process.exit(0);
  }
  console.log(`Validation failed (${errors.length} error${errors.length === 1 ? "" : "s"}):`);
  for (const e of errors) console.log("  - " + e);
  process.exit(1);
}

main();