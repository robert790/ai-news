#!/usr/bin/env node
/**
 * Negative tests for validate-prompt-content.mjs.
 *
 * Each fixture lives under web/src/content/prompts/__fixtures__/<case>/
 * and contains a single pilot-batch-fixture.ts file. Each test runs
 * the validator against a sandboxed copy of the prompts directory in
 * which the canonical index is rewritten to load the fixture as the
 * sole batch. The validator is invoked with patched REPO_ROOT and
 * WEB_ROOT so it operates entirely inside the sandbox.
 *
 * This file does NOT reimplement any validator rules. It only
 * invokes the validator and asserts the failure mode.
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  mkdtempSync,
  mkdirSync,
  rmSync,
  copyFileSync,
  writeFileSync,
  readFileSync,
  readdirSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "..", "..");
const PROMPTS_DIR = resolve(REPO_ROOT, "web", "src", "content", "prompts");
const FIXTURES_DIR = join(PROMPTS_DIR, "__fixtures__");
const VALIDATOR_PATH = join(__dirname, "validate-prompt-content.mjs");

const NEGATIVE_CASES = [
  { name: "missing required field",              fixture: "missing-required-field.ts",     expected: "must be a non-empty string" },
  { name: "malformed input",                      fixture: "malformed-input.ts",             expected: "name must be lowercase snake_case identifier" },
  { name: "malformed source reference",           fixture: "malformed-source-reference.ts",  expected: "kind" },
  { name: "duplicate ID",                        fixture: "duplicate-id.ts",                expected: "duplicate ids" },
  { name: "duplicate slug",                      fixture: "duplicate-slug.ts",              expected: "duplicate slugs" },
  { name: "invalid ID or slug format",           fixture: "invalid-id-format.ts",           expected: "is not lowercase kebab-case" },
  { name: "slug not equal to ID",                fixture: "slug-mismatch.ts",               expected: "must equal id" },
  { name: "duplicate input names",               fixture: "duplicate-input-names.ts",       expected: "duplicate input name" },
  { name: "declared input absent from prompt",   fixture: "declared-input-absent.ts",       expected: "does not appear as a" },
  { name: "undeclared prompt placeholder",       fixture: "undeclared-placeholder.ts",      expected: "has no matching declared input" },
  { name: "invalid post-draft metadata",         fixture: "invalid-post-draft-metadata.ts", expected: "reviewer must be a non-empty string" },
  { name: "invalid ISO timestamp",               fixture: "invalid-iso-timestamp.ts",        expected: "lastReviewedAt must be a valid ISO-8601 string" },
  { name: "invalid commercialUseStatus",         fixture: "invalid-commercial-use.ts",      expected: "commercialUseStatus" },
  { name: "unknown collection ID",               fixture: "unknown-collection-id.ts",       expected: "is not in the registered collection registry" },
  { name: "forbidden prompt-body token",         fixture: "forbidden-token.ts",             expected: "forbidden vendor/model/product phrase" },
  { name: "em dash in a nested user-facing field", fixture: "em-dash-nested.ts",            expected: "em or en dash" },
  { name: "duplicate prompt body",               fixture: "duplicate-prompt-body.ts",       expected: "Duplicate prompt body" },
];

function runValidatorAgainstFixture(fixtureName) {
  const sandbox = mkdtempSync(join(tmpdir(), "openradar-fixture-"));

  // Build <sandbox>/web/src/content/prompts/ and a sibling
  // <sandbox>/web/node_modules/ that contains a copy of the real
  // `typescript` package so the validator copy inside
  // <sandbox>/web/scripts/ can resolve its bare `typescript` import
  // by walking up to the sandbox's node_modules.
  const webSandbox = join(sandbox, "web");
  const sandboxScripts = join(webSandbox, "scripts");
  const sandboxPrompts = join(webSandbox, "src", "content", "prompts");
  mkdirSync(sandboxPrompts, { recursive: true });
  mkdirSync(sandboxScripts, { recursive: true });

  // Copy the typescript package directory so the bare import resolves.
  const realTypescriptDir = resolve(REPO_ROOT, "web", "node_modules", "typescript");
  const sandboxTypescriptDir = join(webSandbox, "node_modules", "typescript");
  copyRecursive(realTypescriptDir, sandboxTypescriptDir);

  // Minimal package.json so Node treats the sandbox as ESM when needed.
  writeFileSync(join(webSandbox, "package.json"), JSON.stringify({ type: "module" }, null, 2));

  copyFileSync(
    join(PROMPTS_DIR, "collections.ts"),
    join(sandboxPrompts, "collections.ts"),
  );

  // Copy types.ts so module-resolution from index.ts succeeds.
  copyFileSync(join(PROMPTS_DIR, "types.ts"), join(sandboxPrompts, "types.ts"));

  // Copy the fixtures directory so fixture imports like "../types"
  // resolve correctly. Only the requested fixture is loaded via the
  // rewritten index, but its relative imports must work.
  const sandboxFixtures = join(sandboxPrompts, "__fixtures__");
  mkdirSync(sandboxFixtures, { recursive: true });
  copyFileSync(
    join(FIXTURES_DIR, fixtureName),
    join(sandboxFixtures, fixtureName),
  );

  // Copy the canonical index.ts but rewrite its pilot-batch-1 import
  // to ./pilot-batch-fixture-1 so the fixture (sitting at that path,
  // matching the validator's pilot-batch-*.ts glob) is the only batch
  // loaded. The fixture's relative import "../types" is rewritten to
  // "./types" so module resolution succeeds.
  const indexSrc = readFileSync(join(PROMPTS_DIR, "index.ts"), "utf8");
  const indexOut = indexSrc.replace(
    /from "\.\/pilot-batch-1"/g,
    'from "./pilot-batch-fixture-1"',
  );
  writeFileSync(join(sandboxPrompts, "index.ts"), indexOut);

  // Place the fixture at <sandboxPrompts>/pilot-batch-fixture-1.ts
  // so the validator's glob picks it up. Rewrite its "../types"
  // import to "./types" so module resolution finds the local copy.
  const fixtureSrc = readFileSync(join(FIXTURES_DIR, fixtureName), "utf8");
  const fixtureOut = fixtureSrc.replace(
    /from "\.\.\/types"/g,
    'from "./types"',
  );
  writeFileSync(
    join(sandboxPrompts, "pilot-batch-fixture-1.ts"),
    fixtureOut,
  );

  // Validator copy lives at <sandbox>/web/scripts/ so it can resolve
  // its `typescript` import via <sandbox>/web/node_modules.
  const validatorCopy = join(sandboxScripts, "validate-prompt-content.mjs");
  const validatorSrc = readFileSync(VALIDATOR_PATH, "utf8");
  const patched = validatorSrc
    .replace(
      /REPO_ROOT = resolve\(__dirname, "\.\.", "\.\."\);/,
      `REPO_ROOT = ${JSON.stringify(join(sandbox, "repo"))};`,
    )
    .replace(
      /WEB_ROOT = resolve\(REPO_ROOT, "web"\);/,
      `WEB_ROOT = ${JSON.stringify(webSandbox)};`,
    );
  writeFileSync(validatorCopy, patched);

  const result = spawnSync(process.execPath, [validatorCopy], {
    encoding: "utf8",
  });

  rmSync(sandbox, { recursive: true, force: true });

  return {
    code: result.status,
    output: (result.stdout || "") + (result.stderr || ""),
  };
}

function copyRecursive(src, dst) {
  mkdirSync(dst, { recursive: true });
  const entries = readdirSync(src, { withFileTypes: true });
  for (const e of entries) {
    const s = join(src, e.name);
    const d = join(dst, e.name);
    if (e.isDirectory()) copyRecursive(s, d);
    else if (e.isFile()) copyFileSync(s, d);
  }
}

NEGATIVE_CASES.forEach(({ name, fixture, expected }) => {
  test(`negative: ${name}`, () => {
    const { code, output } = runValidatorAgainstFixture(fixture);
    assert.notEqual(code, 0, `validator should fail for fixture '${fixture}'`);
    assert.match(
      output,
      new RegExp(expected.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")),
      `expected validator output to match /${expected}/, got: ${output}`,
    );
  });
});