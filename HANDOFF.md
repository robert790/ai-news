# Handoff · OpenRadar

> Romanian-source AI product, English-first user surface.
> Last refreshed: 2026-07-04 · PR #20 (docs-only).

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
| Production SHA | `45d2b03cced77d511cdf93916a4aa7510fd56b26` |
| Last merged PR | **#19 — Learn Real Guide** (squash-merged 2026-07-02) |
| Previous tip | `f245756` (PR #18) |
| HF Space health | 7/7 endpoints HTTP 200 (verified 2026-07-02 post-merge) |
| CI workflow | green on `45d2b03` |
| Deploy-to-HF workflow | green on `45d2b03` |

### Rollback (preferred — preserves history)

```bash
git revert --no-edit 45d2b03cced77d511cdf93916a4aa7510fd56b26
git push origin main
```

HF Space auto-redeploys on push (see §4).

### Rollback (emergency — only if no other work has landed)

```bash
git reset --hard f245756
git push --force-with-lease origin main
```

**DANGER:** `--force-with-lease` rewrites remote history. Use only when no collaborator has pulled `45d2b03`.

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
| **Jobs** | Skill-gap matcher between CV and AI infra roles (Romania focus). |

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

1. **PR #21 candidate — Learning progress persistence.** Write `completed_chapters` + per-method `method_done_*` flags to `./data/progress.json`; read on app start. Highest-impact UX improvement that does not require a new visual layer. On the in-repo short-term list from the pre-PR-#19 HANDOFF.
2. **Prompt Kits copy/code UX.** Polish the curated prompt library section (copy buttons, code block rendering, search/filter).
3. **Mobile polish.** Audit ≤720px breakpoint across all five sections; fix any clipping, horizontal overflow, or hidden nav.
4. **Stale remote branch cleanup (later).** 12 `feat/*` branches + 2 `feature/pr-*` branches. Belongs to a dedicated cleanup PR, not mixed into a feature PR.

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
| Current production SHA | `git rev-parse origin/main` (should be `45d2b03…`) |
| Last PR | `gh pr list --state merged --limit 1` |
| Open PRs | `gh pr list --state open` |
| HF live | `https://vrobert94-ai-news.hf.space/` |
| Rollback (safe) | `git revert --no-edit 45d2b03cced77d511cdf93916a4aa7510fd56b26` |
| Preview start | `bash scripts/preview.sh` |
| Preview stop | `bash scripts/stop-preview.sh` |
| Obsidian HANDOFF | `~/obsidian/AI-Operating-System/02-Current-Projects/openradar/HANDOFF.md` |
| Profile card | `~/obsidian/AI-Operating-System/02-Current-Projects/openradar/profile-card.md` |

---

*This file is a quick-reference, not a journal. Detailed session history lives in Obsidian; architectural decisions live in `07-Decisions/`.*
