import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: em dash in a nested user-facing field.
 * A note body contains an em dash. Validator should fail with
 * "em or en dash".
 */

const record: PromptRecord = {
  id: "fixture-em-dash-nested",
  slug: "fixture-em-dash-nested",
  title: "Fixture em dash nested",
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
  notes: [
    {
      title: "Fixture note",
      body: "This note body has an em dash — right here.",
    },
  ],
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