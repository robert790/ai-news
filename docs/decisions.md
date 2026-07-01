# Decisions

Living log of the "why" behind big choices. Newest on top.

## 2026-07-01 · Product repositioning — AI Career + Tools Radar (PR #10)

**Was:** Romanian-first AI news + learning + jobs aggregator.
**Now:** AI Career + Tools Radar. Five tabs: **Today / Tools / Learn / Jobs / Prompt Kits.**
Target user: people who want to learn AI, use better AI tools, and find AI-related work.

- **Internal section key `news` was deliberately kept** for the new Tools tab to preserve every existing `?section=news` deep-link. Renaming the key to `tools` is a separate, focused PR. Tracked as follow-up debt in app.py, README.md, and the PR body.
- **Prompt Kits is the primary product surface** on the Prompts tab. The full Prompt Bible (1,137 prompts + filters) is demoted to a labeled secondary "power-user" layer below the kits row.
- **Jobs stays static** (role + skill map + outbound search paths). No fake live job feed was introduced.
- **Tools is reorganized into 4 curated use-case buckets** (Build / Ship / Write & Decide / Discover), capped at 4 cards per bucket — explicitly **not** a directory dump.
- **Learn** relabeled, copy nudge to "paths not course". Content unchanged.

Scope deliberately excludes: APIs, DB, auth, payments, GPS, scraping, live job feeds, full redesign, deploy workflow changes.

## 2026-06-27 · Product refocus

**Original scope:** AI news + premium tier + NFC card physical access.

**New scope:** AI news + Learn module (RAG over AI Road) + Jobs module (aggregator + skill matching). NFC cards deferred to v2.0+.

**Why we changed:**

1. NFC distribution needs a working product to distribute. We're not there yet.
2. Personalized learning is a stronger moat than a paywall.
3. Job matching closes the loop — learning → earning is a much stickier narrative than learning alone.
4. Three modules (news, learn, jobs) give three reasons to return, not one.

**User flow:** news → deep dive via RAG → skill extraction → job match.

**No tech debt from pivot:** the modules (rag/, jobs/) were already in the roadmap, just not activated yet. README and roadmap updated.

## 2026-06-27 · Tooling decisions

**Why GitHub + HF Spaces + Vercel + Supabase (in that order)?**

- **GitHub** is the standard for source code hosting. Public repos = portfolio. Every recruiter and investor checks.
- **Hugging Face Spaces** for the app — free Streamlit hosting, official support, perfect for AI products. Alternative: Streamlit Community Cloud (also good).
- **Vercel** for any landing page or Next.js frontend we add later. Free, instant deploy, custom domain support.
- **Supabase** when we need auth + DB. Free tier is generous (500MB DB, 50k monthly active users).

**Why not Hermes CLI yet?**

Hermes is great for code-heavy tasks but we're too early to fragment tooling. One builder (Mavis) + one learner (Zero) = faster learning. We add Hermes when the project needs parallel execution on routine work.

**Why no card access in v1?**

NFC card is a v2.0 concept that depends on having a working product + paying customers + physical distribution. Building it now is premature optimization. We focus on making the digital product excellent first.

## 2026-06-27 · Initial scaffolding

**Why Romanian-first?**

- No competitor exists in Romanian language
- Owns the "localized AI for our market" gap from The AI Road Ch 10
- Aligns with user's language + cultural fluency

**Why DeepSeek as primary LLM?**

- $0.14-0.28 per M tokens vs $2.50-15 for OpenAI
- Quality is comparable for summarization
- Saves money during the testing phase
- Anthropic reserved for premium tier (deeper reasoning)

**Why Streamlit for v1?**

- Fastest path to a working UI
- Python-native (no JS context-switching)
- Easy to upgrade to Next.js later when product-market fit emerges

**Why one source (HN) for v0.1?**

- Tighter feedback loop on the simplest thing that works
- HN Algolia API is keyless + free
- Validates the LLM-summarize-in-Romanian pipeline end-to-end
- Other sources plug in as drop-in replacements

---

## Next decisions to make

- Auth approach for premium tier (Clerk, Supabase, custom?)
- Payment provider (Stripe, Lemon Squeezy?)
- Specific Romanian-language tech RSS feeds to add (startupcafe.ro, wall-street.ro, hotnews.ro tech section?)
- Skill extraction approach for jobs module (LLM extraction vs manual taxonomy)
- Whether to build user profiles in v1 or defer to v1.5