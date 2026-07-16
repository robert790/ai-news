#!/usr/bin/env node
/**
 * Validator for the canonical OpenRadar prompt-content pilot.
 *
 * Architecture
 * ------------
 * Uses the project's installed TypeScript compiler (typescript devDependency)
 * to type-check the canonical index, then evaluates each batch file in a
 * CommonJS context to read its exported `promptRecords` array. This replaces
 * the prior regex-strip + eval path: the compiler enforces `import type`
 * and the discriminated union shape; the validator enforces the editorial
 * rules.
 *
 * Rule set
 * --------
 * - Required top-level fields present and well-typed.
 * - Nested inputs: name is lowercase snake_case; label, description, name
 *   are non-empty; example is string when present.
 * - Nested source references: kind in the enum; label non-empty; url is a
 *   valid http/https URL when present.
 * - id and slug are lowercase kebab-case.
 * - slug === id (v1 rule).
 * - IDs unique across all loaded batch files.
 * - Slugs unique across all loaded batch files.
 * - Input names unique within a record.
 * - Every declared input name appears as a {name} placeholder in the
 *   prompt body.
 * - Every {name} placeholder in the prompt body has a declared input.
 * - Repeated placeholders are allowed.
 * - collectionIds are all members of the registered collection registry.
 * - source-reference count rule per sourceType:
 *     - openradar-original: zero references, or exactly one
 *       'internal-concept' reference.
 *     - openradar-rewrite: at least one reference.
 *     - external-reference: at least one reference.
 * - Review metadata matches the discriminated union:
 *     - 'draft': reviewer === null, lastReviewedAt === null.
 *     - 'editor-reviewed' | 'approved' | 'rejected':
 *         reviewer is a non-empty string; lastReviewedAt is a valid
 *         ISO-8601 string.
 * - commercialUseStatus is one of 'pending' | 'cleared' | 'restricted'.
 * - safetyClass is one of 'general' | 'professional' | 'sensitive'.
 * - contentVersion is a positive integer.
 * - For pilot-batch-1.ts only, the ID set is exactly the canonical five.
 * - Prompt bodies are unique across all loaded records.
 * - TODO, TBD, and 'lorem ipsum' placeholders are forbidden in prompt
 *   bodies.
 * - Em dashes are forbidden recursively in: title, audience, useCase,
 *   input label/description/example, prompt, expectedOutput, note
 *   title/body, anti-pattern title/body, source-reference label and note.
 * - Hard-fail on unambiguous vendor, model, or product phrases in prompt
 *   bodies. Ordinary words such as 'cursor', 'linear', or 'notion' are
 *   NOT hard-failed. This guard does NOT prove neutrality or originality.
 *
 * Usage
 * -----
 *   node scripts/validate-prompt-content.mjs
 *
 * Exits 0 on success, 1 on any rule failure.
 */

import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve, basename } from "node:path";
import { createRequire } from "node:module";

import ts from "typescript";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "..", "..");
const WEB_ROOT = resolve(REPO_ROOT, "web");
const PROMPTS_DIR = resolve(WEB_ROOT, "src", "content", "prompts");
const INDEX_PATH = resolve(PROMPTS_DIR, "index.ts");
const COLLECTIONS_PATH = resolve(PROMPTS_DIR, "collections.ts");

// ---------- expected batch 1 set -------------------------------------------

const BATCH_1_IDS = new Set([
  "code-pr-description",
  "code-review-staff",
  "write-customer-notification",
  "operate-incident-first-15-minutes",
  "design-frontend-page-skeleton",
]);

// ---------- enums ---------------------------------------------------------

const ALLOWED_CATEGORIES = new Set([
  "code",
  "write",
  "research",
  "decide",
  "operate",
  "design",
  "agent",
]);

const ALLOWED_DIFFICULTIES = new Set([
  "beginner",
  "intermediate",
  "advanced",
]);

const ALLOWED_REVIEW_STATUSES = new Set([
  "draft",
  "editor-reviewed",
  "approved",
  "rejected",
]);

const ALLOWED_SOURCE_TYPES = new Set([
  "openradar-original",
  "openradar-rewrite",
  "external-reference",
]);

const ALLOWED_SAFETY_CLASSES = new Set(["general", "professional", "sensitive"]);

const ALLOWED_COMMERCIAL_USE_STATUSES = new Set([
  "pending",
  "cleared",
  "restricted",
]);

const ALLOWED_SOURCE_REFERENCE_KINDS = new Set([
  "internal-concept",
  "public-framework",
  "standard",
  "paper",
  "external-reference",
]);

// ---------- vendor / model / product phrases hard-failed in prompt bodies -

// Hard-fail only unambiguous vendor, model, or product phrases. Ordinary
// English words like 'cursor' or 'linear' are not in this list on
// purpose. This guard does NOT prove neutrality or originality.
const FORBIDDEN_BODY_PHRASES = [
  "chatgpt",
  "gpt-4",
  "gpt-3",
  "claude opus",
  "claude sonnet",
  "claude haiku",
  "gemini pro",
  "gemini ultra",
  "github copilot",
  "hugging face",
  "huggingface",
  "openai api",
  "anthropic api",
];

// ---------- rec ----------------------------------------------------------

const errors = [];

function fail(msg) {
  errors.push(msg);
}

// ---------- pattern helpers ----------------------------------------------

const ID_SLUG_RE = /^[a-z][a-z0-9]*(-[a-z0-9]+)*$/;
const SNAKE_CASE_RE = /^[a-z][a-z0-9_]*$/;
const HTTP_URL_RE = /^https?:\/\/[^\s/$.?#].[^\s]*$/i;
const PLACEHOLDER_RE = /\{([a-z][a-z0-9_]*)\}/g;
const EM_DASH_RE = /[\u2014\u2013]/; // em dash and en dash (defensive)

// ---------- collection registry ------------------------------------------

let COLLECTION_ID_SET = new Set();

function loadCollectionRegistry() {
  // Read collections.ts and extract the COLLECTION_IDS array literal
  // using the TS compiler. The values may be string literals or
  // identifier references to sibling `export const X = "..."`
  // declarations. Build a map of identifier -> string value, then
  // resolve COLLECTION_IDS through it.
  const src = readFileSync(COLLECTIONS_PATH, "utf8");
  const sf = ts.createSourceFile(
    COLLECTIONS_PATH,
    src,
    ts.ScriptTarget.ES2022,
    true,
    ts.ScriptKind.TS,
  );

  const constMap = new Map();
  for (const stmt of sf.statements) {
    if (
      ts.isVariableStatement(stmt) &&
      stmt.declarationList.declarations.length === 1
    ) {
      const decl = stmt.declarationList.declarations[0];
      if (
        ts.isIdentifier(decl.name) &&
        decl.initializer &&
        ts.isStringLiteralLike(decl.initializer)
      ) {
        constMap.set(decl.name.text, decl.initializer.text);
      }
    }
  }

  const out = [];
  for (const stmt of sf.statements) {
    if (
      ts.isVariableStatement(stmt) &&
      stmt.declarationList.declarations.length === 1
    ) {
      const decl = stmt.declarationList.declarations[0];
      if (
        ts.isIdentifier(decl.name) &&
        decl.name.text === "COLLECTION_IDS" &&
        decl.initializer
      ) {
        let init = decl.initializer;
        if (ts.isAsExpression(init)) init = init.expression;
        if (ts.isArrayLiteralExpression(init)) {
          for (const el of init.elements) {
            if (ts.isStringLiteralLike(el)) {
              out.push(el.text);
            } else if (ts.isIdentifier(el) && constMap.has(el.text)) {
              out.push(constMap.get(el.text));
            }
          }
        }
      }
    }
  }

  if (out.length === 0) {
    fail(
      `Could not load collection registry from ${COLLECTIONS_PATH}: no COLLECTION_IDS literal found.`,
    );
  }
  COLLECTION_ID_SET = new Set(out);
  return out;
}

// ---------- ts compiler loader -------------------------------------------

/**
 * Type-check the canonical index using the project's installed
 * TypeScript compiler. Surface every TS diagnostic as a hard failure.
 */
function typeCheckIndex() {
  const program = ts.createProgram([INDEX_PATH], {
    noEmit: true,
    strict: true,
    module: ts.ModuleKind.ESNext,
    moduleResolution: ts.ModuleResolutionKind.Bundler,
    target: ts.ScriptTarget.ES2022,
    skipLibCheck: true,
    jsx: ts.JsxEmit.Preserve,
    esModuleInterop: true,
    allowSyntheticDefaultImports: true,
    types: [],
  });
  const diags = ts.getPreEmitDiagnostics(program);
  for (const d of diags) {
    if (!d.file || !d.start) {
      fail(`TypeScript: ${ts.flattenDiagnosticMessageText(d.messageText, "\n")}`);
      continue;
    }
    const { line, character } = d.file.getLineAndCharacterOfPosition(
      d.start,
    );
    const file = d.file.fileName.replace(WEB_ROOT + "/", "");
    fail(
      `${file}:${line + 1}:${character + 1} ${ts.flattenDiagnosticMessageText(
        d.messageText,
        "\n",
      )}`,
    );
  }
}

// ---------- batch file loading -------------------------------------------

function findBatchFiles() {
  const out = [];
  for (const name of readdirSync(PROMPTS_DIR)) {
    if (!name.startsWith("pilot-batch-") || !name.endsWith(".ts")) continue;
    if (name === "pilot-batch-fixtures.test.ts") continue;
    out.push(resolve(PROMPTS_DIR, name));
  }
  return out.sort();
}

/**
 * Transpile a single TS batch file with the installed TypeScript
 * compiler, then load the resulting CommonJS via the local Node
 * module loader so the exported `promptRecords` array is available.
 *
 * This replaces the prior regex-strip + global-eval path.
 */
function loadBatchRecords(absPath) {
  const src = readFileSync(absPath, "utf8");
  const { outputText } = ts.transpileModule(src, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
      esModuleInterop: true,
      strict: false,
      skipLibCheck: true,
    },
    fileName: absPath,
  });
  // The transpiled module needs to resolve "./types" and "./collections"
  // imports. Strip the TS extensions from those require()s and let
  // Node resolve them via the regular file system.
  const patched = outputText
    .replace(/require\("\.\/(types|collections)"\)/g, (_, m) =>
      `require(${JSON.stringify(resolve(PROMPTS_DIR, `${m}.ts`))})`,
    )
    .replace(
      /require\("\.\.\/\.\.\/\.\.\/node_modules\/typescript"\)/g,
      () => `require(${JSON.stringify(resolve(WEB_ROOT, "node_modules", "typescript"))})`,
    );
  const m = { exports: {} };
  const fn = new Function("require", "module", "exports", "__filename", "__dirname", patched);
  const localRequire = createRequire(import.meta.url);
  fn(localRequire, m, m.exports, absPath, dirname(absPath));
  if (!m.exports || !Array.isArray(m.exports.promptRecords)) {
    throw new Error(
      `${absPath}: did not export a 'promptRecords' array after transpile`,
    );
  }
  return { records: m.exports.promptRecords, sourcePath: absPath };
}

// ---------- per-record checks --------------------------------------------

function checkRecordShape(rec, where) {
  const requiredStrings = [
    "id",
    "slug",
    "title",
    "audience",
    "useCase",
    "prompt",
    "expectedOutput",
    "authorship",
  ];
  for (const key of requiredStrings) {
    if (typeof rec[key] !== "string" || rec[key].trim().length === 0) {
      fail(`${where}: field '${key}' must be a non-empty string`);
    }
  }

  const requiredArrays = [
    "inputs",
    "notes",
    "antiPatterns",
    "collectionIds",
  ];
  for (const key of requiredArrays) {
    if (!Array.isArray(rec[key]) || rec[key].length === 0) {
      fail(`${where}: field '${key}' must be a non-empty array`);
    }
  }
  if (!Array.isArray(rec.sourceReferences)) {
    fail(`${where}: field 'sourceReferences' must be an array`);
  }

  // id and slug format
  if (typeof rec.id === "string") {
    if (!ID_SLUG_RE.test(rec.id)) {
      fail(`${where}: id '${rec.id}' is not lowercase kebab-case`);
    }
  }
  if (typeof rec.slug === "string") {
    if (!ID_SLUG_RE.test(rec.slug)) {
      fail(`${where}: slug '${rec.slug}' is not lowercase kebab-case`);
    }
    if (typeof rec.id === "string" && rec.slug !== rec.id) {
      fail(`${where}: slug '${rec.slug}' must equal id '${rec.id}' in v1`);
    }
  }

  // category
  if (!ALLOWED_CATEGORIES.has(rec.category)) {
    fail(
      `${where}: category '${rec.category}' is not in ${[...ALLOWED_CATEGORIES].join(", ")}`,
    );
  }

  // difficulty
  if (!ALLOWED_DIFFICULTIES.has(rec.difficulty)) {
    fail(
      `${where}: difficulty '${rec.difficulty}' is not in ${[...ALLOWED_DIFFICULTIES].join(", ")}`,
    );
  }

  // review metadata union
  if (!ALLOWED_REVIEW_STATUSES.has(rec.reviewStatus)) {
    fail(
      `${where}: reviewStatus '${rec.reviewStatus}' is not in ${[...ALLOWED_REVIEW_STATUSES].join(", ")}`,
    );
  }
  if (rec.reviewStatus === "draft") {
    if (rec.reviewer !== null) {
      fail(`${where}: reviewer must be null when reviewStatus is 'draft'`);
    }
    if (rec.lastReviewedAt !== null) {
      fail(
        `${where}: lastReviewedAt must be null when reviewStatus is 'draft'`,
      );
    }
  } else {
    // editor-reviewed | approved | rejected
    if (typeof rec.reviewer !== "string" || rec.reviewer.trim().length === 0) {
      fail(
        `${where}: reviewer must be a non-empty string when reviewStatus is '${rec.reviewStatus}'`,
      );
    }
    if (
      typeof rec.lastReviewedAt !== "string" ||
      !isValidIso8601(rec.lastReviewedAt)
    ) {
      fail(
        `${where}: lastReviewedAt must be a valid ISO-8601 string when reviewStatus is '${rec.reviewStatus}' (got ${JSON.stringify(rec.lastReviewedAt)})`,
      );
    }
  }

  // commercialUseStatus
  if (!ALLOWED_COMMERCIAL_USE_STATUSES.has(rec.commercialUseStatus)) {
    fail(
      `${where}: commercialUseStatus '${rec.commercialUseStatus}' is not in ${[...ALLOWED_COMMERCIAL_USE_STATUSES].join(", ")}`,
    );
  }

  // safetyClass
  if (!ALLOWED_SAFETY_CLASSES.has(rec.safetyClass)) {
    fail(
      `${where}: safetyClass '${rec.safetyClass}' is not in ${[...ALLOWED_SAFETY_CLASSES].join(", ")}`,
    );
  }

  // contentVersion
  if (
    !Number.isInteger(rec.contentVersion) ||
    rec.contentVersion < 1
  ) {
    fail(`${where}: contentVersion must be a positive integer`);
  }

  // sourceType
  if (!ALLOWED_SOURCE_TYPES.has(rec.sourceType)) {
    fail(
      `${where}: sourceType '${rec.sourceType}' is not in ${[...ALLOWED_SOURCE_TYPES].join(", ")}`,
    );
  }

  // collectionIds against registry
  if (Array.isArray(rec.collectionIds)) {
    for (const cid of rec.collectionIds) {
      if (!COLLECTION_ID_SET.has(cid)) {
        fail(`${where}: collectionId '${cid}' is not in the registered collection registry`);
      }
    }
  }

  // sourceReferences: per-record rules
  if (Array.isArray(rec.sourceReferences)) {
    if (
      rec.sourceType === "openradar-original" &&
      rec.sourceReferences.length > 1
    ) {
      fail(
        `${where}: sourceReferences must be 0 or 1 for openradar-original (got ${rec.sourceReferences.length})`,
      );
    }
    if (
      rec.sourceType === "openradar-rewrite" &&
      rec.sourceReferences.length < 1
    ) {
      fail(
        `${where}: sourceReferences must include at least one reference for openradar-rewrite`,
      );
    }
    if (
      rec.sourceType === "external-reference" &&
      rec.sourceReferences.length < 1
    ) {
      fail(
        `${where}: sourceReferences must include at least one reference for external-reference`,
      );
    }
    if (
      rec.sourceType === "openradar-original" &&
      rec.sourceReferences.length === 1 &&
      rec.sourceReferences[0].kind !== "internal-concept"
    ) {
      fail(
        `${where}: a single sourceReference for openradar-original must have kind 'internal-concept' (got '${rec.sourceReferences[0].kind}')`,
      );
    }
    rec.sourceReferences.forEach((ref, ridx) => {
      const rw = `${where} sourceReferences[${ridx}]`;
      if (typeof ref !== "object" || ref === null) {
        fail(`${rw}: must be an object`);
        return;
      }
      if (!ALLOWED_SOURCE_REFERENCE_KINDS.has(ref.kind)) {
        fail(
          `${rw}: kind '${ref.kind}' is not in ${[...ALLOWED_SOURCE_REFERENCE_KINDS].join(", ")}`,
        );
      }
      if (typeof ref.label !== "string" || ref.label.trim().length === 0) {
        fail(`${rw}: label must be a non-empty string`);
      }
      if (ref.label && EM_DASH_RE.test(ref.label)) {
        fail(`${rw}: label contains an em or en dash`);
      }
      if (ref.note && EM_DASH_RE.test(ref.note)) {
        fail(`${rw}: note contains an em or en dash`);
      }
      if (ref.url !== undefined) {
        if (typeof ref.url !== "string" || !HTTP_URL_RE.test(ref.url)) {
          fail(`${rw}: url must be a valid http/https URL when present`);
        }
      }
    });
  }

  // inputs structure
  if (Array.isArray(rec.inputs)) {
    const seenNames = new Map();
    const declaredNames = new Set();
    rec.inputs.forEach((input, iidx) => {
      const w = `${where} inputs[${iidx}]`;
      if (typeof input !== "object" || input === null) {
        fail(`${w}: must be an object`);
        return;
      }
      if (typeof input.name !== "string" || !SNAKE_CASE_RE.test(input.name)) {
        fail(`${w}: name must be lowercase snake_case identifier`);
      }
      if (typeof input.label !== "string" || input.label.trim().length === 0) {
        fail(`${w}: label must be a non-empty string`);
      }
      if (
        typeof input.description !== "string" ||
        input.description.trim().length === 0
      ) {
        fail(`${w}: description must be a non-empty string`);
      }
      if (input.example !== undefined && typeof input.example !== "string") {
        fail(`${w}: example must be a string when present`);
      }
      if (typeof input.name === "string" && input.name.length > 0) {
        if (seenNames.has(input.name)) {
          fail(
            `${w}: duplicate input name '${input.name}' (also at inputs[${seenNames.get(input.name)}])`,
          );
        } else {
          seenNames.set(input.name, iidx);
          declaredNames.add(input.name);
        }
      }
    });

    // placeholder / declared-input contract
    if (typeof rec.prompt === "string") {
      const used = new Set();
      let m;
      const re = new RegExp(PLACEHOLDER_RE.source, "g");
      while ((m = re.exec(rec.prompt)) !== null) {
        used.add(m[1]);
      }
      for (const usedName of used) {
        if (!declaredNames.has(usedName)) {
          fail(
            `${where}: prompt placeholder '{${usedName}}' has no matching declared input`,
          );
        }
      }
      for (const declared of declaredNames) {
        if (!used.has(declared)) {
          fail(
            `${where}: declared input '${declared}' does not appear as a {${declared}} placeholder in the prompt body`,
          );
        }
      }
    }
  }

  // recursive em-dash ban
  const dashFields = [
    ["title", rec.title],
    ["audience", rec.audience],
    ["useCase", rec.useCase],
    ["prompt", rec.prompt],
    ["expectedOutput", rec.expectedOutput],
  ];
  for (const [name, val] of dashFields) {
    if (typeof val === "string" && EM_DASH_RE.test(val)) {
      fail(`${where}: field '${name}' contains an em or en dash`);
    }
  }
  if (Array.isArray(rec.inputs)) {
    rec.inputs.forEach((input, iidx) => {
      for (const f of ["label", "description", "example"]) {
        const v = input[f];
        if (typeof v === "string" && EM_DASH_RE.test(v)) {
          fail(
            `${where} inputs[${iidx}].${f}: contains an em or en dash`,
          );
        }
      }
    });
  }
  if (Array.isArray(rec.notes)) {
    rec.notes.forEach((n, nidx) => {
      for (const f of ["title", "body"]) {
        const v = n[f];
        if (typeof v === "string" && EM_DASH_RE.test(v)) {
          fail(
            `${where} notes[${nidx}].${f}: contains an em or en dash`,
          );
        }
      }
    });
  }
  if (Array.isArray(rec.antiPatterns)) {
    rec.antiPatterns.forEach((n, nidx) => {
      for (const f of ["title", "body"]) {
        const v = n[f];
        if (typeof v === "string" && EM_DASH_RE.test(v)) {
          fail(
            `${where} antiPatterns[${nidx}].${f}: contains an em or en dash`,
          );
        }
      }
    });
  }

  // prompt body content rules
  if (typeof rec.prompt === "string") {
    if (/\bTODO\b/i.test(rec.prompt)) {
      fail(`${where}: prompt body contains 'TODO'`);
    }
    if (/\bTBD\b/i.test(rec.prompt)) {
      fail(`${where}: prompt body contains 'TBD'`);
    }
    if (/lorem ipsum/i.test(rec.prompt)) {
      fail(`${where}: prompt body contains 'lorem ipsum'`);
    }
    const lower = rec.prompt.toLowerCase();
    for (const phrase of FORBIDDEN_BODY_PHRASES) {
      if (lower.includes(phrase)) {
        fail(
          `${where}: prompt body contains forbidden vendor/model/product phrase '${phrase}'`,
        );
      }
    }
  }
}

// ---------- ISO-8601 check -----------------------------------------------

function isValidIso8601(s) {
  if (typeof s !== "string" || s.length === 0) return false;
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return false;
  // ISO-8601 requires a T separator or a date-only form; the parser is
  // permissive but the spec wants a real timestamp. Accept date-only too.
  if (!/^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?$/.test(s)) {
    return false;
  }
  return true;
}

// ---------- main ---------------------------------------------------------

function main() {
  loadCollectionRegistry();
  typeCheckIndex();

  const batchFiles = findBatchFiles();
  if (batchFiles.length === 0) {
    fail(`No batch files (pilot-batch-*.ts) found under ${PROMPTS_DIR}`);
    return printAndExit();
  }

  const allRecords = [];
  for (const file of batchFiles) {
    let loaded;
    try {
      loaded = loadBatchRecords(file);
    } catch (err) {
      fail(`Failed to load ${file}: ${err.message}`);
      continue;
    }
    const { records, sourcePath } = loaded;
    const fileTag = basename(sourcePath);

    // unique IDs across all batches
    const ids = records.map((r) => r.id);
    const dupIds = ids.filter((v, i) => ids.indexOf(v) !== i);
    if (dupIds.length > 0) {
      fail(
        `${fileTag}: duplicate ids: ${[...new Set(dupIds)].join(", ")}`,
      );
    }

    // unique slugs across all batches
    const slugs = records.map((r) => r.slug);
    const dupSlugs = slugs.filter((v, i) => slugs.indexOf(v) !== i);
    if (dupSlugs.length > 0) {
      fail(
        `${fileTag}: duplicate slugs: ${[...new Set(dupSlugs)].join(", ")}`,
      );
    }

    // batch-1 specific assertion
    if (fileTag === "pilot-batch-1.ts") {
      const recordSet = new Set(ids);
      const missing = [...BATCH_1_IDS].filter((id) => !recordSet.has(id));
      const extra = ids.filter((id) => !BATCH_1_IDS.has(id));
      if (missing.length > 0) {
        fail(
          `pilot-batch-1.ts: missing expected IDs: ${missing.join(", ")}`,
        );
      }
      if (extra.length > 0) {
        fail(
          `pilot-batch-1.ts: unexpected IDs present: ${extra.join(", ")}`,
        );
      }
      if (records.length !== BATCH_1_IDS.size) {
        fail(
          `pilot-batch-1.ts: expected ${BATCH_1_IDS.size} records, found ${records.length}`,
        );
      }
    }

    // duplicate prompt bodies across all records
    const bodyHashes = new Map();
    records.forEach((rec, i) => {
      const key = (rec.prompt || "").replace(/\s+/g, " ").trim();
      if (bodyHashes.has(key)) {
        fail(
          `Duplicate prompt body between ${bodyHashes.get(key)} and ${rec.id}`,
        );
      } else {
        bodyHashes.set(key, rec.id);
      }
    });

    // per-record shape
    records.forEach((rec, i) => {
      checkRecordShape(rec, `${fileTag} record #${i + 1} (id=${rec.id ?? "<missing>"})`);
    });

    allRecords.push(...records);
  }

  // cross-batch id and slug uniqueness
  const globalIds = allRecords.map((r) => r.id);
  const dupGlobalIds = globalIds.filter(
    (v, i) => globalIds.indexOf(v) !== i,
  );
  if (dupGlobalIds.length > 0) {
    fail(
      `Duplicate ids across batch files: ${[...new Set(dupGlobalIds)].join(", ")}`,
    );
  }
  const globalSlugs = allRecords.map((r) => r.slug);
  const dupGlobalSlugs = globalSlugs.filter(
    (v, i) => globalSlugs.indexOf(v) !== i,
  );
  if (dupGlobalSlugs.length > 0) {
    fail(
      `Duplicate slugs across batch files: ${[...new Set(dupGlobalSlugs)].join(", ")}`,
    );
  }

  printAndExit(allRecords.length);
}

function printAndExit(recordCount = 0) {
  if (errors.length === 0) {
    console.log(`OK: ${recordCount} canonical prompt record(s) validated.`);
    process.exit(0);
  }
  console.log(`Validation failed (${errors.length} error${errors.length === 1 ? "" : "s"}):`);
  for (const e of errors) console.log("  - " + e);
  process.exit(1);
}

main();