# Handoff · OpenRadar

> Romanian-source AI product, English-first user surface.
> Last refreshed: 2026-07-04 · PR #25 (docs-only · post-#26 HANDOFF checkpoint · updated after PR #24 and PR #26).

---

## 0. Source of truth

**Read in this order. Newer overrides older.**

1. **GitHub `main` and open PRs** — `robert790/ai-news` · canonical.
2. **Obsidian OpenRadar HANDOFF** — `~/obsidian/AI-Operating-System/02-Current-Projects/openradar/HANDOFF.md`.
3. **This file** — in-repo quick-reference; lags Obsidian by intent.
4. **Old default-profile sessions** — archive only. Do not use as live context.

---

## 1. Active profile

| Field | Value |
|-------|-------|
| Hermes profile | `openradar` |
| Repo (local) | `/home/opencode/projects/openradar` |
| GitHub | `robert790/ai-news` |
| HuggingFace Space | `vrobert94/ai-news` |
| Live URL | `https://vrobert94-ai-news.hf.space/` |
| Default model | `MiniMax-M3` via `custom:minimax-v1` (1M context) |
| OpenAI / GPT-5.5 | **not available on this profile** — use `default` or ChatGPT Control Room |

**New OpenRadar sessions must start in the `openradar` profile and begin with a read-only grounding check** (see §9). Old default-profile OpenRadar sessions are historical archive only.

---

## 2. Current production

| Field | Value |
|-------|-------|
| Production branch | `main` |
| Production SHA | `f956edfb4efc23149e16b5b3c13bf3e7acdc88af` |
| Last merged PR | **#26 — Tools + Jobs UX cleanup** (squash-merged 2026-07-04) |
| Previous tip | `60e59c50` (PR #24 — Romania Jobs Expansion) |
| HF Space health | 7/7 endpoints HTTP 200 (verified 2026-07-04 post-#26 merge) |
| CI workflow | green on `f956edfb` |
| Deploy-to-HF workflow | green on `f956edfb` |

### Recent merged PRs (chronological)

- **#20 — Refresh Repo HANDOFF** (2026-07-04, docs-only). Replaced the Mavis-era in-repo HANDOFF with the post-#19 quick-reference.
- **#21 — Learning Progress Link UX** (2026-07-04). Added the "How your progress is saved" affordance + Reset progress button to the Learn section. The persistence transport itself (`learning/progress.py` signed query-param token) shipped earlier as PR #3 and was already on main.
- **#22 — Prompt Kits How-to-use + hierarchy polish** (2026-07-04). Two small UX changes to the Prompt Kits section: a short English how-to-use block, and a fix to the section heading hierarchy so the "Prompt Bible" h1 correctly introduces the full search/filter area (not the kit grid).
- **#23 — HANDOFF checkpoint** (2026-07-04, docs-only). Refreshed this file after PR #21 + PR #22; updated production SHA, last-merged-PR, recent-PR list, and the next-task pointers.
- **#24 — Romania Jobs Expansion** (2026-07-04). Content-only expansion of the Romania role map from 4 to 7 role directions: AI Automation Engineer, Data + AI Analyst, AI Solutions Architect added to the existing DRUID/Bitdefender/ClusterPower/UiPath cards. New cards use neutral company labels ("Automation teams / partners", "Enterprise data teams", "IT services / consulting") — no claim is made that any company is currently hiring. Section copy updated from "Four" to "Seven" (English) and from "Patru" to "Șapte" (Romanian). Confirms Romania-first positioning (see §6).
- **#26 — Tools + Jobs UX cleanup** (2026-07-04). Three small UX changes: (a) Jobs and Tools tabs now have one h1 each (the second `section_head` in each was demoted to a small `or-eyebrow` block, matching PR #22's pattern); (b) Prompt Kits' "HOW TO USE" block moved from mid-page to the top of the section so first-time users see the instructions before the catalog; (c) two Romanian offline-fallback strings on Tools translated to English (`Încearcă din nou` → `Try again`). Also added an honest intro line under the Tools eyebrow: "Three feeds to scan today. None are Romania-specific yet — they help you see what is moving in AI tools globally." `app.py` only, no theme change, no behavior change, no new files.

### Rollback (preferred — preserves history)

```bash
git revert --no-edit f956edfb4efc23149e16b5b3c13bf3e7acdc88af
git push origin main
```

HF Space auto-redeploys on push (see §4).

### Rollback (emergency — only if no other work has landed)

```bash
git reset --hard 60e59c50
git push --force-with-lease origin main
```

**DANGER:** `--force-with-lease` rewrites remote history. Use only when no collaborator has pulled `f956edfb`.

---

## 3. Workflow lanes

| Lane | Purpose | Allowed actions |
|------|---------|-----------------|
| **WORK** | open/fix PRs, preview locally | read, branch, edit, commit, push branch, open PR, run preview |
| **REVIEW** | read-only browser/QA | inspect, screenshot, comment on PR, run preview |
| **PROD** | merge/deploy/health-check | merge approved PR, verify HF deploy, smoke-check, rollback if needed |
| **Control Room** | owner/ChatGPT approves next task and merge/no-merge | decision, scope change, abort |

**WORK never merges. PROD never opens new branches. REVIEW never edits files.** ChatGPT Control Room (owner-facing) decides what becomes the next PR and signs off on merge.

---

## 4. Deploy truth

**HF deploy is automated via GitHub Actions on push to `main`.** The `Deploy to Hugging Face Space` workflow runs on every push; successful runs are visible in the GitHub Actions tab.

- Do **not** claim HF deploy is manual unless future verification proves automation changed.
- A successful CI run + a successful Deploy-to-HF run on the same commit means production is mirrored. Verify both before announcing a release.
- If Deploy-to-HF fails on `main`, treat it as an incident: stop merging, post in Control Room, hold all PRs that target `main` until the deploy is green or rolled back.

---

## 5. Preview

| Action | Command |
|--------|---------|
| Start preview | `bash scripts/preview.sh` |
| Stop preview | `bash scripts/stop-preview.sh` |
| Port | `8780` |

**Post-merge state:** preview is **stopped**. Start it only when actively reviewing a branch.

---

## 6. Product state

### User-facing sections (PR #19 onwards)

| Section | What it is |
|---------|-----------|
| **Home** | Landing — OpenRadar identity, daily briefing anchor. |
| **Tools** | Curated tool directory. |
| **Prompt Kits** | Curated prompt library with copy buttons. |
| **Learn** | Guided English-first course (10 chapters, PR #19). |
| **Jobs** | Romania role map — 7 AI role directions (PR #24) with outbound search paths to LinkedIn / BestJobs / eJobs / Indeed RO. Single h1, "ROLE MAP" is a small or-eyebrow subsection header (PR #26). Not a live job board. |

### Internal section keys (compatibility, not copy)

The runtime may still use older internal keys — `groq`, `news`, `prompts`, `learning`, `jobs` — in `st.session_state`, `st.query_params`, and the section dispatch table. This is **internal compatibility**, not product copy. The user-facing tab names are the section names from the table above.

If you touch the section dispatch:

- Update the public-facing name in `app.py` (nav + section render) **and** the internal key in the same commit.
- Keep `?section=learning&learn_chapter=ch3` deep-link behaviour working — old URLs in the wild rely on it.
- Verify with `scripts/preview.sh` on port 8780 before opening the PR.

### Learn (PR #19 specifics)

- 10-chapter guided course, English-first.
- Romanian source content is **preserved** in the chapter corpus (in-repo `learning/content/`) but is not rendered in the English guide. Do not delete the Romanian source — future work may re-surface it (e.g. locale toggle, RAG corpus).
- Per-chapter verifiers, methods overlay, "Următorul capitol" card, methods progress counter all live in `learning/learning_render.py` and `learning/chapters.py`.

### Stack (current)

- Python 3.9 (HF) / 3.13 (local VPS)
- Streamlit 1.50 local · **1.32.0 pinned on HF** via the HF Space Dockerfile
- `httpx`, `beautifulsoup4`, `openai` client pointed at Groq
- Optional Anthropic path via `ANTHROPIC_API_KEY` for the `PREMIUM_ENABLED` tier
- No pydantic, no SQLAlchemy, no LangChain — kept minimal for HF cold start

---

## 7. Known failures / do-not-continue

These are explicit no-fly zones. Reviving any of them blocks the next PR.

- **Do not revive PR #13 — homepage radar/personality redesign.** Closed; direction was rejected.
- **Do not revive PR #14 — Home Workbench Dashboard.** Closed; direction was rejected.
- **Do not use stale Mavis-era copy, the "Mavis Agent" name, or "minimax Code Agent" framing in user copy.** This repo's HANDOFF was Mavis-era until PR #20; that era is closed.
- **Do not do a broad homepage redesign without explicit owner approval.** Small targeted edits inside the existing Home section are fine; structural redesigns require Control Room sign-off.
- **Do not claim HF deploy is manual.** It is automated (see §4). Future re-verification may change this, but until then, do not write the older claim anywhere.
- **Do not delete Romanian source content from `learning/content/`.** It is preserved on purpose.
- **Do not commit secrets, `.env`, or HF/GitHub tokens.** Use `.env.example` for new env knobs.

---

## 8. Current next likely tasks

In priority order, subject to Control Room sign-off per task:

1. **Done — Learning progress persistence (PR #3 transport + PR #21 affordance).** The transport is a stdlib-only signed query-param token: snapshot of Learning state is zlib-compressed + urlsafe-base64-encoded into `?p=...`; restoring is a one-shot gated by a session marker. See `learning/progress.py` for `snapshot_for_chapters / encode / decode / apply_incoming_query_param / sync_query_param`. No disk, no cookies, no localStorage, no auth, no database. The first-class UX work (the "How your progress is saved" affordance + Reset button) shipped as PR #21.
2. **Done — Prompt Kits copy/code UX (PR #22).** Short English how-to-use block, light kit-card hierarchy polish (dropped redundant "▸ KIT N OF 5" eyebrow, made the outcome line legible, moved the "Prompt Bible" h1 to the full search/filter area).
3. **Done — Jobs + Tools + Prompt Kits UX cleanup (PR #26).** One h1 per tab (the second `section_head` in Jobs and Tools demoted to a small `or-eyebrow` block); Prompt Kits' "HOW TO USE" block moved to the top of the section; two Romanian offline-fallback strings on Tools translated to English.
4. **Next candidate — Responsive / card system audit.** Audit the card system (or-mini, or-bento-mini, or-static-action) at ≤720px and ≤1024px viewports across all five sections. Fix any clipping, horizontal overflow, or hidden nav. Earlier "Mobile polish" intent (before PR #26) was narrow; this widens to a card-system audit and explicitly includes the kit bento (2-up grid) and the role-map bento (2-up grid, 7 cards = 4 rows with 1-card last row) which both deserve a per-card-width check. **Not started — pending Control Room sign-off.**
5. **Stale branch cleanup (pending, separate maintenance action).** A handful of `feat/*` and `feature/pr-*` remote branches are stale pointers to old state. **The exact list must be re-verified at the time of cleanup** — branch counts in this file have been wrong before and the previous audit caught a count mismatch. Do **not** delete branches from this HANDOFF; re-run `git branch -r` and a per-branch reachability check at cleanup time. Do **not** revive the closed PR #13 (homepage radar/personality redesign) or PR #14 (Home Workbench Dashboard) — see §7.

**Note:** PR #25 (this docs checkpoint) was originally created after PR #24 and remained open. It was rebased onto post-#26 `main` and updated in-place to reflect the post-#26 state, instead of being closed and superseded by a new PR.

---

## 9. Session guidance

**Starting a new OpenRadar session on this profile:**

1. **Confirm profile and model.** You should already be on `openradar` with `MiniMax-M3` / `custom:minimax-v1`. If not, switch before any work.
2. **Read-only grounding check.** `pwd`, `git status -s`, `git branch --show-current`, `git log --oneline -8`, `git rev-parse origin/main`. Stop if dirty.
3. **Re-read §0–§4 of this file** (and the Obsidian HANDOFF if the question touches workflow, rollback, or HF state).
4. **Re-read the Obsidian profile card** for the current profile's allowed-actions and stop-conditions.
5. **Pick the lane (WORK / REVIEW / PROD / Control Room)** and stay in it. Do not silently mix lanes.
6. **Plan → owner approval → execute.** WORK does not merge. PROD does not open branches. The Control Room signs off on the next task and on merge.

**Old default-profile OpenRadar sessions are historical archive only.** Do not use them as live context; they predate the profile split, the WORK/PROD lane split, and the automated HF deploy.

---

## 10. Quick reference

| Need | Go to |
|------|-------|
| Current production SHA | `git rev-parse origin/main` (should be `f956edfb…`) |
| Last PR | `gh pr list --state merged --limit 1` |
| Open PRs | `gh pr list --state open` |
| HF live | `https://vrobert94-ai-news.hf.space/` |
| Rollback (safe) | `git revert --no-edit f956edfb4efc23149e16b5b3c13bf3e7acdc88af` |
| Preview start | `bash scripts/preview.sh` |
| Preview stop | `bash scripts/stop-preview.sh` |
| Obsidian HANDOFF | `~/obsidian/AI-Operating-System/02-Current-Projects/openradar/HANDOFF.md` |
| Profile card | `~/obsidian/AI-Operating-System/02-Current-Projects/openradar/profile-card.md` |

---

*This file is a quick-reference, not a journal. Detailed session history lives in Obsidian; architectural decisions live in `07-Decisions/`.*
