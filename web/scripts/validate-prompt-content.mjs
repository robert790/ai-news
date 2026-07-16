#!/usr/bin/env node
/**
 * Validator for the canonical OpenRadar prompt-content pilot.
 *
 * Architecture
 * ------------
 * The canonical index (`web/src/content/prompts/index.ts`) is the sole
 * catalog source. There is no runtime file globbing. The validator:
 *
 *   1. Compiles the canonical index and every module reachable from it
 *      with the installed TypeScript compiler. Syntactic and semantic
 *      diagnostics are treated as hard failures.
 *   2. Emits the canonical index graph to a temporary directory.
 *   3. Imports the emitted module via the normal Node loader. No
 *      `new Function`, no `eval`, no hand-written require/import string
 *      rewriting, no execution of batch files not reachable from the
 *      canonical index.
 *   4. Runs the pure validation functions on the loaded catalog.
 *   5. Cleans up the temporary output.
 *
 * Validation functions live in `validate-prompt-content.lib.mjs` and
 * are exported so the negative-test suite can validate supplied record
 * arrays directly, without subprocesses or fixture files.
 *
 * Exit codes
 * ----------
 *   0 -- all checks pass.
 *   1 -- at least one check failed.
 */

import { mkdtempSync, rmSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import ts from "typescript";

import {
  validateCatalog,
  validateBatch1Lock,
  BATCH_1_LOCK_IDS,
} from "./validate-prompt-content.lib.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "..", "..");
const WEB_ROOT = resolve(REPO_ROOT, "web");
const INDEX_PATH = resolve(WEB_ROOT, "src", "content", "prompts", "index.ts");
const COLLECTIONS_PATH = resolve(WEB_ROOT, "src", "content", "prompts", "collections.ts");

function fail(message) {
  console.error(message);
  process.exit(1);
}

/**
 * Read the collection registry literal from collections.ts using the
 * TS compiler. Pure AST walk; no runtime eval of the registry module.
 */
function loadCollectionIdSet() {
  const src = readFileSync(COLLECTIONS_PATH, "utf8");
  const sf = ts.createSourceFile(
    COLLECTIONS_PATH,
    src,
    ts.ScriptTarget.ES2022,
    true,
    ts.ScriptKind.TS,
  );
  const constMap = new Map();
  for (const stmt of sf.statements) {
    if (
      ts.isVariableStatement(stmt) &&
      stmt.declarationList.declarations.length === 1
    ) {
      const decl = stmt.declarationList.declarations[0];
      if (
        ts.isIdentifier(decl.name) &&
        decl.initializer &&
        ts.isStringLiteralLike(decl.initializer)
      ) {
        constMap.set(decl.name.text, decl.initializer.text);
      }
    }
  }
  const out = [];
  for (const stmt of sf.statements) {
    if (
      ts.isVariableStatement(stmt) &&
      stmt.declarationList.declarations.length === 1
    ) {
      const decl = stmt.declarationList.declarations[0];
      if (
        ts.isIdentifier(decl.name) &&
        decl.name.text === "COLLECTION_IDS" &&
        decl.initializer
      ) {
        let init = decl.initializer;
        if (ts.isAsExpression(init)) init = init.expression;
        if (ts.isArrayLiteralExpression(init)) {
          for (const el of init.elements) {
            if (ts.isStringLiteralLike(el)) {
              out.push(el.text);
            } else if (ts.isIdentifier(el) && constMap.has(el.text)) {
              out.push(constMap.get(el.text));
            }
          }
        }
      }
    }
  }
  if (out.length === 0) {
    fail(
      `Could not load collection registry from ${COLLECTIONS_PATH}: no COLLECTION_IDS literal found.`,
    );
  }
  return new Set(out);
}

async function main() {
  const collectionIdSet = loadCollectionIdSet();

  // 1. Compile the canonical index graph.
  const program = ts.createProgram([INDEX_PATH], {
    noEmit: false,
    strict: true,
    module: ts.ModuleKind.ESNext,
    moduleResolution: ts.ModuleResolutionKind.Bundler,
    target: ts.ScriptTarget.ES2022,
    skipLibCheck: true,
    jsx: ts.JsxEmit.Preserve,
    esModuleInterop: true,
    allowSyntheticDefaultImports: true,
  });
  const diagnostics = ts.getPreEmitDiagnostics(program);
  if (diagnostics.length > 0) {
    for (const d of diagnostics) {
      const file = d.file ? d.file.fileName.replace(WEB_ROOT + "/", "") : "<unknown>";
      const pos =
        d.file && d.start !== undefined
          ? d.file.getLineAndCharacterOfPosition(d.start)
          : { line: 0, character: 0 };
      const msg = ts.flattenDiagnosticMessageText(d.messageText, "\n");
      console.error(`${file}:${pos.line + 1}:${pos.character + 1} ${msg}`);
    }
    console.error(`Validation failed: ${diagnostics.length} TypeScript diagnostic(s).`);
    process.exit(1);
  }

  // 2. Emit to a temporary directory.
  const tmp = mkdtempSync(join(tmpdir(), "openradar-validate-"));
  try {
    // 2. Emit the canonical index graph to a temporary directory as
    //    CommonJS. We emit CJS because Node's CJS resolver handles
    //    extension-less imports natively, satisfying the "normal
    //    Node require" rule without rewriting import strings. The
    //    canonical source stays ESM; only the emitted copy is CJS.
    const emitProgram = ts.createProgram([INDEX_PATH], {
      noEmit: false,
      strict: true,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.Node10,
      target: ts.ScriptTarget.ES2022,
      skipLibCheck: true,
      jsx: ts.JsxEmit.Preserve,
      esModuleInterop: true,
      allowSyntheticDefaultImports: true,
      outDir: tmp,
      rootDir: WEB_ROOT,
    });
    const emitResult = emitProgram.emit();
    const emitDiags = ts
      .getPreEmitDiagnostics(emitProgram)
      .concat(emitResult.diagnostics);
    if (emitDiags.length > 0) {
      for (const d of emitDiags) {
        const file = d.file ? d.file.fileName : "<unknown>";
        const msg = ts.flattenDiagnosticMessageText(d.messageText, "\n");
        console.error(`${file}: ${msg}`);
      }
      console.error(`Validation failed: ${emitDiags.length} emit-time diagnostic(s).`);
      rmSync(tmp, { recursive: true, force: true });
      process.exit(1);
    }

    // 3. Load the emitted module via the normal CJS loader.
    const emittedIndexPath = join(
      tmp,
      "src",
      "content",
      "prompts",
      "index.js",
    );
    const { createRequire } = await import("node:module");
    const req = createRequire(import.meta.url);
    const mod = req(emittedIndexPath);
    if (!mod || !Array.isArray(mod.promptRecords)) {
      console.error(
        `Emitted module did not export a 'promptRecords' array: ${emittedIndexPath}`,
      );
      rmSync(tmp, { recursive: true, force: true });
      process.exit(1);
    }
    if (!Array.isArray(mod.pilotBatch1Records)) {
      console.error(
        `Emitted module did not export a 'pilotBatch1Records' array: ${emittedIndexPath}`,
      );
      rmSync(tmp, { recursive: true, force: true });
      process.exit(1);
    }

    // 4a. Run the Batch 1 lock check on the separately-exported
    //     pilotBatch1Records. The lock is not derived from the
    //     complete promptRecords catalog.
    const lockResult = validateBatch1Lock(
      mod.pilotBatch1Records,
      BATCH_1_LOCK_IDS,
    );
    if (lockResult.errors.length > 0) {
      console.log(
        `Batch 1 lock failed (${lockResult.errors.length} error${lockResult.errors.length === 1 ? "" : "s"}):`,
      );
      for (const e of lockResult.errors) console.log("  - " + e);
      rmSync(tmp, { recursive: true, force: true });
      process.exit(1);
    }

    // 4b. Run pure catalog validation on the complete promptRecords.
    const result14 = validateCatalog(mod.promptRecords, {
      collectionIdSet,
    });
    if (result14.errors.length === 0) {
      console.log(
        `OK: ${lockResult.recordCount} Batch 1 record(s) locked; ${result14.recordCount} canonical prompt record(s) validated.`,
      );
      rmSync(tmp, { recursive: true, force: true });
      process.exit(0);
    }
    console.log(
      `Validation failed (${result14.errors.length} error${result14.errors.length === 1 ? "" : "s"}):`,
    );
    for (const e of result14.errors) console.log("  - " + e);
    rmSync(tmp, { recursive: true, force: true });
    process.exit(1);
  } catch (err) {
    rmSync(tmp, { recursive: true, force: true });
    console.error(`Validator crashed: ${err.stack || err.message}`);
    process.exit(1);
  }
}

await main();