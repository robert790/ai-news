/**
 * Canonical Prompt Record contract for OpenRadar Web V2.
 *
 * This file is the single source of truth for the editorial shape of a
 * canonical prompt record. It is intentionally explicit so the dependency-free
 * validator (web/scripts/validate-prompt-content.mjs) can check the same
 * shape against the runtime JSON emitted by pilot-batch-*.ts without needing
 * a TypeScript toolchain.
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
  | "editorial-review"
  | "legal-review"
  | "approved";

export type PromptSafetyClass =
  | "general"
  | "professional"
  | "sensitive";

export interface PromptInput {
  /**
   * Stable name of the input, used as the placeholder key inside the prompt
   * body. Always lowercase, hyphen-separated, no spaces.
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

export interface PromptRecord {
  /** Stable canonical ID, must match the frozen scope document. */
  id: string;
  /** URL-safe slug derived from id, must be unique. */
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
  /** Collection IDs this record belongs to. */
  collectionIds: string[];
  /** Where this record came from. */
  sourceType: PromptSourceType;
  /** Free-form references supporting the sourceType claim. */
  sourceReferences: string[];
  /** Who wrote it. */
  authorship: string;
  /** Where this record sits in the editorial pipeline. */
  reviewStatus: PromptReviewStatus;
  /** Reviewer identifier when reviewStatus is past draft, otherwise null. */
  reviewer: string | null;
  /** ISO-8601 timestamp of last review, or null while in draft. */
  lastReviewedAt: string | null;
  /** Monotonically increasing editorial version. */
  contentVersion: number;
  /** Editorial safety classification. */
  safetyClass: PromptSafetyClass;
  /** Whether this prompt's wording is cleared for commercial publication. */
  commercialUseAllowed: boolean;
}