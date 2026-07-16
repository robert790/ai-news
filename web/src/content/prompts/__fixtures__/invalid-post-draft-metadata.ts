import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: invalid post-draft metadata.
 * reviewStatus is 'editor-reviewed' but reviewer is the empty
 * string. Validator should fail with
 * "reviewer must be a non-empty string".
 */

const record: PromptRecord = {
  id: "fixture-invalid-post-draft",
  slug: "fixture-invalid-post-draft",
  title: "Fixture invalid post draft metadata",
  category: "code",
  difficulty: "beginner",
  audience: "Fixture audience.",
  useCase: "Fixture use case.",
  inputs: [
    {
      name: "input_a",
      label: "Input A",
      description: "Description for input A.",
    },
  ],
  prompt: ["Fixture prompt body.", "", "Input A: {input_a}"].join("\n"),
  expectedOutput: "Fixture expected output.",
  notes: [{ title: "Fixture note", body: "Fixture note body." }],
  antiPatterns: [
    { title: "Fixture anti-pattern", body: "Fixture anti-pattern body." },
  ],
  collectionIds: ["builder-bench"],
  sourceType: "openradar-original",
  sourceReferences: [],
  authorship: "OpenRadar editorial",
  reviewStatus: "editor-reviewed",
  reviewer: "",
  lastReviewedAt: "2026-07-15T12:00:00Z",
  contentVersion: 1,
  safetyClass: "general",
  commercialUseStatus: "pending",
};

export const promptRecords: PromptRecord[] = [record];