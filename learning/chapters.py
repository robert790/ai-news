"""AI Road chapter data · Learning v0.4.

Each chapter maps to a section in the AI Road course at
ai-beginners-guide/index.html. Complexity is 1 (foundation) to 4 (advanced).
Domain groups branches in the skill tree.

Source for chapter content: /Users/zero/.minimax-agent/projects/ai-beginners-guide/index.html
"""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Chapter:
    id: str
    number: int
    title: str           # metaphorical title from the course
    subtitle: str        # plain-language subtitle
    blurb: str           # 1-2 sentence summary
    domain: str          # foundations | applied | research | romania | career | tools
    complexity: int      # 1=foundations, 2=building blocks, 3=intermediate, 4=advanced
    prerequisites: List[str] = field(default_factory=list)
    anchor: str = ""     # link anchor in the course HTML


CHAPTERS: Dict[str, Chapter] = {
    ch.__dict__.get("id"): ch for ch in [
        # type: ignore  # mypy dance
        Chapter(
            id="ch1", number=1,
            title="The Magic Kitchen",
            subtitle="Ce este AI-ul? O introducere clară.",
            blurb="Ce e AI, ce nu e, ce poate face azi. Mituri, hype, realitate. "
                  "Fără jargon, fără matematică.",
            domain="foundations", complexity=1,
            prerequisites=[],
            anchor="ch1",
        ),
        Chapter(
            id="ch2", number=2,
            title="The kid who kept digging",
            subtitle="Istoria AI pe scurt.",
            blurb="De laSymbolic AI la expert systems la deep learning la transformers. "
                  "60 de ani de iterații, în 5 minute.",
            domain="foundations", complexity=2,
            prerequisites=["ch1"],
            anchor="ch2",
        ),
        Chapter(
            id="ch3", number=3,
            title="The genius in the small kitchen",
            subtitle="Cum funcționează machine learning.",
            blurb="Supervised, unsupervised, reinforcement. Rețele neuronale, "
                  "backprop, de ce 'deep' e mai bun.",
            domain="foundations", complexity=2,
            prerequisites=["ch1"],
            anchor="ch3",
        ),
        Chapter(
            id="ch4", number=4,
            title="How to cook AI for any business",
            subtitle="AI în business: use cases, ROI, cum identifici ce are sens.",
            blurb="Framework simplu pentru a evalua unde AI adaugă valoare reală. "
                  "Exemple concrete din industrii diferite.",
            domain="applied", complexity=3,
            prerequisites=["ch1"],
            anchor="ch4",
        ),
        Chapter(
            id="ch5", number=5,
            title="Talking to AI like a pro",
            subtitle="Prompting: cum scrii prompturi care obțin rezultate.",
            blurb="Structuri de prompt, role prompting, chain-of-thought, "
                  "few-shot examples. Plus când NU funcționează prompting-ul.",
            domain="applied", complexity=3,
            prerequisites=["ch3"],
            anchor="ch5",
        ),
        Chapter(
            id="ch6", number=6,
            title="Reading papers without crying",
            subtitle="Cum citești o lucrare AI.",
            blurb="Structura tipică a unui paper. Ce să cauți, ce să sari, "
                  "cum să verifici rezultatele. Fără doctorate.",
            domain="research", complexity=3,
            prerequisites=["ch3"],
            anchor="ch6",
        ),
        Chapter(
            id="ch7", number=7,
            title="Your move",
            subtitle="Ce faci mâine: primii pași concreți.",
            blurb="Un plan de 30 / 90 / 365 zile pentru cineva care vrea să "
                  "înceapă serios.",
            domain="career", complexity=3,
            prerequisites=["ch1", "ch3"],
            anchor="ch7",
        ),
        Chapter(
            id="ch8", number=8,
            title="Romania's GPU infrastructure",
            subtitle="Cum stăm cu GPU-uri în România.",
            blurb="ClusterPower, providers locali, opțiuni cloud vs on-prem. "
                  "Costuri reale, latențe, capcane.",
            domain="romania", complexity=3,
            prerequisites=["ch3"],
            anchor="ch8",
        ),
        Chapter(
            id="ch9", number=9,
            title="Romania's AI ecosystem",
            subtitle="Companii, acceleratori, comunități AI locale.",
            blurb="Cine face AI în România, cine angajează, unde te poți conecta. "
                  "ClusterPower, Druid, Bitdefender, UiPath și restul.",
            domain="romania", complexity=3,
            prerequisites=["ch1"],
            anchor="ch9",
        ),
        Chapter(
            id="ch10", number=10,
            title="Where the gaps are",
            subtitle="Ce skill-uri lipsesc pe piață acum.",
            blurb="Harta cererii vs ofertei. Cei mai căutați oameni, "
                  "ce se cere, ce se va cere în 1-2 ani.",
            domain="career", complexity=4,
            prerequisites=["ch7"],
            anchor="ch10",
        ),
        Chapter(
            id="ch11", number=11,
            title="The roles that exist",
            subtitle="AI job roles — ce există azi.",
            blurb="LLM Engineer, AI Product Manager, AI Solutions Architect, "
                  "ML Engineer, AI Consultant. Definiții oneste.",
            domain="career", complexity=4,
            prerequisites=["ch10"],
            anchor="ch11",
        ),
        Chapter(
            id="ch12", number=12,
            title="Portfolio projects that get you hired",
            subtitle="Cum construiești un portofoliu care te vinde.",
            blurb="Ce tipuri de proiecte impresionează, ce demonstrează "
                  "producție gata. Exemplu cu Ziarul Digital.",
            domain="career", complexity=4,
            prerequisites=["ch11"],
            anchor="ch12",
        ),
        Chapter(
            id="ch13", number=13,
            title="Certifications, ranked honestly",
            subtitle="Ce certificări valorează, care nu.",
            blurb="Un ranking cinstit. AWS, Azure, Google, DeepLearning.AI, "
                  "Hugging Face. Cu cost-beneficiu concret.",
            domain="career", complexity=4,
            prerequisites=["ch11"],
            anchor="ch13",
        ),
        Chapter(
            id="ch14", number=14,
            title="Your tools stack",
            subtitle="Ce tool-uri să înveți.",
            blurb="Python, PyTorch, Hugging Face, LangChain, vector DBs, "
                  "Streamlit. Minimal viable stack pentru azi.",
            domain="tools", complexity=3,
            prerequisites=["ch5"],
            anchor="ch14",
        ),
        Chapter(
            id="ch15", number=15,
            title="Staying current",
            subtitle="Cum rămâi la curent fără să-ți pierzi zilele.",
            blurb="Surse curate, ritual de 15 min dimineața, semnale vs noise. "
                  "Și Ziarul Digital, bineînțeles.",
            domain="tools", complexity=4,
            prerequisites=["ch14"],
            anchor="ch15",
        ),
    ]
}


# Domain meta — colors, descriptions, icon
DOMAIN_META = {
    "foundations": {
        "label": "Foundations",
        "color": "#a8c0ae",   # sage
        "icon": "🌱",
        "blurb": "Înțelege ce e AI înainte să-l folosești.",
    },
    "applied": {
        "label": "Applied",
        "color": "#e8a598",   # coral
        "icon": "🔧",
        "blurb": "Aplică AI în contexte reale, cu rezultate.",
    },
    "research": {
        "label": "Research",
        "color": "#a5c5d4",   # sky
        "icon": "🔬",
        "blurb": "Citește, înțelege, evaluează.",
    },
    "romania": {
        "label": "Romania",
        "color": "#d9b87a",   # warm gold
        "icon": "🇷🇴",
        "blurb": "Cum stăm local, ce se face aici.",
    },
    "career": {
        "label": "Career",
        "color": "#b5a8c9",   # lavender
        "icon": "💼",
        "blurb": "Treci de la citit la angajat.",
    },
    "tools": {
        "label": "Tools",
        "color": "#8a8478",   # muted / neutral
        "icon": "🛠",
        "blurb": "Învață stack-ul care contează azi.",
    },
}


COMPLEXITY_META = {
    1: {"label": "Lvl 1 · foundations",  "color": "#a8c0ae"},
    2: {"label": "Lvl 2 · building blocks", "color": "#9bb88a"},
    3: {"label": "Lvl 3 · intermediate",  "color": "#d9b87a"},
    4: {"label": "Lvl 4 · advanced",     "color": "#c98a82"},
}


def get_all_chapters() -> List[Chapter]:
    """Return all chapters in numerical order."""
    return sorted(CHAPTERS.values(), key=lambda c: c.number)


def get_chapter(chapter_id: str) -> Chapter:
    return CHAPTERS[chapter_id]


def get_root_id() -> str:
    """The chapter with no prerequisites — the tree root."""
    for ch in CHAPTERS.values():
        if not ch.prerequisites:
            return ch.id
    return "ch1"