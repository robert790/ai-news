import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: invalid commercialUseStatus.
 * commercialUseStatus is a value outside the allowed enum.
 * Validator should fail with "commercialUseStatus".
 */

const record = {
  id: "fixture-bad-commercial-use",
  slug: "fixture-bad-commercial-use",
  title: "Fixture bad commercial use",
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
  prompt: ["Fixture prompt body.", "", "Input A: {input_a}"].join("\n"),
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
  commercialUseStatus: "undecided-but-also-probably-fine",
} as unknown as PromptRecord;

export const promptRecords: PromptRecord[] = [record];