import type { PromptRecord } from "./types";

/**
 * Pilot Batch 1 -- five canonical OpenRadar prompt records.
 *
 * Drafts only. Every record is editorial: OpenRadar-authored wording, tool
 * agnostic, no vendor sample blocks, no living-creator names, no em dashes
 * in user-facing content, variables explicitly marked and explained.
 *
 * Inclusion does NOT equal legal clearance or publication approval.
 * Promotion requires editorial review, reviewer metadata, and the explicit
 * checks described in web/src/content/prompts/README.md.
 */

const baseEditorial: Pick<
  PromptRecord,
  | "sourceType"
  | "sourceReferences"
  | "authorship"
  | "reviewStatus"
  | "reviewer"
  | "lastReviewedAt"
  | "contentVersion"
  | "safetyClass"
  | "commercialUseAllowed"
> = {
  sourceType: "openradar-original",
  sourceReferences: [],
  authorship: "OpenRadar editorial",
  reviewStatus: "draft",
  reviewer: null,
  lastReviewedAt: null,
  contentVersion: 1,
  safetyClass: "general",
  commercialUseAllowed: false,
};

export const promptRecords: PromptRecord[] = [
  {
    ...baseEditorial,
    id: "code-pr-description",
    slug: "code-pr-description",
    title: "Pull request description that reads like a change record",
    category: "code",
    difficulty: "beginner",
    audience:
      "Engineers opening pull requests on a team with code review and a shared trunk.",
    useCase:
      "When you are about to open a pull request and want the description to land cleanly on the first review pass.",
    inputs: [
      {
        name: "change_summary",
        label: "Change summary",
        description:
          "Two or three sentences describing what the pull request actually changes. State the user-visible behavior, the internal mechanism, and the motivation.",
        example:
          "Add a retry wrapper around the HTTP client. Three retries with exponential backoff. Closes the prod incident from last Tuesday.",
      },
      {
        name: "testing_evidence",
        label: "Testing evidence",
        description:
          "What you ran, what passed, and any new automated coverage. Include manual verification steps when the change is hard to cover with tests.",
        example:
          "Unit tests cover the wrapper. Manual run with a flaky upstream showed three attempts before success. Added a test for backoff timing.",
      },
      {
        name: "risk_notes",
        label: "Risk notes",
        description:
          "Anything that could break in production that a reviewer should pay attention to: rollback steps, feature flags, migration order, external dependencies.",
        example:
          "No migration. The wrapper is opt-in per call site. If the upstream is fully down, requests will block for the full backoff window.",
      },
    ],
    prompt: [
      "Write a pull request description for the change described below.",
      "",
      "Change summary:",
      "{change_summary}",
      "",
      "Testing evidence:",
      "{testing_evidence}",
      "",
      "Risk notes:",
      "{risk_notes}",
      "",
      "Structure the description with these sections, in this order:",
      "1. Summary -- one paragraph that a reviewer can read in 20 seconds.",
      "2. Why -- the problem this change solves, in plain language.",
      "3. What changed -- bullet list of the user-visible and internal moves.",
      "4. Testing -- what you ran and what you did not.",
      "5. Risks and rollback -- what could go wrong and how to undo it.",
      "",
      "Tone: factual, no marketing language, no hedging that does not add information. Match the length of the change: small change gets a short description, large change gets a long one.",
    ].join("\n"),
    expectedOutput:
      "A pull request description with the five labeled sections above. Each section sized to the change. The Summary paragraph stands on its own without the rest of the document.",
    notes: [
      {
        title: "Why five sections",
        body:
          "A pull request description is read at two speeds: a skim during queue triage and a close read during review. The Summary carries the skim, and the rest carries the close read. Skipping either leaves the reviewer working harder than they should.",
      },
      {
        title: "Why the change summary is structured input, not freeform prompt",
        body:
          "If you ask the model to invent the change, it will invent a plausible-looking one that is not yours. The structured inputs force the user to bring the actual facts; the model only organizes them.",
      },
    ],
    antiPatterns: [
      {
        title: "Dumping the diff into the prompt",
        body:
          "Asking the model to summarize a long diff produces a description that mirrors the code structure instead of the change. Reviewers can read the diff. They want to know the why and the risk.",
      },
      {
        title: "Asking the model to write the title too",
        body:
          "Pull request titles are short and follow the conventions of the team and the change management tool. Letting the model invent a title produces inconsistent titles across the repo.",
      },
    ],
    collectionIds: ["builder-bench"],
  },

  {
    ...baseEditorial,
    id: "code-review-staff",
    slug: "code-review-staff",
    title: "Staff-level code review that catches the real issues",
    category: "code",
    difficulty: "advanced",
    audience:
      "Senior engineers reviewing pull requests where correctness, design, and operational behavior all matter.",
    useCase:
      "When you are the senior reviewer on a non-trivial change and need to leave a review that pushes the design forward without nitpicking.",
    inputs: [
      {
        name: "diff_or_change",
        label: "Diff or change description",
        description:
          "The full diff, or a detailed change description if the diff is too large to paste. Include the surrounding context for any non-obvious decisions.",
        example:
          "Pasted the diff in full, with the surrounding test file for the new helper.",
      },
      {
        name: "design_context",
        label: "Design context",
        description:
          "What the author told you about the design intent, any earlier discussions, links to design docs, and any constraints you should respect.",
        example:
          "Author wants this to be a drop-in replacement for the old API. Old clients should keep working. Performance target is two times faster on the hot path.",
      },
      {
        name: "concerns_to_weigh",
        label: "Concerns to weigh",
        description:
          "Specific things you want to check: invariants, edge cases, error paths, performance, observability, security, migration, rollback.",
        example:
          "Focus on concurrency around the shared cache. The old code had a known race that this rewrite is supposed to remove.",
      },
    ],
    prompt: [
      "You are reviewing a change as a staff-level engineer.",
      "",
      "Diff or change description:",
      "{diff_or_change}",
      "",
      "Design context:",
      "{design_context}",
      "",
      "Concerns to weigh:",
      "{concerns_to_weigh}",
      "",
      "Leave a code review with the following sections:",
      "1. Verdict -- one of: approve, approve with comments, request changes. State the verdict in the first line.",
      "2. Design -- does the change match the stated intent. Is the shape of the code right for the problem. Are there simpler alternatives that were missed.",
      "3. Correctness -- race conditions, error paths, invariants, edge cases.",
      "4. Operability -- logging, metrics, timeouts, retries, rollback, feature flags.",
      "5. Tests -- what is covered, what is missing, what would you add.",
      "6. Nitpicks -- small issues that are not blocking but worth a follow-up.",
      "",
      "Calibration rules:",
      "- Distinguish blocking from non-blocking explicitly.",
      "- When you flag a concern, name the file and line or the smallest possible reproduction.",
      "- Do not restate the diff back to the author.",
      "- If you cannot tell whether something is wrong, say what additional information you would need.",
    ].join("\n"),
    expectedOutput:
      "A code review starting with a verdict line, followed by the six labeled sections, each grounded in the provided diff and context. Every blocking concern points at a specific file and line or a concrete reproduction.",
    notes: [
      {
        title: "Why the verdict is forced to the first line",
        body:
          "When the verdict is buried under analysis, reviewers end up re-reading the whole thing to find out whether they should merge. Putting the verdict first forces the analysis to justify itself.",
      },
      {
        title: "Why nitpicks are separated",
        body:
          "Mixing nitpicks with blocking issues trains authors to ignore all comments. A separate nitpicks section lets the author treat them as a backlog instead of as objections.",
      },
    ],
    antiPatterns: [
      {
        title: "Reviewing style as if it were design",
        body:
          "Flagging every variable name or import order as a blocker turns the review into noise. Style feedback goes in nitpicks or in a shared style document, not in the verdict.",
      },
      {
        title: "Asking the model to fix the code",
        body:
          "A code review describes problems and leaves fixes to the author. Generating a fix in the review conflates two roles and produces rewrites the author did not sign off on.",
      },
    ],
    collectionIds: ["builder-bench"],
  },

  {
    ...baseEditorial,
    id: "write-customer-notification",
    slug: "write-customer-notification",
    title: "Customer-facing incident notification that informs without spinning",
    category: "write",
    difficulty: "advanced",
    audience:
      "Engineers, support leads, or product managers who need to send a customer-facing message during or after an incident.",
    useCase:
      "When you need to send a status update, an incident report, or a post-incident summary to customers and you want the message to be honest, calm, and useful.",
    inputs: [
      {
        name: "incident_summary",
        label: "Incident summary",
        description:
          "What happened, in plain language. State the user-visible impact first, the internal cause second, and the current status third. Avoid technical jargon the customer does not need.",
        example:
          "Customers could not place new orders between 14:02 and 14:38 UTC. The cause was a stuck deploy that held connections open. Orders placed during the window were not lost.",
      },
      {
        name: "customer_impact",
        label: "Customer impact",
        description:
          "Who was affected, how many, for how long, and what they saw. State any data exposure explicitly if there was any.",
        example:
          "About 12 percent of customers in the EU region. Some saw a generic error page. No payment data was exposed.",
      },
      {
        name: "next_steps",
        label: "Next steps",
        description:
          "What you are doing next, what the customer should do, and when you will update them again.",
        example:
          "We have rolled back the deploy and added a guardrail so it cannot ship again in this state. We will publish a full post-incident report by Friday.",
      },
    ],
    prompt: [
      "Write a customer-facing incident notification for the situation below.",
      "",
      "Incident summary:",
      "{incident_summary}",
      "",
      "Customer impact:",
      "{customer_impact}",
      "",
      "Next steps:",
      "{next_steps}",
      "",
      "Constraints:",
      "- Tone: calm, factual, adult. No marketing language. No apologizing more than once.",
      "- Structure: short opening paragraph with what is going on right now, a section on who was affected, a section on what we are doing, and a section on what the customer should do.",
      "- Length: a status update can be three short paragraphs. A post-incident report can be longer, but every section must earn its place.",
      "- Do not speculate about root cause beyond what is in the inputs. If the root cause is not yet known, say so.",
      "- Do not include internal tool names, on-call rotations, or anything the customer cannot act on.",
    ].join("\n"),
    expectedOutput:
      "A customer-facing message with the four labeled sections. The opening paragraph stands on its own and contains the most important facts: what is happening, who is affected, what the customer should do right now.",
    notes: [
      {
        title: "Why the customer impact is a separate input",
        body:
          "Impact is the part customers care most about. Treating it as a structured field forces the writer to state it explicitly instead of burying it under technical narrative.",
      },
      {
        title: "Why the tone rules are spelled out",
        body:
          "Customer notifications drift toward either over-apologizing or technical coldness without explicit guidance. The constraints are short because the writer should not have to argue with the model about tone.",
      },
    ],
    antiPatterns: [
      {
        title: "Lead with the apology",
        body:
          "Starting with a long apology buries the facts customers need. The opening paragraph should state what is happening and what to do; the apology, if appropriate, comes after.",
      },
      {
        title: "Speculating about root cause to look thorough",
        body:
          "Inventing a root cause to make the notification feel complete produces a public statement that has to be walked back later. If the root cause is unknown, say so.",
      },
    ],
    collectionIds: ["editor-desk"],
  },

  {
    ...baseEditorial,
    id: "operate-incident-first-15-minutes",
    slug: "operate-incident-first-15-minutes",
    title: "First fifteen minutes of an incident without losing the thread",
    category: "operate",
    difficulty: "advanced",
    audience:
      "On-call engineers and incident commanders during the first minutes of a production incident.",
    useCase:
      "When an incident has just been declared and you need a structured opening playbook so the response does not lose the thread in the first fifteen minutes.",
    inputs: [
      {
        name: "incident_signal",
        label: "Incident signal",
        description:
          "The alert, the customer report, or the symptom that triggered the response. Quote it verbatim if possible. State what is currently firing and what is currently quiet.",
        example:
          "PagerDuty: checkout error rate above 5 percent for 3 minutes. Customer support ticket volume up. No change in upstream provider status.",
      },
      {
        name: "blast_radius",
        label: "Blast radius",
        description:
          "What is currently affected: customers, regions, services, internal teams. State what is not affected if that is informative.",
        example:
          "EU region only. Checkout and account login. Internal tools unaffected. US region looks clean.",
      },
      {
        name: "recent_changes",
        label: "Recent changes",
        description:
          "Deploys, config changes, dependency changes, or external events in the last few hours that could be relevant.",
        example:
          "Deploy at 13:40 UTC to checkout service. No other deploys in the last two hours. No upstream provider status change.",
      },
    ],
    prompt: [
      "Generate a structured opening playbook for the first fifteen minutes of an incident.",
      "",
      "Incident signal:",
      "{incident_signal}",
      "",
      "Blast radius:",
      "{blast_radius}",
      "",
      "Recent changes:",
      "{recent_changes}",
      "",
      "Produce the following sections:",
      "1. One-line status -- a sentence that fits in a status page update.",
      "2. Roles -- who is the incident commander, who is the communications lead, who is the scribe. State defaults if not yet assigned.",
      "3. Immediate checks -- the three or four things to look at in the first five minutes: dashboards, logs, recent deploys, dependency status.",
      "4. Stabilize before diagnosing -- the smallest action that can reduce customer impact right now, with the tradeoff explicitly named.",
      "5. Comms cadence -- when the next status update is due and to whom.",
      "6. Stop conditions -- when to escalate, when to call in additional help, when to invoke the disaster recovery plan.",
      "",
      "Constraints:",
      "- Assume you have at most three people available in the first fifteen minutes.",
      "- Prefer reversible actions over irreversible ones.",
      "- Do not invent dashboards, runbooks, or people that are not in the inputs.",
    ].join("\n"),
    expectedOutput:
      "A playbook with the six labeled sections above. The one-line status is copy-pasteable into a status page. Each item in Immediate checks names a specific dashboard, log query, or change to inspect.",
    notes: [
      {
        title: "Why roles are defaults, not questions",
        body:
          "Asking who is the incident commander during the first minutes wastes time. Naming defaults (incident commander is whoever acks the page, scribe is the second responder) lets the response start immediately.",
      },
      {
        title: "Why stop conditions are explicit",
        body:
          "Most incidents are handled by a small group without escalation. The ones that need more help are the ones where people do not ask for it in time. Pre-committing to a stop condition removes that delay.",
      },
    ],
    antiPatterns: [
      {
        title: "Diagnose before stabilize",
        body:
          "Trying to find the root cause before reducing customer impact extends the incident. The first move is the smallest action that reduces harm; the diagnosis can wait.",
      },
      {
        title: "Generate the full incident timeline now",
        body:
          "A clean timeline is built at the end of the incident from real timestamps. Generating one in the first fifteen minutes produces a plausible-looking artifact that is wrong about key facts.",
      },
    ],
    collectionIds: ["operator-playbook"],
  },

  {
    ...baseEditorial,
    id: "design-frontend-page-skeleton",
    slug: "design-frontend-page-skeleton",
    title: "Frontend page skeleton from purpose and content, not from a template",
    category: "design",
    difficulty: "intermediate",
    audience:
      "Frontend engineers and product designers sketching a new page when there is no existing template to copy.",
    useCase:
      "When you are about to start a new page and want the structural layout to follow from what the page is for and what content it needs, instead of copying a template that may not fit.",
    inputs: [
      {
        name: "page_purpose",
        label: "Page purpose",
        description:
          "One or two sentences on what the page is for, who lands on it, and what they should be able to do or learn within five seconds.",
        example:
          "A settings index page. Logged-in users land here from the avatar menu. They should see every settings section in under five seconds and enter any of them in one click.",
      },
      {
        name: "content_blocks",
        label: "Content blocks",
        description:
          "The distinct pieces of content the page needs to show, in the order a user would encounter them. For each block, state whether it is interactive or static.",
        example:
          "Header with page title and breadcrumb. Section list of nine settings groups. Search field that filters the section list. Footer with support link.",
      },
      {
        name: "viewport_notes",
        label: "Viewport notes",
        description:
          "Anything you know about how the page should behave on narrow screens, on print, or on the smallest supported device.",
        example:
          "Section list collapses to a single column below 600px. Search field becomes sticky on small screens.",
      },
    ],
    prompt: [
      "Generate a frontend page skeleton for the page described below.",
      "",
      "Page purpose:",
      "{page_purpose}",
      "",
      "Content blocks:",
      "{content_blocks}",
      "",
      "Viewport notes:",
      "{viewport_notes}",
      "",
      "Produce the following sections:",
      "1. Skeleton -- a tree of the page's regions, in plain language, from the outermost region to the smallest interactive component. Each region has a one-line purpose.",
      "2. Layout rules -- how the regions stack, wrap, or rearrange at three breakpoints: narrow, medium, wide.",
      "3. Interactive elements -- every region that is clickable, focusable, or otherwise interactive, with the action it triggers.",
      "4. Empty states -- what each region shows when it has no content yet.",
      "5. What is intentionally absent -- components or patterns the page does NOT need, with the reason.",
      "",
      "Constraints:",
      "- Tool agnostic. Do not name a specific framework, library, or component name.",
      "- Do not invent content that is not in the inputs.",
      "- Do not include pixel sizes or hex colors. Layout, not visual design.",
    ].join("\n"),
    expectedOutput:
      "A page skeleton with the five labeled sections. The Skeleton tree can be read top-to-bottom and rebuilt into markup by a frontend engineer without further questions.",
    notes: [
      {
        title: "Why content blocks are a structured input",
        body:
          "Pages that are designed before their content is known end up reorganizing twice. Treating content blocks as a fixed input forces the layout to follow the content instead of the other way around.",
      },
      {
        title: "Why the absent section exists",
        body:
          "Naming what the page intentionally does not have stops the model from padding the design with hero sections, testimonials, or other patterns that were never requested.",
      },
    ],
    antiPatterns: [
      {
        title: "Generate markup instead of structure",
        body:
          "Asking the model for HTML or JSX ties the skeleton to a specific framework and a specific version of it. Generating structure first lets the team pick the markup that fits the codebase.",
      },
      {
        title: "Invent visual design tokens",
        body:
          "Adding colors, font sizes, or spacing values in a structural skeleton creates drift from the design system. Visual design lives in tokens, not in page-level decisions.",
      },
    ],
    collectionIds: ["studio-foundation"],
  },
];