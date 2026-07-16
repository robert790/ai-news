/**
 * Canonical index for OpenRadar Web V2 prompt content.
 *
 * This file is the sole catalog source for the content pilot. Every
 * canonical batch file is imported here explicitly. There is no
 * runtime file globbing. The validator loads this index, type-checks
 * the whole reachable module graph, emits the graph to a temporary
 * directory, and imports the emitted module via the normal Node
 * loader. Downstream consumers also import from here.
 */

import { pilotBatch1Records } from "./pilot-batch-1";

import type { PromptCollectionId } from "./collections";

/**
 * Batch 1 records, exposed for downstream consumers that want to
 * reference Batch 1 specifically (for example the validator's
 * exact-five-ID lock test).
 */
export { pilotBatch1Records };

/**
 * The complete catalog. New batches are added by importing their
 * record array and spreading it into this array. There is no
 * globbing; the structure of the catalog is a static import graph.
 */
export const promptRecords = [...pilotBatch1Records];

// Type-only re-exports keep `types` and `collections` out of the
// runtime dependency graph for downstream consumers that only need
// the catalog.
export type { PromptCollectionId } from "./collections";
export type {
  PromptRecord,
  PromptCategory,
  PromptDifficulty,
  PromptSourceType,
  PromptReviewStatus,
  PromptCommercialUseStatus,
  PromptSafetyClass,
  PromptSourceReferenceKind,
  PromptSourceReference,
  PromptInput,
  PromptNote,
  PromptAntiPattern,
  PromptReviewMetadata,
} from "./types";