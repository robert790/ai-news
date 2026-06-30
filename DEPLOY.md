# Deploy to Hugging Face Spaces · step by step

5 minutes from this doc to a live URL your friends can open.

> **Truth after the 2026-06-30 takeover (Hermes session)**
>
> - **GitHub is canonical.** The source of truth is `https://github.com/robert790/ai-news`. All app changes land there first (PR + CI smoke), before any Hugging Face push.
> - **Hugging Face is a manual deploy target only.** There is no GitHub Action, webhook, or repo secret that mirrors `main` to HF. The only way the Space updates today is `git push huggingface main` from a machine that has the HF token in its git credential store.
> - **HF tokens must not be stored in this repo** (no `.env`, no GitHub Actions secret, no CI variable). The HF credential lives only on Robert's workstation.
> **The current LLM is Groq, not DeepSeek.** `config.py` reads `GROQ_API_KEY` (and optionally `ANTHROPIC_API_KEY`). `DEEPSEEK_API_KEY` is a legacy name from an earlier build and is **ignored by the current code**; you can leave it or remove it from the HF Space's variables/secrets as you prefer — current code does not read it.
> - **Defer automated deploys.** Until you explicitly want a workflow-driven HF mirror, keep deploys explicit and per-release. The pattern is: green CI on GitHub → manual `git push huggingface main` → ~60s HF rebuild → smoke-check the live URL.
- **Drift history.** At takeover on 2026-06-30, public probes suggested the live Space was some hours behind GitHub `main` (no auto-mirror was active at that moment). Re-check the Space's `last-modified` after each manual push — if it stays still, the push didn't land.

## Prerequisites

1. **A Hugging Face account** — free at [huggingface.co/join](https://huggingface.co/join)
2. **A Git repo on your machine** — already done, you're in `/Users/zero/Minimax Projects/ai-news/`

## Step 1 · Create the Space (in browser)

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Space name:** `ziarul-digital` (or whatever you want)
   - **License:** MIT
   - **SDK:** Streamlit
   - **Space hardware:** CPU basic · Free (perfect for this)
   - **Visibility:** Public (so friends can access without login)
3. Click **Create Space**

You'll see a page with a "git push" command. **Don't run it yet.**

## Step 2 · Add HF as a git remote

In your terminal:

```bash
cd "/Users/zero/Minimax Projects/ai-news"
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/ziarul-digital
git remote -v
```

You should see both `origin` (none yet — that's fine) and `huggingface`.

## Step 3 · Push the code

```bash
git push huggingface main
```

It will ask for credentials. Use:
- **Username:** your HF username
- **Password:** your HF access token (NOT your account password)

Get the token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) → "+ Create new token" → Type: **Write** → copy it.

If the push succeeds, you'll see HF start building the Space. Watch the build log in the browser at `huggingface.co/spaces/YOUR_USERNAME/ziarul-digital`.

## Step 4 · Add the API keys (recommended for live summaries)

Without an LLM key the app runs in demo mode (template summaries — still works), but
real summaries require the Groq key (the current LLM is Groq, not DeepSeek).

To get real LLM summaries:

1. Get a free Groq key at [console.groq.com/keys](https://console.groq.com/keys)
2. (Optional, premium tier) get an Anthropic key at [console.anthropic.com](https://console.anthropic.com)
3. In your Space, go to **Settings** → **Variables and secrets**
4. Click **+ New secret**
5. For Groq:
   - Name: `GROQ_API_KEY`
   - Value: paste your key
6. (Optional) repeat for `ANTHROPIC_API_KEY`
7. Save

The Space restarts automatically.

> **Legacy / stale names** — `DEEPSEEK_API_KEY` was used in an earlier build but is
> no longer read by `config.py`. If it is still set in the Space's secrets, it does
> nothing for current code; remove only after confirming no older deployment or
> runtime still references it (the only paths that read env are `config.py` and the
> `llm/` package, neither of which names it). Safe to keep or delete.

## Step 5 · Share

Your app is live at:

```
https://huggingface.co/spaces/YOUR_USERNAME/ziarul-digital
```

There's usually also a custom subdomain like:

```
https://YOUR_USERNAME-ziarul-digital.hf.space
```

Share that link. Done.

## After deploy

The app auto-deploys on every `git push huggingface main`. To update:

```bash
# make changes locally, test with `streamlit run app.py`
git add .
git commit -m "describe what you changed"
git push huggingface main
```

## Troubleshooting

**Build fails:** check the build log in the Space page. Most common cause: missing dep in `requirements.txt`.

**App loads but stays blank:** usually means `app.py` threw an error. Check the **Logs** tab in the Space.

**Port issues:** HF Streamlit Spaces run on port 7860 by default. No action needed unless you have a custom Dockerfile (we don't).

**Secrets not working:** the env var names in code (`config.py` reads `GROQ_API_KEY` and optionally `ANTHROPIC_API_KEY`) must match exactly what you set in Settings.

## Why Hugging Face (and not Vercel / Render / Railway)?

- **Free** with no credit card
- **Designed for AI/ML apps** — Streamlit is a first-class citizen
- **Git-based deploys** — no CI/CD setup needed
- **Built-in sharing** — public URL, embed, API
- **No sleep/cold-start** — apps stay warm

When we add the Jobs module (v0.6) and need auth, we'll evaluate Supabase + Vercel. For now, HF is perfect.