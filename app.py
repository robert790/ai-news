"""Streamlit UI for AI News · v0.1.

Run: streamlit run app.py

The UI:
- Pulls fresh stories on first load + every 30 min
- Shows a clean feed of AI news with Romanian summaries
- Has a placeholder for the future "Premium · Explain" button
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Make project root importable
sys.path.insert(0, str(Path(__file__).parent))

from scrapers import fetch_hackernews_ai
from llm import summarize_batch
from llm.summarizer import summarize
import config


st.set_page_config(
    page_title="AI News · RO",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---- Header ----
st.title("AI News · RO")
st.caption("Știri AI globale și locale, rezumate în română. Prima sursă: Hacker News. Mai multe vin.")

# ---- Status banner ----
with st.container():
    cols = st.columns([2, 1, 1])
    cols[0].markdown(
        f"**Limbă:** {config.APP_LANGUAGE.upper()}  ·  "
        f"**Cache:** {config.NEWS_CACHE_HOURS}h  ·  "
        f"**Premium:** {'🟢 enabled' if config.PREMIUM_ENABLED else '⚪ coming soon'}"
    )
    if not config.has_deepseek():
        cols[1].warning("⚠ Demo mode · adaugă DEEPSEEK_API_KEY pentru rezumate reale")
    else:
        cols[1].success("✓ DeepSeek connected")
    cols[2].markdown(f"🔄 _Updated {datetime.now().strftime('%H:%M')}_")

st.divider()


# ---- Data loading ----
@st.cache_data(ttl=1800, show_spinner="Se încarcă știrile...")
def load_news():
    raw = fetch_hackernews_ai(limit=20)
    return summarize_batch(raw)


with st.spinner("Se aduc știrile de pe Hacker News..."):
    items = load_news()


# ---- Filter chips ----
filter_cols = st.columns(4)
filter_cols[0].button("🔥 Toate", type="primary", use_container_width=True)
filter_cols[1].button("🇷🇴 România", use_container_width=True, disabled=True, help="vine în curând")
filter_cols[2].button("🇪🇺 Europa", use_container_width=True, disabled=True, help="vine în curând")
filter_cols[3].button("🌍 Global", use_container_width=True, disabled=True, help="vine în curând")

st.write("")


# ---- Feed ----
if not items:
    st.error("Nu s-au putut încărca știri. Verifică conexiunea sau încearcă mai târziu.")
else:
    st.subheader(f"📰 {len(items)} știri · Hacker News · ultimele 7 zile")
    st.caption("Rezumatele sunt generate automat. _Premium tier_ va permite explicarea în profunzime folosind cursul AI Road.")

    for item in items:
        with st.container(border=True):
            cols = st.columns([6, 1])

            with cols[0]:
                st.markdown(f"### [{item.title}]({item.url})")
                st.markdown(f"_{item.summary}_")
                meta = f"`{item.source}` · ⬆ {item.score} · 👤 {item.author or 'unknown'}"
                if item.published_at:
                    try:
                        dt = datetime.fromisoformat(item.published_at)
                        meta += f" · 🕐 {dt.strftime('%d %b %H:%M')}"
                    except Exception:
                        pass
                st.caption(meta)

            with cols[1]:
                if config.PREMIUM_ENABLED:
                    st.button("🔍 Explică", key=f"explain-{item.external_id}", use_container_width=True)
                else:
                    st.button("🔒 Premium", key=f"locked-{item.external_id}", disabled=True, use_container_width=True, help="vine în curând")


# ---- Footer ----
st.divider()
st.markdown("""
<div style="text-align: center; color: #7c7a72; font-size: 13px; padding: 24px 0;">
  <strong>AI News · RO</strong> · v0.1 · primul pas.<br>
  Urmează: surse românești, filtrare EU, premium tier cu explicații din <em>The AI Road</em>.<br>
  <a href="../ai-beginners-guide/index.html">Citește cursul →</a>
</div>
""", unsafe_allow_html=True)