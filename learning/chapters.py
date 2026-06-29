"""AI Road chapter data · Learning v0.4.

Each chapter maps to a section in the AI Road course at
ai-beginners-guide/index.html. Complexity is 1 (foundation) to 4 (advanced).
Domain groups branches in the skill tree.

Source for chapter content: /Users/zero/.minimax-agent/projects/ai-beginners-guide/index.html
"""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Method:
    """A specific approach or technique within a chapter.

    BLUE-inspired: a chapter teaches the topic, methods teach the different
    ways to do it. One method can be `recommended=True` — the "Better Methods
    can move up" rule, applied to our content.

    Fields:
        id:          unique slug, e.g., "ch5-m-cot" — used for cross-refs later
        name:        human-readable name, e.g., "Chain-of-Thought"
        summary:     1-2 sentences explaining the method
        when_to_use: when this method shines vs the alternatives
        recommended: True if this is the canonical/main method for the chapter
    """
    id: str
    name: str
    summary: str
    when_to_use: str
    recommended: bool = False


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
    methods: List[Method] = field(default_factory=list)  # BLUE-inspired methods system
    # BLUE verifiers — concrete signals that prove the chapter landed
    verifiers: List[str] = field(default_factory=list)
    # BLUE action/goal focus — one concrete thing you can BUILD after reading
    build_this: str = ""
    # Recommended sequence "pillar" — chapters flagged this drive the
    # BLUE "Better Methods can move up" recommendation for the curated
    # reading order. Visualised as a dashed line on the skill tree.
    recommended_pillar: bool = False


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
            recommended_pillar=True,
            verifiers=[
                "Poți explica în 30 de secunde ce e AI și ce nu e.",
                "Recunoști 3 exemple de narrow AI din viața ta (autocomplete, recomandări, OCR).",
                "Știi de ce LLM-urile nu 'gândesc' în sens uman.",
                "Diferențiezi hype-ul de progresul real pe un articol recent.",
            ],
            build_this="Scrie pe o pagină definiția ta proprie de AI. Compară cu definiția din capitol. "
                      "Dacă diferă, de ce?",
        ),
        Chapter(
            id="ch2", number=2,
            title="The kid who kept digging",
            subtitle="Istoria AI pe scurt.",
            blurb="De la Symbolic AI la expert systems la deep learning la transformers. "
                  "60 de ani de iterații, în 5 minute.",
            domain="foundations", complexity=2,
            prerequisites=["ch1"],
            anchor="ch2",
            verifiers=[
                "Pui 4 epoci pe timeline (symbolic, expert systems, ML, deep learning).",
                "Identifici 2 lecții din cele două AI winters.",
                "Știi cine a câștigat ImageNet 2012 și de ce contează.",
            ],
            build_this="Timeline vizual în 5 slide-uri: Perceptron → Expert Systems → Backprop → AlexNet → "
                      "Transformers. Include datele cheie și motivele eșecurilor / victoriilor.",
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
            recommended_pillar=True,
            verifiers=[
                "Explici supervised vs unsupervised vs reinforcement cu exemplu propriu.",
                "Desenezi o rețea simplă cu input/hidden/output.",
                "Înțelegi de ce 'deep' înseamnă mai multe straturi, nu magie.",
                "Știi ce e backprop în 1 propoziție.",
            ],
            build_this="Antrenezi un model scikit-learn pe Titanic (sau orice dataset simplu) "
                      "și explici fiecare parametru din API.",
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
            verifiers=[
                "Identifici 2 use cases concrete din industria ta.",
                "Calculezi ROI estimat pentru un proiect AI simplu.",
                "Știi cele 4 întrebări de pus înainte de a începe un proiect AI.",
            ],
            build_this="One-pager: \"Dacă AI ar costa 0, ce aș automatiza în echipa mea?\" "
                      "Ajustezi la cost real. Trimite-l unui stakeholder.",
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
            recommended_pillar=True,
            methods=[
                Method(
                    id="ch5-m-cot", name="Chain-of-Thought",
                    summary="Forțezi modelul să gândească pas cu pas, înainte de răspuns final.",
                    when_to_use="Logică, matematică, raționament multi-step, planificare.",
                    recommended=True,
                ),
                Method(
                    id="ch5-m-fewshot", name="Few-shot examples",
                    summary="Arăți 2-5 exemple input→output înainte de task-ul real.",
                    when_to_use="Clasificare, format-matching, stil, structuri repetitive.",
                ),
                Method(
                    id="ch5-m-role", name="Role prompting",
                    summary="Acorzi modelului un personaj, un context, o expertiză.",
                    when_to_use="Când vrei ton specific, explicații la nivel X, simulare expert.",
                ),
                Method(
                    id="ch5-m-react", name="ReAct (Reason + Act)",
                    summary="Modelul alternează între raționament și acțiuni (tool calls, search).",
                    when_to_use="Agenți care au nevoie de info externă, research, debugging.",
                ),
            ],
            verifiers=[
                "Scrii un CoT prompt pe un task logic și vezi diferența vs zero-shot.",
                "Diferențiezi few-shot de zero-shot cu exemplu propriu pe același task.",
                "Știi când prompting-ul eșuează (math exact, facts, consistency).",
            ],
            build_this="3 prompturi salvate — unul per metodă (CoT, few-shot, role) pe același task, "
                      "cu rezultate comparate într-un tabel.",
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
            verifiers=[
                "Identifici contribuția principală a unui paper în 5 minute.",
                "Treci prin abstract→intro→conclusions→method în 15 min fără să te blochezi.",
                "Verifici un benchmark cu un grafic critic (sample size, baseline, setup).",
            ],
            build_this="Citești 'Attention is All You Need' și scrii 1-pager: "
                      "ce problemă rezolvă, metoda, rezultatele, limitele. Explică unui prieten non-tehnic.",
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
            verifiers=[
                "Ai un plan concret pe 30/90/365 zile scris undeva public.",
                "Știi un mentor sau comunitate unde mergi în prima săptămână.",
                "Ai identificat 3 skill-uri de upskilling concrete.",
            ],
            build_this="Planul tău pe 30 zile public (Notion, blog, journal). "
                      "Publicarea te obligă — alții te văd, te întreabă, te țin minte.",
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
            recommended_pillar=True,
            verifiers=[
                "Comanzi 3 furnizori diferiți și compari preț/latență/SLA pe hârtie.",
                "Știi diferența H100 vs A100 vs L40S pentru inference vs training.",
                "Calculezi cost-per-1k-tokens pentru un model mediu cu prețurile reale.",
            ],
            build_this="Spin-up pe ClusterPower (sau alt provider local) cu un model mic. "
                      "Măsoară cost-per-request și latency end-to-end. Documentează.",
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
            verifiers=[
                "Numești 5 companii locale care fac AI ca produs (nu doar integrează).",
                "Cunoști 1 accelerator sau program de mentorat din RO activ în 2026.",
                "Ai 2 contacte în domeniu pe LinkedIn cu care poți bea o cafea.",
            ],
            build_this="Aplici la 1 accelerator/eveniment AI RO + faci 1 reach-out către un angajator local "
                      "cu un proiect specific, nu un CV generic.",
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
            verifiers=[
                "Identifici 3 roluri cu cerere mare și ofertă mică în RO.",
                "Compari salariile pentru 2 roluri similare pe 3 surse (LinkedIn, Glassdoor, anunțuri).",
                "Anticipezi 1 trend pe 1-2 ani bazat pe semnale concrete (joburi, talk-uri, funding).",
            ],
            build_this="Tabel: 5 roluri × coloane (cerere, ofertă, salariu median, traiectorie 2 ani). "
                      "Cu date reale din RO.",
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
            recommended_pillar=True,
            methods=[
                Method(
                    id="ch11-m-llm", name="LLM Engineer",
                    summary="Construiești aplicații cu LLM-uri: RAG, prompts, tools, evaluare.",
                    when_to_use="Când vrei shipping rapid, integrare în produse, prototipuri.",
                    recommended=True,
                ),
                Method(
                    id="ch11-m-ml", name="ML Engineer",
                    summary="Fine-tuning, training, deployment de modele custom la scară.",
                    when_to_use="Când ai nevoie de performanță specifică domeniului, date proprii.",
                ),
                Method(
                    id="ch11-m-pm", name="AI Product Manager",
                    summary="Definesști ce construiești, prioritizezi, măsori impact.",
                    when_to_use="Când ești între business și tech, traduci nevoi în specificații.",
                ),
                Method(
                    id="ch11-m-architect", name="AI Solutions Architect",
                    summary="Design end-to-end: model, infra, cost, latency, security.",
                    when_to_use="Când proiectele sunt mari, multi-team, multi-vendor.",
                ),
            ],
            verifiers=[
                "Descrii fiecare rol în 2 propoziții fără jargon.",
                "Identifici overlap-ul între LLM Engineer și ML Engineer.",
                "Știi pe care l-ai alege pentru tine și de ce — și poți justifica.",
            ],
            build_this="Mini-self-assessment: care rol ți se potrivește, ce știi deja, "
                      "ce trebuie învățat, ce proiect demonstrează fiecare. 1 pagină.",
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
            verifiers=[
                "Ai 1 proiect cu useri reali (nu doar demo pe localhost).",
                "Fiecare proiect are README, screenshots și 'ce a demonstrat'.",
                "Code-ul tău are teste măcar pentru logica critică.",
            ],
            build_this="1 proiect end-to-end: idee → MVP → 1 user real → feedback iterat. "
                      "Public pe GitHub cu README scris pentru un non-author.",
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
            verifiers=[
                "Diferențiezi o certificare 'marketable' de una 'vanity' pe un exemplu concret.",
                "Calculezi costul total (timp + bani) vs salary bump așteptat.",
                "Știi 1 certificare care contează pentru rolul tău țintă și 1 care nu.",
            ],
            build_this="Tabel: 5 certificări × coloane (cost, timp, semnal pe piață, ROI estimat). "
                      "Decide pe care o faci în următoarele 90 de zile.",
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
            recommended_pillar=True,
            methods=[
                Method(
                    id="ch14-m-python", name="Python-first",
                    summary="Înveți Python, requests, FastAPI, deployment pe HF/Streamlit.",
                    when_to_use="Început, prototipuri rapide, cost minim.",
                    recommended=True,
                ),
                Method(
                    id="ch14-m-hf", name="Hugging Face-first",
                    summary="Transformers, Datasets, Hub, Spaces — open-source end-to-end.",
                    when_to_use="Când vrei modele open, fine-tuning, evaluare standard.",
                ),
                Method(
                    id="ch14-m-langchain", name="LangChain-first",
                    summary="Framework cu abstracții: agents, chains, retrievers, vector DBs.",
                    when_to_use="Când proiectul are RAG, tools complexe, multi-step.",
                ),
                Method(
                    id="ch14-m-streamlit", name="Streamlit-first",
                    summary="Demo-uri, dashboards, MVP-uri vizuale în Python pur.",
                    when_to_use="Showcase rapid, intern, iterație rapidă cu stakeholder-i.",
                ),
            ],
            verifiers=[
                "Instalezi și rulezi local un proiect Hugging Face end-to-end.",
                "Deploy un Streamlit app pe Hugging Face Spaces în sub 30 min.",
                "Alegi Python-first pentru un MVP rapid și poți justifica.",
            ],
            build_this="Pick o metodă (Python / HF / LangChain / Streamlit) și construiește "
                      "1 mini-app pe ea. Publică-l undeva.",
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
            recommended_pillar=True,
            verifiers=[
                "Ai 3 surse curate (nu 30).",
                "Ai un ritual zilnic de 15 min (news, paper, prompt).",
                "Știi să separi 'signal' de 'noise' rapid pe un feed supraîncărcat.",
            ],
            build_this="Construiește-ți propriul feed agregat (script, Notion database, "
                      "sau folosește Ziarul Digital ca exemplu). Îmbunătățește-l lunar.",
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