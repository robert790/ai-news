/**
 * Pure validation functions for the OpenRadar prompt-content pilot.
 *
 * These functions are environment-free: they take a record array (and
 * any extra inputs the caller wants to feed in), and return either
 * `{ errors: [] }` or `{ errors: [...], recordCount }`. No I/O, no
 * process spawning, no subprocess sandboxes. The negative-test suite
 * imports from here directly.
 *
 * The wrapper script `validate-prompt-content.mjs` is the one that
 * handles TypeScript compilation, temporary emit, and normal-import
 * loading. It feeds the loaded catalog to `validateCatalog` here.
 */

/**
 * The exact five-ID Batch 1 lock. A separate deterministic rule from
 * the rest of the contract. The complete catalog may include more
 * records in the future; this rule only checks that Batch 1 contains
 * exactly these five IDs and that none of them are missing.
 */
export const BATCH_1_LOCK_IDS = Object.freeze([
  "code-pr-description",
  "code-review-staff",
  "write-customer-notification",
  "operate-incident-first-15-minutes",
  "design-frontend-page-skeleton",
]);

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

const ALLOWED_SAFETY_CLASSES = new Set([
  "general",
  "professional",
  "sensitive",
]);

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

const ID_SLUG_RE = /^[a-z][a-z0-9]*(-[a-z0-9]+)*$/;
const SNAKE_CASE_RE = /^[a-z][a-z0-9_]*$/;
const HTTP_URL_RE = /^https?:\/\/[^\s/$.?#].[^\s]*$/i;
const PLACEHOLDER_RE_GLOBAL = /\{([a-z][a-z0-9_]*)\}/g;
const EM_DASH_RE = /[\u2014\u2013]/;

// Vendor / model / product phrases hard-failed in prompt bodies.
// Ordinary English words like 'cursor' or 'linear' are not on this
// list on purpose. This guard does NOT prove neutrality or originality.
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

export function isValidIso8601(s) {
  if (typeof s !== "string" || s.length === 0) return false;
  if (
    !/^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?$/.test(
      s,
    )
  ) {
    return false;
  }
  const d = new Date(s);
  return !Number.isNaN(d.getTime());
}

/**
 * Validate the Batch 1 lock against the separately-exported
 * pilotBatch1Records. The lock is a separate deterministic rule from
 * the rest of the contract and is NOT derived from the complete
 * promptRecords catalog.
 *
 * Rules:
 *  - pilotBatch1Records length equals the lock length.
 *  - its ID set exactly equals BATCH_1_LOCK_IDS.
 *  - no missing IDs.
 *  - no extra IDs.
 *  - no duplicate IDs.
 *
 * @param {unknown} pilotBatch1Records
 * @param {readonly string[]} [batch1LockIds]
 * @returns {{errors: string[]; recordCount: number}}
 */
export function validateBatch1Lock(pilotBatch1Records, batch1LockIds = BATCH_1_LOCK_IDS) {
  const errors = [];
  if (!Array.isArray(pilotBatch1Records)) {
    return {
      errors: ["pilotBatch1Records is not an array"],
      recordCount: 0,
    };
  }

  const recordCount = pilotBatch1Records.length;

  if (recordCount !== batch1LockIds.length) {
    errors.push(
      `Batch 1 lock: pilotBatch1Records has ${recordCount} record(s); expected exactly ${batch1LockIds.length}`,
    );
  }

  const seen = new Map();
  for (let i = 0; i < pilotBatch1Records.length; i++) {
    const rec = pilotBatch1Records[i];
    if (rec === null || typeof rec !== "object") {
      errors.push(`Batch 1 lock: record #${i + 1}: must be an object`);
      continue;
    }
    const id = rec.id;
    if (typeof id !== "string" || id.length === 0) {
      errors.push(`Batch 1 lock: record #${i + 1}: id must be a non-empty string`);
      continue;
    }
    if (seen.has(id)) {
      errors.push(
        `Batch 1 lock: duplicate id '${id}' at #${seen.get(id) + 1} and #${i + 1}`,
      );
    } else {
      seen.set(id, i);
    }
  }

  for (const id of batch1LockIds) {
    if (!seen.has(id)) {
      errors.push(`Batch 1 lock: missing expected ID '${id}'`);
    }
  }
  for (const id of seen.keys()) {
    if (!batch1LockIds.includes(id)) {
      errors.push(`Batch 1 lock: unexpected ID '${id}'`);
    }
  }

  return { errors, recordCount };
}

/**
 * Run the full validation suite against a catalog of records.
 *
 * @param {unknown} catalog -- the records to validate. Must be an array.
 * @param {object} [options]
 * @param {ReadonlySet<string>} [options.collectionIdSet] -- set of
 *   registered collection IDs. When omitted, validation skips the
 *   collection-id membership check.
 * @param {readonly string[]} [options.batch1LockIds] -- the five-ID
 *   Batch 1 lock. Defaults to BATCH_1_LOCK_IDS.
 * @returns {{errors: string[]; recordCount: number}}
 */
export function validateCatalog(catalog, options = {}) {
  const errors = [];
  const collectionIdSet = options.collectionIdSet;

  if (!Array.isArray(catalog)) {
    return { errors: ["catalog is not an array"], recordCount: 0 };
  }

  const recordCount = catalog.length;

  // Global cross-record checks.
  const seenIds = new Map();
  const seenSlugs = new Map();
  const bodyHashes = new Map();

  for (let i = 0; i < catalog.length; i++) {
    const rec = catalog[i];
    if (rec === null || typeof rec !== "object") {
      errors.push(
        `record #${i + 1}: must be an object (got ${rec === null ? "null" : typeof rec})`,
      );
      continue;
    }
    const where = `record #${i + 1} (id=${typeof rec.id === "string" ? rec.id : "<missing>"})`;

    checkRecordShape(rec, where, errors, { collectionIdSet });

    if (typeof rec.id === "string" && rec.id.length > 0) {
      if (seenIds.has(rec.id)) {
        errors.push(
          `Duplicate id '${rec.id}' (also at #${seenIds.get(rec.id) + 1})`,
        );
      } else {
        seenIds.set(rec.id, i);
      }
    }
    if (typeof rec.slug === "string" && rec.slug.length > 0) {
      if (seenSlugs.has(rec.slug)) {
        errors.push(
          `Duplicate slug '${rec.slug}' (also at #${seenSlugs.get(rec.slug) + 1})`,
        );
      } else {
        seenSlugs.set(rec.slug, i);
      }
    }

    if (typeof rec.prompt === "string") {
      const key = rec.prompt.replace(/\s+/g, " ").trim();
      if (bodyHashes.has(key)) {
        errors.push(
          `Duplicate prompt body between ${bodyHashes.get(key)} and ${rec.id}`,
        );
      } else {
        bodyHashes.set(key, rec.id ?? `#${i + 1}`);
      }
    }
  }

  // The Batch 1 lock is enforced separately against pilotBatch1Records
  // (see validateBatch1Lock). It is NOT derived from the complete
  // promptRecords catalog.

  return { errors, recordCount };
}

function checkRecordShape(rec, where, errors, options) {
  const collectionIdSet = options.collectionIdSet;

  // Required strings
  for (const key of [
    "id",
    "slug",
    "title",
    "audience",
    "useCase",
    "prompt",
    "expectedOutput",
    "authorship",
  ]) {
    if (typeof rec[key] !== "string" || rec[key].trim().length === 0) {
      errors.push(`${where}: field '${key}' must be a non-empty string`);
    }
  }

  // Required arrays (sourceReferences may be empty for openradar-original)
  for (const key of ["inputs", "notes", "antiPatterns", "collectionIds"]) {
    if (!Array.isArray(rec[key]) || rec[key].length === 0) {
      errors.push(`${where}: field '${key}' must be a non-empty array`);
    }
  }
  if (!Array.isArray(rec.sourceReferences)) {
    errors.push(`${where}: field 'sourceReferences' must be an array`);
  }

  // id and slug
  if (typeof rec.id === "string" && !ID_SLUG_RE.test(rec.id)) {
    errors.push(`${where}: id '${rec.id}' is not lowercase kebab-case`);
  }
  if (typeof rec.slug === "string") {
    if (!ID_SLUG_RE.test(rec.slug)) {
      errors.push(`${where}: slug '${rec.slug}' is not lowercase kebab-case`);
    }
    if (typeof rec.id === "string" && rec.slug !== rec.id) {
      errors.push(
        `${where}: slug '${rec.slug}' must equal id '${rec.id}' in v1`,
      );
    }
  }

  // category
  if (!ALLOWED_CATEGORIES.has(rec.category)) {
    errors.push(
      `${where}: category '${rec.category}' is not in ${[...ALLOWED_CATEGORIES].join(", ")}`,
    );
  }
  // difficulty
  if (!ALLOWED_DIFFICULTIES.has(rec.difficulty)) {
    errors.push(
      `${where}: difficulty '${rec.difficulty}' is not in ${[...ALLOWED_DIFFICULTIES].join(", ")}`,
    );
  }

  // review metadata union
  if (!ALLOWED_REVIEW_STATUSES.has(rec.reviewStatus)) {
    errors.push(
      `${where}: reviewStatus '${rec.reviewStatus}' is not in ${[...ALLOWED_REVIEW_STATUSES].join(", ")}`,
    );
  }
  if (rec.reviewStatus === "draft") {
    if (rec.reviewer !== null) {
      errors.push(
        `${where}: reviewer must be null when reviewStatus is 'draft'`,
      );
    }
    if (rec.lastReviewedAt !== null) {
      errors.push(
        `${where}: lastReviewedAt must be null when reviewStatus is 'draft'`,
      );
    }
  } else {
    if (typeof rec.reviewer !== "string" || rec.reviewer.trim().length === 0) {
      errors.push(
        `${where}: reviewer must be a non-empty string when reviewStatus is '${rec.reviewStatus}'`,
      );
    }
    if (
      typeof rec.lastReviewedAt !== "string" ||
      !isValidIso8601(rec.lastReviewedAt)
    ) {
      errors.push(
        `${where}: lastReviewedAt must be a valid ISO-8601 string when reviewStatus is '${rec.reviewStatus}' (got ${JSON.stringify(rec.lastReviewedAt)})`,
      );
    }
  }

  // commercialUseStatus
  if (!ALLOWED_COMMERCIAL_USE_STATUSES.has(rec.commercialUseStatus)) {
    errors.push(
      `${where}: commercialUseStatus '${rec.commercialUseStatus}' is not in ${[...ALLOWED_COMMERCIAL_USE_STATUSES].join(", ")}`,
    );
  }
  // safetyClass
  if (!ALLOWED_SAFETY_CLASSES.has(rec.safetyClass)) {
    errors.push(
      `${where}: safetyClass '${rec.safetyClass}' is not in ${[...ALLOWED_SAFETY_CLASSES].join(", ")}`,
    );
  }
  // contentVersion
  if (!Number.isInteger(rec.contentVersion) || rec.contentVersion < 1) {
    errors.push(`${where}: contentVersion must be a positive integer`);
  }

  // sourceType
  if (!ALLOWED_SOURCE_TYPES.has(rec.sourceType)) {
    errors.push(
      `${where}: sourceType '${rec.sourceType}' is not in ${[...ALLOWED_SOURCE_TYPES].join(", ")}`,
    );
  }

  // collectionIds against registry
  if (Array.isArray(rec.collectionIds)) {
    if (collectionIdSet !== undefined) {
      for (const cid of rec.collectionIds) {
        if (!collectionIdSet.has(cid)) {
          errors.push(
            `${where}: collectionId '${cid}' is not in the registered collection registry`,
          );
        }
      }
    }
  }

  // sourceReferences: per-record rules
  if (Array.isArray(rec.sourceReferences)) {
    if (
      rec.sourceType === "openradar-rewrite" &&
      rec.sourceReferences.length < 1
    ) {
      errors.push(
        `${where}: sourceReferences must include at least one reference for openradar-rewrite`,
      );
    }
    if (
      rec.sourceType === "external-reference" &&
      rec.sourceReferences.length < 1
    ) {
      errors.push(
        `${where}: sourceReferences must include at least one reference for external-reference`,
      );
    }
    rec.sourceReferences.forEach((ref, ridx) => {
      const rw = `${where} sourceReferences[${ridx}]`;
      if (ref === null || typeof ref !== "object") {
        errors.push(`${rw}: must be an object`);
        return;
      }
      if (!ALLOWED_SOURCE_REFERENCE_KINDS.has(ref.kind)) {
        errors.push(
          `${rw}: kind '${ref.kind}' is not in ${[...ALLOWED_SOURCE_REFERENCE_KINDS].join(", ")}`,
        );
      }
      if (typeof ref.label !== "string" || ref.label.trim().length === 0) {
        errors.push(`${rw}: label must be a non-empty string`);
      }
      if (typeof ref.label === "string" && EM_DASH_RE.test(ref.label)) {
        errors.push(`${rw}: label contains an em or en dash`);
      }
      if (ref.note !== undefined) {
        if (typeof ref.note !== "string" || ref.note.trim().length === 0) {
          errors.push(`${rw}: note must be a non-empty string when present`);
        } else if (EM_DASH_RE.test(ref.note)) {
          errors.push(`${rw}: note contains an em or en dash`);
        }
      }
      if (ref.url !== undefined) {
        if (typeof ref.url !== "string" || ref.url.trim().length === 0) {
          errors.push(`${rw}: url must be a non-empty string when present`);
        } else if (!HTTP_URL_RE.test(ref.url)) {
          errors.push(`${rw}: url must be a valid http/https URL when present`);
        }
      }
    });
  }

  // inputs
  if (Array.isArray(rec.inputs)) {
    const seenNames = new Map();
    const declaredNames = new Set();
    rec.inputs.forEach((input, iidx) => {
      const w = `${where} inputs[${iidx}]`;
      if (input === null || typeof input !== "object") {
        errors.push(`${w}: must be an object`);
        return;
      }
      if (typeof input.name !== "string" || !SNAKE_CASE_RE.test(input.name)) {
        errors.push(`${w}: name must be lowercase snake_case identifier`);
      }
      if (
        typeof input.label !== "string" ||
        input.label.trim().length === 0
      ) {
        errors.push(`${w}: label must be a non-empty string`);
      }
      if (
        typeof input.description !== "string" ||
        input.description.trim().length === 0
      ) {
        errors.push(`${w}: description must be a non-empty string`);
      }
      if (input.example !== undefined) {
        if (typeof input.example !== "string") {
          errors.push(`${w}: example must be a string when present`);
        } else if (input.example.trim().length === 0) {
          errors.push(`${w}: example must be a non-empty string when present`);
        }
      }
      if (typeof input.name === "string" && input.name.length > 0) {
        if (seenNames.has(input.name)) {
          errors.push(
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
      const re = new RegExp(PLACEHOLDER_RE_GLOBAL.source, "g");
      while ((m = re.exec(rec.prompt)) !== null) {
        used.add(m[1]);
      }
      for (const usedName of used) {
        if (!declaredNames.has(usedName)) {
          errors.push(
            `${where}: prompt placeholder '{${usedName}}' has no matching declared input`,
          );
        }
      }
      for (const declared of declaredNames) {
        if (!used.has(declared)) {
          errors.push(
            `${where}: declared input '${declared}' does not appear as a {${declared}} placeholder in the prompt body`,
          );
        }
      }
    }
  }

  // notes
  if (Array.isArray(rec.notes)) {
    rec.notes.forEach((n, nidx) => {
      if (n === null || typeof n !== "object") {
        errors.push(`${where} notes[${nidx}]: must be an object`);
        return;
      }
      if (typeof n.title !== "string" || n.title.trim().length === 0) {
        errors.push(`${where} notes[${nidx}]: title must be a non-empty string`);
      } else if (EM_DASH_RE.test(n.title)) {
        errors.push(`${where} notes[${nidx}].title: contains an em or en dash`);
      }
      if (typeof n.body !== "string" || n.body.trim().length === 0) {
        errors.push(`${where} notes[${nidx}]: body must be a non-empty string`);
      } else if (EM_DASH_RE.test(n.body)) {
        errors.push(`${where} notes[${nidx}].body: contains an em or en dash`);
      }
    });
  }

  // antiPatterns
  if (Array.isArray(rec.antiPatterns)) {
    rec.antiPatterns.forEach((n, nidx) => {
      if (n === null || typeof n !== "object") {
        errors.push(
          `${where} antiPatterns[${nidx}]: must be an object`,
        );
        return;
      }
      if (typeof n.title !== "string" || n.title.trim().length === 0) {
        errors.push(
          `${where} antiPatterns[${nidx}]: title must be a non-empty string`,
        );
      } else if (EM_DASH_RE.test(n.title)) {
        errors.push(
          `${where} antiPatterns[${nidx}].title: contains an em or en dash`,
        );
      }
      if (typeof n.body !== "string" || n.body.trim().length === 0) {
        errors.push(
          `${where} antiPatterns[${nidx}]: body must be a non-empty string`,
        );
      } else if (EM_DASH_RE.test(n.body)) {
        errors.push(
          `${where} antiPatterns[${nidx}].body: contains an em or en dash`,
        );
      }
    });
  }

  // recursive em-dash ban
  for (const [name, val] of [
    ["title", rec.title],
    ["audience", rec.audience],
    ["useCase", rec.useCase],
    ["prompt", rec.prompt],
    ["expectedOutput", rec.expectedOutput],
  ]) {
    if (typeof val === "string" && EM_DASH_RE.test(val)) {
      errors.push(`${where}: field '${name}' contains an em or en dash`);
    }
  }
  if (Array.isArray(rec.inputs)) {
    rec.inputs.forEach((input, iidx) => {
      for (const f of ["label", "description", "example"]) {
        const v = input[f];
        if (typeof v === "string" && v.length > 0 && EM_DASH_RE.test(v)) {
          errors.push(
            `${where} inputs[${iidx}].${f}: contains an em or en dash`,
          );
        }
      }
    });
  }

  // prompt body content rules
  if (typeof rec.prompt === "string") {
    if (/\bTODO\b/i.test(rec.prompt)) {
      errors.push(`${where}: prompt body contains 'TODO'`);
    }
    if (/\bTBD\b/i.test(rec.prompt)) {
      errors.push(`${where}: prompt body contains 'TBD'`);
    }
    if (/lorem ipsum/i.test(rec.prompt)) {
      errors.push(`${where}: prompt body contains 'lorem ipsum'`);
    }
    const lower = rec.prompt.toLowerCase();
    for (const phrase of FORBIDDEN_BODY_PHRASES) {
      if (lower.includes(phrase)) {
        errors.push(
          `${where}: prompt body contains forbidden vendor/model/product phrase '${phrase}'`,
        );
      }
    }
  }
}