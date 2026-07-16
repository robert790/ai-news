/**
 * Canonical Prompt Collection registry for OpenRadar Web V2.
 *
 * The registry is the single source of truth for the collection IDs that
 * a `PromptRecord.collectionIds` field is allowed to reference. The
 * validator cross-checks every record's `collectionIds` against this
 * registry and fails on unknown IDs.
 *
 * This file exports both:
 * - The runtime registry: COLLECTION_IDS, COLLECTION_ID_SET.
 * - The PromptCollectionId type, used by the canonical schema.
 *
 * No batch or types file imports from this module's runtime values.
 * types.ts imports the type only.
 */

export const BUILDER_BENCH = "builder-bench";
export const EDITOR_DESK = "editor-desk";
export const OPERATOR_PLAYBOOK = "operator-playbook";
export const STUDIO_FOUNDATION = "studio-foundation";

/**
 * The canonical registry. Frozen for v1 of the Web V2 pilot. Any new
 * collection is an explicit registry change, not a record-level change.
 */
export const COLLECTION_IDS = [
  BUILDER_BENCH,
  EDITOR_DESK,
  OPERATOR_PLAYBOOK,
  STUDIO_FOUNDATION,
] as const;

export type PromptCollectionId = (typeof COLLECTION_IDS)[number];

/**
 * Set form for O(1) membership checks. Built once from the array above.
 */
export const COLLECTION_ID_SET: ReadonlySet<string> = new Set(COLLECTION_IDS);