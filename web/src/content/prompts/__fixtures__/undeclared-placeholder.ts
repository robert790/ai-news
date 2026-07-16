import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: undeclared prompt placeholder.
 * The prompt body uses {undeclared_input} but no matching input
 * is declared. Validator should fail with
 * "has no matching declared input".
 */

const record: PromptRecord = {
  id: "fixture-undeclared-placeholder",
  slug: "fixture-undeclared-placeholder",
  title: "Fixture undeclared placeholder",
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
  prompt: [
    "Fixture prompt body.",
    "",
    "Input A: {input_a}",
    "Other: {undeclared_input}",
  ].join("\n"),
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