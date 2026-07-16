import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: declared input absent from prompt body.
 * Declared input `input_b` does not appear as {input_b} in the
 * prompt body. Validator should fail with "does not appear as a".
 */

const record: PromptRecord = {
  id: "fixture-declared-input-absent",
  slug: "fixture-declared-input-absent",
  title: "Fixture declared input absent",
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
    {
      name: "input_b",
      label: "Input B",
      description: "Description for input B.",
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