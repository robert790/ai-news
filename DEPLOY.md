# Deploy to Hugging Face Spaces · step by step

5 minutes from this doc to a live URL your friends can open.

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

## Step 4 · Add the API key (optional but recommended)

Without DEEPSEEK_API_KEY the app runs in demo mode (template summaries — still works).

To get real LLM summaries:

1. Get a DeepSeek key at [platform.deepseek.com](https://platform.deepseek.com) (free tier gives plenty)
2. In your Space, go to **Settings** → **Variables and secrets**
3. Click **+ New secret**
4. Name: `DEEPSEEK_API_KEY`
5. Value: paste your key
6. Save

The Space restarts automatically.

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

**Secrets not working:** the env var name in code (`config.py` reads `DEEPSEEK_API_KEY`) must match exactly what you set in Settings.

## Why Hugging Face (and not Vercel / Render / Railway)?

- **Free** with no credit card
- **Designed for AI/ML apps** — Streamlit is a first-class citizen
- **Git-based deploys** — no CI/CD setup needed
- **Built-in sharing** — public URL, embed, API
- **No sleep/cold-start** — apps stay warm

When we add the Jobs module (v0.6) and need auth, we'll evaluate Supabase + Vercel. For now, HF is perfect.