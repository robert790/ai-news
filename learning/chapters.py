"""Learning chapters · OpenRadar · Hartă AI pe categorii.

CURRICULUM: 10 capitole, fiecare capitol acoperă **o categorie mare
de AI** cu basics + un exercițiu hands-on. Nu e o poveste personală
— e un manual scurt care te pune în temă cu ce există.

    1. Fundamente        — istorie + cele 7 ere
    2. LLMs              — text in/out, tokens, context, hallucination
    3. Prompting         — cum vorbești cu un model ca un pro
    4. Vision AI         — classification, detection, OCR
    5. Diffusion & Media — image gen, video gen (Stable Diffusion, Sora)
    6. Speech & Audio    — STT, TTS, music gen, voice cloning
    7. Embeddings & RAG  — vector search, retrieval-augmented generation
    8. Agents            — tool use, planning, MCP
    9. Cum construiești  — SDK, Ollama, OpenRouter, n8n
   10. Aplică            — piața AI din RO, portofoliu, primul job

Why this matters:
- Cineva care începe cu AI-ul azi nu are nevoie de „un proiect personal
  narativ". Are nevoie de **hartă**: ce categorii există, ce face
  fiecare, cum pune mâna pe ea în 30 de minute.
- Sebastian's Methods (the structured pedagogy from BLUE AI Road)
  va fi adăugat ulterior ca overlay per capitol — vezi TODO mai jos.

TODO [→ methods overlay]:
    Fiecare capitol va câștiga un bloc `methods: List[Method]` cu
    metoda recomandată (◆) și 2-3 alternative (○). Metodele vin din
    pedagogia Sebastian Rey — „Better Methods can move up" pattern.
    Structura e deja definită (`@dataclass class Method` mai jos).

Each chapter has:
    - id         : "ch1" .. "ch10"  (kept stable for caches)
    - number     : 1..10
    - title      : capitol titlu scurt, RO
    - subtitle   : hook-ul (1 propoziție, RO)
    - body_md    : conținutul, markdown (cu '<svg>' inline pentru ilustrații)
    - verifiers  : 2-3 întrebări scurte «Ai înțeles?» — bifat e OK
    - build_this : 1 acțiune concretă pe care o faci ACUM
    - prereqs    : ["ch1", ...] — cap de capitole anterioare
    - domain     : vezi DOMAINS mai jos
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Method:
    name: str
    summary: str
    when_to_use: str
    recommended: bool = False


@dataclass
class Chapter:
    id: str
    number: int
    title: str
    subtitle: str
    body_md: str
    verifiers: List[str] = field(default_factory=list)
    build_this: str = ""
    prereqs: List[str] = field(default_factory=list)
    domain: str = "concepts"
    era: str = "2026"


# ---------------------------------------------------------------
# CAPITOLUL 01 · De unde vine AI-ul
# ---------------------------------------------------------------
# (CH2 — Proiectul Erica — eliminated. Cursul e pe categorii, nu pe
# poveste personală. Sebastian's Methods vin ca overlay per capitol.)
# ---------------------------------------------------------------

CH1_BODY = r"""
Înainte să punem mâna pe tastatură, fă un pas înapoi. Nu ca să devii
istoric, ci ca să înțelegi **de ce lumea AI-ului arată cum arată azi**.

### Era 1: Reguli scrise de mână · 1950–1990

Primele programe AI nu "gândeau". Urmau reguli scrise de un om.
Muzica jucată pe Atari? 50 de linii de cod `if`. Traducere automată?
Dicționare de reguli scrise de lingviști. Funcționa pe bucăți mici.
Când ieșea din bucăți mici, eșua.

### Era 2: Machine learning · 1990–2012

Inginerii și-au dat seama: e mai util să arăți algoritmului **1.000
de exemple** decât să-i scrii 1.000 de reguli. Algoritmul găsea singur
pattern-urile. Recunoaștere vocală, spam filtering, recomandări pe
Amazon. ML era real, dar limitat la sarcini înguste.

### Era 3: Deep learning · 2012–2017

În 2012, o echipă de la Toronto (AlexNet) a câștigat o competiție
de recunoaștere de imagini. Rețeaua lor neuronală era de 8 straturi.
Simplu. Dar a bătut tot ce exista înainte cu 10%. Următorii 5 ani
au fost o cursă: 16 straturi, 50, 152. Rezultate care au explodat.

### Era 4: Transformer · 2017

O echipă de la Google a publicat o lucrare cu titlu simplu —
"Attention is all you need". Ideea: în loc să procesezi text cuvânt
cu cuvânt, privești tot textul odată și decizi ce contează. Asta a
schimbat totul. Toate modelele pe care le folosești azi — GPT, Claude,
Llama, Qwen — folosesc arhitectura asta.

### Era 5: LLM-uri · 2020–2022

GPT-3 cu 175 miliarde de parametri. Apoi ChatGPT, lansat în
noiembrie 2022. 100 de milioane de utilizatori în 2 luni — cel mai
rapid produs din istorie. AI-ul a încetat să fie o unealtă de
cercetare. A devenit o conversație.

### Era 6: Restricții · 2025+

Nu e tehnic. E politic. Guvernele au început să taie accesul la cele
mai puternice modele. Capitolul următor pe asta construiește.

### Era 7: Fuziune · 2026+

N-avem un model grozav. Avem 5 modele bune. Întreaga industrie se
reorientează spre **cum combini modele mici** ca să simulezi ce
aveai cu unul mare.

Suntem în era 7. Asta e locul unde înveți, undeva pe curbă.

**De ce-ți pasă**: dacă știi doar "AI = chatGPT", ești un user.
Dacă știi cele 7 ere, poți citi orice știre tech cu context.
"""

CH1 = Chapter(
    id="ch1",
    number=1,
    title="De unde vine AI-ul",
    subtitle="De la reguli scrise de mână la modele care simulează gândire. Cele 7 ere.",
    body_md=CH1_BODY,
    verifiers=[
        "Știu că AI modern înseamnă rețele neuronale profunde (deep learning).",
        "Știu ce a făcut Transformer-ul în 2017 și de ce contează.",
        "Știu că LLM-urile folosesc arhitectura Transformer.",
    ],
    build_this=(
        "Desenează pe hârtie o linie a timpului cu cele 7 ere. "
        "Pune lângă fiecare un cuvânt-cheie: reguli, ML, DL, "
        "Transformer, LLM, restricții, fuziune."
    ),
    prereqs=[],
    domain="history",
    era="1950–2022",
)


# ---------------------------------------------------------------
# CAPITOLUL 02 · Cum gândește un LLM  (fostul CH3)
# ---------------------------------------------------------------

CH2_BODY = r"""
LLM-ul nu gândește. Recitește text prin statistică. Dar e suficient
de bun cât să pară că gândește. Hai să vezi cum.

### Analogia: ucenicul cu 500 GB de text

Imaginează un student care a citit 500 GB de text de pe internet.
Wikipedia, forumuri, cărți, rețele sociale, cod sursă. Când îi pui
o întrebare, el **nu caută** răspunsul. Ghicește continuarea cea mai
probabilă pe baza pattern-urilor pe care le-a văzut.

Asta e un LLM: o "mașinărie de continuat texte" care a citit prea
mult ca să mai vorbească prost.

### Token-uri, nu cuvinte

LLM-ul nu vede cuvinte. Vede **token-uri** — bucăți de caractere.

```
"Hello world"       → 2 token-uri
"Cryptocurrency"    → 4 token-uri
"Anticonstituționalitate" → 7 token-uri
```

De ce contează: **fiecare model are un cost-per-1.000-token-uri**
și un **context window** (câte token-uri vede simultan).
GPT-4o = 128k token-uri. Claude 3.5 = 200k. Llama 3.3 = 128k.

Context window = memoria lui de lucru. Conversații lungi îl blochează.

### Temperatura

Cât de "creativ" răspunde. Între 0 și 1:

- **0.0** — robot, răspunsul cel mai probabil mereu.
- **0.7** — default, echilibru.
- **1.2** — haos, variază mult.

Pentru sarcini tehnice (cod, matematică): **0.0–0.3**. Pentru
creativitate (brainstorming, copy): **0.7–0.9**.

### Hallucination

Când LLM-ul nu știe, **completează**. Asta nu e un bug; e felul
cum funcționează. Sample din probabilități, nu din realitate.

Exemple reale:

- Avocați americani au citat cazuri fabricate de ChatGPT în instanță.
- Oameni pun întrebări medicale. Modelul inventează studii.
- Erori financiare: modele care dau prețuri de active inexistente.

**Regulă**: tot ce zice AI-ul despre lumea reală, verifică la sursă.
AI-ul e partener de brainstorming, nu enciclopedie.

### Ce nu e LLM-ul

- Nu "știe" — combină pattern-uri.
- Nu "gândește" ca tine — are altă arhitectură.
- Nu e Google — nu caută, compune.
- Nu e conștient — n-are experiență subiectivă.

### Ce e LLM-ul

- **Un instrument de compoziție statistică** care e foarte bun la
  sarcini text-based.
- **Un prim ajutor în programare** (atent, dar util).
- **Un asistent de redactare** (draft-uri rapide).
- **Un partener de gândire** (brainstorming + structurare).

Cu cât îi înțeleli limitele, cu atât îl folosești mai bine.
"""

CH2 = Chapter(
    id="ch2",
    number=2,
    title="Cum gândește un LLM",
    subtitle="Pattern-uri pe 500 GB de text. Nu gândește — prezice. Și e suficient cât să pară că gândește.",
    body_md=CH2_BODY,
    verifiers=[
        "Știu ce e un token și cum se formează.",
        "Știu ce e context window și de ce contează.",
        "Știu că LLM-ul poate 'halucina' și trebuie să verific sursa.",
    ],
    build_this=(
        "Deschide chat.ai (orice). Trimite: «Câte token-uri are acest "
        "mesaj?» Apoi trimite același mesaj cu temperatura 0 vs 0.9. "
        "Notează diferența."
    ),
    prereqs=["ch1"],
    domain="llm",
    era="2022",
)


# ---------------------------------------------------------------
# CAPITOLUL 04 · Prompting ca un Pro
# ---------------------------------------------------------------

CH3_BODY = r"""
Diferența dintre un prompt prost și un prompt bun = **câteva ore
de lucru salvate pe zi**. Prompting-ul nu e artă misterioasă. E
**comunicare clară cu un coleg literal**.

### Principiul 1: Dă un rol

"Ești un contabil cu 20 ani experiență în firme IT românești."

Fără rol, modelul face media pe toți oamenii care ar putea ajuta.
Cu rol, se fixează pe un stil și o bază de cunoștințe specifică.

### Principiul 2: Specifică formatul

"Răspunde în 3 bullet-uri, max 15 cuvinte fiecare."

Asta e o constrângere. Constrângerile eliberează — îți dau ce vrei,
fără variație inutilă. Poți specifica:

- lungime ("max 200 cuvinte")
- structură ("primul paragraf X, al doilea Y")
- ton ("direct, fără flosculițe")
- audiență ("ca pentru un client non-tehnic")

### Principiul 3: Arată, nu doar spune (few-shot)

Nu poți descrie perfect un ton. Arată un exemplu.

```
Output asemănător cu:
«Da, optimizați spațiul. Vă costă 200 EUR/lună în plus.»

Acum generează pentru: client întreabă despre costul unui API
```

LLM-ul învață stilul din exemplu. Mai puternic decât orice
instrucțiune scrisă.

### Principiul 4: Constrângeri negative

"**Nu inventa.** Dacă nu știi, spune «nu știu»."

Modelele ascultă "nu" la fel de bine ca "da". Folosește-te de asta
ca să tai erorile: "Fără disclaimer la final", "Fără jargon tehnic",
"Nu te preface că ai citit surse pe care nu le-ai citit".

### Principiul 5: Chain of thought

Pentru probleme complexe, cere-i să gândească pas cu pas.

```
Gândește pas cu pas. Pentru fiecare pas, dă:
- ce ai presupus
- cum ai verificat
- la ce ai ajuns
```

Funcționează mai ales pe matematică, cod, planificare. **Costă
mai mulți token-uri, dar dă răspunsuri semnificativ mai bune.**

### Greșeli frecvente

- Prea lung, fără structură. → Folosește headings.
- Cere prea mult într-un singur prompt. → Sparge în bucăți.
- Vrei totul perfect la prima încercare. → Iterează.

### Analogia: angajarea unui asistent

E ca angajarea unui nou coleg: îi spui clar **cine e**, **ce face**,
**cum arată rezultatul**, **ce nu vrei**. Cu cât e mai clar, cu atât
lucrează mai bine. Nu e magie. E onboarding.
"""

CH3 = Chapter(
    id="ch3",
    number=3,
    title="Prompting ca un Pro",
    subtitle="Comunică cu AI-ul ca un manager cu un coleg nou: clar, structurat, cu exemple.",
    body_md=CH3_BODY,
    verifiers=[
        "Știu să dau un rol într-un prompt.",
        "Știu să specifice formatul exact al răspunsului.",
        "Știu să folosesc constrângeri negative.",
    ],
    build_this=(
        "Ia o sarcină reală de la tine de la muncă. "
        "Scrie 3 versiuni de prompt: prost, cu rol, cu exemplu. "
        "Testează-le pe chat.ai. Păstrează ce funcționează."
    ),
    prereqs=["ch2"],
    domain="prompting",
    era="2022",
)


# ---------------------------------------------------------------
# CAPITOLUL 04 · Vision AI  (NOU)
# ---------------------------------------------------------------

CH4_BODY = r"""
Computer Vision (CV) e categoria AI care lucrează cu **imagini și
video**: recunoaște obiecte, citește text, urmărește mișcare,
generează imagini noi. E a doua categorie ca impact economic după
LLM-uri.

### Sarcinile de bază

| Sarcină | Ce face | Exemplu real |
|---|---|---|
| **Clasificare** | Etichetează o imagine | „pisică" vs „câine" |
| **Detection** | Găsește obiecte + cutiebounding | „2 persoane, 1 mașină" |
| **Segmentation** | Conturează la nivel de pixel | hărți medicale, mașini autonome |
| **OCR** | Extrage text din imagini | facturi, documente scanate |
| **Face recognition** | Identifică persoane | securitate, tagging foto |
| **Pose estimation** | Urmărește scheletul uman | sport, AR/VR |

### Cum funcționează (pe scurt)

Înainte de 2012, CV se baza pe filtre scrise de mână (edge detection,
SIFT, HOG). **AlexNet (2012)** a câștigat ImageNet cu o rețea
neuronală convoluțională (CNN) — și toată lumea a trecut pe deep
learning peste noapte.

Astăzi, vision models sunt transformer-based (ViT — Vision Transformer),
antrenate pe miliarde de imagini cu subtitrări (CLIP, DINO, SAM).

### Foundation models (2024+)

- **CLIP** (OpenAI) — leagă imagini și text în același spațiu
  vectorial. Poți căuta într-o bază de imagini cu text natural:
  „poze cu câini în zăpadă".
- **SAM** (Meta) — segment anything. Dai un click pe obiect, îți
  decupează conturul exact.
- **Florence 2** (Microsoft) — tiny model (270M parametri) care
  face detection + captioning + OCR într-o singură trecere.

### Unde se folosește

- Retail: count people, detect empty shelves
- Medical: X-ray analysis, tumor detection
- Automotive: pedestrian detection, lane keeping
- Agriculture: crop disease, yield estimation
- Insurance: damage assessment din poze
- Industrial: defect detection pe linii de fabricație

### Cum începi tu

**1. Începe cu un API gata făcut**: Google Cloud Vision, AWS
Rekognition, Azure Computer Vision. Trimiti poză, primești JSON cu
ce-a detectat. 5 minute setup, $1-2 per 1000 imagini.

**2. Apoi încearcă modele open-source**: YOLO v8/v11 pentru
detection rapidă, Florence-2 pentru captioning, SAM pentru
segmentation. Rulează local cu `pip install ultralytics`.

**3. Fine-tune** dacă ai nevoie de ceva specific (ex: defecte
industriale ale tale). Ia YOLO pre-antrenat, antrenează-l pe
100-500 poze etichetate.

### Greșeli frecvente

- Vrei „AI care vede" și te gândești la ceva general. Nu există.
  Există detection SAU classification SAU segmentation — alege una.
- Antrenare fără date suficiente. Sub 1000 de exemple pe clasă,
  nu te aștepta la miracole.
- Ignori lumina și unghiul. Modelele sunt pretențioase la poze
  diferite de cele din train.
"""

CH4 = Chapter(
    id="ch4",
    number=4,
    title="Vision AI",
    subtitle="Clasificare, detection, OCR, segmentation. A doua categorie AI ca impact economic.",
    body_md=CH4_BODY,
    verifiers=[
        "Știu diferența dintre classification, detection și segmentation.",
        "Știu ce e CLIP și de ce e util pentru image search.",
        "Știu că pot folosi un API gata făcut (Google Vision, AWS) fără antrenare.",
    ],
    build_this=(
        "Descarcă 20 poze cu pisici și 20 cu câini. "
        "Încarcă-le pe Google Cloud Vision (sau Roboflow free tier). "
        "Compară classification vs detection. "
        "Notează ce a greșit și de ce."
    ),
    prereqs=["ch3"],
    domain="vision",
    era="2024",
)


# ---------------------------------------------------------------
# CAPITOLUL 05 · Diffusion & Generative Media  (NOU)
# ---------------------------------------------------------------

CH5_BODY = r"""
Până în 2020, „AI-ul care generează imagini" era un toy cu rezoluție
mică și fețe distorsionate. Azi, **Stable Diffusion, Midjourney,
DALL-E 3, Imagen, Sora, Veo** produc imagini și video la nivel
profesional. Toate se bazează pe **diffusion models**.

### Cum funcționează diffusion (pe scurt, fără matematică)

Imaginează-ți o poză clară. Adaugi treptat zgomot aleator până
devine doar pure static. Rețeaua neuronală **învață să facă procesul
invers**: din zgomot pur, reconstruiește o imagine coerentă.

```
Imagine clară → adaugă zgomot (1000 pași) → zgomot pur
                                          │
                       rețeaua învață să meargă invers
                                          ▼
Zgomot pur → scoate zgomot (1000 pași) → imagine clară
```

Training: milioane de imagini cu descrieri. Inference: pornești
de la zgomot aleator + un text prompt, modelul merge înapoi.

### Concepte esențiale

- **Prompt** — textul care descrie ce vrei. Cu cât mai specific,
  cu atât mai bine: „portret cinematografic, bărbat 30 ani, lumină
  de apus, stil foto-documentar" bate „bărbat".
- **Negative prompt** — ce NU vrei: „blur, mâini deformate, text
  ilizibil, calitate scăzută".
- **Guidance scale** — cât de strict ascultă modelul prompt-ul.
  Mare = literal dar boring. Mic = creativ dar pierde detalii.
- **Steps** — câte iterații de denoising. 20-30 e sweet spot.
- **Seed** — număr care controlează random. Același seed + același
  prompt = aceeași imagine. Util pentru iterații.

### Tools (2026)

| Tool | Tip | Cost | Note |
|---|---|---|---|
| **Midjourney** | Cloud (Discord) | $10/lună | Cel mai „artistic", preferat de designeri |
| **DALL-E 3** | Cloud (API OpenAI) | per imagine | Integrare bună cu ChatGPT |
| **Stable Diffusion** | Open-source, local | gratuit | Rulezi pe Mac M2+ sau cu GPU |
| **Flux** | Open-source (Black Forest Labs) | gratuit | Calitate > SD, mai nou |
| **ComfyUI** | UI pentru SD/Flux local | gratuit | Pipeline-uri vizuale complexe |

### Video gen (2025+)

**Sora** (OpenAI), **Veo** (Google), **Runway Gen-3**, **Kling**
(chinezesc, foarte bun) — toate generează clipuri 5-30 secunde
din text. Costă mult per clip, dar calitatea a depășit orice
animație tradițională pentru multe use case-uri.

### Use cases reale

- Marketing: vizualuri pentru ads în ore, nu zile
- E-commerce: pune haine pe modele care nu există
- Arhitectură: randări din schițe
- Gaming: texturi generate procedural
- Educativ: ilustrații on-demand

### Greșeli frecvente

- Prompt vag → output mediocru
- Ignori composition (regula treimilor, focal point)
- Nu iterezi. Prima imagine nu e cea mai bună.
"""

CH5 = Chapter(
    id="ch5",
    number=5,
    title="Diffusion & Generative Media",
    subtitle="Cum generează AI imagini și video din text. Stable Diffusion, Midjourney, Sora.",
    body_md=CH5_BODY,
    verifiers=[
        "Știu ce e un diffusion model și cum funcționează pe scurt.",
        "Știu diferența dintre prompt și negative prompt.",
        "Știu că pot rula Stable Diffusion local pe Mac M2+.",
    ],
    build_this=(
        "Instalează Stable Diffusion local (sau folosește Midjourney). "
        "Scrie 5 prompturi pentru același subiect cu stiluri diferite "
        "(cinematic, pictură, desen, foto, anime). "
        "Salvează ce funcționează într-un folder cu seed + prompt."
    ),
    prereqs=["ch3"],
    domain="diffusion",
    era="2024",
)


# ---------------------------------------------------------------
# CAPITOLUL 06 · Speech & Audio AI  (NOU)
# ---------------------------------------------------------------

CH6_BODY = r"""
A treia mare categorie: AI pentru **voce și sunet**. Include speech-
to-text (transcriere), text-to-speech (sinteză vocală), music
generation, voice cloning, audio enhancement.

### Speech-to-Text (STT)

Transformă audio în text. Utilizări: transcriere meeting-uri,
subtitrări, interfețe vocale, dictare medicală.

| Tool | Limbi | Preț | Calitate |
|---|---|---|---|
| Whisper (OpenAI) | 99 | gratuit, local | excelent |
| Deepgram | 36+ | per minut | excelent, rapid |
| Google Speech-to-Text | 125+ | per minut | bun |
| AssemblyAI | engleză best | per minut | excelent |

Whisper e special: open-source, rulează local, suportă 99 limbi.
Îl instalezi cu `pip install openai-whisper` și transcrii orice.

### Text-to-Speech (TTS)

Transformă text în audio cu voce naturală. Trecut: voci robotice.
Azi: indistinguishable de om.

- **ElevenLabs** — cel mai realist, suportă voice cloning
- **OpenAI TTS** — 6 voci, simplu, ieftin
- **Google Cloud TTS** — multe voci, multe limbi
- **Coqui TTS / Piper** — open-source, local

### Voice cloning

Cu 10-30 secunde de audio, poți clona vocea cuiva. Utilizări:
- Narare audiobook în vocea autorului (cu permisiune)
- Dublare în altă limbă păstrând vocea originală
- Personaje consistente în jocuri/animații

**Atenție etică**: voice cloning fără consimțământ e deepfake.
Legislativ: EU AI Act cere consimțământ explicit + watermarking.

### Music Generation

- **Suno** — generează melodii complete (voce + instrumente) din text
- **Udio** — similar, calitate foarte bună
- **Stable Audio** (Stability AI) — open-source, pentru background music
- **AIVA** — specializat pe compoziție clasică/cinematică

Use cases: jingle-uri pentru ads, muzică de fundal pentru video,
prototipuri pentru compozitori.

### Audio enhancement

- **ElevenLabs Sound Effects** — generează SFX din text
- **Adobe Podcast** — remove noise, enhance voice (gratuit, magic)
- **Demucs** (Meta) — separă vocea de instrumentale (open-source)

### Cum începi

1. Instalează Whisper local — transcrie 10 fișiere audio din viața ta
2. Testează ElevenLabs cu 5 voci diferite — vezi care îți place
3. Încearcă Suno — generează un jingle de 30 secunde pentru ceva

### Greșeli frecvente

- STT pe audio cu noise mult → output dezastruos. Curăță întâi.
- TTS fără pauze potrivite → sună robotic. Folosește SSML.
- Music gen cu prompt vag → rezultat generic. Fii specific la gen, mood, tempo.
"""

CH6 = Chapter(
    id="ch6",
    number=6,
    title="Speech & Audio AI",
    subtitle="Transcriere (Whisper), sinteză vocală (ElevenLabs), music gen (Suno).",
    body_md=CH6_BODY,
    verifiers=[
        "Știu să instalez Whisper și să transcriu audio local.",
        "Știu diferența dintre STT, TTS, voice cloning și music gen.",
        "Știu că voice cloning cere consimțământ (legal + etic).",
    ],
    build_this=(
        "Instalează Whisper local. "
        "Ia un fișier audio de 5 minute (un podcast, o prelegere). "
        "Transcrie-l. "
        "Notează: ce-a greșit, unde s-a descurcat, cum poți îmbunătăți."
    ),
    prereqs=["ch3"],
    domain="speech",
    era="2024",
)


# ---------------------------------------------------------------
# CAPITOLUL 07 · Embeddings & RAG  (NOU)
# ---------------------------------------------------------------

CH7_BODY = r"""
LLM-urile știu multe, dar **nu știu nimic specific despre tine sau
compania ta**. Asta e limita fundamentală. Soluția: **RAG**
(Retrieval-Augmented Generation) — adaugi context din documente
proprii înainte de a cere modelului să răspundă.

### Ce sunt embeddings

Un embedding e un **vector de numere** (de obicei 384–3072 dim)
care reprezintă semantic o bucată de text. Texte similare au vectori
apropiați.

```
„câinele latră"       → [0.12, -0.45, 0.78, ..., 0.34]
„câinele scheună"    → [0.15, -0.42, 0.76, ..., 0.33]   # aproape
„mașina merge"       → [-0.56, 0.22, -0.18, ..., 0.05]  # departe
```

Măsura de „aproape" = **cosine similarity** (unghiul dintre vectori).

### Cum faci embeddings

Modele populare:
- **OpenAI text-embedding-3-small** (1536 dim, $0.02/M tokens)
- **Cohere embed-v3** (1024 dim, multilingual)
- **bge-large** (BAAI, open-source, 1024 dim)
- **e5-large-v2** (Microsoft, open-source)
- **nomic-embed-text** (local, 768 dim)

```python
import openai
resp = openai.embeddings.create(
    model="text-embedding-3-small",
    input="Cum funcționează un LLM?"
)
vec = resp.data[0].embedding  # list of 1536 floats
```

### Vector databases

Stochezi embeddings + metadata, cauți rapid „cel mai apropiat" de
un query. Opțiuni:

| DB | Tip | Cost |
|---|---|---|
| **Chroma** | Local, simplu | gratuit |
| **FAISS** (Meta) | Local, foarte rapid | gratuit |
| **Qdrant** | Server, production-ready | self-host sau cloud |
| **Weaviate** | Server, bogat în features | self-host sau cloud |
| **Pinecone** | Managed, foarte simplu | pay-as-you-go |

### RAG pattern (ce trebuie să știi)

```
Întrebare utilizator
        │
        ▼
[1] Embedding pe întrebare
        │
        ▼
[2] Caută top-K documente similare în vector DB
        │
        ▼
[3] Concatenăzi: context găsit + întrebare
        │
        ▼
[4] Trimite la LLM cu prompt: "Răspunde pe baza contextului"
        │
        ▼
[5] LLM-ul produce răspuns grounded în datele tale
```

De ce RAG > fine-tuning pentru date proprii:
- Date proaspete fără re-antrenare (re-embed + restart)
- Poți cita sursa exactă (audit + verificare)
- Cost mic (nu re-antrenezi un model de miliarde $)

### Use cases

- Chatbot pe documentele companiei tale (HR, legal, suport)
- Căutare semantică în codebase (Gitingest, Cursor)
- Q&A pe baza ta de cunoștințe (Notion, Confluence)
- Recommendation systems (produse similare)

### Greșeli frecvente

- Chunking prost. Bucăți prea mari = prea puțin context specific.
  Prea mici = pierdut context. Sweet spot: 200-800 tokens cu overlap.
- Fără reranking. Embedding search nu e perfect; adaugă un re-ranker
  (Cohere Rerank, cross-encoder) pentru top-50 → top-5.
- Ignori evaluarea. Testează cu întrebări reale și măsoară
  recall@5, MRR.
"""

CH7 = Chapter(
    id="ch7",
    number=7,
    title="Embeddings & RAG",
    subtitle="Cum adaugi AI-ului context din datele tale. Vector DB + retrieval.",
    body_md=CH7_BODY,
    verifiers=[
        "Știu ce e un embedding și cum se calculează similaritatea.",
        "Știu diferența dintre RAG și fine-tuning.",
        "Știu să aleg o vector DB (Chroma local, Qdrant production).",
    ],
    build_this=(
        "Ia 10 documente (articole, pagini wiki, fișiere). "
        "Încarcă-le în Chroma (local, gratuit). "
        "Pune o întrebare. "
        "Verifică: primele 3 rezultate sunt chiar ce-ai vrut?"
    ),
    prereqs=["ch2"],
    domain="rag",
    era="2024",
)


# ---------------------------------------------------------------
# CAPITOLUL 08 · Agents  (NOU)
# ---------------------------------------------------------------

CH8_BODY = r"""
LLM-ul singur răspunde la întrebări. **Agentul** ia decizii, apelează
unelte, iterează. E diferența dintre „calculator" și „operator".

### Ce e un agent

Un agent = LLM + buclă de raționament + acces la unelte.

```python
while not done:
    thought = llm("Ce urmează?", context=history)
    action = llm.parse(thought)  # tool call
    result = tools[action.name](**action.args)
    history.append((thought, action, result))
done = llm("Rezumă ce-ai aflat")
```

Exemple de unelte: search web, read file, run code, query DB, send email.

### Patterns

- **ReAct** (Reason + Act) — gândește, acționează, observă, repetă
- **Plan-and-Execute** — face un plan, execută pas cu pas
- **Multi-agent** — mai mulți agenți colaborează (1 cercetează,
  altul scrie, al treilea verifică)
- **Reflexion** — agentul se auto-evaluează și încearcă din nou

### MCP — Model Context Protocol

Anthropic a lansat în 2024 **MCP**, un standard deschis pentru
conectarea toolurilor la agenți. E ca **USB-C pentru AI**: agentul
conectat la un MCP server poate citi fișiere, rula comenzi, accesa
API-uri în mod standardizat.

Ecosistemul crește rapid: Claude Code, Cursor, Continue, n8n, multe
altele suportă MCP. Dacă vrei să construiești un tool pentru AI,
expune-l ca MCP server.

### Frameworks

| Framework | Limbă | Note |
|---|---|---|
| **LangChain** | Python/JS | Cel mai popular, mulți abstractions |
| **LangGraph** | Python/JS | Production-grade agents, stateful graphs |
| **CrewAI** | Python | Multi-agent simplu, role-based |
| **AutoGen** (Microsoft) | Python | Multi-agent conversațional |
| **Haystack** | Python | Deepset, mai orientat pe RAG |

### Use cases reale

- Customer support agent (citește docs, răspunde, escaladează)
- Coding agent (Claude Code, Cursor — citește repo, editează, testează)
- Research agent (căutare web, sinteză, raport)
- Data analyst agent (query SQL, generează chart, explică)

### Greșeli frecvinte

- Agent cu prea multe unelte → confuz, aleator. Max 5-10 unelte
  inițial, extinde pe măsură ce testezi.
- Fără limită de iterații. Un agent blocat poate rula la infinit.
  Pune max_steps = 10-20.
- Fără human-in-the-loop pentru acțiuni distructive (ștergere fișiere,
  send email, payment). Confirmă înainte de execuție.
- Overengineering. 80% din use cases se rezolvă cu un simplu tool
  call. Agentul complet e pentru 20%.
"""

CH8 = Chapter(
    id="ch8",
    number=8,
    title="Agents",
    subtitle="LLM + unelte + buclă. De la chat la automatizare. MCP ca USB-C pentru AI.",
    body_md=CH8_BODY,
    verifiers=[
        "Știu ce e un agent și cum diferă de un simplu tool call.",
        "Știu ce e MCP și de ce e important.",
        "Știu cel puțin un framework (LangChain / LangGraph / CrewAI).",
    ],
    build_this=(
        "Folosește Claude Code SAU Cursor cu un proiect mic. "
        "Dă-i o sarcină simplă: «adaugă teste pentru funcția X». "
        "Observă cum iterează. "
        "Notează: unde a funcționat, unde a eșuat, de ce."
    ),
    prereqs=["ch7"],
    domain="agents",
    era="2025",
)


# ---------------------------------------------------------------
# CAPITOLUL 09 · Cum construiești cu AI  (combinat, tools + restrictions)
# ---------------------------------------------------------------

CH9_BODY = r"""
Chat-ul e pentru conversație. SDK-ul e pentru aplicații. Ollama e
pentru local. **Aici legăm tot ce-am învățat într-unelte reale
pe care le poți folosi mâine.**

### Nivelurile de utilizare

**1. Chat direct**: chat.ai, Claude.ai, Gemini. Tu scrii, modelul
răspunde. Manual. Simplu. Limitat la tine + o fereastră.

**2. SDK / API**: programatorul scrie cod care cheamă modelul.
5 linii Python:

```python
import openai
client = openai.OpenAI()
resp = client.chat.completions.create(
    model="llama-3.3-70b",
    messages=[{"role": "user", "content": "Rezumă acest articol"}]
)
print(resp.choices[0].message.content)
```

Asta poate rula în batch, într-un flow, într-o aplicație. **De aici
încolo începe puterea.**

**3. Local-first**: rulezi modelul pe laptopul tău, fără internet.
Cu **Ollama**. Descarci un model, conversează prin terminal sau
prin SDK-ul local.

### De ce local-first contează

- **Date sensibile** — nu pleacă de pe laptopul tău.
- **Cost 0** — după descărcare, rulezi la infinit.
- **Offline** — funcționează și în avion.
- **Latency mic** — fără round-trip la server.

Limitări: modele locale sunt mai mici (3B–70B parametri), deci mai
slabe decât frontier modele (Claude Opus, GPT-5).

### Cele 3 SDK-uri principale

| Vendor | SDK | Note |
|---|---|---|
| OpenAI | `openai` | Standardul. Compatibil cu OpenRouter, Groq, Together, etc. |
| Anthropic | `anthropic` | Pentru Claude. |
| Ollama | `ollama-python` | Pentru modele locale. |

Marele trick: **OpenAI SDK funcționează cu orice model compatibil**
printr-un OpenAI-compatible endpoint. Deci poți scrie cod o singură
dată și schimba modelul schimbând URL-ul.

### MCP — Model Context Protocol

Anthropic a lansat în 2024 un standard deschis: **MCP**. E ca un
USB-C pentru AI: un model conectat la MCP poate citi fișiere, rula
comenzi, accesa API-uri. Claude Code, Cursor, n8n folosesc MCP.

### Cele 5 unelte pe care le stăpânești

**1. Cursor** — editor de cod cu AI integrat. Vorbești cu codul:
„Refactorizează funcția asta", „Adaugă teste". $20/lună Pro.

**2. Claude Code CLI** — agent terminal de la Anthropic. Citește,
editează, creează fișiere. Bun pentru sarcini lungi multi-file.

**3. n8n** (sau Langflow) — GUI open-source pentru flow-uri AI fără
cod. Monitorizează folder → Ollama → Notion. Trigger email → LLM → Trello.

**4. Ollama** — AI local, gratuit, offline. Modele recomandate:
- producție: Llama 3.3 70B (64 GB RAM sau M2 Ultra)
- laptop normal: Qwen 2.5 14B sau Mistral Small
- viteză: Llama 3.2 3B sau Phi 4 mini

**5. OpenRouter** — un API key, 50+ modele. Switch între ele la
runtime. Util pentru testare, failover, cost optimization.

### Flow-uri fără cod

**n8n** (open-source) și **Langflow**: GUI drag-and-drop pentru a
construi pipeline-uri AI fără cod. Utile pentru automatizări simple.
Limitate pentru logică complexă.

### Restricții 2026

| Tier | Ce ai | Cost | Calitate |
|---|---|---|---|
| Closed frontier | GPT-5, Claude Opus | $$$, API gate | ★★★★★ |
| Closed mid-tier | GPT-5 mini, Claude Haiku, Gemini Flash | $ | ★★★ |
| Open-weight top | Llama 3.3 70B, Qwen 2.5 72B | $0 (local) | ★★★★ |
| Open-weight small | Llama 3.2 3B, Phi 4, Gemma 2 | $0 | ★★ |

EU AI Act + US export controls = modelele frontier sunt limitate.
Open-source (Llama, Qwen, DeepSeek) e alternativa reală.

### Ce faci acum

1. Instalează Ollama și descarcă `llama3.2` (2 GB) — primul model local
2. Fă un script Python cu OpenAI SDK care cheamă Ollama local
3. Testează 3 modele pe OpenRouter pe aceeași sarcină
4. Instalează n8n și fă un flow: trigger → Ollama → fișier
"""

CH9 = Chapter(
    id="ch9",
    number=9,
    title="Cum construiești cu AI",
    subtitle="Chat = pentru tine. SDK = pentru program. Ollama = local. OpenRouter = 50+ modele.",
    body_md=CH9_BODY,
    verifiers=[
        "Știu diferența dintre chat, SDK și local (Ollama).",
        "Știu că OpenAI SDK funcționează cu orice model compatibil.",
        "Știu ce e MCP și de ce contează ca standard deschis.",
    ],
    build_this=(
        "Instalează Ollama. Descarcă llama3.2. "
        "Scrie un script Python (OpenAI SDK) care trimite un prompt "
        "la Ollama local și afișează răspunsul. "
        "Salvează-l. E primul tău AI tool."
    ),
    prereqs=["ch2"],
    domain="tools",
    era="2026",
)

# ---------------------------------------------------------------
# CAPITOLUL 10 · Aplică acum
# ---------------------------------------------------------------

CH10_BODY = r"""
Ai învățat. Acum trebuie să câștigi. **Diferența dintre «știu AI»
și «am proiectele» e salariul.**

### Starea pieței 2026, România

- **91+ companii AI** în România.
- Salariul mediu AI-engineer: **€3.500–6.000 net** (junior), **€7.000–12.000** (mid), **€12.000+** (senior/lead).
- Remote-friendly cu firme din: Germania, UK, US, Israel, Franța.
- Cele mai mari hub-uri: București, Cluj, Iași, Timișoara.

### Poziții principale

| Rol | Ce face | Stack tipic | Salariu entry |
|---|---|---|---|
| AI Engineer | Integrează LLM-uri în produse | Python + OpenAI/Ollama | €3.5–5k |
| ML Engineer | Antrenează și fine-tunează modele | PyTorch + GPU | €4–6k |
| MLOps | Pune modele în producție | Docker/K8s + GPU | €4.5–7k |
| AI Infra | Clustere, GPU, distribuție | K8s + SLURM + RDMA | €5–8k |
| AI Product Manager | Decide ce construiești | Mix tehnic + business | €4–6k |
| AI Researcher | Publică, experimentează cu modele noi | PyTorch + papers | €3.5–5k |

Alege **una**. Aplică pe aia. Specializare > generalist la junior.

### Ce face un AI Engineer zilnic

- scrie cod Python
- cheamă modele prin API/SDK
- construiește flow-uri cu LangChain/LangGraph/n8n
- testează cu date reale
- scrie evaluări (modelul e destul de bun?)
- documentează + prezintă

### Cum aplici concret

1. **Profil LinkedIn** complet: titlu clar ("AI Engineer"), summary
   scurt, proiectele tale în featured.
2. **GitHub** cu 4 proiecte active + READMEs clare.
3. **Aplică** la 3 poziții pe săptămână. Mai bine 3 bine țintite
   decât 30 random.
4. **Întrebare de aur la interviu**: "Povestește-mi despre un proiect
   pe care l-ai construit." Ai 4 pregătite.

### Interviuri AI în România

Tipic 3 runde:

1. **Screening call** (30 min) — fit + motivație
2. **Tech interview** (60-90 min) — Python live + întrebări despre LLM-uri
3. **System design + culture** (60-90 min) — cum ai proiecta un flow AI

Întrebări tehnice comune:

- Cum reduci halucinațiile unui LLM?
- Cum faci cost control când folosești API-uri scumpe?
- Ce e temperature și când îl schimbi?
- Cum evaluezi dacă un model e destul de bun pentru o sarcină?
- Ce e RAG și când îl folosești?

### Bonus: mindset-ul meu

După 6 luni de la acest curs, vreau să văd **4 proiecte pe GitHub**
ale absolvenților. Altfel, cursul a fost doar informativ.

Aplică. Nu mai aștepta "condițiile perfecte". Aplică acum.

We are all in this. Tu, eu, toți cei care au crezut prea devreme.
Acum suntem la momentul potrivit.
"""

CH10 = Chapter(
    id="ch10",
    number=10,
    title="Aplică acum",
    subtitle="Ai proiectele. Aplică la 3 poziții azi. We are all in this.",
    body_md=CH10_BODY,
    verifiers=[
        "Am ales o poziție țintă (AI Engineer / ML Engineer / MLOps / etc.)",
        "Am profil LinkedIn cu titlu + proiectele mele.",
        "Am aplicat la minim 1 poziție azi (sau o voi face în următoarele 30 min).",
    ],
    build_this=(
        "Alege 3 anunțuri pe LinkedIn pentru poziția ta. "
        "Aplică la unul ACUM. "
        "Celelalte 2 mâine dimineață. "
        "Salvează link la fiecare pentru follow-up peste 1 săptămână."
    ),
    prereqs=["ch9"],
    domain="career",
    era="2026",
)


# ---------------------------------------------------------------
# THE FULL COURSE
# ---------------------------------------------------------------

CHAPTERS: list[Chapter] = [
    CH1, CH2, CH3, CH4, CH5, CH6, CH7, CH8, CH9, CH10,
]


def get_chapter(chapter_id: str) -> Chapter:
    for c in CHAPTERS:
        if c.id == chapter_id:
            return c
    raise KeyError(f"Unknown chapter: {chapter_id}")


def get_all_chapters() -> list[Chapter]:
    return list(CHAPTERS)


# Domains — used by the chip grid + skill tree.
DOMAINS = {
    "history":   ("Istoric",    "cuminte"),
    "llm":       ("LLMs",       "lavender"),
    "prompting": ("Prompting",  "amethyst"),
    "vision":    ("Vision AI",  "sky"),
    "diffusion": ("Diffusion",  "coral"),
    "speech":    ("Speech",     "amber"),
    "rag":       ("Embeddings", "sage"),
    "agents":    ("Agents",     "rose"),
    "tools":     ("Unelte",     "warm"),
    "career":    ("Carieră",    "amethyst"),
}


def domain_color(domain_id: str) -> str:
    palette = {
        "history":   "#d4cebf",
        "llm":       "#b5a8c9",
        "prompting": "#c98a82",
        "vision":    "#a5c5d4",
        "diffusion": "#d4a574",
        "speech":    "#d9b87a",
        "rag":       "#a8c0ae",
        "agents":    "#e8a598",
        "tools":     "#c4b9a7",
        "career":    "#c98a82",
    }
    return palette.get(domain_id, "#b5a8c9")


# ---------------------------------------------------------------
# Backward-compatible aliases for old `from learning.chapters import …`
# names (DOMAIN_META, COMPLEXITY_META, get_root_id, Method).
# ---------------------------------------------------------------

DOMAIN_META = {
    d: {"label": lbl, "color": domain_color(d), "blurb": ""}
    for d, (lbl, _) in DOMAINS.items()
}

COMPLEXITY_META = {
    "foundations": {"label": "Lvl 1 · fundamente",    "color": "#d4cebf"},
    "applied":     {"label": "Lvl 2 · aplicat",        "color": "#a8c0ae"},
    "specialist":  {"label": "Lvl 3 · specialist",     "color": "#b5a8c9"},
}


def get_root_id() -> str:
    """Return the canonical first chapter id."""
    return CHAPTERS[0].id
