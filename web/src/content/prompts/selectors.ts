/**
 * Prompt Pilot V1 selector — the only place the Web V2 /prompt-kits
 * route reads canonical prompt data.
 *
 * Architectural rules
 * -------------------
 * 1. The canonical catalog (`web/src/content/prompts/index.ts`) is the
 *    sole source of prompt records. There is no static prompt-text
 *    fallback or duplicated dataset inside the page route.
 *
 * 2. A record is eligible for the /prompt-kits surface only when ALL
 *    FIVE fields hold:
 *      - reviewStatus           === "approved"
 *      - commercialUseStatus    === "cleared"
 *      - publicationEligibility === "prompt-kits"
 *      - reviewer               is a non-empty string
 *      - lastReviewedAt         is a non-empty valid ISO-8601 timestamp
 *
 * 3. The set of IDs that may appear in the Web V2 /prompt-kits pilot
 *    is exactly the canonical Pilot V1 lock, in this order:
 *      1. code-pr-description
 *      2. code-review-staff
 *      3. write-customer-notification
 *      4. operate-incident-first-15-minutes
 *      5. design-frontend-page-skeleton
 *
 *    Other canonical records (including any future Batch 2) are
 *    explicitly excluded until they are owner-promoted and added to
 *    the lock.
 *
 * 4. EXACT-FIVE FAIL-CLOSED CONTRACT.
 *    `selectPromptKitsPilotV1` MUST return all five lock records in
 *    canonical order, or it MUST throw `PromptKitsPilotV1UnavailableError`.
 *    The selector never returns a partial Pilot V1 set.
 *
 *    It throws when:
 *      - promptRecords is not an array,
 *      - any required lock id is missing from the catalog,
 *      - any required lock id is duplicated,
 *      - any required lock record fails the five-field eligibility
 *        predicate (including: empty reviewer, missing reviewer,
 *        null lastReviewedAt, missing lastReviewedAt, invalid
 *        lastReviewedAt, or any non-promotion triple failure).
 *
 *    The error message may include the list of failing / missing
 *    / duplicated ids. The route surfaces a product-safe copy and
 *    does not render the diagnostic string to the public.
 *
 * 5. Draft, pending, restricted, rejected, or internal records are
 *    never surfaced through this selector.
 *
 * 6. The returned records are returned unchanged. No field is
 *    mutated; no placeholder is substituted; no metadata is
 *    prepended.
 */

import type { PromptRecord } from "./types";

/**
 * The canonical Pilot V1 lock. Frozen for v1 of the Web V2 pilot.
 * MUST stay in lock-step with `BATCH_1_LOCK_IDS` in
 * `web/scripts/validate-prompt-content.lib.mjs`.
 *
 * The order of these ids IS the canonical rendering order on the
 * page. Do not reorder without an owner-promoted canonical change.
 */
export const PILOT_V1_LOCK_IDS: ReadonlyArray<string> = Object.freeze([
  "code-pr-description",
  "code-review-staff",
  "write-customer-notification",
  "operate-incident-first-15-minutes",
  "design-frontend-page-skeleton",
]);

/**
 * The exact three professional-safety prompts that must show a
 * restrained human-review notice in the expanded detail region.
 *
 * Each key maps to the verbatim notice text required by the
 * Stage 7C.1 spec. Other professional-safety records would also need
 * an entry here; the map is keyed by id on purpose so the route
 * cannot silently apply the wrong notice.
 */
export const PROFESSIONAL_SAFETY_NOTICES: Readonly<Record<string, string>> =
  Object.freeze({
    "code-review-staff":
      "Human review is required before acting on consequential review findings.",
    "write-customer-notification":
      "Human review is required before customer delivery.",
    "operate-incident-first-15-minutes":
      "Operational recommendations remain proposals until approved by an authorized responder.",
  });

/**
 * Sentinel thrown by `selectPromptKitsPilotV1` when the canonical
 * catalog cannot satisfy the exact-five fail-closed contract.
 */
export class PromptKitsPilotV1UnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PromptKitsPilotV1UnavailableError";
  }
}

/**
 * Test whether a single record satisfies the five-field eligibility
 * predicate for the /prompt-kits surface.
 *
 * Fields required (all five must hold):
 *   - reviewStatus           === "approved"
 *   - commercialUseStatus    === "cleared"
 *   - publicationEligibility === "prompt-kits"
 *   - reviewer               is a non-empty string
 *   - lastReviewedAt         is a non-empty valid ISO-8601 timestamp
 *
 * Exported so the negative-test suite can pin the predicate.
 */
export function isPromptKitsEligible(rec: unknown): rec is PromptRecord {
  if (rec === null || typeof rec !== "object") return false;
  const r = rec as Record<string, unknown>;
  return (
    r.reviewStatus === "approved" &&
    r.commercialUseStatus === "cleared" &&
    r.publicationEligibility === "prompt-kits" &&
    typeof r.reviewer === "string" &&
    r.reviewer.trim().length > 0 &&
    typeof r.lastReviewedAt === "string" &&
    r.lastReviewedAt.length > 0 &&
    isValidIsoTimestamp(r.lastReviewedAt)
  );
}

/**
 * Test whether an id is part of the canonical Pilot V1 lock.
 */
export function isPilotV1LockId(id: unknown): id is string {
  return typeof id === "string" && PILOT_V1_LOCK_IDS.includes(id);
}

/**
 * Minimal ISO-8601 timestamp validator. Mirrors the canonical
 * validator's semantics for the lastReviewedAt field: accepts
 * YYYY-MM-DD and YYYY-MM-DDTHH:MM:SS[.fraction][Z|±HH:MM].
 */
function isValidIsoTimestamp(s: string): boolean {
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
 * Detail the reasons a single record fails the eligibility
 * predicate. Used by `selectPromptKitsPilotV1` to build a
 * developer-actionable diagnostic message; not surfaced to public
 * UI.
 */
function eligibilityFailures(rec: unknown): string[] {
  const fails: string[] = [];
  if (rec === null || typeof rec !== "object") {
    return ["not-an-object"];
  }
  const r = rec as Record<string, unknown>;
  const id =
    typeof r.id === "string" && r.id.length > 0 ? r.id : "<missing-id>";

  if (r.reviewStatus !== "approved") {
    fails.push(`${id}: reviewStatus is not 'approved'`);
  }
  if (r.commercialUseStatus !== "cleared") {
    fails.push(`${id}: commercialUseStatus is not 'cleared'`);
  }
  if (r.publicationEligibility !== "prompt-kits") {
    fails.push(`${id}: publicationEligibility is not 'prompt-kits'`);
  }
  if (typeof r.reviewer !== "string" || r.reviewer.trim().length === 0) {
    fails.push(`${id}: reviewer is missing or empty`);
  }
  if (typeof r.lastReviewedAt !== "string" || r.lastReviewedAt.length === 0) {
    fails.push(`${id}: lastReviewedAt is missing or empty`);
  } else if (!isValidIsoTimestamp(r.lastReviewedAt)) {
    fails.push(`${id}: lastReviewedAt is not a valid ISO-8601 timestamp`);
  }
  return fails;
}

/**
 * Select the Pilot V1 records for the /prompt-kits surface under the
 * EXACT-FIVE FAIL-CLOSED contract.
 *
 * Behavior:
 *  - Rejects non-array input by throwing.
 *  - Walks the input and identifies every record whose id is a
 *    lock id.
 *  - Detects duplicates among lock ids; throws on any duplicate.
 *  - Detects lock ids that are missing entirely from the input;
 *    throws listing the missing ids.
 *  - For each lock id that is present, applies the five-field
 *    eligibility predicate. Any ineligible lock record causes a
 *    throw listing the failing ids and a short reason per id.
 *  - On success, returns the five records in canonical lock order.
 *
 * The returned `PromptRecord` objects are the catalog records
 * unchanged.
 */
export function selectPromptKitsPilotV1(
  promptRecords: unknown,
): ReadonlyArray<PromptRecord> {
  if (!Array.isArray(promptRecords)) {
    throw new PromptKitsPilotV1UnavailableError(
      "selectPromptKitsPilotV1: promptRecords is not an array",
    );
  }

  // Walk input. For each lock-id record, capture the FIRST occurrence
  // and flag any duplicate lock ids.
  const seenLockIds = new Map<string, number>(); // id -> first occurrence index
  const lockRecordsById = new Map<string, PromptRecord>();
  const duplicateLockIds: string[] = [];

  for (let i = 0; i < promptRecords.length; i++) {
    const candidate = promptRecords[i] as Record<string, unknown> | null;
    if (candidate === null || typeof candidate !== "object") continue;
    const id = candidate.id;
    if (typeof id !== "string" || !isPilotV1LockId(id)) continue;

    if (seenLockIds.has(id)) {
      if (!duplicateLockIds.includes(id)) duplicateLockIds.push(id);
      continue;
    }
    seenLockIds.set(id, i);
    lockRecordsById.set(id, candidate as unknown as PromptRecord);
  }

  if (duplicateLockIds.length > 0) {
    throw new PromptKitsPilotV1UnavailableError(
      "selectPromptKitsPilotV1: duplicate lock id(s) in catalog: " +
        duplicateLockIds.join(", "),
    );
  }

  const missingLockIds = PILOT_V1_LOCK_IDS.filter(
    (id) => !lockRecordsById.has(id),
  );
  if (missingLockIds.length > 0) {
    throw new PromptKitsPilotV1UnavailableError(
      "selectPromptKitsPilotV1: missing required lock id(s): " +
        missingLockIds.join(", "),
    );
  }

  // Apply the five-field eligibility predicate to every lock record.
  const ineligibleIds: string[] = [];
  const failureLines: string[] = [];
  for (const id of PILOT_V1_LOCK_IDS) {
    const rec = lockRecordsById.get(id);
    if (!rec) continue; // already handled above
    if (!isPromptKitsEligible(rec)) {
      ineligibleIds.push(id);
      failureLines.push(...eligibilityFailures(rec));
    }
  }
  if (ineligibleIds.length > 0) {
    throw new PromptKitsPilotV1UnavailableError(
      "selectPromptKitsPilotV1: ineligible lock record(s) [" +
        ineligibleIds.join(", ") +
        "]: " +
        failureLines.join("; "),
    );
  }

  // Emit in canonical lock order. By construction every lock id is
  // present and eligible.
  return PILOT_V1_LOCK_IDS.map(
    (id) => lockRecordsById.get(id) as PromptRecord,
  );
}

/**
 * Convenience: list the safety-notice text for a record, or null
 * when the record is not professional or has no mapped notice.
 *
 * The route uses this to render the restrained banner inside the
 * expanded detail region. Other safety classes return null and the
 * banner is not rendered.
 */
export function professionalSafetyNoticeFor(rec: unknown): string | null {
  if (rec === null || typeof rec !== "object") return null;
  const r = rec as Record<string, unknown>;
  if (r.safetyClass !== "professional") return null;
  if (typeof r.id !== "string") return null;
  if (!Object.prototype.hasOwnProperty.call(PROFESSIONAL_SAFETY_NOTICES, r.id)) {
    return null;
  }
  return PROFESSIONAL_SAFETY_NOTICES[r.id as keyof typeof PROFESSIONAL_SAFETY_NOTICES];
}