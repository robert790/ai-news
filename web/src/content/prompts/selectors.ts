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
 *    three hold:
 *      - reviewStatus           === "approved"
 *      - commercialUseStatus    === "cleared"
 *      - publicationEligibility === "prompt-kits"
 *
 * 3. The set of IDs that may appear in the Web V2 /prompt-kits pilot
 *    is exactly the canonical Batch 1 lock:
 *      - code-pr-description
 *      - code-review-staff
 *      - write-customer-notification
 *      - operate-incident-first-15-minutes
 *      - design-frontend-page-skeleton
 *
 *    Other canonical records (including any future Batch 2) are
 *    explicitly excluded until they are owner-promoted and added to
 *    the lock.
 *
 * 4. The returned records are ordered to match the canonical lock
 *    sequence. Order in `promptRecords` is ignored.
 *
 * 5. `selectPromptKitsPilotV1` throws `PromptKitsPilotV1UnavailableError`
 *    if zero records are eligible. This is the dev-time fail-fast
 *    signal that the wiring has been broken.
 *
 * 6. Draft, pending, restricted, rejected, or internal records are
 *    never surfaced through this selector.
 */

import type { PromptRecord } from "./types";

/**
 * The canonical Batch 1 lock. Frozen for v1 of the Web V2 pilot.
 * MUST stay in lock-step with `BATCH_1_LOCK_IDS` in
 * `web/scripts/validate-prompt-content.lib.mjs`.
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
 * catalog contains zero records that satisfy the eligibility triple.
 */
export class PromptKitsPilotV1UnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PromptKitsPilotV1UnavailableError";
  }
}

/**
 * Test whether a single record satisfies the eligibility triple for
 * the /prompt-kits surface.
 *
 * Exported so the negative-test suite can pin the predicate.
 */
export function isPromptKitsEligible(rec: unknown): rec is PromptRecord {
  if (rec === null || typeof rec !== "object") return false;
  const r = rec as Record<string, unknown>;
  return (
    r.reviewStatus === "approved" &&
    r.commercialUseStatus === "cleared" &&
    r.publicationEligibility === "prompt-kits"
  );
}

/**
 * Test whether an id is part of the canonical Pilot V1 lock.
 */
export function isPilotV1LockId(id: unknown): id is string {
  return typeof id === "string" && PILOT_V1_LOCK_IDS.includes(id);
}

/**
 * Select the Pilot V1 records for the /prompt-kits surface.
 *
 * Behavior:
 *  - Filters by the eligibility triple.
 *  - Intersects with the canonical lock id set (drops non-lock ids).
 *  - Reorders the result to match the canonical lock sequence.
 *  - Throws when the result is empty (dev-time fail-fast).
 */
export function selectPromptKitsPilotV1(
  promptRecords: unknown,
): ReadonlyArray<PromptRecord> {
  if (!Array.isArray(promptRecords)) {
    throw new PromptKitsPilotV1UnavailableError(
      "selectPromptKitsPilotV1: promptRecords is not an array",
    );
  }

  // First pass: keep only eligibility-passing records whose id is in
  // the lock. Use a Map for O(1) lookup keyed by id.
  const byId = new Map<string, PromptRecord>();
  for (const candidate of promptRecords) {
    if (!isPromptKitsEligible(candidate)) continue;
    if (!isPilotV1LockId(candidate.id)) continue;
    if (!byId.has(candidate.id)) {
      byId.set(candidate.id, candidate);
    }
  }

  // Second pass: emit in canonical lock order. If a lock id is
  // missing from the catalog, it is simply omitted from the result
  // (the canonical validator already enforces the lock on the
  // catalog itself; this selector tolerates a catalog that has not
  // yet been promoted to the full lock without crashing the page).
  const ordered: PromptRecord[] = [];
  for (const id of PILOT_V1_LOCK_IDS) {
    const rec = byId.get(id);
    if (rec) ordered.push(rec);
  }

  if (ordered.length === 0) {
    throw new PromptKitsPilotV1UnavailableError(
      "selectPromptKitsPilotV1: zero canonical Pilot V1 records available. " +
        "Expected the canonical Batch 1 lock (5 ids) to be present and eligible.",
    );
  }

  return ordered;
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