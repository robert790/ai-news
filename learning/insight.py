"""Learning × Groq · Insight generation for the Learning tab.

Three Groq-powered features:

1. `chapter_tldr(chapter_id)`            — 2-3 sentence summary,
                                          rendered at the top of Read
                                          tab. Cached per chapter/day.
2. `azis_take(chapter_id, recent_news)`  — 1 short paragraph that
                                          connects the chapter's lesson
                                          to what was in the news feed
                                          today. Cached per chapter/day.
3. `ask_azi(question, chapter_id)`       — Conversational Q&A with
                                          chapter as context. No cache
                                          (real-time, but rate-limited
                                          in app.py).

Caching strategy: pure in-memory (lru_cache on the chapter_id+date
key). On Streamlit reruns we re-evaluate function args but the lru
cache returns the cached string — no extra Groq call.

Fallback: if Groq is not configured or the call fails, deterministic
demo strings so the UI is never empty. This matters on first deploy
before HF Variable is wired.

Why this works for engagement: ChatGPT can give you the chapter
explanation. ChatGPT CAN'T tell you "this is what landed in
Hacker News this week about THIS chapter's topic". That's the moat.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
from functools import lru_cache
from typing import Optional

import config


# ---------- Date-keyed cache ----------

def _today_key() -> str:
    return _dt.date.today().isoformat()


@lru_cache(maxsize=128)
def _tldr_cache(chapter_id: str, day: str) -> str:
    """Memoized wrapper. Forces re-call only when day changes."""
    return _generate_tldr(chapter_id)


@lru_cache(maxsize=128)
def _take_cache(chapter_id: str, day: str, news_signature: str) -> str:
    return _generate_take(chapter_id, news_signature)


# ---------- Demo fallbacks ----------

_DEMO_TLDR = {
    "ch1": "Rețeaua neuronală e un lanț de operații matematice simple. Fiecare strat ia input-ul, îl transformă puțin, și-l dă mai departe. La final, din ingrediente iese un răspuns — la fel cum dintr-o rețetă iese o prăjitură.",
    "ch5": "Prompting-ul e arta de a fi clar cu AI-ul: îi spui cine e, ce are de făcut, ce exemple vrei. Cu cât promptul e mai precis, cu atât răspunsul e mai util. E cea mai importantă skillă pe care o poți învăța.",
    "ch8": "România are deja GPU-uri, clustere HPC și un plan pe hârtie. Cloud-ul privat de la ICI, plus Bitdefender și clusterele din Iași, înseamnă că infrastructura există. Mai lipsește adoptarea.",
    "ch11": "Există 5 tipuri principale de muncă în AI: research, applied AI, MLOps, AI infra, și produs. Fiecare are skill stack diferit. Alege după cum gândești, nu după ce e trendy.",
}


def _demo_tldr(chapter_id: str) -> str:
    if chapter_id in _DEMO_TLDR:
        return _DEMO_TLDR[chapter_id]
    return (
        "Acest capitol face parte din AI Road — un curs scurt, fără fluff, "
        "scris pentru cititori tehnici din România. Citește-l, apoi încearcă "
        "verificatorii și construiește ce e în secțiunea «Build this»."
    )


def _demo_take(chapter_id: str, news_sig: str) -> str:
    return (
        "Azi, pe fluxul nostru de știri, nu am găsit potriviri directe "
        "pentru acest capitol. Verifică din nou după următorul refresh — "
        "cross-refs sunt generate pe baza articolelor din ultimele 7 zile."
    )


# ---------- Groq path ----------

from openai import OpenAI
from learning.chapters import get_chapter
from learning.reader import load_chapter_meta
from learning.chapter_tags import tags_for


SYSTEM_TLDR = (
    "Ești redactor pentru OpenRadar (RO). Primești titlul, tagline-ul "
    "și lead-ul unui capitol tehnic. Rezumă conținutul în EXACT 2-3 "
    "propoziții scurte, în română, ton prietenos, fără jargon. "
    "Primele cuvinte trebuie să fie substantive (nu «Acest capitol...» "
    "sau «În acest capitol...»). Sub 80 de cuvinte total."
)

SYSTEM_TAKE = (
    "Ești Azi — un redactor AI care face legătura dintre un capitol "
    "de curs AI și știrile reale din ziua respectivă. Primești titlul "
    "capitolului, niște tag-uri de matching, și 1-3 titluri de știri "
    "relevante. Scrie UN SINGUR paragraf (3-4 propoziții) în română "
    "care: (1) leagă lecția capitolului de știrile concrete, "
    "(2) explică de ce e relevant pentru cineva care construiește în AI "
    "în România, (3) NU menționa că ești AI. Ton direct, specific, nu generic. "
    "Max 120 cuvinte. Dacă știrile nu sunt cu adevărat relevante, spune asta "
    "clar («Azi n-am văzut știri care să se potrivească direct...») și "
    "dă o povață generală."
)

SYSTEM_ASK = (
    "Ești Azi, asistent de curs pentru OpenRadar. Răspunzi la "
    "întrebări despre un capitol tehnic. Primești: titlul capitolului, "
    "un rezumat, și întrebarea utilizatorului. Răspunde în română, "
    "ton direct, exact, max 150 cuvinte. Folosește ce știi despre capitol "
    "ca să dai un răspuns concret — nu fi generic, nu «este o întrebare "
    "interesantă». Dacă nu știi, spune clar «Nu știu din acest capitol» "
    "și sugerează ce ar putea citi."
)


def _groq_chat(system: str, user: str, *, max_tokens: int = 280, temperature: float = 0.4) -> Optional[str]:
    if not config.has_llm():
        return None
    client = OpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)
    try:
        resp = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[insight] groq error: {e}")
        return None


def _generate_tldr(chapter_id: str) -> str:
    meta = load_chapter_meta(chapter_id)
    user = (
        f"Capitol: {chapter_id}\n"
        f"Titlu: {meta.get('title', '?')}\n"
        f"Tagline: {meta.get('tagline', '?')}\n"
        f"Lead: {meta.get('lead', '?')}\n\n"
        f"Scrie TL;DR."
    )
    out = _groq_chat(SYSTEM_TLDR, user, max_tokens=180, temperature=0.3)
    return out or _demo_tldr(chapter_id)


def _generate_take(chapter_id: str, news_signature: str) -> str:
    out = _groq_chat(
        SYSTEM_TAKE,
        _generate_take_user(chapter_id, news_signature),
        max_tokens=320,
        temperature=0.55,
    )
    return out or _demo_take(chapter_id, news_signature)


def _generate_take_user(chapter_id: str, news_signature: str) -> str:
    meta = load_chapter_meta(chapter_id)
    tags = tags_for(chapter_id)
    return (
        f"Capitol: {meta.get('title', '?')}\n"
        f"Tagline: {meta.get('tagline', '?')}\n"
        f"Tag-uri: {', '.join(t[0] for t in tags[:6])}\n"
        f"Știri de azi (cele mai relevante): {news_signature}\n\n"
        f"Scrie Azi's take în română."
    )


# ---------- Public API ----------

def chapter_tldr(chapter_id: str) -> tuple[str, str]:
    """Return (tldr_text, source) where source is 'groq' or 'demo'."""
    has_llm = config.has_llm()
    tldr = _tldr_cache(chapter_id, _today_key())
    if has_llm and tldr != _demo_tldr(chapter_id):
        return tldr, "groq"
    return tldr, "demo"


def azis_take(chapter_id: str, recent_news_titles: list[str]) -> tuple[str, str]:
    """Return (take_text, source).

    `recent_news_titles` are the already-matched top-3 news titles
    for this chapter. We pass them as context so the take ties the
    lesson to real, current items.

    `news_signature` is a tiny hash to invalidate the cache when the
    news feed changes within the same day.
    """
    has_llm = config.has_llm()
    titles_str = " | ".join(t for t in recent_news_titles if t)[:600]
    sig = hashlib.md5(titles_str.encode()).hexdigest()[:10]
    take = _take_cache(chapter_id, _today_key(), sig)
    if has_llm and take != _demo_take(chapter_id, sig):
        return take, "groq"
    return take, "demo"


def ask_azi(question: str, chapter_id: str) -> tuple[str, str]:
    """Answer a free-text question about a chapter. Uses Groq if available."""
    if not question.strip():
        return ("", "demo")
    meta = load_chapter_meta(chapter_id)
    user_prompt = (
        f"Capitol: {meta.get('title', '?')}\n"
        f"Tagline: {meta.get('tagline', '?')}\n"
        f"Lead: {meta.get('lead', '?')}\n\n"
        f"Întrebare utilizator: {question}\n\n"
        f"Răspunde."
    )
    out = _groq_chat(SYSTEM_ASK, user_prompt, max_tokens=380, temperature=0.55)
    if out:
        return out, "groq"
    return (
        "Nu am putut genera un răspuns acum (LLM-ul e offline). "
        "Citește conținutul capitolului și încearcă verificatorii — "
        "ei îți confirmă dacă ai înțeles.",
        "demo",
    )
