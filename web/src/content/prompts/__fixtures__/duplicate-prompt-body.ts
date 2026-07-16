import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: duplicate prompt body.
 * Two records share the same prompt body (after whitespace
 * normalization). Validator should fail with "Duplicate prompt body".
 */

const sharedPrompt = ["Fixture prompt body.", "", "Input A: {input_a}"].join("\n");

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
  prompt: sharedPrompt,
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
  id: "fixture-dup-body-a",
  slug: "fixture-dup-body-a",
  title: "Fixture duplicate body A",
};

const b: PromptRecord = {
  ...base,
  id: "fixture-dup-body-b",
  slug: "fixture-dup-body-b",
  title: "Fixture duplicate body B",
};

export const promptRecords: PromptRecord[] = [a, b];