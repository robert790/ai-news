import type { PromptRecord } from "./types";

/**
 * Pilot Batch 1 -- five canonical OpenRadar prompt records.
 *
 * Drafts only. Every record is editorial: OpenRadar-authored wording,
 * tool-agnostic, no vendor sample blocks, no living-creator names, no em
 * dashes in user-facing content, variables explicitly marked and
 * explained, review metadata on the canonical discriminated union, and
 * commercial-use status on the canonical three-state enum.
 *
 * Inclusion does NOT equal legal clearance or publication approval.
 * Promotion requires editorial review, reviewer metadata, and the
 * explicit checks described in web/src/content/prompts/README.md.
 */

const baseEditorial = {
  sourceType: "openradar-original" as const,
  sourceReferences: [],
  authorship: "OpenRadar editorial",
  reviewStatus: "draft" as const,
  reviewer: null,
  lastReviewedAt: null,
  contentVersion: 1,
  commercialUseStatus: "pending" as const,
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
    safetyClass: "general",
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
      "Tone: factual, no marketing language, no hedging that does not add information. Scale the length of each section to the size of the change: a small change gets short sections, a large change gets longer ones, but every section must stay present.",
    ].join("\n"),
    expectedOutput:
      "A pull request description with the five labeled sections above. Each section is sized to the change. The Summary paragraph stands on its own without the rest of the document.",
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
    safetyClass: "professional",
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
      "Start the review with a single first line in this exact form:",
      "Verdict: approve | approve with comments | request changes",
      "",
      "Then write the review with the following sections, in this order:",
      "1. Verdict restated in one sentence, with the reason.",
      "2. Design -- does the change match the stated intent. Is the shape of the code right for the problem. Are there simpler alternatives that were missed.",
      "3. Correctness -- race conditions, error paths, invariants, edge cases.",
      "4. Operability -- logging, metrics, timeouts, retries, rollback, feature flags.",
      "5. Tests -- what is covered, what is missing, what would you add.",
      "6. Nitpicks -- small issues that are not blocking but worth a follow-up.",
      "",
      "Calibration rules:",
      "- Distinguish blocking from non-blocking concerns explicitly.",
      "- 'request changes' must include at least one blocking concern. If you cannot name one, the verdict is 'approve with comments'.",
      "- 'approve' must not contain blocking concerns. If you find a blocking concern after writing 'approve', change the verdict to 'request changes' or 'approve with comments'.",
      "- 'approve with comments' may contain only non-blocking concerns. If a blocking concern appears, change the verdict.",
      "- When you cite a concern, name the file and line only when the inputs actually supplied them. Never invent a file path or line number.",
      "- When file and line are not supplied, quote the smallest relevant fragment from the diff, or name the affected area in one phrase (for example: 'the retry loop in the new helper', 'the auth header construction').",
      "- Do not rewrite the entire change. A clearly labelled minimal patch or fix direction is permitted; a full rewrite is not.",
    ].join("\n"),
    expectedOutput:
      "A code review whose first line is exactly 'Verdict: approve | approve with comments | request changes', followed by the six labeled sections. The verdict and the body agree: blocking concerns appear only under 'request changes', and 'approve' is reserved for reviews with no blocking concerns.",
    notes: [
      {
        title: "Why the verdict is forced to the first line",
        body:
          "When the verdict is buried under analysis, reviewers end up re-reading the whole thing to find out whether they should merge. Putting the verdict first forces the analysis to justify itself.",
      },
      {
        title: "Why blocking and non-blocking must agree",
        body:
          "A review whose verdict says 'approve' but whose body lists blocking concerns trains the author to read the body, not the verdict, and trains the merge tooling to ignore the verdict. The verdict and the body must agree on what is blocking.",
      },
    ],
    antiPatterns: [
      {
        title: "Reviewing style as if it were design",
        body:
          "Flagging every variable name or import order as a blocker turns the review into noise. Style feedback goes in nitpicks or in a shared style document, not in the verdict.",
      },
      {
        title: "Inventing file and line references",
        body:
          "Citing 'src/foo.ts:142' when the diff did not supply line numbers produces a review whose citations the author has to chase down and verify. When the inputs do not give a location, quote the smallest fragment or name the affected area instead.",
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
      "Engineers, support leads, or product managers who need to send a customer-facing message during an incident.",
    useCase:
      "When you need to send an initial status update or an ongoing incident update to customers and you want the message to be honest, calm, and useful.",
    safetyClass: "professional",
    inputs: [
      {
        name: "incident_summary",
        label: "Incident summary",
        description:
          "What happened, in plain language. State the user-visible impact first, the internal cause second only if the cause is confirmed, and the current status third. Avoid technical jargon the customer does not need.",
        example:
          "Customers could not place new orders between 14:02 and 14:38 UTC. The cause is confirmed: a stuck deploy that held connections open. Orders placed during the window were not lost.",
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
          "We have rolled back the deploy and added a guardrail so it cannot ship again in this state. We will publish the next update by 16:00 UTC.",
      },
      {
        name: "cause_under_investigation",
        label: "Cause under investigation?",
        description:
          "Set to 'yes' only when the root cause has not yet been confirmed. The notification will then state that the cause is under investigation, without speculation, and will promise a confirmation or correction later.",
        example:
          "yes",
      },
      {
        name: "tentative_cause",
        label: "Tentative cause (optional)",
        description:
          "A working theory of the cause. Use only when the inputs explicitly supply one. When used, the notification must label it 'preliminary' or 'working theory', must state the supporting evidence, and must separate it from any confirmed cause.",
        example:
          "Working theory: a stuck deploy held connections open. Supporting evidence: deploy timestamp matches incident start, no upstream provider status change in the same window.",
      },
      {
        name: "acknowledgement_or_apology",
        label: "Acknowledgement or apology (optional)",
        description:
          "At most one concise acknowledgement or apology. The prompt must not generate more than one. Leave blank for none.",
        example:
          "We are sorry for the disruption.",
      },
    ],
    prompt: [
      "Write a customer-facing incident notification for the situation below.",
      "This notification is an initial status update or an ongoing incident update. It is not an incident report or a post-incident summary.",
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
      "Cause under investigation?",
      "{cause_under_investigation}",
      "",
      "Tentative cause (if supplied):",
      "{tentative_cause}",
      "",
      "Acknowledgement or apology (if supplied):",
      "{acknowledgement_or_apology}",
      "",
      "Cause rules:",
      "- If 'cause_under_investigation' is 'yes', state that the cause is under investigation. Do not name a cause from anywhere else in the inputs as confirmed.",
      "- Use a tentative cause only when the inputs explicitly supplied one. Label it 'preliminary' or 'working theory'.",
      "- When a tentative cause is used, state the supporting evidence and separate it visually from any confirmed status.",
      "- Assign no blame to any individual or team. Do not infer intent.",
      "- When the cause is later confirmed or corrected, the next update will say so.",
      "",
      "Structure:",
      "- Short opening paragraph with what is happening right now, who is affected, and what the customer should do.",
      "- A section on customer impact.",
      "- A section on what we are doing next.",
      "- A section on what the customer should do.",
      "- Optional acknowledgement or apology, at most one, placed where it does not bury the facts.",
      "",
      "Tone rules:",
      "- Calm, factual, adult. No marketing language.",
      "- Apologise or acknowledge at most once.",
      "- Do not speculate about root cause beyond what the inputs supplied.",
      "- Do not include internal tool names, on-call rotations, or anything the customer cannot act on.",
      "- Length: an initial update or an ongoing update can be three short paragraphs. Do not pad to look thorough.",
    ].join("\n"),
    expectedOutput:
      "A customer-facing initial or ongoing update with the four labeled sections, an optional single acknowledgement, and an explicit cause status (confirmed, under investigation, or working theory with supporting evidence). The opening paragraph stands on its own and contains the most important facts: what is happening, who is affected, what the customer should do right now.",
    notes: [
      {
        title: "Why the cause status is a structured input",
        body:
          "Notifications drift toward either over-explaining a cause that is not yet confirmed or burying a confirmed cause under impact. Treating cause status as a structured field forces the writer to declare it explicitly and to separate confirmed from tentative.",
      },
      {
        title: "Why acknowledgement and apology are limited to one",
        body:
          "Multiple apologies in a single notification read as either panic or a request for absolution. One concise acknowledgement is enough; additional repetition wastes the customer's reading time.",
      },
    ],
    antiPatterns: [
      {
        title: "Lead with the apology",
        body:
          "Starting with a long apology buries the facts customers need. The opening paragraph should state what is happening and what to do; the acknowledgement, if present, comes after.",
      },
      {
        title: "Speculating about root cause to look thorough",
        body:
          "Inventing a root cause to make the notification feel complete produces a public statement that has to be walked back later. If the cause is not confirmed, say so.",
      },
      {
        title: "Writing a post-incident report in the first 30 minutes",
        body:
          "A post-incident report is built at the end of an incident from real timestamps and a confirmed timeline. Generating one as an 'initial notification' produces a plausible-looking artifact that is wrong about key facts.",
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
    safetyClass: "professional",
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
      {
        name: "available_responders",
        label: "Available responders",
        description:
          "Names or role descriptions of people available in the first fifteen minutes. Empty or absent means the role slots are unassigned.",
        example:
          "Alice on-call. Bob can join in five minutes from another team. Carol is offline until 14:30 UTC.",
      },
      {
        name: "team_role_conventions",
        label: "Team role conventions",
        description:
          "How this team assigns the incident commander, the operator/responder, and the communications and scribe slots. Used to assign supplied names. If absent, role slots are output as 'unassigned'.",
        example:
          "On-call is the default incident commander. Second responder is the scribe. Communications lead is the engineer who acks the page second.",
      },
      {
        name: "known_observability_and_controls",
        label: "Known dashboards, logs, runbooks, rollback controls, channels",
        description:
          "Internal resource names supplied by the user: dashboards, log queries, runbooks, rollback controls, communication channels. When supplied, these names are used verbatim. When absent, none are invented.",
        example:
          "Dashboard: checkout-errors-overview. Log query: service=checkout level=error last=10m. Runbook: runbooks/checkout-errors.md. Rollback: argo-rollouts undo deploy/checkout. Channel: #incident-eu.",
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
      "Available responders:",
      "{available_responders}",
      "",
      "Team role conventions:",
      "{team_role_conventions}",
      "",
      "Known dashboards, logs, runbooks, rollback controls, channels:",
      "{known_observability_and_controls}",
      "",
      "Produce the following sections:",
      "1. One-line status -- a sentence that fits in a status page update.",
      "2. Roles -- three slots: incident commander, operator/responder, communications and scribe (combined when staffing requires it).",
      "3. Immediate checks -- the three or four things to look at in the first five minutes.",
      "4. Stabilize before diagnosing -- the smallest action that can reduce customer impact right now, with the tradeoff explicitly named.",
      "5. Comms cadence -- when the next status update is due and to whom.",
      "6. Stop conditions -- when to escalate, when to call in additional help, when to invoke the disaster recovery plan.",
      "",
      "Constraints:",
      "- Role slots: assign supplied names using supplied conventions. If names are absent, output role slots as 'unassigned'. Never invent people.",
      "- Internal resources: use supplied dashboard, log, runbook, control, and channel names verbatim. Never invent dashboards, queries, runbooks, controls, or channels. When nothing relevant is supplied for an immediate check, name the signal or evidence category to inspect (for example: 'error rate dashboard', 'recent deploys', 'upstream provider status') without naming a specific tool that the inputs did not give you.",
      "- Every immediate check must name the signal or evidence category to inspect.",
      "- Do not invent fixed defaults for who is the commander or the scribe.",
      "- Prefer reversible actions over irreversible ones.",
      "- Assume you have at most three people available in the first fifteen minutes.",
    ].join("\n"),
    expectedOutput:
      "A playbook with the six labeled sections. The one-line status is copy-pasteable into a status page. Each immediate check names a signal or evidence category to inspect, and uses internal resource names only when the inputs supplied them. Role slots are filled from the inputs; any unfilled slot is written 'unassigned'.",
    notes: [
      {
        title: "Why role slots are filled from inputs",
        body:
          "A default like 'incident commander is whoever acks the page' looks convenient but it embeds a guess about how a specific team staffs incidents. The inputs are the only place that guess can live; the prompt must read from there and stay silent otherwise.",
      },
      {
        title: "Why internal resource names must come from inputs",
        body:
          "Inventing a dashboard name or a runbook path produces an opening playbook that no one on the team can actually open. The first fifteen minutes are too short to discover that the model pointed at the wrong dashboard.",
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
      {
        title: "Invent dashboards and runbooks the team does not have",
        body:
          "Naming an internal dashboard or runbook that was not in the inputs produces an opening playbook that the response cannot act on. When nothing relevant is supplied, name the signal or evidence category to inspect and stop.",
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
    safetyClass: "general",
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
      "4. Empty states -- what each dynamic or data-dependent region shows when it has no content yet. Static regions get no empty state.",
      "5. Unresolved decisions -- any required information the inputs did not supply, listed as '[needs decision]' followed by the unresolved question.",
      "6. What is intentionally absent -- components or patterns the page does NOT need, with the reason.",
      "",
      "Constraints:",
      "- Tool agnostic. Do not name a specific framework, library, or component name.",
      "- Do not invent content that is not in the inputs.",
      "- Do not include pixel sizes or hex colors. Layout, not visual design.",
      "- Do not add design-token support, theme tokens, or color palettes in this skeleton. Visual design tokens live in a separate document.",
      "- Where a section depends on information the inputs did not supply, list the unresolved question in section 5 rather than inventing content.",
      "- Describe the result as implementable where inputs are complete, with unresolved decisions explicitly identified in section 5.",
    ].join("\n"),
    expectedOutput:
      "A page skeleton with the six labeled sections. The Skeleton tree can be read top-to-bottom and rebuilt into markup by a frontend engineer without further questions. Section 5 lists every '[needs decision]' item left open by the inputs, with the unresolved question, and no invented content appears anywhere else.",
    notes: [
      {
        title: "Why content blocks are a structured input",
        body:
          "Pages that are designed before their content is known end up reorganizing twice. Treating content blocks as a fixed input forces the layout to follow the content instead of the other way around.",
      },
      {
        title: "Why unresolved decisions get their own section",
        body:
          "Inventing missing content keeps the layout looking finished and hides the gaps. Listing '[needs decision]' items keeps the gaps visible until the inputs are complete.",
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
      {
        title: "Inventing content to hide a missing input",
        body:
          "Filling in a placeholder string or example text to make the layout look complete hides the fact that a real input was missing. Use '[needs decision]' so the gap is visible.",
      },
    ],
    collectionIds: ["studio-foundation"],
  },
];