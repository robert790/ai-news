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

export type PromptSafetyClass = "general" | "professional" | "sensitive";

export type PromptSourceReferenceKind =
  | "internal-concept"
  | "public-framework"
  | "standard"
  | "paper"
  | "external-reference";

/**
 * Editorial reference supporting the sourceType claim.
 *
 * Reference kinds:
 * - "internal-concept": an internal OpenRadar concept or running record.
 * - "public-framework": a public framework or body of practice.
 * - "standard": a published specification (W3C, ISO, OWASP, etc.).
 * - "paper": a published research paper with a URL.
 * - "external-reference": any other public reference.
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
  /**
   * Short label that a user can read. Plain language, no jargon.
   */
  label: string;
  /**
   * One or two sentences explaining what the user should put here, and
   * what a good value looks like.
   */
  description: string;
  /**
   * Optional example value to make the input concrete.
   */
  example?: string;
}

export interface PromptNote {
  /**
   * Short heading for the note.
   */
  title: string;
  /**
   * One paragraph explaining why this prompt works, written for a working
   * practitioner. No marketing language.
   */
  body: string;
}

export interface PromptAntiPattern {
  /**
   * Short heading naming the failure mode.
   */
  title: string;
  /**
   * One paragraph describing what goes wrong and why.
   */
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

export type PromptRecord = PromptReviewMetadata & {
  /** Stable canonical ID, lowercase kebab-case, immutable. */
  id: string;
  /** Routing identity. In v1, slug is always equal to id. */
  slug: string;
  /** Human-readable title. */
  title: string;
  /** Editorial category. */
  category: PromptCategory;
  /** Difficulty level. */
  difficulty: PromptDifficulty;
  /** Who this prompt is for. */
  audience: string;
  /** Short description of when to use this prompt. */
  useCase: string;
  /** Structured inputs the user must fill in before sending. */
  inputs: PromptInput[];
  /** The actual prompt body, with {input_name} placeholders. */
  prompt: string;
  /** What the model should produce when the prompt is used correctly. */
  expectedOutput: string;
  /** Editorial notes explaining why the prompt works. */
  notes: PromptNote[];
  /** Real failure modes the user should avoid. */
  antiPatterns: PromptAntiPattern[];
  /** Registered collection IDs this record belongs to. */
  collectionIds: string[];
  /** Where this record came from. */
  sourceType: PromptSourceType;
  /**
   * Structured references supporting the sourceType claim.
   * Rules per sourceType are enforced by the validator.
   */
  sourceReferences: PromptSourceReference[];
  /** Who wrote it. */
  authorship: string;
  /** Editorial safety classification. */
  safetyClass: PromptSafetyClass;
  /** Commercial-use editorial state. */
  commercialUseStatus: PromptCommercialUseStatus;
  /** Monotonically increasing editorial version. */
  contentVersion: number;
};