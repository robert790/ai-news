/**
 * Canonical Prompt Record contract for OpenRadar Web V2.
 *
 * Single source of truth for the editorial shape of a canonical prompt
 * record. The TypeScript compiler is what enforces the contract at write
 * time; the validator (web/scripts/validate-prompt-content.mjs) uses the
 * installed compiler to enforce it again at validation time.
 *
 * Drafts only. Inclusion does not equal legal or publication approval.
 */

import type { PromptCollectionId } from "./collections";

export type PromptCategory =
  | "code"
  | "write"
  | "research"
  | "decide"
  | "operate"
  | "design"
  | "agent";

export type PromptDifficulty = "beginner" | "intermediate" | "advanced";

export type PromptSourceType =
  | "openradar-original"
  | "openradar-rewrite"
  | "external-reference";

export type PromptReviewStatus =
  | "draft"
  | "editor-reviewed"
  | "approved"
  | "rejected";

export type PromptCommercialUseStatus = "pending" | "cleared" | "restricted";

export type PromptPublicationEligibility = "internal" | "prompt-kits";

export type PromptSafetyClass = "general" | "professional" | "sensitive";

export type PromptSourceReferenceKind =
  | "internal-concept"
  | "public-framework"
  | "standard"
  | "paper"
  | "external-reference";

/**
 * Editorial reference supporting the sourceType claim.
 */
export interface PromptSourceReference {
  kind: PromptSourceReferenceKind;
  label: string;
  url?: string;
  note?: string;
}

export interface PromptInput {
  /**
   * Stable name of the input, used as the placeholder key inside the prompt
   * body. Always lowercase snake_case, no spaces. Unique within a record.
   * Every declared input must appear in the prompt body as {name}, and
   * every {name} placeholder in the prompt body must have a declared input.
   */
  name: string;
  label: string;
  description: string;
  example?: string;
}

export interface PromptNote {
  title: string;
  body: string;
}

export interface PromptAntiPattern {
  title: string;
  body: string;
}

/**
 * Review metadata is a discriminated union on `reviewStatus`.
 *
 * Draft carries null reviewer and null timestamp. Post-draft states
 * ("editor-reviewed" | "approved" | "rejected") carry a non-empty
 * reviewer and a valid ISO-8601 timestamp. No additional payloads.
 */
export type PromptReviewMetadata =
  | {
      reviewStatus: "draft";
      reviewer: null;
      lastReviewedAt: null;
    }
  | {
      reviewStatus: "editor-reviewed" | "approved" | "rejected";
      reviewer: string;
      lastReviewedAt: string;
    };

/**
 * Promotion invariants:
 *  - publicationEligibility: "prompt-kits" requires:
 *      - reviewStatus: "approved"
 *      - commercialUseStatus: "cleared"
 *      - non-empty reviewer
 *      - valid lastReviewedAt
 *  - draft, editor-reviewed, or rejected records cannot use "prompt-kits"
 *  - rejected records must use "internal"
 *
 * Eligibility records owner approval only. It does NOT claim the record
 * is currently wired into the public route or visible to end users.
 */

export type PromptRecord = PromptReviewMetadata & {
  /** Stable canonical ID, lowercase kebab-case, immutable. */
  id: string;
  /** Routing identity. In v1, slug is always equal to id. */
  slug: string;
  title: string;
  category: PromptCategory;
  difficulty: PromptDifficulty;
  audience: string;
  useCase: string;
  inputs: PromptInput[];
  prompt: string;
  expectedOutput: string;
  notes: PromptNote[];
  antiPatterns: PromptAntiPattern[];
  /** Registered collection IDs this record belongs to. */
  collectionIds: PromptCollectionId[];
  sourceType: PromptSourceType;
  sourceReferences: PromptSourceReference[];
  authorship: string;
  safetyClass: PromptSafetyClass;
  commercialUseStatus: PromptCommercialUseStatus;
  /** Editorial publication-eligibility state. */
  publicationEligibility: PromptPublicationEligibility;
  /** Monotonically increasing editorial version. */
  contentVersion: number;
};