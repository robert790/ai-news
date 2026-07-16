import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: duplicate ID.
 * Two records with the same id. Validator should fail with
 * "duplicate ids".
 */

const base = {
  category: "code" as const,
  difficulty: "beginner" as const,
  audience: "Fixture audience.",
  useCase: "Fixture use case.",
  inputs: [
    {
      name: "input_a",
      label: "Input A",
      description: "Description for input A.",
    },
  ],
  prompt: ["Fixture prompt body A.", "", "Input A: {input_a}"].join("\n"),
  expectedOutput: "Fixture expected output.",
  notes: [{ title: "Fixture note", body: "Fixture note body." }],
  antiPatterns: [
    { title: "Fixture anti-pattern", body: "Fixture anti-pattern body." },
  ],
  collectionIds: ["builder-bench"],
  sourceType: "openradar-original" as const,
  sourceReferences: [],
  authorship: "OpenRadar editorial",
  reviewStatus: "draft" as const,
  reviewer: null,
  lastReviewedAt: null,
  contentVersion: 1,
  safetyClass: "general" as const,
  commercialUseStatus: "pending" as const,
};

const a: PromptRecord = {
  ...base,
  id: "fixture-duplicate-id",
  slug: "fixture-duplicate-id",
  title: "Fixture duplicate id A",
};

const b: PromptRecord = {
  ...base,
  id: "fixture-duplicate-id",
  slug: "fixture-duplicate-id-b",
  title: "Fixture duplicate id B",
  prompt: ["Fixture prompt body B.", "", "Input A: {input_a}"].join("\n"),
};

export const promptRecords: PromptRecord[] = [a, b];