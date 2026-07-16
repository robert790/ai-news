import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: duplicate input names.
 * Two declared inputs share the name "input_a". Validator should
 * fail with "duplicate input name".
 */

const record: PromptRecord = {
  id: "fixture-duplicate-input-names",
  slug: "fixture-duplicate-input-names",
  title: "Fixture duplicate input names",
  category: "code",
  difficulty: "beginner",
  audience: "Fixture audience.",
  useCase: "Fixture use case.",
  inputs: [
    {
      name: "input_a",
      label: "Input A first",
      description: "First description for input_a.",
    },
    {
      name: "input_a",
      label: "Input A second",
      description: "Second description for input_a.",
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
  reviewStatus: "draft",
  reviewer: null,
  lastReviewedAt: null,
  contentVersion: 1,
  safetyClass: "general",
  commercialUseStatus: "pending",
};

export const promptRecords: PromptRecord[] = [record];