import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: unknown collection ID.
 * collectionIds contains a value not in the registry. Validator
 * should fail with "is not in the registered collection registry".
 */

const record: PromptRecord = {
  id: "fixture-unknown-collection",
  slug: "fixture-unknown-collection",
  title: "Fixture unknown collection",
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
  collectionIds: ["this-collection-is-not-registered"],
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