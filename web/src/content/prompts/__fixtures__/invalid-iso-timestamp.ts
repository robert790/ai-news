import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: invalid ISO timestamp.
 * reviewStatus is 'editor-reviewed' but lastReviewedAt is not a
 * valid ISO-8601 string. Validator should fail with
 * "lastReviewedAt must be a valid ISO-8601 string".
 */

const record: PromptRecord = {
  id: "fixture-invalid-iso-timestamp",
  slug: "fixture-invalid-iso-timestamp",
  title: "Fixture invalid ISO timestamp",
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
  reviewer: "fixture-reviewer",
  lastReviewedAt: "not-a-real-date",
  contentVersion: 1,
  safetyClass: "general",
  commercialUseStatus: "pending",
};

export const promptRecords: PromptRecord[] = [record];