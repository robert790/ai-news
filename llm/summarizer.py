"""LLM summarizer · takes a news item and produces a Romanian (or English) summary.

Uses DeepSeek (OpenAI-compatible) by default. Falls back to a deterministic
template-based summary when no API key is set, so the app still demos.

The summary style target: 2-3 sentences, friendly, no jargon, explains
why a Romanian reader should care.
"""
from openai import OpenAI
import config
from scrapers import NewsItem


# ---------- Demo fallback (no API key) ----------

def _demo_summary(item: NewsItem, language: str = "ro") -> str:
    """Cheap deterministic summary so the UI is never empty."""
    if language == "ro":
        return (
            f"O postare pe Hacker News despre {item.title[:80]}. "
            f"A primit {item.score} puncte de la comunitate. "
            f"Citește mai mult la sursă."
        )
    return (
        f"A Hacker News story about {item.title[:80]}. "
        f"Got {item.score} points from the community. "
        f"Read more at the source."
    )


# ---------- Real LLM path ----------

SYSTEM_PROMPT_RO = """Ești un redactor AI pentru un buletin de știri tech în limba română, destinat cititorilor interesați de AI dar care nu sunt ingineri. Rezumă fiecare știre în 2-3 propoziții scurte, în română, cu un ton prietenos și fără jargon inutil. Dacă știrea este relevantă pentru România sau Europa, menționează astfel clar. Dacă nu, prezintă-o ca pe o știre globală importantă."""

SYSTEM_PROMPT_EN = """You are an AI editor for a friendly tech news bulletin. Summarize each story in 2-3 short sentences, plain language, no jargon. If the story is relevant to Romania or Europe, mention that clearly. Otherwise frame it as an important global story."""


def _build_user_prompt(item: NewsItem) -> str:
    return f"""Titlu: {item.title}
Sursă: {item.source}
Scor comunitar: {item.score}
URL: {item.url}
Snippet: {item.summary or '(no snippet)'}

Scrie rezumatul în 2-3 propoziții."""


def _summarize_with_deepseek(item: NewsItem, language: str = "ro") -> str:
    """Call DeepSeek via OpenAI-compatible API."""
    if not config.has_deepseek():
        return _demo_summary(item, language)

    client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)
    system = SYSTEM_PROMPT_RO if language == "ro" else SYSTEM_PROMPT_EN

    try:
        resp = client.chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": _build_user_prompt(item)},
            ],
            max_tokens=200,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[summarizer] DeepSeek call failed: {e}")
        return _demo_summary(item, language)


def summarize(item: NewsItem, language: str = None) -> str:
    """Public entry point. Picks language from config if not specified."""
    if language is None:
        language = config.APP_LANGUAGE if config.APP_LANGUAGE in ("ro", "en") else "ro"
    return _summarize_with_deepseek(item, language)


def summarize_batch(items: list, language: str = None) -> list:
    """Summarize a batch. Sequential for now; could parallelize later."""
    out = []
    for item in items:
        item.summary = summarize(item, language)
        out.append(item)
    return out


if __name__ == "__main__":
    from scrapers import fetch_hackernews_ai
    items = fetch_hackernews_ai(limit=3)
    if items:
        summarized = summarize_batch(items)
        for item in summarized:
            print(f"→ {item.title[:60]}")
            print(f"  {item.summary}\n")