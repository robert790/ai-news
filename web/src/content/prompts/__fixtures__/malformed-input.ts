import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: malformed input.
 * Input name uses uppercase + spaces (not lowercase snake_case).
 * Validator should fail with "name must be lowercase snake_case identifier".
 */

const record: PromptRecord = {
  id: "fixture-malformed-input",
  slug: "fixture-malformed-input",
  title: "Fixture malformed input",
  category: "code",
  difficulty: "beginner",
  audience: "Fixture audience.",
  useCase: "Fixture use case.",
  inputs: [
    {
      name: "Bad Name",
      label: "Input A",
      description: "Description for input A.",
    },
    {
      name: "input_b",
      label: "Input B",
      description: "Description for input B.",
    },
  ],
  prompt: ["Fixture prompt body.", "", "Bad Name: {input_b}"].join("\n"),
  expectedOutput: "Fixture expected output.",
  notes: [{ title: "Fixture note", body: "Fixture note body." }],
  antiPatterns: [
    { title: "Fixture anti-pattern", body: "Fixture anti-pattern body." },
  ],
  collectionIds: ["builder-bench"],
  sourceType: "openradar-original",
  sourceReferences: [],
  authorship: "OpenRadar editorial",
  reviewStatus: "draft",
  reviewer: null,
  lastReviewedAt: null,
  contentVersion: 1,
  safetyClass: "general",
  commercialUseStatus: "pending",
};

export const promptRecords: PromptRecord[] = [record];