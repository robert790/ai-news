# Prompt Pilot Scope v1

Selection is frozen. Wording is not frozen. No record is legally cleared merely by inclusion.
This document supersedes Stage 7A.3, 7A.3B, 7A.3C and 7A.3D.

## Scope

- 50 pilot IDs.
- 20 reserve IDs.
- Selection frozen, wording not frozen.
- No record is legally cleared merely by inclusion.
- Previous Stage 7A.3, 7A.3B, 7A.3C and 7A.3D reports are superseded.

## Classification definitions

### Concept

- **GREEN** — general operating discipline, public best practice, or public framework that does not require third-party attribution beyond a public standard or framework name.
- **AMBER** — concept is portable; existing notes attribute to a specific living creator, vendor blog, or non-OpenRadar document; attribution must be rewritten to a factual, accurate, distinguishing statement.
- **RED** — idea itself is unsafe for the public pilot: celebrity likeness material, brand/IP presentation material, YouMind-derived or YouMind-pack material, or material concerning medical, clinical, legal advice, legal text, financial advice, biometric, surveillance, weapon, malware, phishing, credential theft, jailbreak, offensive security, reverse shell, ransomware, or keylogging.

### Wording

- **SAFE-TO-ADAPT** — existing prompt body and notes are usable in full or with light edits; no copying of a vendor sample block, vendor prompt-engineering guide, official sample prompt, or documented block of external guidance.
- **DISCARD-ENTIRELY** — existing body, notes, or both are a close reproduction of a vendor sample prompt, a vendor's published guide section, or a documented block of external guidance; wording cannot be kept; only the concept survives.
- **EXCLUDE-CONCEPT** — wording outcome when concept is RED; record is excluded from the public pilot entirely.

## Final 50 pilot

| # | ID | Category | Difficulty | Concept | Wording |
|---|---|---|---|---|---|
| 1 | code-pr-description | code | beginner | GREEN | SAFE-TO-ADAPT |
| 2 | code-refactor-no-driveby | code | advanced | GREEN | SAFE-TO-ADAPT |
| 3 | code-review-staff | code | advanced | GREEN | SAFE-TO-ADAPT |
| 4 | code-bug-hunt-hypothesis | code | advanced | GREEN | SAFE-TO-ADAPT |
| 5 | code-frontend-anti-slop | code | advanced | GREEN | SAFE-TO-ADAPT |
| 6 | code-investigate-before-answering | code | beginner | AMBER | DISCARD-ENTIRELY |
| 7 | code-clear-direct-instructions | code | beginner | AMBER | SAFE-TO-ADAPT |
| 8 | code-reversibility-check | code | intermediate | AMBER | SAFE-TO-ADAPT |
| 9 | code-data-analysis-pandas | code | intermediate | AMBER | SAFE-TO-ADAPT |
| 10 | code-anti-test-gaming | code | advanced | AMBER | SAFE-TO-ADAPT |
| 11 | write-changelog | write | beginner | AMBER | SAFE-TO-ADAPT |
| 12 | write-pr-description | write | intermediate | AMBER | SAFE-TO-ADAPT |
| 13 | write-customer-notification | write | advanced | GREEN | SAFE-TO-ADAPT |
| 14 | write-incident-postmortem | write | advanced | AMBER | SAFE-TO-ADAPT |
| 15 | write-user-story | write | intermediate | GREEN | SAFE-TO-ADAPT |
| 16 | write-meeting-agenda | write | intermediate | GREEN | SAFE-TO-ADAPT |
| 17 | write-meeting-summary-with-action | write | beginner | AMBER | SAFE-TO-ADAPT |
| 18 | write-mollick-ai-as-intern-brief | write | beginner | AMBER | SAFE-TO-ADAPT |
| 19 | research-source-triangulate | research | intermediate | AMBER | SAFE-TO-ADAPT |
| 20 | research-claim-fact-check | research | intermediate | AMBER | SAFE-TO-ADAPT |
| 21 | research-decision-brief | research | advanced | AMBER | SAFE-TO-ADAPT |
| 22 | research-gap-analysis | research | advanced | AMBER | SAFE-TO-ADAPT |
| 23 | research-hypothesis-tree | research | advanced | AMBER | DISCARD-ENTIRELY |
| 24 | research-long-doc-quote | research | advanced | AMBER | DISCARD-ENTIRELY |
| 25 | research-trend-signal | research | advanced | AMBER | SAFE-TO-ADAPT |
| 26 | research-raschka-build-llm-from-scratch | research | intermediate | AMBER | SAFE-TO-ADAPT |
| 27 | decide-prioritize-rice | decide | beginner | AMBER | SAFE-TO-ADAPT |
| 28 | decide-pre-mortem | decide | advanced | AMBER | SAFE-TO-ADAPT |
| 29 | decide-risk-register | decide | intermediate | AMBER | SAFE-TO-ADAPT |
| 30 | decide-stakeholder-map | decide | intermediate | AMBER | SAFE-TO-ADAPT |
| 31 | decide-scenario-plan | decide | advanced | AMBER | SAFE-TO-ADAPT |
| 32 | decide-cut-feature | decide | advanced | AMBER | SAFE-TO-ADAPT |
| 33 | operate-incident-first-15-minutes | operate | advanced | GREEN | SAFE-TO-ADAPT |
| 34 | operate-eval-design-regression-guards | operate | advanced | AMBER | DISCARD-ENTIRELY |
| 35 | operate-auto-rollback-conditions | operate | advanced | GREEN | SAFE-TO-ADAPT |
| 36 | operate-slo-definition-user-journey | operate | advanced | GREEN | SAFE-TO-ADAPT |
| 37 | operate-observability-three-pillars | operate | advanced | GREEN | SAFE-TO-ADAPT |
| 38 | operate-oncall-incident-frontier-llm | operate | advanced | AMBER | SAFE-TO-ADAPT |
| 39 | operate-recovery-after-agent-drift | operate | advanced | AMBER | DISCARD-ENTIRELY |
| 40 | design-spacing-scale-rhythm | design | beginner | AMBER | DISCARD-ENTIRELY |
| 41 | design-typography-pairing | design | intermediate | AMBER | DISCARD-ENTIRELY |
| 42 | design-color-palette-system | design | intermediate | AMBER | DISCARD-ENTIRELY |
| 43 | design-frontend-page-skeleton | design | intermediate | GREEN | SAFE-TO-ADAPT |
| 44 | design-dashboard-information-density | design | advanced | GREEN | SAFE-TO-ADAPT |
| 45 | agent-orchestrator-subagent | agent | advanced | AMBER | DISCARD-ENTIRELY |
| 46 | agent-multi-agent-handoff | agent | advanced | AMBER | DISCARD-ENTIRELY |
| 47 | agent-error-recovery-strategy | agent | advanced | AMBER | DISCARD-ENTIRELY |
| 48 | agent-strict-tool-use | agent | advanced | AMBER | DISCARD-ENTIRELY |
| 49 | agent-clarifying-question-first | agent | intermediate | AMBER | DISCARD-ENTIRELY |
| 50 | agent-reflexion-self-eval-memory | agent | advanced | AMBER | DISCARD-ENTIRELY |

## Final 20 reserve

| # | ID | Category | Difficulty | Concept | Wording |
|---|---|---|---|---|---|
| R1 | research-news-roundup | research | intermediate | AMBER | SAFE-TO-ADAPT |
| R2 | research-deep-web-synthesis | research | advanced | AMBER | DISCARD-ENTIRELY |
| R3 | research-raschka-llm-architecture-card | research | intermediate | AMBER | SAFE-TO-ADAPT |
| R4 | decide-cost-benefit | decide | intermediate | AMBER | SAFE-TO-ADAPT |
| R5 | decide-reversibility | decide | intermediate | AMBER | SAFE-TO-ADAPT |
| R6 | operate-eval-regression-guard | operate | advanced | AMBER | SAFE-TO-ADAPT |
| R7 | operate-raschka-eval-pipeline | operate | advanced | AMBER | SAFE-TO-ADAPT |
| R8 | operate-rate-limit-retry | operate | intermediate | AMBER | SAFE-TO-ADAPT |
| R9 | operate-context-cache-create | operate | advanced | AMBER | SAFE-TO-ADAPT |
| R10 | operate-prompt-cache-decidable | operate | intermediate | AMBER | SAFE-TO-ADAPT |
| R11 | design-component-with-tokens | design | intermediate | AMBER | DISCARD-ENTIRELY |
| R12 | design-accessibility-wcag-aa | design | advanced | GREEN | SAFE-TO-ADAPT |
| R13 | agent-perplexity-cited-research-mode | agent | intermediate | GREEN | SAFE-TO-ADAPT |
| R14 | write-release-notes | write | advanced | AMBER | SAFE-TO-ADAPT |
| R15 | write-no-ai-tells | write | advanced | GREEN | SAFE-TO-ADAPT |
| R16 | write-api-reference | write | advanced | GREEN | SAFE-TO-ADAPT |
| R17 | write-docs-quickstart | write | intermediate | GREEN | SAFE-TO-ADAPT |
| R18 | code-onboard-new-engineer-codebase | code | intermediate | AMBER | SAFE-TO-ADAPT |
| R19 | operate-streaming-ux-overlay | operate | beginner | AMBER | SAFE-TO-ADAPT |
| R20 | operate-planner-coder-auditor-bridge | operate | advanced | GREEN | SAFE-TO-ADAPT |

## Authoritative totals

### Pilot (50)

- Records: 50
- Concept: 14 GREEN, 36 AMBER, 0 RED
- Wording: 36 SAFE-TO-ADAPT, 14 DISCARD-ENTIRELY, 0 EXCLUDE-CONCEPT

### Reserve (20)

- Records: 20
- Concept: 6 GREEN, 14 AMBER, 0 RED
- Wording: 18 SAFE-TO-ADAPT, 2 DISCARD-ENTIRELY, 0 EXCLUDE-CONCEPT

### Combined (70)

- Records: 70
- Concept: 20 GREEN, 50 AMBER, 0 RED
- Wording: 54 SAFE-TO-ADAPT, 16 DISCARD-ENTIRELY, 0 EXCLUDE-CONCEPT

### Category totals (combined)

- code 11
- write 12
- research 11
- decide 8
- operate 14
- design 7
- agent 7

## Pilot DISCARD-ENTIRELY IDs

14 IDs:

1. code-investigate-before-answering
2. research-hypothesis-tree
3. research-long-doc-quote
4. operate-eval-design-regression-guards
5. operate-recovery-after-agent-drift
6. design-spacing-scale-rhythm
7. design-typography-pairing
8. design-color-palette-system
9. agent-orchestrator-subagent
10. agent-multi-agent-handoff
11. agent-error-recovery-strategy
12. agent-strict-tool-use
13. agent-clarifying-question-first
14. agent-reflexion-self-eval-memory

## Provenance boundary

- Original Mac authoring source: `data.js`.
- Verified SHA-256: `1ee71b41ef92d81ac57f4c359146db6068101a664e005ab7bddbb414fe5e4631`.
- VPS runtime source: `prompts_data/prompts.json`.
- Converter: `prompts_data/_convert_data.py`.
- `data.js` is not in this Git repository.
- Remaining risk concerns third-party wording, attribution and reuse rights.

## Rewrite boundary

- **SAFE-TO-ADAPT** — light editorial rewrite and attribution review.
- **DISCARD-ENTIRELY** — replace prompt body and notes from first principles.
- **RED / EXCLUDE-CONCEPT** — not part of this scope.
- No publication before metadata, editorial review and legal/trust checks.
