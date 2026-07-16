import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: forbidden prompt-body token.
 * The prompt body contains an unambiguous vendor phrase from the
 * validator's hard-fail list ("chatgpt"). Validator should fail
 * with "forbidden vendor/model/product phrase".
 */

const record: PromptRecord = {
  id: "fixture-forbidden-token",
  slug: "fixture-forbidden-token",
  title: "Fixture forbidden token",
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
    "",
    "Tooling reference: chatgpt for some reason.",
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