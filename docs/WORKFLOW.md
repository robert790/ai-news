# OpenRadar Delivery Workflow

Single source of truth for how a change goes from a PR to a live HF
Space, and how visual QA happens on the way. If anything in this file
contradicts `DEPLOY.md` or `HANDOFF.md`, this file wins.

## TL;DR

- GitHub `main` is the source of truth.
- VPS PR preview = `bash scripts/preview.sh` on port **8780** (loopback).
- Mac tunnels to the VPS preview for visual QA.
- HF live is separate from VPS preview.
- HF deploy is **manual** from Robert's workstation until deploy
  automation is approved (not yet shipped).

## VPS PR preview

**One command, one port:**

```bash
bash scripts/preview.sh
```

That script:

1. Verifies cwd is the OpenRadar git repo.
2. Refuses to start if port 8780 is held by something other than
   `streamlit run app.py` (so it never trampling on Hermes or any
   unrelated service).
3. Spawns `streamlit run app.py` bound to `127.0.0.1:8780`,
   logs to `preview.log`, and waits up to 15s for
   `/_stcore/health` to come up.
4. Prints the branch, commit, PID, health status, the Mac SSH
   tunnel command, and the browser URLs.

**Mac tunnel** (run on the workstation, NOT on the VPS):

```bash
ssh -N -L 8780:127.0.0.1:8780 opencode@srv1351019
```

Then open in the Mac browser:

```
http://127.0.0.1:8780
http://127.0.0.1:8780/?section=learning
```

## Rules

1. **8780 is the standard OpenRadar PR preview port.** Don't keep
   inventing new ports (8765, 8766, 8767, 8768, 8781, etc.). If a
   previous PR review left a stale 8780 server, restart it via
   `bash scripts/preview.sh` (the script re-uses a healthy existing
   listener instead of double-binding).
2. **If 8780 is held by something that isn't `streamlit run app.py`,
   stop and inspect.** `preview.sh` will refuse to start in that
   case. Use `ss -ltnp | grep 8780` and `ps -p <pid>` to identify
   the holder.
3. **HF live is separate from VPS preview.** HF Space rebuilds
   only happen via `git push huggingface main` from Robert's
   workstation (see `DEPLOY.md`). Until HF deploy automation ships,
   PR visual QA on the VPS is the only way to see in-progress work
   live.
4. **Mac is a deploy bridge, not a preview host.** Until HF deploy
   automation exists, Mac's role is exclusively `git push
   huggingface main` after a PR is merged. The Mac does NOT run a
   second `streamlit run app.py` server for QA — that lives on
   the VPS, on port 8780, accessed via SSH tunnel.

## Stop

```bash
bash scripts/stop-preview.sh
```

Only kills processes whose cmdline matches `streamlit run app.py`
bound to 8780. Never touches Hermes (9119) or unrelated listeners.

## Why this shape

- One port = one Mac tunnel command = no confusion about which
  URL the reviewer's browser is hitting.
- Loopback bind (`127.0.0.1`) = the server is reachable only via
  the SSH tunnel, never exposed to the LAN.
- The script refuses to start on a busy wrong-port = it can't
  accidentally kill an unrelated service or fork-bomb the box.
- Manual HF deploy = zero new secrets in the repo, zero new
  GitHub Actions, zero new failure modes. We add automation only
  when the friction is real and the design is settled.

## HF auto-deploy (post-PR #8)

`.github/workflows/deploy-hf.yml` mirrors GitHub `main` to the
Hugging Face Space (`vrobert94/ai-news`) on every push to `main`.
Trigger is also exposed via `workflow_dispatch` for manual re-runs.

**Required repo secret:** `HF_TOKEN` — an HF fine-grained write
token scoped to the Space. Set it in
**Settings → Secrets and variables → Actions → New repository
secret**. Never store the token in this repo, in `.env`, on the
VPS, or in any other workflow step that could echo it.

**Flow after a merge to `main`:**

```
merge to main
   ↓
ci.yml smoke (informational)
   ↓
deploy-hf.yml job: sync to HF Space (requires HF_TOKEN)
   ↓
HF Space rebuilds in ~60s
   ↓
Robert checks Space URL → done
```

**Manual fallback** (if the workflow is broken or paused):

```bash
# On Robert's workstation, with the HF token in his git credential store:
git push huggingface main
```

See `DEPLOY.md` for the historical full-throw instructions.

**Why this shape:**

- One secret (HF_TOKEN), stored on GitHub's side, never on the VPS.
- Workflow never runs on `pull_request` — PR CI lives in `ci.yml`
  and doesn't burn HF quota on every PR push.
- Workflow never writes the token to stdout (masked via
  `::add-mask::` and sourced only from `secrets.HF_TOKEN`).
- Manual Mac push remains the documented fallback — same HF token,
  no new failure modes.

## Future (not yet shipped)

These are the planned next steps, parked until the workflow above
is the daily routine:

- **Build stamp** — `build_info.json` (gitignored, generated at
  runtime) with the live commit SHA + branch + PR number, rendered
  top-right of every page so Robert always sees which commit is on
  screen.
- **Branch protection** — `Require CI / smoke to pass before
  merge` set in the GitHub UI. Configured by Robert, not from this
  repo.