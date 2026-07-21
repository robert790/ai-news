import type { PromptRecord } from "./types";

/**
 * Pilot Batch 2 -- five canonical OpenRadar prompt records.
 *
 * Provenance in Batch 2 is not uniform. Four records (code-refactor-no-driveby,
 * write-incident-postmortem, research-source-triangulate, operate-auto-rollback-conditions)
 * use OpenRadar-authored wording developed around frozen internal concept IDs;
 * each carries exactly one structured `internal-concept` sourceReferences entry
 * that names the frozen concept ID and notes that the wording was rewritten from
 * first principles. The fifth record (decide-pre-mortem) uses openradar-rewrite
 * with one `public-framework` reference for the named pre-mortem method; no URL
 * is attached because none has been verified for inclusion. The wording across
 * all five records is OpenRadar-authored from first principles.
 *
 * Every record in this batch is a draft. None of the Batch 2 records is
 * eligible for the public Prompt Kits surface. Eligibility requires an explicit
 * owner-promoted canonical change (record moves through editor-reviewed, then
 * approved, with commercialUseStatus cleared and publicationEligibility set to
 * prompt-kits), and the IDs must be added to PILOT_V1_LOCK_IDS in
 * `selectors.ts`. None of those changes are part of this batch.
 *
 * No em dashes in user-facing content. Variables use declared snake_case
 * placeholders. The prompts are tool-agnostic and copy-paste ready. Every
 * record requires human review for consequential use; safetyClass is
 * "professional" on every record for that reason.
 *
 * Provenance is a per-record editorial classification, not a validator-proven
 * fact. Validation enforces structural correctness (id format, sourceType /
 * reference kind membership, em-dash policy, placeholder contract) but does
 * not judge whether a sourceReference is historically accurate, legally
 * cleared, or appropriate for promotion. Owner and legal-trust review are the
 * gates that decide whether a record moves out of draft.
 */

const baseEditorial = {
  sourceType: "openradar-original" as const,
  authorship: "OpenRadar editorial",
  reviewStatus: "draft" as const,
  reviewer: null,
  lastReviewedAt: null,
  contentVersion: 1,
  commercialUseStatus: "pending" as const,
  publicationEligibility: "internal" as const,
  safetyClass: "professional" as const,
};

const provenance = (id: string) => [
  {
    kind: "internal-concept" as const,
    label: `Legacy Prompt Bible concept: ${id}`,
    note:
      "Frozen concept reference. The wording below was rewritten from first principles for canonical OpenRadar content; legacy wording is not reused.",
  },
];

/**
 * Provenance for the one Batch 2 record that names a public framework
 * rather than only a frozen internal concept. The pre-mortem method
 * is a named public framework; the record treats the wording as an
 * OpenRadar rewrite of that framework, with no URL or citation that
 * has not been verified.
 *
 * The label names the method. The note explicitly disclaims a URL:
 * any external reference would need to be verified before attachment,
 * and the validator rejects URLs that are not valid http/https.
 */
const publicFrameworkRewriteProvenance = () => [
  {
    kind: "public-framework" as const,
    label: "Pre-mortem method (public decision-analysis framework)",
    note:
      "OpenRadar rewrite of the named pre-mortem method. No URL or citation has been verified for attachment; the reference is included by framework name only. Owner/legal-trust review must verify any external citation before this reference is promoted out of draft.",
  },
];

export const pilotBatch2Records: PromptRecord[] = [
  {
    ...baseEditorial,
    id: "code-refactor-no-driveby",
    slug: "code-refactor-no-driveby",
    title: "Refactor that stays inside the boundary you were given",
    category: "code",
    difficulty: "advanced",
    audience:
      "Engineers asked to refactor part of a codebase where the surrounding code, tests, or contract must keep behaving the way they do today.",
    useCase:
      "When the task is a refactor and the change is at risk of growing beyond what was asked, either by editing code that was not in scope or by quietly rewriting behavior that already works.",
    inputs: [
      {
        name: "refactor_boundary",
        label: "Refactor boundary",
        description:
          "The exact scope of the refactor. State what is in scope (files, components, modules, behavior) and what is explicitly out of scope. Quote the task text or ticket when possible.",
        example:
          "Refactor the retry logic inside src/clients/http.ts. Out of scope: any call site, the public client interface, retry metrics, and the connection pool.",
      },
      {
        name: "behavior_to_preserve",
        label: "Behavior to preserve",
        description:
          "The externally observable behavior that must not change: API contracts, return shapes, error semantics, performance budgets, logging contracts, and any contract with downstream callers. Mark which items are confirmed and which are assumed.",
        example:
          "Confirmed: error type and message for timeouts stay identical. Assumed: the order of internal log lines stays identical. Not required: exact timing of individual retries.",
      },
      {
        name: "investigation_findings",
        label: "Investigation findings (if available)",
        description:
          "Anything you discovered while reading the code before editing: the actual call graph, the tests that cover this area, dead code, hidden coupling, or contracts the inputs did not mention. When nothing is supplied, the prompt must investigate first instead of editing.",
        example:
          "The retry helper is called from 11 call sites; two of them rely on the helper logging a specific warning string; one test pins the warning text in a snapshot.",
      },
      {
        name: "repository_access",
        label: "Repository access",
        description:
          "State whether the prompt has actual repository access (and which tool: filesystem, version-control tool, code search, language server) or whether all inspection will be drawn from supplied text. When no actual access is available, every inspection item must be labelled 'planned, not performed'.",
        example:
          "Actual access: filesystem and grep over the repo root. No language server. Supplied diff was pasted from the change-management tool.",
      },
      {
        name: "unrelated_cleanup_seen",
        label: "Unrelated cleanup seen along the way",
        description:
          "Improvements noticed while reading the code that are not part of the refactor. These go in a deferred list, not in the diff.",
        example:
          "Three call sites have duplicated timeout values; one test name does not match what it asserts; the helper accepts an unused retry count parameter.",
      },
      {
        name: "verification_plan",
        label: "Verification plan",
        description:
          "The targeted checks that justify merging: which tests, which manual repros, which behavior diffs, which performance checks. When nothing is supplied, the prompt must state what it would run and what 'safe' looks like.",
        example:
          "Run the unit tests for src/clients and the integration test suite. Manually exercise one flaky-upstream scenario. Confirm error type and message stay identical for the timeout case.",
      },
      {
        name: "rejected_scope_expansion",
        label: "Rejected scope-expansion requests",
        description:
          "Drive-by changes the inputs tempted toward but the user explicitly rejected (or that the boundary explicitly forbids). These belong in section 7, not in the diff.",
        example:
          "Reject: reformatting the call sites. Reject: renaming the helper. Reject: pulling the timeout values into a config file.",
      },
    ],
    prompt: [
      "You are performing a refactor. Your job is to make the requested change and only the requested change, without growing scope and without quietly changing behavior that was not part of the task.",
      "",
      "Refactor boundary:",
      "{refactor_boundary}",
      "",
      "Behavior to preserve:",
      "{behavior_to_preserve}",
      "",
      "Investigation findings (if supplied):",
      "{investigation_findings}",
      "",
      "Repository access:",
      "{repository_access}",
      "",
      "Unrelated cleanup seen along the way:",
      "{unrelated_cleanup_seen}",
      "",
      "Verification plan:",
      "{verification_plan}",
      "",
      "Rejected scope-expansion requests:",
      "{rejected_scope_expansion}",
      "",
      "Produce the following sections, in this order:",
      "1. Boundary restatement -- one short paragraph that restates what is in scope and what is explicitly out of scope, in your own words. If anything in the inputs is ambiguous, list the ambiguity here as an unresolved question rather than guessing.",
      "2. Behavior contract -- the list of externally observable behaviors that must not change. Mark each item as confirmed, assumed, or not-required.",
      "3. Investigation before editing -- the evidence you read before opening the diff. Each inspection item must be labelled either 'performed' (with the actual supplied or observed evidence attached) or 'planned, not performed' (with the file, component, command, test, or repository area named and the action that would be taken once access is available). When repository access is unavailable, refer only to a supplied repository area, a requested path, or a supplied component or module. Never invent a file path.",
      "4. Required changes -- the edits that the refactor must make. Each change must trace to the boundary restatement or the behavior contract. Mark each item as either 'performed' (the actual edit, with the file or component and the change made) or 'planned, not performed' (the exact edit that would be made once the boundary is confirmed). Preserve the exact supplied or observed command or tool name when reproducibility requires it. Do not invent commands or tools.",
      "5. Deferred improvements -- the items from 'unrelated_cleanup_seen' that you noticed but did not touch, each with one sentence on why it stays out of scope. Only items actually supplied or observed belong here; do not invent deferred items from speculation.",
      "6. Targeted verification -- the exact checks you ran, the result of each, and the one thing that would tell you the refactor was not safe to merge. Mark each check as 'performed' (with the actual result) or 'planned, not performed' (with the check that would be run). Preserve the exact supplied or observed command or tool name when reproducibility requires it.",
      "7. Out-of-scope items rejected -- drive-by changes the inputs tempted you toward but you did not make, each labelled with the reason. Drawn from 'rejected_scope_expansion' when supplied, and from any item the boundary explicitly forbids.",
      "8. Human-review gate -- an explicit checklist the reviewer confirms before merge: (a) the refactor boundary matches what was authorized; (b) the changed files are exactly the files named in the diff; (c) the behavior contract is preserved; (d) the verification evidence actually demonstrates the contract is preserved. Each item carries a tick or a 'not confirmed -- [needs decision: <unresolved question>]'.",
      "",
      "Constraints:",
      "- Preserve externally observable behavior unless the inputs explicitly authorize otherwise. When behavior changes are authorized, state each change and the authorization source.",
      "- Separate required changes from unrelated cleanup. Unrelated cleanup belongs in section 5, never in the diff.",
      "- Investigate before editing. Read the affected files or components, the tests that cover them, and the call sites that depend on them. Every inspection item must carry the 'performed' or 'planned, not performed' label. Do not claim a file, component, command, test, or repository area was inspected unless supplied findings or actual repository access supports the claim.",
      "- Distinguish actual edits from proposed edits. Section 4 carries the label on every change. Preserve the exact supplied or observed command or tool name when reproducibility requires it; do not invent commands or tools that the inputs did not supply.",
      "- Identify affected files or components only when the inputs supplied them or your investigation actually opened them. Cite the smallest relevant fragment or area when a precise path is not supplied.",
      "- Require targeted verification before declaring the refactor done. Section 6 names the checks, the result, and the single signal that would have made you stop and reconsider. Each check carries the 'performed' or 'planned, not performed' label.",
      "- Report deferred improvements separately in section 5, each labelled with the reason it is deferred. Section 7 closes the loop on drive-by temptations the writer explicitly rejected, drawn from 'rejected_scope_expansion' or from items the boundary explicitly forbids.",
      "- Stop scope expansion. Reject 'while I am here' changes; they go in section 7, not in section 4.",
      "- Do not invent file paths, line numbers, call sites, tests, or contracts. When the inputs do not give them, name the area in plain language and label the item 'planned, not performed' until the actual evidence is available.",
      "- Use generic tool wording unless an exact command or tool name was supplied or observed and is required for reproducibility. Preserve those names verbatim. Never invent a command, tool, or vendor.",
      "- When any input is missing and the missing piece would change the answer, list it under section 1 as an unresolved question rather than guessing.",
      "- The human-review gate in section 8 is mandatory. The refactor is not safe to merge until every item there is confirmed by an authorized reviewer.",
    ].join("\n"),
    expectedOutput:
      "A refactor work record or plan, with every inspection, edit, and verification item labelled performed or planned, not performed.",
    notes: [
      {
        title: "Why the boundary restatement is the first section",
        body:
          "Refactors fail when the scope grows invisibly. Restating the boundary in the model's own words forces the rest of the plan to either stay inside it or call out the deviation explicitly. The reader can spot drift in section 1 before it lands in section 4.",
      },
      {
        title: "Why deferred improvements get their own section",
        body:
          "Improvements noticed along the way are valuable, but they belong in a follow-up, not in this diff. Putting them in section 5 keeps them visible without letting them expand the change. Section 7 closes the loop on drive-by temptations the writer explicitly rejected.",
      },
    ],
    antiPatterns: [
      {
        title: "Editing code that was not in scope",
        body:
          "Touching call sites, renaming files, reformatting unrelated regions, or fixing small bugs found along the way grows the diff and the review surface. The refactor's job is the boundary; everything else is a follow-up.",
      },
      {
        title: "Quietly changing observable behavior",
        body:
          "Returning a richer error object, reordering log lines, adjusting a default timeout, or simplifying a public method all change behavior callers may rely on. Behavior changes need explicit authorization in the inputs and a separate section in the output, not a quiet edit.",
      },
      {
        title: "Skipping the investigation step",
        body:
          "Refactors based on a one-line task text miss hidden coupling. Reading the affected files, the tests that cover them, and the call sites that depend on them is the cheapest insurance against a refactor that breaks an unrelated path.",
      },
      {
        title: "Claiming verification that did not happen",
        body:
          "Listing 'ran the test suite' without naming which suite, which test, and the result produces a plan that looks safe and is not. Verification has to be specific: which check, what it confirmed, what would have made you stop.",
      },
    ],
    collectionIds: ["builder-bench"],
    sourceReferences: provenance("code-refactor-no-driveby"),
  },

  {
    ...baseEditorial,
    id: "write-incident-postmortem",
    slug: "write-incident-postmortem",
    title: "Blameless incident postmortem from supplied evidence",
    category: "write",
    difficulty: "advanced",
    audience:
      "Engineers, incident commanders, and reliability leads writing a post-incident document after the incident has been declared resolved.",
    useCase:
      "When an incident has been resolved and you need to produce a blameless postmortem that the team, leadership, and downstream stakeholders can trust.",
    inputs: [
      {
        name: "confirmed_incident_summary",
        label: "Confirmed incident summary",
        description:
          "A short factual summary of what happened, restricted to facts the inputs actually confirm. State what is confirmed and what is not. Do not include cause, scope, or impact numbers unless they are confirmed in this input.",
        example:
          "Confirmed: a deploy at 13:40 UTC preceded a period of elevated checkout errors. Not confirmed: that the deploy was the cause, or the exact end of the impact window.",
      },
      {
        name: "customer_or_operational_impact",
        label: "Customer or operational impact",
        description:
          "What users or operators experienced: who was affected, in which regions or segments, for how long, and what they saw. Mark numbers as confirmed or estimated.",
        example:
          "Confirmed: customers in the EU region saw checkout failures for a confirmed window of 36 minutes. Estimated (not confirmed): approximately 12 percent of EU customers were affected. Not observed: any data exposure.",
      },
      {
        name: "evidence_timeline",
        label: "Evidence timeline",
        description:
          "The events the inputs can support, in time order, with the source of each event: alert, log, deploy record, customer report, status page entry, manual action. Where timestamps come from different clocks, state the source.",
        example:
          "13:40 UTC: deploy started (deploy log). 13:42 UTC: error rate alert fired (alerting system). 13:47 UTC: rollback initiated (deploy log). 14:18 UTC: error rate returned to baseline (alerting system).",
      },
      {
        name: "detection_and_response_actions",
        label: "Detection and response actions",
        description:
          "What fired, who acknowledged, who joined, what mitigations were applied, when each happened. Mark each item with its source. Items not in the inputs are absent from the output.",
        example:
          "13:42 alert fired. 13:44 on-call acknowledged. 13:45 incident commander declared. 13:47 rollback initiated. 13:55 communications update posted. 14:18 incident downgraded.",
      },
      {
        name: "confirmed_or_unresolved_cause",
        label: "Confirmed or unresolved cause",
        description:
          "Either a confirmed root cause with the evidence that supports it, or a clear statement that the cause is unresolved, with the working theories and the evidence that would distinguish them. No third option.",
        example:
          "Unresolved. Working theory A: the deploy introduced a regression in checkout validation. Working theory B: an upstream provider change intersected with the deploy. Distinguishing evidence would be: pre-deploy canary results, and provider status for the window.",
      },
      {
        name: "contributing_factors",
        label: "Contributing factors",
        description:
          "The structural or process factors that made the incident more likely, slower to detect, or harder to resolve. Each factor must be supported by something in the inputs.",
        example:
          "Detection relied on a single error-rate threshold with no leading indicator. The rollback runbook assumed a permission the on-call did not have during the window.",
      },
      {
        name: "what_worked_and_what_failed",
        label: "What worked and what failed",
        description:
          "Aspects of the response that worked and aspects that did not. Drawn from the inputs; absent items stay absent.",
        example:
          "Worked: alerting fired within two minutes of impact. Worked: rollback completed within five minutes of decision. Failed: the status page update lagged the actual recovery by twelve minutes.",
      },
      {
        name: "corrective_actions",
        label: "Corrective actions (when supplied)",
        description:
          "Concrete follow-up actions with an owner and a target date when the inputs supply them. Items without a supplied owner or date are listed as '[needs decision: <unresolved question>]'.",
        example:
          "Add a pre-deploy canary for the checkout path (owner: Alice, target: 2026-08-15). Lower the rollback permission scope (owner: [needs decision: <unresolved question>], target: [needs decision: <unresolved question>]).",
      },
      {
        name: "open_questions_and_followup_evidence",
        label: "Open questions and follow-up evidence (when supplied)",
        description:
          "Anything still unresolved, the evidence that would resolve it, and who owns collecting it. When the input is empty, this section still exists and states that no open questions were supplied.",
        example:
          "Open: confirm or rule out upstream provider involvement in the window. Owner: Bob. Evidence needed: provider status report for 13:30 to 14:30 UTC.",
      },
    ],
    prompt: [
      "Write a blameless incident postmortem from the inputs below.",
      "Use only what the inputs supply. Where the inputs do not supply a fact, state that the fact is 'not supplied'. Never infer 'none' or 'not observed' for impact window, user impact, or data exposure. Every material timestamp, number, impact statement, causal claim, contributing factor, and corrective action must cite a supplied source identifier or say 'source not supplied'. The summary reflects the evidence available for the current draft. If later review changes the cause state, update the summary before reuse.",
      "",
      "Confirmed incident summary:",
      "{confirmed_incident_summary}",
      "",
      "Customer or operational impact:",
      "{customer_or_operational_impact}",
      "",
      "Evidence timeline:",
      "{evidence_timeline}",
      "",
      "Detection and response actions:",
      "{detection_and_response_actions}",
      "",
      "Confirmed or unresolved cause:",
      "{confirmed_or_unresolved_cause}",
      "",
      "Contributing factors:",
      "{contributing_factors}",
      "",
      "What worked and what failed:",
      "{what_worked_and_what_failed}",
      "",
      "Corrective actions (when supplied):",
      "{corrective_actions}",
      "",
      "Open questions and follow-up evidence (when supplied):",
      "{open_questions_and_followup_evidence}",
      "",
      "Produce the following sections, in this order:",
      "1. Executive summary -- two or three sentences that stand on their own. State the impact window, the user-visible effect, and the current state of the root cause (confirmed, working theory, or unresolved). The summary reflects the evidence available for the current draft. If later review changes the cause state, update the summary before reuse.",
      "2. Impact -- who was affected, in which regions or segments, for how long, what they saw, and whether any data was exposed. For impact window, user impact, and data exposure, if the inputs do not supply the fact, write 'not supplied' rather than inferring 'none' or 'not observed'. Mark each number as confirmed or estimated, and cite the supplied source identifier for each material claim.",
      "3. Timeline -- the evidence-based timeline, in time order, with each event labelled by its source. Do not invent timestamps. Where timestamps come from different clocks, state the source. Each event carries the supplied source identifier.",
      "4. Detection and response -- a summary of who acknowledged, who joined, and what mitigations were applied, in time order. The full chronology lives in section 3; this section summarizes and references timeline events (for example: 'rollback at 13:47 UTC, see timeline entry 3') instead of restating timestamps. Each action carries the supplied source identifier.",
      "5. Root cause -- either a confirmed cause with the evidence that supports it, or a clear statement that the cause is unresolved, with the working theories and the evidence that would distinguish them. Cite the supplied source identifier for every causal claim.",
      "6. Contributing factors -- the structural or process factors that made the incident more likely, slower to detect, or harder to resolve. Each factor must be supported by something in the inputs and must cite the supplied source identifier.",
      "7. What worked and what failed -- the parts of the response that worked and the parts that did not, drawn only from the inputs. Cite the supplied source identifier.",
      "8. Corrective actions -- concrete follow-up actions. Each action with an owner and a target date when the inputs supplied them; otherwise mark '[needs decision: <unresolved question>]'. Cite the supplied source identifier.",
      "9. Open questions and follow-up evidence -- anything still unresolved, the evidence that would resolve it, and who owns collecting it. When the inputs supply nothing, state explicitly that no open questions were supplied.",
      "10. Resolution status -- an explicit statement of whether the incident is resolved. Do not describe the incident as resolved unless the inputs supply that status or an authorized incident lead has confirmed it. When the inputs do not supply a resolution status, write 'resolution status: not supplied'.",
      "",
      "Constraints:",
      "- Do not invent timestamps, causes, owners, metrics, regions, customer counts, or certainty. Every number or attribution must trace to a supplied input.",
      "- For impact window, user impact, and data exposure, write 'not supplied' when the inputs do not give the fact. Never infer 'none' or 'not observed'.",
      "- Every material timestamp, number, impact statement, causal claim, contributing factor, and corrective action must cite a supplied source identifier or say 'source not supplied'. The summary rule in section 1 binds the executive summary to the same citation discipline.",
      "- Detection and response (section 4) summarizes and references timeline events; it does not duplicate the chronology from section 3.",
      "- Individual actions may be causally relevant, but record them factually. Do not claim character, intent, motivation, or judgement about any person or team.",
      "- Analyze the system conditions that are supported by the inputs (configuration, deployment, telemetry, runbook state). Do not assign cause to personality or intent.",
      "- Do not describe the incident as resolved unless the inputs supply that status or an authorized incident lead has confirmed it. When unresolved, the document is a draft until confirmation.",
      "- Assign no blame to any individual or team. Describe actions and decisions, not character or intent.",
      "- Use 'confirmed', 'estimated', 'working theory', 'unresolved', 'not supplied', and 'source not supplied' as the honest labels for non-trivial claims. Do not introduce other labels.",
      "- When a corrective action is listed without a supplied owner or target date, mark it '[needs decision: <unresolved question>]'. Do not invent dates or assignees.",
      "- Distinguish facts from assumptions in the executive summary. The summary reflects the evidence available for the current draft. If later review changes the cause state, update the summary before reuse.",
      "- Use supplied source identifiers verbatim. Otherwise use generic tool wording and do not invent vendor names.",
      "- The postmortem is a draft until an authorized reviewer confirms the evidence and the corrective actions. Treat the output as a proposal for review.",
    ].join("\n"),
    expectedOutput:
      "A blameless postmortem with the ten labeled sections. The executive summary stands on its own, labels the cause state honestly, and reflects the evidence available for this draft. The timeline contains only events whose source is in the inputs, with timestamps attached to their source identifier. The detection-and-response section summarizes and references timeline events instead of duplicating them. The root-cause section is either confirmed with supporting evidence or clearly unresolved with the working theories. Corrective actions carry owners and target dates only when the inputs supplied them; missing items are '[needs decision: <unresolved question>]'. Section 10 states the resolution status as confirmed by the inputs or an authorized incident lead, or as 'not supplied'. No invented timestamps, causes, owners, metrics, certainty, 'none', or 'not observed' for impact window, user impact, or data exposure.",
    notes: [
      {
        title: "Why six honest labels instead of one",
        body:
          "Postmortems drift toward either over-confident summaries that have to be walked back later, or vague 'under investigation' language that hides what is actually known. The six honest labels -- 'confirmed', 'estimated', 'working theory', 'unresolved', 'not supplied', and 'source not supplied' -- force the writer to declare what kind of evidence backs each claim. 'confirmed' and 'estimated' apply when the inputs supply the value; 'working theory' and 'unresolved' apply when the cause is not yet pinned down; 'not supplied' applies when the inputs do not give the fact; 'source not supplied' applies when a citation is required but the inputs do not identify the source. Mixing the labels, or inventing others, is what produces posts that have to be walked back.",
      },
      {
        title: "Why owners and dates belong in the inputs, not in the writer",
        body:
          "A postmortem that invents owners and target dates produces a follow-up plan that has to be re-checked by every named person. Pulling owners and dates from the inputs keeps the action list attributable, and '[needs decision: <unresolved question>]' keeps the gap visible until a real owner is named.",
      },
    ],
    antiPatterns: [
      {
        title: "Inventing timestamps to make the timeline flow",
        body:
          "Filling in timestamps the inputs did not supply produces a timeline that reads cleanly and is wrong about key facts. If a timestamp is missing, state that it is missing and name the source that should have it.",
      },
      {
        title: "Naming a root cause to feel complete",
        body:
          "A confident root cause in the executive summary, written before the evidence is in, produces a public statement that has to be walked back. If the cause is not confirmed, say so and list the working theories with the evidence that distinguishes them.",
      },
      {
        title: "Individual actions and system conditions",
        body:
          "Record individual actions factually when supported, without character, intent, or motivation claims. Analyze the supplied system conditions as the primary context.",
      },
      {
        title: "Writing the postmortem before the incident is resolved",
        body:
          "Generating a 'postmortem' inside the first hour of an incident produces a plausible-looking artifact that is wrong about key facts. A postmortem is an evidence-based document that may include confirmed facts, estimates, working theories, unresolved questions, and missing-source labels. During active response, use a status update rather than presenting the postmortem draft as final.",
      },
    ],
    collectionIds: ["operator-playbook"],
    sourceReferences: provenance("write-incident-postmortem"),
  },

  {
    ...baseEditorial,
    id: "research-source-triangulate",
    slug: "research-source-triangulate",
    title: "Triangulate a research question across independent sources",
    category: "research",
    difficulty: "intermediate",
    audience:
      "Researchers, analysts, and engineers who need to answer a factual question where the answer depends on which sources are reliable.",
    useCase:
      "When you have a research question and the inputs include one or more sources, and you need to compare them, weight them, and surface what is actually supported versus what is asserted.",
    inputs: [
      {
        name: "research_question",
        label: "Research question",
        description:
          "The question to answer, stated precisely enough that it can be broken into concrete claims. Avoid questions that depend on access the inputs do not supply.",
        example:
          "What is the current state of evidence on whether intermittent fasting reduces average blood pressure in adults without diagnosed hypertension.",
      },
      {
        name: "candidate_claims",
        label: "Candidate claims",
        description:
          "The claims the research question breaks into. Each claim should be a single, falsifiable statement. The triangulation will treat each claim separately.",
        example:
          "Claim 1: intermittent fasting reduces average systolic blood pressure by at least 3 mmHg in adults without diagnosed hypertension. Claim 2: the effect is observed in randomized trials but not in observational studies. Claim 3: the effect persists at 12-month follow-up.",
      },
      {
        name: "supplied_sources",
        label: "Supplied sources",
        description:
          "The sources the inputs provide, with enough detail to identify them: author or organization, year, type (primary, secondary, meta-analysis, blog, vendor report), and any access notes. When the input is empty, no sources are available and the prompt must say so.",
        example:
          "Source A: peer-reviewed randomized trial, 2024, primary. Source B: systematic review, 2023, secondary. Source C: industry blog post, 2025, secondary, vendor-attached.",
      },
      {
        name: "access_constraints",
        label: "Access constraints",
        description:
          "Anything that limits what can actually be checked: paywalls, language, recency requirements, missing citations, or restrictions on contacting authors. Used to mark claims as unsupported because of access, not because of evidence.",
        example:
          "Two of the supplied sources are abstracts only. One citation is incomplete and cannot be verified.",
      },
      {
        name: "uncertainty_or_unknowns",
        label: "Uncertainty or unknowns",
        description:
          "Areas where the researcher already knows the evidence is thin, contested, or missing. The triangulation should preserve these and not paper over them.",
        example:
          "Long-term effects beyond 24 months are not well covered in the supplied sources.",
      },
    ],
    prompt: [
      "You are triangulating a research question across the supplied sources.",
      "Your job is to break the question into concrete claims, compare what each source actually says, and surface what is supported, what is contested, and what is missing. You do not have access to sources outside the inputs. Never invent a quotation, citation, publication detail, or access to material the inputs do not provide.",
      "",
      "Research question:",
      "{research_question}",
      "",
      "Candidate claims:",
      "{candidate_claims}",
      "",
      "Supplied sources:",
      "{supplied_sources}",
      "",
      "Access constraints:",
      "{access_constraints}",
      "",
      "Uncertainty or unknowns:",
      "{uncertainty_or_unknowns}",
      "",
      "Produce the following sections, in this order:",
      "1. Question restatement -- the research question in one sentence, in your own words, plus the boundaries (population, scope, time window) drawn from the inputs.",
      "2. Claim breakdown -- the candidate claims, numbered, each a single falsifiable statement.",
      "3. Source register -- a table or list of the supplied sources, each with identifier, type (primary, secondary, meta-analysis, vendor report, blog), year, and a one-line note on recency, authority, directness, and any visible conflict of interest. For each source, also note the evidence family it belongs to (study, dataset, filing, press release, citation chain, controlled authorship chain, or controlled funding chain). Sources that share an evidence family do not count as independent corroboration.",
      "4. Per-claim evidence map -- for each claim, the sources that address it and the per-source classification: Supports, Qualifies, Contradicts, or Not assessable. Each classification cites the source identifier and the exact item in the source that supports it (a section, a table, a quote location, or 'unspecified' when the inputs do not give it).",
      "5. Cross-source independence check -- for each claim with two or more sources, an explicit check on whether the sources are independent. Sources do not count as independent corroboration when they derive from the same study, dataset, filing, press release, citation chain, controlled authorship chain, or controlled funding chain. Compare independent evidence families, not raw document counts.",
      "6. Per-claim triangulation -- for each claim, the resulting label after the independence check: supported (independent corroboration), partially supported (one source or non-independent family only), contested (independent sources disagree), unsupported (no source supports it), or insufficient evidence (sources address it but the data is thin).",
      "7. Source-quality assessment -- for each source, a brief read on recency, authority (peer review, institutional, vendor, blog), directness (does the source itself report the evidence, or does it cite another source), and any visible conflict of interest.",
      "8. Single-family and single-source limitations -- every claim that relies on a single source or a single evidence family, stated honestly with the limitation. Do not paper over the single-source dependency.",
      "9. Missing evidence and access gaps -- the claims that the inputs cannot support, the access constraints that explain the gap, and the kind of source that would resolve each gap.",
      "10. Claim-level citations -- for each claim, the source identifiers (for example: 'Source A', 'Source B') that support it, with the per-source classification. Where no source supports a claim, mark it 'unsupported'.",
      "11. Honest answer to the research question -- a short answer that reflects the supported, contested, and unsupported parts of the evidence. The answer preserves uncertainty and does not collapse it.",
      "",
      "Constraints:",
      "- Prioritize primary sources. Treat secondary and tertiary sources as summaries of primary sources, not as the final word.",
      "- Compare independent evidence families, not raw document counts. Two sources from the same study, dataset, filing, press release, citation chain, controlled authorship chain, or controlled funding chain are not independent corroboration; they are a single family.",
      "- Document single-family and single-source limitations honestly. When a claim rests on a single source or a single family, say so and reduce the claim's confidence accordingly.",
      "- Use 'Supports', 'Qualifies', 'Contradicts', or 'Not assessable' as the per-source classification. Do not introduce other classifications.",
      "- Separate agreement, disagreement, and missing evidence into different sections. Do not let 'missing' silently turn into 'contested'.",
      "- Preserve uncertainty. Use 'supported', 'partially supported', 'contested', 'unsupported', and 'insufficient evidence' as the honest labels. Do not collapse them.",
      "- Never fabricate a quotation, citation, publication detail, author affiliation, year, or claim of access to material the inputs do not provide.",
      "- Where a source itself cites another source, follow the citation only when the primary source is also in the inputs. Otherwise flag the chain as indirect and note the citation chain as the evidence family.",
      "- For each source, note recency, authority, directness, conflicts of interest, and the evidence family it belongs to. State these even when the source looks reliable; the reader is the one who weighs them.",
      "- Use generic tool wording unless an exact command, tool, source identifier, or vendor name was supplied or observed and is required for reproducibility. Preserve those names verbatim. Never invent a command, tool, or vendor.",
      "- The triangulation is a draft until the researcher verifies the citations and the access constraints. Treat the output as a proposal for review.",
    ].join("\n"),
    expectedOutput:
      "A triangulation with the eleven labeled sections. The claim breakdown is concrete and falsifiable. The source register names each supplied source with type, year, evidence family, and quality notes. The per-claim evidence map classifies every relevant source as Supports, Qualifies, Contradicts, or Not assessable with the supporting item cited. The cross-source independence check explicitly flags sources that share an evidence family and refuses to count them as independent corroboration. Single-family and single-source limitations are stated honestly. The honest answer in section 11 reflects the actual evidence and preserves the gaps. No invented quotation, citation, publication detail, or access to material the inputs did not provide.",
    notes: [
      {
        title: "Why the claim breakdown comes before the source register",
        body:
          "Triangulation drifts when the writer reads sources first and then frames the question to fit what the sources happened to say. Breaking the question into claims before reading the sources forces the sources to address the question rather than the other way around.",
      },
      {
        title: "Why unsupported and insufficient evidence are separate labels",
        body:
          "An unsupported claim and an insufficiently evidenced claim look similar but mean different things. Unsupported means the supplied sources do not address it; insufficient evidence means the sources address it but the data is thin. Collapsing the two hides where the real work needs to happen.",
      },
    ],
    antiPatterns: [
      {
        title: "Quoting sources the inputs did not provide",
        body:
          "Writing 'according to a 2024 meta-analysis' when the inputs did not supply one produces a triangulation that reads like research and is not. Quote only what the inputs actually supplied, and mark the source identifier next to every claim.",
      },
      {
        title: "Collapsing contested and supported into a single answer",
        body:
          "Producing a confident paragraph that smooths over disagreement between sources produces a research output that is wrong about the evidence. The honest answer section has to reflect the disagreement, not absorb it.",
      },
      {
        title: "Treating a single source as confirmation",
        body:
          "A single source, however authoritative, is not triangulation. When only one source addresses a claim, label the claim 'unsupported by additional sources' and note the gap, even if the one source is strong.",
      },
      {
        title: "Skipping the source-quality assessment",
        body:
          "Listing what each source says without assessing its recency, authority, directness, and conflicts of interest produces a triangulation the reader cannot weigh. The assessment is what lets the reader apply their own judgement to the answer.",
      },
    ],
    collectionIds: ["research-desk"],
    sourceReferences: provenance("research-source-triangulate"),
  },

  {
    ...baseEditorial,
    id: "decide-pre-mortem",
    slug: "decide-pre-mortem",
    title: "Pre-mortem that turns a decision into named, testable failure modes",
    category: "decide",
    difficulty: "advanced",
    audience:
      "Decision makers, product leads, and engineers about to commit to a course of action where the failure modes are not yet visible.",
    useCase:
      "When a decision has been proposed and you need to think through how it could fail before committing to it, in a way the team can actually act on.",
    inputs: [
      {
        name: "proposed_decision",
        label: "Proposed decision",
        description:
          "The decision under consideration, stated as a concrete commitment rather than a direction. Include the scope, the timing, and the reversibility class (reversible, partially reversible, irreversible).",
        example:
          "Adopt vendor X as the primary identity provider for the EU region by 2026-09-01, with a 90-day parallel-run period. Reversibility: partially reversible (data export exists, but session migration is one-way).",
      },
      {
        name: "context_and_assumptions",
        label: "Context and assumptions",
        description:
          "The context the decision sits in and the assumptions that the decision rests on. Each assumption should be testable. Mark which assumptions are confirmed and which are assumed.",
        example:
          "Confirmed: vendor X is on the approved vendor list. Assumed: vendor X meets our latency budget in the EU region. Assumed: parallel-run coverage is sufficient to catch session-loss regressions.",
      },
      {
        name: "known_risk_register",
        label: "Known risk register (when supplied)",
        description:
          "Risks the team has already named. The pre-mortem should build on these rather than duplicate them. When the input is empty, the pre-mortem starts from scratch.",
        example:
          "Already named: vendor lock-in, data residency in the EU, cost increase at the next renewal.",
      },
      {
        name: "available_signals_and_instruments",
        label: "Available signals and instruments",
        description:
          "The signals, dashboards, runbooks, or experiments the inputs name as available for monitoring the decision after it lands. When the input is empty, no instruments are assumed.",
        example:
          "Signals supplied: error rate, login latency p95, support ticket volume, weekly sync with vendor X.",
      },
      {
        name: "decision_gates_and_stop_conditions",
        label: "Decision gates and stop conditions (when supplied)",
        description:
          "Any pre-committed gates at which the decision must be re-evaluated, and any stop conditions that would trigger a halt or rollback. When the input is empty, the prompt must propose candidate gates and stop conditions, each marked '[needs decision: <unresolved question>]'.",
        example:
          "Gate at 30 days: re-evaluate against the original assumptions. Stop condition: error rate above baseline plus 2 percent for any consecutive 24 hours.",
      },
    ],
    prompt: [
      "You are running a pre-mortem on a proposed decision.",
      "Assume the decision failed. Your job is to generate distinct, plausible failure modes, weight them, name the leading indicators that would tell you they are happening, and propose proportionate mitigations. Distinguish reversible from irreversible risks. Do not present speculative risks as facts.",
      "",
      "Proposed decision:",
      "{proposed_decision}",
      "",
      "Context and assumptions:",
      "{context_and_assumptions}",
      "",
      "Known risk register (when supplied):",
      "{known_risk_register}",
      "",
      "Available signals and instruments:",
      "{available_signals_and_instruments}",
      "",
      "Decision gates and stop conditions (when supplied):",
      "{decision_gates_and_stop_conditions}",
      "",
      "Produce the following sections, in this order:",
      "1. Decision restatement -- the proposed decision in one paragraph, in your own words, including scope, timing, and reversibility class.",
      "2. Assumptions to validate -- the assumptions the decision rests on, each labelled confirmed or assumed, with the test that would validate each assumed one.",
      "3. Failure modes -- distinct, plausible failure modes the decision could produce. Each failure mode is a single scenario, not a theme. No duplicate wording. Each failure mode is labelled with reversibility (reversible, partially reversible, irreversible).",
      "4. Per-failure-mode assessment -- for each failure mode: likelihood (low, medium, high, unknown), impact (low, medium, high, unknown), detectability (low, medium, high, unknown), and time horizon (days, weeks, months, quarters, unknown). Detectability is defined as: high = likely to be detected early; low = likely to remain hidden. When any rating rests on the inputs, mark it 'input-grounded'; when the rating rests on inference or judgement in the absence of input evidence, mark it 'speculative'. 'unknown' is the honest label when evidence is insufficient.",
      "5. Leading indicators -- the signals that would tell you each failure mode is happening, with the supplied instrument that would surface them. When no instrument is supplied, name the signal category to monitor without naming a specific tool.",
      "6. Mitigations -- proportionate mitigations for each failure mode, matched to reversibility. Reversible risks get fast-detection and rollback-oriented mitigations; irreversible risks get prevention-oriented mitigations. Partially reversible risks get a separate treatment per the next section.",
      "7. Partially reversible and irreversible risks -- for every partially reversible or irreversible risk, three sub-sections: (a) containment -- the actions that limit the blast radius once the failure mode begins; (b) residual harm after rollback -- the part of the harm that survives a successful rollback or stop; (c) prevention -- the actions taken before the point of no return that reduce the irreversible portion. For every partially reversible or irreversible risk, also identify: (d) the point of no return -- the event or commitment after which rollback cannot undo the harm; (e) the last pre-commit decision gate -- the latest moment the decision can be halted before the point of no return.",
      "8. Reversible vs irreversible -- a short section that names the irreversible risks separately, with the reason each is irreversible and the gate that would still allow the decision to be stopped.",
      "9. Decision gates -- the gates at which the decision must be re-evaluated, drawn from the inputs when supplied; otherwise proposed candidates, each marked '[needs decision: <unresolved question>]'.",
      "10. Stop conditions -- the conditions that would trigger a halt or rollback, drawn from the inputs when supplied; otherwise proposed candidates, each marked '[needs decision: <unresolved question>]'.",
      "11. Open assumptions requiring validation -- the assumptions the decision rests on that are not yet confirmed, with the validation step that would confirm each one.",
      "",
      "Constraints:",
      "- Assume the proposed decision failed. Generate failure modes from that assumption, not from a generic risk template.",
      "- Generate distinct failure modes. Do not phrase the same risk in two different ways. If two failure modes overlap, merge them.",
      "- Assess likelihood, impact, detectability, and time horizon for each failure mode. Use the same scale for all failure modes, and use 'unknown' when evidence is insufficient. Distinguish input-grounded ratings from speculative estimates.",
      "- Identify leading indicators for each failure mode. When no instrument is supplied, name the signal category (for example: 'error rate', 'login latency', 'support ticket volume', 'vendor status reports') without naming a specific tool.",
      "- Distinguish reversible from irreversible risks. Apply the matching mitigation style to each. Partially reversible risks require a separate containment / residual harm / prevention treatment plus the point of no return and the last pre-commit decision gate.",
      "- Identify decision gates and stop conditions. When the inputs supply none, propose candidates and mark each '[needs decision: <unresolved question>]'.",
      "- Avoid presenting speculative risks as facts. Phrase speculative risks as 'this could happen if ...' and tie them to a specific assumption that would have to be true.",
      "- Do not invent vendor, metric, dashboard, owner, or organizational authority. When something is missing, mark it '[needs decision: <unresolved question>]'.",
      "- Use generic tool wording unless an exact command, tool, source identifier, or vendor name was supplied or observed and is required for reproducibility. Preserve those names verbatim. Never invent a command, tool, or vendor.",
      "- The pre-mortem is a draft until the decision maker confirms the gates, the stop conditions, the point-of-no-return definitions, and the assumption-validation steps. Treat the output as a proposal for review.",
    ].join("\n"),
    expectedOutput:
      "A pre-mortem with the eleven labeled sections. The decision restatement captures scope, timing, and reversibility. Failure modes are distinct and not duplicates; each carries likelihood, impact, detectability (defined as 'high = likely detected early; low = likely remains hidden'), time horizon, and a reversibility label. Each rating is marked 'input-grounded' or 'speculative', and 'unknown' is used when evidence is insufficient. Section 7 gives partially reversible and irreversible risks a separate treatment: containment, residual harm after rollback, and prevention, plus the point of no return and the last pre-commit decision gate. Section 8 separates the irreversible risks with the gates that would still allow stopping. Decision gates and stop conditions are present and labelled '[needs decision: <unresolved question>]' when the inputs supplied none. Speculative risks are tied to assumptions. No invented vendor, metric, dashboard, owner, or organizational authority.",
    notes: [
      {
        title: "Why assume the decision failed",
        body:
          "Pre-mortems work because they bypass the social cost of naming a risk. Asking 'how could this fail' in a room where the decision has just been defended produces polite answers. Asking 'imagine a year from now it failed: what happened' produces a concrete failure mode the team can address.",
      },
      {
        title: "Why reversibility drives the mitigation style",
        body:
          "Reversible risks can be addressed with detection and rollback; irreversible risks can only be addressed with prevention. A mitigation that is appropriate for a reversible risk (a slow rollout, a flag, a rollback) is not appropriate for an irreversible one (a data migration, a public commitment, a regulatory filing). The reversibility label is what makes the mitigation proportionate.",
      },
    ],
    antiPatterns: [
      {
        title: "Generating the same risk in two wordings",
        body:
          "Listing 'vendor lock-in' and 'switching cost is high' as separate failure modes inflates the failure-mode count without adding information. Merge them into a single failure mode with a clear scenario.",
      },
      {
        title: "Presenting speculative risks as facts",
        body:
          "Writing 'vendor X will raise prices at renewal' as a confident failure mode hides the assumption that prices are negotiable or that vendor X has signalled a change. Speculative risks must be tied to a specific assumption that would have to be true.",
      },
      {
        title: "Skipping the irreversible-risk callout",
        body:
          "Treating all failure modes as reversible and assuming rollback will work hides the failures that rollback cannot fix. A pre-mortem that does not separate the irreversible risks has not done its job.",
      },
      {
        title: "Inventing gates and stop conditions without flagging them",
        body:
          "Naming a 30-day gate and a stop condition as if they were committed, when the inputs did not supply them, produces a pre-mortem that looks finalized and is not. Mark uncommitted gates and stop conditions '[needs decision: <unresolved question>]' so the decision maker owns the commitment.",
      },
    ],
    collectionIds: ["decision-room"],
    sourceType: "openradar-rewrite",
    sourceReferences: publicFrameworkRewriteProvenance(),
  },

  {
    ...baseEditorial,
    id: "operate-auto-rollback-conditions",
    slug: "operate-auto-rollback-conditions",
    title: "Auto-rollback policy proposal with named signals and thresholds",
    category: "operate",
    difficulty: "advanced",
    audience:
      "Reliability engineers, SREs, and on-call leads drafting an automatic rollback policy for a deploy, a feature flag, or an infrastructure change.",
    useCase:
      "When you are about to commit to an automatic rollback for a change and you need a policy proposal that names the signals, thresholds, evaluation windows, and overrides before the change ships.",
    inputs: [
      {
        name: "change_under_rollback",
        label: "Change under rollback",
        description:
          "The change the rollback policy applies to: what is being deployed, what region or segment is affected, what time window the rollback must work in, and what the rollback path is (deploy revert, flag flip, traffic shift, infra teardown).",
        example:
          "Deploy of checkout service v3.2.0 to the EU region. Rollback path: revert to v3.1.4 via the deploy tool. Expected rollback time: under 90 seconds from signal.",
      },
      {
        name: "authorization_scope",
        label: "Authorization scope",
        description:
          "Who is authorized to approve or execute rollback for this change, and the scope of that authorization (single-region, all-regions, partial). When empty or stale, the policy must NOT classify rollback as automatic; automatic rollback requires supplied authorization scope AND supplied rollback feasibility.",
        example:
          "Authorized rollback approver: on-call incident commander. Scope: EU region only. Approver must be reachable within the evaluation window. Escalation: VP Engineering after 3 overrides in 24 hours.",
      },
      {
        name: "known_good_rollback_target",
        label: "Known-good rollback target",
        description:
          "The specific version, configuration, or flag state the rollback returns the system to. Must be supplied for the policy to be classifiable as automatic; missing or stale target means the policy is manual-only.",
        example:
          "Rollback target: checkout service v3.1.4 with feature flag checkout_v3 disabled. Verified last at 2026-07-15 deployment.",
      },
      {
        name: "schema_and_state_compatibility",
        label: "Schema and state compatibility",
        description:
          "Any schema, migration, or state-compatibility constraint between the current version and the rollback target. New columns, removed columns, irreversible migrations, or one-way data migrations are noted here.",
        example:
          "v3.2.0 introduced the 'cart_id_v2' column. v3.1.4 does not read this column; rollback is safe as long as no in-flight writes depend on it. No irreversible migrations between v3.1.4 and v3.2.0.",
      },
      {
        name: "forward_only_or_destructive",
        label: "Forward-only or destructive operations",
        description:
          "Any forward-only or destructive operation that has already run and cannot be reversed by the rollback (data deletion, one-way encryption, third-party side effects).",
        example:
          "Forward-only: 1.2 million checkout sessions migrated to the v3 schema. A rollback to v3.1.4 keeps the migrated data but the legacy readers in v3.1.4 will not see it.",
      },
      {
        name: "dependent_changes",
        label: "Dependent changes",
        description:
          "Other services, flags, config maps, or downstream systems that move with this change, and whether each dependent change is included in the rollback path.",
        example:
          "Tightly coupled: the payments service reads the same checkout flag. Not coupled: the account-login service.",
      },
      {
        name: "blast_radius_limit",
        label: "Blast-radius limit",
        description:
          "The maximum region, segment, or percentage of traffic that an automatic rollback may touch, beyond which the action must escalate to manual.",
        example:
          "Automatic rollback is limited to the EU region and 100 percent of EU traffic. Cross-region rollback requires manual approval.",
      },
      {
        name: "max_automatic_attempts",
        label: "Maximum automatic attempts",
        description:
          "The maximum number of automatic rollback attempts within a defined window, beyond which further automatic action halts and escalation begins. When empty, do NOT propose a default; mark the policy as manual-only and add a '[needs decision: ...]' entry per the policy rules.",
        example:
          "Maximum automatic attempts: 1 per 30 minutes per change. After 1 automatic attempt, further action halts and the on-call is paged.",
      },
      {
        name: "stop_conditions_supplied",
        label: "Stop conditions (when supplied)",
        description:
          "Conditions under which further automatic action halts, including cooldown expiry, max-attempts reached, telemetry-suppression triggered, or rollback verification failed or inconclusive.",
        example:
          "Stop after one automatic attempt. Stop when telemetry is missing for more than 2 minutes. Stop when rollback verification is inconclusive.",
      },
      {
        name: "escalation_or_incident_response_path",
        label: "Escalation or incident-response path",
        description:
          "The path that receives the page when automatic rollback halts: who is paged, the channel, and the incident-response procedure that follows.",
        example:
          "Page on-call engineer via the paging system. Channel: incident channel. Procedure: declare incident if not already declared; follow the runbook for unresolved rollback.",
      },
      {
        name: "monitored_signals_supplied",
        label: "Monitored signals (when supplied)",
        description:
          "The signals the inputs name as available for monitoring the change. For each: the metric or log, the source, the freshness, and any known noise. When the input is empty, the prompt names signal categories without inventing specific metrics or dashboards.",
        example:
          "Error rate per minute (5-minute windows). Login latency p95. Support ticket volume. Synthesized checkout flow success rate.",
      },
      {
        name: "thresholds_supplied",
        label: "Thresholds (when supplied)",
        description:
          "Any thresholds the inputs already commit to. When the input is empty, do not propose a numeric threshold. Mark the required comparator, direction, unit, scope, baseline, and trigger class as unresolved decisions; keep the policy manual-only where the missing threshold affects safe automatic operation.",
        example:
          "Error rate above baseline plus 2 percent for two consecutive minutes. Login latency p95 above 1500 ms for two consecutive minutes.",
      },
      {
        name: "evaluation_window_supplied",
        label: "Evaluation window (when supplied)",
        description:
          "The window over which a signal must breach before triggering, and the minimum sample or traffic required for the signal to be considered meaningful. When the input is empty, do not propose numeric windows or minimum samples. Mark each missing window, persistence, sample, freshness, stabilization, and low-traffic rule as an unresolved decision.",
        example:
          "Two consecutive one-minute windows. Minimum traffic: 100 checkouts per minute in the affected region.",
      },
      {
        name: "data_quality_checks_supplied",
        label: "Data-quality checks (when supplied)",
        description:
          "Conditions under which the signal itself is suspect: missing data, partial collection, deploy in progress, known noisy window. Missing, stale, partial, or unreliable telemetry suspends automatic action and triggers alert or manual escalation. Missing telemetry must never be interpreted as healthy.",
        example:
          "Suppress evaluation when the alerting system reports missing data for the region. Suppress evaluation during a deploy in progress.",
      },
      {
        name: "false_positive_safeguards",
        label: "False-positive safeguards (when supplied)",
        description:
          "Cool-down rules, hysteresis, confirmation steps, or persistence rules the inputs commit to. When the input is empty, do not propose numeric cooldown, hysteresis, confirmation, or persistence values. Mark each missing safeguard as an unresolved decision.",
        example:
          "Persist the trigger across two consecutive windows. Cool-down: do not auto-rollback more than once per 30 minutes.",
      },
      {
        name: "rollback_verification_steps",
        label: "Rollback verification (when supplied)",
        description:
          "The checks that confirm the rollback actually fixed the signal. If verification fails or is inconclusive, halt further automatic attempts and enter the supplied escalation or incident-response path.",
        example:
          "After rollback, wait 5 minutes, then confirm error rate returned to baseline. If not, halt and escalate.",
      },
      {
        name: "manual_override_and_escalation",
        label: "Manual override and escalation (when supplied)",
        description:
          "Who can override the auto-rollback, who must be notified, and the escalation path when the override is used or when auto-rollback is disabled.",
        example:
          "Override: on-call engineer. Notification: incident commander and change owner. Escalation: VP Engineering after 3 overrides in 24 hours.",
      },
      {
        name: "audit_trail_and_communication",
        label: "Audit trail and communication (when supplied)",
        description:
          "What must be recorded when the auto-rollback fires, and who is notified beyond the immediate responders. Audit and communications describe required future events and recipients; they must not claim notifications were sent or verification was completed.",
        example:
          "Record: trigger signal, threshold breach timestamp, rollback initiation timestamp, verification result. Notify: change owner, incident commander, status page.",
      },
    ],
    prompt: [
      "You are drafting an automatic rollback policy for the change described below.",
      "Your job is to name the signals, the thresholds, the evaluation window, the data-quality checks, the false-positive safeguards, the boundary between automatic and manual rollback, the override path, and the audit and communication requirements. Use only what the inputs supply. Where a value is required but the inputs do not provide it, write '[needs decision: <unresolved question>]'. Do not invent dashboards, metrics, thresholds, commands, services, owners, or organizational authority. Do not invent numeric candidates for thresholds, evaluation windows, samples, persistence, freshness, low-traffic rules, safeguards, or trigger values; mark them as unresolved decisions.",
      "",
      "Authority boundary: This output does not grant authority, configure automation, invoke a rollback, or claim that any rollback, notification, audit event, or verification occurred.",
      "",
      "Change under rollback:",
      "{change_under_rollback}",
      "",
      "Authorization scope:",
      "{authorization_scope}",
      "",
      "Known-good rollback target:",
      "{known_good_rollback_target}",
      "",
      "Schema and state compatibility:",
      "{schema_and_state_compatibility}",
      "",
      "Forward-only or destructive operations:",
      "{forward_only_or_destructive}",
      "",
      "Dependent changes:",
      "{dependent_changes}",
      "",
      "Blast-radius limit:",
      "{blast_radius_limit}",
      "",
      "Maximum automatic attempts:",
      "{max_automatic_attempts}",
      "",
      "Stop conditions (when supplied):",
      "{stop_conditions_supplied}",
      "",
      "Escalation or incident-response path:",
      "{escalation_or_incident_response_path}",
      "",
      "Monitored signals (when supplied):",
      "{monitored_signals_supplied}",
      "",
      "Thresholds (when supplied):",
      "{thresholds_supplied}",
      "",
      "Evaluation window (when supplied):",
      "{evaluation_window_supplied}",
      "",
      "Data-quality checks (when supplied):",
      "{data_quality_checks_supplied}",
      "",
      "False-positive safeguards (when supplied):",
      "{false_positive_safeguards}",
      "",
      "Rollback verification (when supplied):",
      "{rollback_verification_steps}",
      "",
      "Manual override and escalation (when supplied):",
      "{manual_override_and_escalation}",
      "",
      "Audit trail and communication (when supplied):",
      "{audit_trail_and_communication}",
      "",
      "Produce the following sections, in this order:",
      "1. Change summary -- the change the policy applies to, including the rollback path and the expected rollback time. One paragraph.",
      "2. Rollback feasibility, authorization, and automatic-classification gate -- whether the policy is classifiable as automatic or only as manual. Automatic classification requires every material feasibility and governance input to be supplied without conflict: authorization scope, known-good rollback target, schema and state compatibility, forward-only or destructive-operation analysis, dependent changes, blast-radius limit, maximum automatic attempts, stop conditions, escalation or incident-response path, and the rollback verification path. Automatic classification ALSO requires no unresolved conflict among the authority or rollback-path inputs. If any required item is missing or conflicting, classify the policy as manual-only, add a '[needs decision: ...]' entry, and do not propose an automatic default. State explicitly which inputs were supplied and which were not.",
      "3. Monitored signals -- the signals the policy watches. Use the supplied names when the inputs supplied them; when the inputs are empty, name the signal categories (for example: 'error rate', 'latency p95', 'support ticket volume', 'synthesized flow success') without inventing specific metric names. For each signal, also state: (a) observability alert class, (b) freshness limit, and (c) the lowest-traffic or low-traffic behavior under which the signal is still meaningful.",
      "4. Objective thresholds -- the threshold for each signal. Every threshold must define: comparator (for example: greater-than, less-than, equal-to), direction (higher-is-worse, lower-is-worse), unit (percent, milliseconds, requests-per-minute, count), scope (region, segment, service), baseline or reference period (for example: 'last 7 days at the same hour-of-day', 'pre-deploy baseline'), and trigger class (observability alert only, or rollback trigger). Do NOT invent numeric threshold candidates. Use supplied values; otherwise '[needs decision: <unresolved question>]' with the question stated. Where a missing threshold affects safe automatic operation, keep the policy manual-only.",
      "5. Aggregation window and persistence -- the time window over which a breach must persist, and the rule that requires the breach across multiple valid windows before triggering. Do NOT invent numeric candidates for the aggregation window or persistence rule. Use supplied values; otherwise '[needs decision: <unresolved question>]'.",
      "6. Post-change stabilization period -- the window after the change begins during which signals are not yet considered stable and triggers are suppressed or downgraded. Do NOT invent numeric candidates. Use supplied values; otherwise '[needs decision: <unresolved question>]'.",
      "7. Minimum sample and low-traffic behavior -- the minimum sample or traffic required for the signal to be considered meaningful, and the policy behavior under low traffic. Do NOT invent numeric candidates. Use supplied values; otherwise '[needs decision: <unresolved question>]'.",
      "8. Data-quality checks and telemetry rules -- the conditions under which the signal itself is suspect and evaluation should be suppressed. State explicitly that missing, stale, partial, or unreliable telemetry suspends automatic action and triggers alert or manual escalation, and that missing telemetry must never be interpreted as healthy. Use supplied values; otherwise '[needs decision: <unresolved question>]'.",
      "9. False-positive safeguards -- the specific protections against needless rollbacks (cool-down, hysteresis, confirmation steps). Do NOT invent numeric candidates for cool-down, hysteresis, or confirmation steps. Use supplied values; otherwise '[needs decision: <unresolved question>]'.",
      "10. Automatic vs manual rollback boundary -- the conditions that trigger automatic rollback without human approval, and the conditions that escalate to manual decision instead. State the boundary in plain language. If the policy is manual-only, say so explicitly here.",
      "11. Cooldown, maximum automatic attempts, and stop conditions -- the cool-down window, the maximum number of automatic rollback attempts within a defined window, and the stop conditions. State explicitly that during cooldown or after the maximum automatic attempt count, further automatic action halts and the policy escalates through the supplied path. When the inputs do not supply a maximum, apply this rule: 'When maximum automatic attempts are not supplied, mark [needs decision: what maximum automatic-attempt count and time window are authorized?] and classify the policy as manual-only.'",
      "12. Rollback verification -- the checks that confirm the rollback actually fixed the signal, the action to take if it did not, and the explicit rule that if verification fails or is inconclusive, further automatic attempts halt and the policy enters the supplied escalation or incident-response path. Section 12 defines the evidence required to determine, after an authorized rollback occurs, whether it worked. Use supplied values; otherwise '[needs decision: <unresolved question>]'.",
      "13. Manual override and escalation path -- who can override, who must be notified, and the escalation path. Use supplied values; otherwise '[needs decision: <unresolved question>]'.",
      "14. Audit trail and communication -- the required future events and recipients when the auto-rollback fires, and the records that will be kept. Describe what must happen and to whom; do NOT claim that notifications were sent or verification was completed. Use supplied values; otherwise '[needs decision: <unresolved question>]'.",
      "15. Unsafe-rollback conditions -- explicit manual-only classifications for any of: forward-only operations, destructive effects, incompatible state, unresolved dependencies, or unresolved rollback-path conflicts. The policy is manual-only for those conditions unless a supplied and explicitly authorized safe recovery procedure resolves the risk. State each condition, the inputs that triggered it, and whether the supplied authorization resolves the risk. Do not invent a recovery procedure.",
      "16. Open decisions -- a flat list of every '[needs decision: <unresolved question>]' item from sections 2 to 15, including unresolved authority and rollback-path decisions and any conflicting inputs, so the decision maker can resolve them in one place.",
      "",
      "Constraints:",
      "- This output does not grant authority, configure automation, invoke a rollback, or claim that any rollback, notification, audit event, or verification occurred. The output is a policy proposal only.",
      "- Do not invent dashboards, metrics, thresholds, commands, services, owners, on-call rotations, team names, or organizational authority. Every value in the policy must trace to a supplied input.",
      "- Automatic classification requires every material feasibility and governance input (authorization scope, known-good rollback target, schema and state compatibility, forward-only or destructive-operation analysis, dependent changes, blast-radius limit, maximum automatic attempts, stop conditions, escalation or incident-response path, and the rollback verification path) AND no unresolved conflict among authority or rollback-path inputs. If any required item is missing or conflicting, classify the policy as manual-only, add a '[needs decision: ...]' entry, and do not propose an automatic default.",
      "- When maximum automatic attempts are not supplied, mark '[needs decision: what maximum automatic-attempt count and time window are authorized?]' and classify the policy as manual-only. Do not propose a default.",
      "- Do NOT invent numeric candidates for thresholds, evaluation windows, samples, persistence, freshness, low-traffic rules, safeguards, or trigger values. Mark them as unresolved decisions and, where they affect safe automatic operation, keep the policy manual-only.",
      "- Missing, stale, partial, or unreliable telemetry suspends automatic action and triggers alert or manual escalation. Missing telemetry must never be interpreted as healthy.",
      "- Every threshold must define: comparator, direction, unit, scope, baseline or reference period, and trigger class. A threshold that does not carry these six fields is not yet a threshold; mark it '[needs decision: <unresolved question>]'.",
      "- Distinguish observability alert from rollback trigger. A signal can be an observability alert without being a rollback trigger. The trigger class field in section 4 makes this explicit.",
      "- During cooldown or after the maximum automatic attempt count, halt further automatic action and escalate through the supplied path.",
      "- If rollback verification fails or is inconclusive, halt further automatic attempts and enter the supplied escalation or incident-response path.",
      "- Require manual-only classification when rollback may be unsafe because of forward-only operations, destructive effects, incompatible state, unresolved dependencies, or unresolved rollback-path conflicts, unless a supplied and explicitly authorized safe recovery procedure resolves the risk.",
      "- When a value is required but the inputs do not supply it, mark '[needs decision: <unresolved question>]'. Use the same wording in section 16 so nothing is lost. Collect unresolved authority and rollback-path decisions from every section, including conflicting inputs.",
      "- Prefer reversible actions over irreversible ones. When the rollback itself could make things worse (forward-only operations, schema mismatch), name the risk in section 15 and require a confirmation step.",
      "- Audit and communications describe required future events and recipients. They must not claim notifications were sent or verification was completed.",
      "- Use generic tool wording unless an exact command or tool name was supplied or observed and is required for reproducibility. Preserve those names verbatim. Never invent a command, tool, or vendor.",
      "- The policy is a draft until the decision maker confirms every '[needs decision: <unresolved question>]' item. Treat the output as a proposal for review.",
    ].join("\n"),
    expectedOutput:
      "An auto-rollback policy proposal with the sixteen labeled sections. Section 2 enforces the automatic-classification gate (every material feasibility and governance input supplied with no unresolved conflict among authority or rollback-path inputs); any missing or conflicting input forces manual-only classification with a '[needs decision: ...]' entry, and no automatic default is proposed. Section 4 defines every threshold with comparator, direction, unit, scope, baseline or reference period, and trigger class; numeric threshold candidates are never invented. Sections 5, 6, 7, and 9 treat aggregation, stabilization, minimum sample, low-traffic, and safeguard values as unresolved decisions rather than invented numeric candidates. Section 8 enforces the rule that missing, stale, partial, or unreliable telemetry suspends automatic action and is never interpreted as healthy. Section 10 distinguishes automatic rollback from manual rollback. Section 11 halts further automatic action during cooldown or after the maximum automatic attempt count and escalates. Section 12 halts further automatic attempts if rollback verification fails or is inconclusive and defines the evidence required to determine, after an authorized rollback occurs, whether it worked. Section 14 describes audit and communication as required future events and recipients, never as completed actions. Section 15 explicitly classifies the policy as manual-only when rollback may be unsafe because of forward-only operations, destructive effects, incompatible state, unresolved dependencies, or unresolved rollback-path conflicts, unless a supplied and explicitly authorized safe recovery procedure resolves the risk. Section 16 collects every unresolved decision, including unresolved authority and rollback-path decisions and conflicting inputs, in one place. The output carries the authority-boundary statement: it does not grant authority, configure automation, invoke a rollback, or claim that any rollback, notification, audit event, or verification occurred. No invented dashboards, metrics, thresholds, commands, services, owners, or organizational authority.",
    notes: [
      {
        title: "Why every missing value is marked the same way",
        body:
          "Auto-rollback policies fail when the missing values are filled in by whoever writes the policy, often without realizing they are inventing an organizational commitment. Marking every missing value '[needs decision: <unresolved question>]' makes the gap visible at write time, not at incident time.",
      },
      {
        title: "Why verification is its own section",
        body:
          "An auto-rollback that does not verify the rollback actually fixed the signal can silently leave the system in a worse state. The verification step is what closes the loop. Without it, the policy is a trigger, not a recovery.",
      },
      {
        title: "Why authorization scope is a precondition for automatic",
        body:
          "An automatic rollback that fires without a supplied authorization scope is a liability, not a safety net. The rollback tool may have the technical capability to act, but acting without authorization crosses an organizational boundary. Treating authorization scope as a precondition forces the policy to fall back to manual when the boundary is missing.",
      },
      {
        title: "Why missing telemetry is not healthy telemetry",
        body:
          "An alerting gap is not a green light. Treating missing telemetry as a positive signal lets a real outage ride through the silence. The policy treats missing, stale, partial, or unreliable telemetry as an explicit stop condition: suspend automatic action and trigger alert or manual escalation.",
      },
      {
        title: "Why cooldown and max-attempts halt automatic action",
        body:
          "A second automatic rollback inside the cooldown window is almost always a re-trigger of the same signal, often without new information. Halting further automatic action and escalating forces a human to read the evidence and decide whether the system is in a state that justifies another attempt.",
      },
      {
        title: "Why the output does not grant authority",
        body:
          "An auto-rollback policy that looked like an authorization would be a liability. The policy proposal describes what an authorized rollback would do; it does not authorize, configure, invoke, or claim any rollback, notification, audit event, or verification. The authority-boundary statement belongs in the preamble so a reader cannot mistake the proposal for a commitment.",
      },
      {
        title: "Why unsafe rollback conditions force manual-only",
        body:
          "Forward-only operations, destructive effects, incompatible state, unresolved dependencies, or unresolved rollback-path conflicts can each turn a successful rollback into a worse outcome than no rollback. The policy must classify itself as manual-only for those conditions unless a supplied and explicitly authorized safe recovery procedure resolves the risk. Inventing a recovery procedure is not a substitute for supplied authorization.",
      },
    ],
    antiPatterns: [
      {
        title: "Inventing dashboards and metric names",
        body:
          "Naming a specific dashboard or metric that the inputs did not supply produces a policy that the on-call cannot act on. Name signal categories when the inputs are empty; let the decision maker attach the actual metrics.",
      },
      {
        title: "Picking thresholds without authority",
        body:
          "Setting a threshold value when the inputs did not supply one looks decisive and is not. The threshold is a commitment the system will act on; it must come from the inputs or be marked '[needs decision: <unresolved question>]'. Numeric candidates for thresholds, evaluation windows, samples, persistence, freshness, low-traffic rules, safeguards, or trigger values are never invented; they are marked as unresolved decisions.",
      },
      {
        title: "Confusing automatic with manual rollback",
        body:
          "A policy that says 'the system rolls back when an engineer decides' is a manual policy, not an automatic one. State the boundary in plain language: here, automatic rollback fires; here, it escalates to a human.",
      },
      {
        title: "Skipping the verification step",
        body:
          "A rollback that fires and is not verified can leave the system in a partially-fixed state. Section 12 defines the evidence required to determine, after an authorized rollback occurs, whether it worked. Without it, the policy is half a recovery.",
      },
      {
        title: "Treating missing telemetry as healthy",
        body:
          "Reading silence as a green light lets a real outage ride through the gap. The policy treats missing, stale, partial, or unreliable telemetry as a stop condition; it is never interpreted as healthy.",
      },
      {
        title: "Looping automatic rollbacks without a halt",
        body:
          "Continuing to fire automatic rollback attempts inside the cooldown window or after the max-attempts count is reached produces a policy that fights itself. The halt rule in section 11 forces escalation so a human can read the evidence.",
      },
      {
        title: "Claiming notifications were sent or verification was completed",
        body:
          "The audit and communications section is a description of required future events and recipients. Writing 'notified the incident commander' or 'verified the rollback' claims that an action has happened that the policy itself does not perform. Describe what must happen and to whom; let the audit trail record what actually happened.",
      },
      {
        title: "Proposing an automatic default when inputs are missing",
        body:
          "Reaching for a one-attempt default, a single-threshold default, or any invented numeric default to fill a missing input is the same mistake as inventing a dashboard. The policy must classify itself as manual-only for the affected condition, mark '[needs decision: <unresolved question>]', and stop.",
      },
      {
        title: "Classifying rollback as automatic when rollback may be unsafe",
        body:
          "An automatic classification in the presence of forward-only operations, destructive effects, incompatible state, unresolved dependencies, or unresolved rollback-path conflicts is a guarantee the policy cannot keep. The policy must classify itself as manual-only for those conditions unless a supplied and explicitly authorized safe recovery procedure resolves the risk.",
      },
    ],
    collectionIds: ["operator-playbook"],
    sourceReferences: provenance("operate-auto-rollback-conditions"),
  },
];
