import type { PromptRecord } from "../types";

/**
 * NEGATIVE FIXTURE: malformed source reference.
 * Source reference has an unknown kind. Validator should fail mentioning
 * "kind".
 *
 * sourceType is openradar-rewrite so the validator must check the
 * reference rules for non-original sourceTypes.
 */

const record: PromptRecord = {
  id: "fixture-bad-ref",
  slug: "fixture-bad-ref",
  title: "Fixture bad reference",
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
  collectionIds: ["builder-bench"],
  sourceType: "openradar-rewrite",
  sourceReferences: [
    {
      kind: "totally-bogus-kind",
      label: "Bogus reference",
    },
  ],
  authorship: "OpenRadar editorial",
  reviewStatus: "draft",
  reviewer: null,
  lastReviewedAt: null,
  contentVersion: 1,
  safetyClass: "general",
  commercialUseStatus: "pending",
};

export const promptRecords: PromptRecord[] = [record];