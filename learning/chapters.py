"""Learning chapters · OpenRadar · Drumul Erica.

We replaced the Sebastian Rey BLUE AI Road (course page) with a
NARRATIVE-DRIVEN, ROMANIAN, STORY-ARCED curriculum:

    era 1 (reguli) → era 2 (ML) → era 3 (DL) → era 4 (LLM) →
    era 5 (restricții guvernamentale) → era 6 (fuziune) →
    TU, aici, acum.

Why this matters:
- ChatGPT poate face un curs AI 101. Nu poate face un curs care
  leagă fundamentele cu realitatea 2026 (AI Act, export controls,
  open-source model gap) ȘI cu un proiect personal care se
  construiește pe parcurs (Erica). Asta e diferența.
- 10 capitole nu 15 — mai puțin e mai mult când publicul e
  începător. Calitate > cantitate.

Each chapter has:
    - id         : "ch1" .. "ch10"  (kept stable for caches)
    - number     : 1..10
    - title      : capitol titlu scurt, RO
    - subtitle   : hook-ul (1 propoziție, RO)
    - body_md    : conținutul, markdown (cu '<svg>' inline pentru ilustrații)
    - verifiers  : 2-3 întrebări scurte «Ai înțeles?» — bifat e OK
    - build_this : 1 acțiune concretă pe care o faci ACUM
    - prereqs    : ["ch1", ...] — cap de capitole anterioare
    - domain     : "history" | "story" | "concepts" | "skills" |
                   "tools" | "policy" | "fusion" | "career"
    - era        : "1950" | "1970" | "2012" | "2017" | "2022" |
                   "2025" | "2026" | "tu"
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
    era="2012",
)


# ---------------------------------------------------------------
# CAPITOLUL 02 · Proiectul Erica
# ---------------------------------------------------------------

CH2_BODY = r"""
Aici începe povestea personală. **Pe parcursul acestor 10 capitole
construim un singur lucru: un asistent AI pe care îl cheamă Erica.**

### Ce va fi Erica

Un asistent personal — al tău, pe laptopul tău, care:

- îți citește email-urile și îți scrie draft-uri de răspuns.
- citește notițele tale și extrage task-uri.
- te ajută la cod, în editor.
- răspunde la întrebări chiar și când ești offline.
- nu trimite nimic pe niciun server, dacă nu vrei.

### Cum o construim

Fiecare capitol adaugă o piesă concretă la Erica:

| Capitol | Ce primește Erica |
|---|---|
| 3 — Cum gândește un LLM | alegi modelul potrivit |
| 4 — Prompting | îi dai instrucțiuni clare |
| 5 — Cum construiești cu AI | o faci să ruleze local (Ollama) |
| 6 — Restricții | înțelegi limitele |
| 7 — Fuziune | combini mai multe modele |
| 8 — Unelte | o integrezi în workflow-ul tău |
| 9 — Portofoliu | o arăți lumii |
| 10 — Aplică | o folosești ca să aplici la joburi |

La finalul cursului ai: **un asistent AI personal, instalat pe
laptop, care te cunoaște și te ajută**. Nu e toy. E infrastructură
pentru cariera ta.

### De ce contează

Nu construim Erica ca exercițiu tehnic. O construim ca **să
demonstrăm un principiu**: cine știe să-și facă propriul AI tool
are un edge real în piață. Nu "știu să folosesc ChatGPT". Ci
"am un sistem AI personal care face exact ce am eu nevoie".

### Unde ești acum

Ai ales drumul. Capitolul următor: cum stă Erica în spatele
cortinei — cum "gândește" un LLM. Fără matematică, cu analogii.
"""

CH2 = Chapter(
    id="ch2",
    number=2,
    title="Proiectul Erica",
    subtitle="Construim împreună un asistent AI personal. Îl vei folosi la muncă.",
    body_md=CH2_BODY,
    verifiers=[
        "Știu că Erica e un proiect personal al meu, nu o platformă corporativă.",
        "Știu că o construiesc pe parcursul capitolelor.",
        "Știu că o voi rula local și va fi a mea.",
    ],
    build_this=(
        "Scrie 3 sarcini repetitive pe care le faci la muncă și "
        "pe care vrei ca Erica să ți le preia. "
        "Fă o listă în Notes / Notion / pe hârtie."
    ),
    prereqs=["ch1"],
    domain="story",
    era="2026",
)


# ---------------------------------------------------------------
# CAPITOLUL 03 · Cum gândește un LLM
# ---------------------------------------------------------------

CH3_BODY = r"""
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

CH3 = Chapter(
    id="ch3",
    number=3,
    title="Cum gândește un LLM",
    subtitle="Pattern-uri pe 500 GB de text. Nu gândește — prezice. Și e suficient cât să pară că gândește.",
    body_md=CH3_BODY,
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
    prereqs=["ch2"],
    domain="concepts",
    era="2022",
)


# ---------------------------------------------------------------
# CAPITOLUL 04 · Prompting ca un Pro
# ---------------------------------------------------------------

CH4_BODY = r"""
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

CH4 = Chapter(
    id="ch4",
    number=4,
    title="Prompting ca un Pro",
    subtitle="Comunică cu AI-ul ca un manager cu un coleg nou: clar, structurat, cu exemple.",
    body_md=CH4_BODY,
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
    prereqs=["ch3"],
    domain="skills",
    era="2022",
)


# ---------------------------------------------------------------
# CAPITOLUL 05 · Cum construiești cu AI
# ---------------------------------------------------------------

CH5_BODY = r"""
Chat-ul e pentru conversație. SDK-ul e pentru aplicații.
Diferența e **ceea ce poți automatiza**.

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

E un subiect avansat, dar important. Îl aprofundăm la capitolul
de unelte.

### Flow-uri fără cod

**n8n** (open-source) și **Langflow**: GUI drag-and-drop pentru a
construi pipeline-uri AI fără cod. Utile pentru automatizări simple.
Limitate pentru logică complexă.

### Ce construiești pentru Erica acum

La capitolul următor (Restricții) instalezi Ollama și descarci un
model local — primul pas pentru o Erica care rulează pe laptopul tău.
"""

CH5 = Chapter(
    id="ch5",
    number=5,
    title="Cum construiești cu AI",
    subtitle="Chat = pentru tine. SDK = pentru program. Ollama = pentru tine, fără internet.",
    body_md=CH5_BODY,
    verifiers=[
        "Știu diferența dintre chat și SDK/API.",
        "Știu ce e Ollama și de ce aș vrea să rulez AI local.",
        "Știu că OpenAI SDK funcționează cu multe modele compatibile.",
    ],
    build_this=(
        "Instalează Ollama (ollama.com). "
        "Descarcă `ollama pull llama3.2` (~2 GB). "
        "Conversează cu el din terminal: `ollama run llama3.2`. "
        "Întreabă-l ceva simplu. Salvează conversația."
    ),
    prereqs=["ch3"],
    domain="tools",
    era="2026",
)


# ---------------------------------------------------------------
# CAPITOLUL 06 · Restricțiile au venit
# ---------------------------------------------------------------

CH6_BODY = r"""
Din 2025, guvernele au tăiat accesul la cele mai puternice modele.
Nu e tehnică. E geopolitică. Capitolul ăsta îți pune contextul pe
care ChatGPT nu ți-l dă — pentru că nu vrea să te sperii.

### EU AI Act (intrat 2024–2025)

Uniunea Europeană a adoptat primul cadru legal cuprinzător pentru
AI. Orice model peste **10^25 FLOPs** de antrenament intră sub
regim special:

- evaluări de risc obligatorii
- transparență despre date
- supraveghere umană obligatorie pentru decizii
- interdicții pentru anumite use cases (social scoring, etc.)

Efectul: frontier labs (OpenAI, Anthropic, Google) trebuie să
respecte reguli înainte de a lansa modele în Europa. Unele le
launch-ui mai întâi în State, altele le restricționează.

### US Export Controls (Biden, continuate Trump)

SUA au blocat exportul de GPU-uri high-end (A100, H100, B200)
spre China și alte țări. E un Act al războiului tehnologic.

Asta a forțat China să-și construiască propriile GPU-uri (Huawei
Ascend) și propriile modele (DeepSeek, Qwen, GLM, Kimi).

### Efectul pentru tine

**Realitatea 2026**: modelele frontier sunt limitate, scumpe, sau
imposibil de accesat. Ce-ți rămâne:

| Tier | Ce ai | Cost | Calitate |
|---|---|---|---|
| Closed frontier | GPT-5, Claude Opus | $$$, API gate | ★★★★★ |
| Closed mid-tier | GPT-5 mini, Claude Haiku, Gemini Flash | $ | ★★★ |
| Open-weight top | Llama 3.3 70B, Qwen 2.5 72B | $0 (rulezi local) | ★★★★ |
| Open-weight small | Llama 3.2 3B, Phi 4, Gemma 2 | $0 | ★★ |

Dacă știi doar ChatGPT, te bazezi pe un singur tier și pe bunul
voinței unui singur vendor. Dacă știi fuziune, ești imun.

### Ce nu e apocalipsa

Restricțiile nu sunt "AI-ul se termină". Sunt **realiniere**. Cine
știe să combine modele mici e mai valoros decât cine știe să scrie
un prompt într-o singură fereastră.

Și mai e ceva: **open-source e mai bun ca niciodată**. Llama 3.3
70B bate GPT-4 la multe benchmark-uri. Qwen 2.5 bate GPT-4o la
matematică în limba chineză. Frontier ≠ best.

### Ce înseamnă pentru Erica

Erica va rula local (Ollama). Va fi **imună** la schimbările
geopolitice. Asta nu e pregătire pentru dezastru, e **design
inteligent**.

### Ce faci acum

Dacă încă nu ai Ollama instalat de la capitolul anterior, instalează.
Dacă l-ai instalat, descarcă și `qwen2.5` și `llama3.3` — începe să
experimentezi cu mai multe modele locale.
"""

CH6 = Chapter(
    id="ch6",
    number=6,
    title="Restricțiile au venit",
    subtitle="EU AI Act, export controls, China. Nu e tehnic, e geopolitic. Noi nu așteptăm.",
    body_md=CH6_BODY,
    verifiers=[
        "Știu ce e EU AI Act și de ce afectează modelele frontier.",
        "Știu de ce open-source (Llama, Qwen) e o alternativă reală.",
        "Știu că modelele locale pot fi imune la schimbările geopolitice.",
    ],
    build_this=(
        "Documentează 2 modele pe care le-ai folosit deja "
        "(unul closed, unul open) și unul pe care nu l-ai încercat. "
        "Notează: cost, context window, ce-l face bun, ce-l face slab."
    ),
    prereqs=["ch5"],
    domain="policy",
    era="2025",
)


# ---------------------------------------------------------------
# CAPITOLUL 07 · Era Fuziunii
# ---------------------------------------------------------------

CH7_BODY = r"""
Nu mai ai un model grozav. Ai 5 modele bune. **Trucul e să le faci
să lucreze împreună ca să simulezi unul grozav.** Asta e era 7.

### Conceptul: routing

Un model mic (3B) primește toate întrebările. Decide care model e
mai potrivit. Trimite întrebarea acolo.

```
Întrebare: "Cum sortez un array în Python?"
                    │
                    ▼
           ┌─── Router (Llama 3.2 3B) ───┐
           │ Decide: cod → Qwen Coder  │
           │ Decide: matematică → DeepSeek-Math │
           │ Decide: chat generic → Llama 3.3 70B │
           ▼
           Modelul ales răspunde
```

Cost: plătești un model mic permanent pentru decizie, dar taxezi
doar modelul mare când e nevoie.

### Conceptul: cascading

Model mic răspunde primul. Dacă nu e "sigur" pe răspuns (confidence
scăzut), pasează la model mare pentru verificare.

```
Răspuns mic (Qwen 3B): "Funcția sorted()"
        │
        ▼ Router analizează dacă e "complet"
        │
   ┌────┴─────┐
   │          │
 Încredere   Fără încredere
 mare (>0.8)  (<0.8)
   │          │
 Returnă     Trimite la Claude
 direct      Opus pentru răspuns complet
```

### Conceptul: ensemble

Trei modele generează răspunsuri. Un al patrulea le compară și
alege ce-i mai potrivit sau combină perspectivele.

```
Întrebare → LLM A, LLM B, LLM C (în paralel)
                │
                ▼
           LLM Judge — alege cel mai bun răspuns
                │
                ▼
           Output final
```

Costisitor, dar funcționează bine pentru decizii importante.

### Conceptul: prompt piping

Rezultatul unui model devine input pentru altul. Lanț de procesoare.

```
LLM 1: rezumă articolul (3 paragrafe)
LLM 2: extrage 5 idei principale (din rezumat)
LLM 3: generează un titlu SEO-friendly (din idei)
LLM 4: traduce în română (din titlu)
```

### Unelte care te ajută

- **OpenRouter** — un API key, 50+ modele, pay-as-you-go. Oferă
  routing în build.
- **LiteLLM** — proxy Python care route automat. Compatibil cu orice
  SDK OpenAI-style.
- **LangGraph** — orchestrare de fluxuri multi-agent. De studiat mai
  târziu (capitol intermediar).

### Analogia: bucătăria cu 5 bucătari

Nu mai ai un singur bucătar-șef care face tot. Ai o echipă unde:

- unul face paste,
- altul face desert,
- al treilea face salate,
- tu ești managerul care decide cine face ce.

Cu cât echipa e mai bună, cu atât meniul e mai divers.

### Ce construiești pentru Erica

Un **router simplu** care direcționează întrebări:
- dacă e despre cod → Qwen Coder (local)
- dacă e despre tine (date personale) → Llama 3.3 (local)
- dacă nu e sigur → Claude API (cloud)

Câteva zeci de linii Python. E cel mai important capitol tehnic.
"""

CH7 = Chapter(
    id="ch7",
    number=7,
    title="Era fuziunii",
    subtitle="5 modele bune > 1 model grozav. Routing, cascading, ensemble, prompt piping.",
    body_md=CH7_BODY,
    verifiers=[
        "Știu ce e routing și la ce ajută.",
        "Știu ce e cascading și cum diferă de ensemble.",
        "Știu ce e OpenRouter și de ce e util pentru experimentare.",
    ],
    build_this=(
        "Alege o sarcină pe care o faci des. "
        "Identifică 3 modele care ar fi bune pentru bucăți din ea. "
        "Testează pe OpenRouter (openrouter.ai) sau direct prin API. "
        "Notează care a câștigat și de ce."
    ),
    prereqs=["ch5", "ch6"],
    domain="fusion",
    era="2026",
)


# ---------------------------------------------------------------
# CAPITOLUL 08 · Cele 5 unelte
# ---------------------------------------------------------------

CH8_BODY = r"""
Nu ai nevoie de 50. Ai nevoie de **5**. Restul e shiny object
syndrome.

### Unelta 1 · Cursor

Editor de cod cu AI integrat. Poți vorbi cu codul tău:
"Refactorizează funcția asta", "Adaugă teste", "Explică de ce nu
merge". Poți selecta fișiere întregi ca context.

Folosește Claude sau GPT-5 sub capotă. Costă $20/lună pentru tier
Pro. Pentru cineva care scrie cod zilnic, e rentabil din prima lună.

### Unelta 2 · Claude Code CLI

Instrument terminal de la Anthropic. Rulează agenți AI care citesc,
editează, creează fișiere. Funcționează cu orice repo Git.

Diferența față de Cursor: stă în terminal, nu în editor. Bun pentru
sarcini lungi, multi-file, automatizări.

Instalezi cu `npm i -g @anthropic-ai/claude-code`. Primești un API
key de la Anthropic.

### Unelta 3 · n8n (sau Langflow)

GUI open-source pentru flow-uri AI fără cod.

Exemple:
- monitorizează un folder, când apare PDF trimite-l la Ollama, salvează
  rezumatul în Notion
- primește email, extrage task-uri, pune-le pe Trello
- scrapează un site zilnic, alertează-mă pe Telegram dacă apare ceva
  cu un keyword

Alternativă: **Langflow** pentru flow-uri mai vizuale și orientate
pe agenți AI.

### Unelta 4 · Ollama (repetat, important)

AI local, gratuit, offline. Îl ai deja din capitolul 5. Recomandare:

- pentru producție: Llama 3.3 70B (rulează pe 64 GB RAM sau Apple M2 Ultra+)
- pentru laptop normal: Qwen 2.5 14B sau Mistral Small
- pentru viteză: Llama 3.2 3B sau Phi 4 mini

### Unelta 5 · OpenRouter

Un API key, 50+ modele. Switch între ele la runtime. Excelent
pentru:

- testare mai rapidă
- failover (dacă un model e jos, altul preia)
- cost optimization (rutezi automat la cel mai ieftin)
- evaluare comparativă

### De ce aceste 5

Acoperă 95% din use case-uri reale, în România 2026:

- scrii cod → Cursor / Claude Code
- automatizezi ceva → n8n
- vrei AI pe date sensibile → Ollama
- experimentezi cu mai multe modele → OpenRouter

Restul (Lovable, Bolt, Windsurf, Cody, Continue) sunt bune, dar
adaugă complexity inutilă înainte să ai o bază solidă.

### Ce construiești pentru Erica acum

Un script (~100 linii Python) care:

1. Citește conținutul unui folder
2. Trimite fiecare fișier la Ollama (Llama 3.2 3B local)
3. Salvează rezumatele într-un fișier JSON
4. Permite query-uri: "ce zice fișierul X despre Y?"

Acesta e primul feature real al Erico-ai. Încă simplu, dar e al tău.
"""

CH8 = Chapter(
    id="ch8",
    number=8,
    title="Cele 5 unelte pe care trebuie să le stăpânești",
    subtitle="Cursor · Claude Code · n8n · Ollama · OpenRouter. Cu astea faci 95% din muncă.",
    body_md=CH8_BODY,
    verifiers=[
        "Am folosit sau testat Cursor.",
        "Am rulat Ollama cu un model local descărcat.",
        "Am făcut un mini-proiect cu n8n SAU am folosit OpenRouter.",
    ],
    build_this=(
        "Instalează toate 5 dacă nu le ai. "
        "Fă un script în Cursor care folosește Ollama local. "
        "Încarcă-l pe un repo Git (chiar și privat). "
        "Scrie un README de 10 rânduri."
    ),
    prereqs=["ch5", "ch7"],
    domain="tools",
    era="2026",
)


# ---------------------------------------------------------------
# CAPITOLUL 09 · Construiește-ți portofoliul
# ---------------------------------------------------------------

CH9_BODY = r"""
Recrutorii te judecă pe **30 de secunde din CV** și pe **GitHub**.
Fără proiecte, ești un alt «știu AI» pe hârtie.

### Principiul: 4 proiecte, fiecare demonstrează altceva

| # | Proiect | Demonstrează | Stack |
|---|---|---|---|
| 1 | CLI care rezumă fișiere locale cu Ollama | Local AI basics | Python + Ollama |
| 2 | Flow cu OpenRouter + cascading | Routing + cost optimization | Python + LiteLLM |
| 3 | Aplicație mică cu Cursor | Gen AI product thinking | Cursor + Claude |
| 4 | Agent cu MCP care citește un folder | Agentic AI | Claude Code + MCP |

### Anti-pattern-uri de evitat

- ❌ Tutorial clonat fără modificări.
- ❌ Demo toy fără date reale.
- ❌ Proiect fără README.
- ❌ Repo fără commit-uri regulate (arată că ai lucrat constant).

### Cum prezinți proiectul

README.md cu:

```
## Nume proiect
Scrie 1 propoziție: ce face și pentru cine.

## Demo
[link la video de 60 secunde SAU screenshot]

## Instalare
3 pași clari. Cineva care n-a lucrat cu tine să poată rula în 5 min.

## Ce am învățat
2-3 bullet-uri. Onest. Arată că ai gândit.
```

### Unde publici

- **GitHub** — toate 4 proiectele, publice sau private cu demo video.
- **LinkedIn** — pune-le în featured. Profilul tău se schimbă complet.
- **Site personal** (opțional) — despre al tău + 4 proiecte.

### Commit-uri regulate

Recrutorii se uită la activitatea ta GitHub. Arată consecvență:

- nu comita totul într-o zi
- arată iterații, experimentare, fails
- scrie mesaje de commit clare: "add routing for math queries", not "stuff"

### Mindset

Proiectele nu trebuie să fie perfecte. Trebuie să fie **oneste și
funcționale**. Un proiect simplu care merge e mai valoros decât unul
ambițios care nu merge.

Dacă ai 4 proiecte pe GitHub și 4 README-uri clare, ești deja în
top 20% al candidaților AI junior din România.

### Anti-procrastinare

Nu "când am inspirație". **Acum**. 30 de minute pe proiect pe zi.
În 12 zile ai 4 proiecte. În 30 de zile ai primul interview care
cere să povestești despre ele.
"""

CH9 = Chapter(
    id="ch9",
    number=9,
    title="Construiește-ți portofoliul",
    subtitle="4 proiecte, 4 README-uri, 1 profil LinkedIn. Asta te pune în top 20%.",
    body_md=CH9_BODY,
    verifiers=[
        "Am cel puțin 1 proiect publicat pe GitHub cu README.",
        "Am un profil LinkedIn actualizat cu proiectele.",
        "Știu diferența dintre proiect «demo» și proiect «real».",
    ],
    build_this=(
        "Alege un proiect pe care îl vei face ACUM. "
        "În 30 de minute creează repo + skeleton + README. "
        "Commită. Trimite link la 2 persoane. Cere feedback."
    ),
    prereqs=["ch8"],
    domain="career",
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
    "history":  ("Istoric", "cuminte/introvertit"),
    "story":    ("Poveste", "warm"),
    "concepts": ("Concepte", "lavender"),
    "skills":   ("Skills", "sage"),
    "tools":    ("Unelte", "coral"),
    "policy":   ("Politică", "amber"),
    "fusion":   ("Fuziune", "sky"),
    "career":   ("Carieră", "amethyst"),
}


def domain_color(domain_id: str) -> str:
    palette = {
        "history":  "#d4cebf",
        "story":    "#e8a598",
        "concepts": "#b5a8c9",
        "skills":   "#a8c0ae",
        "tools":    "#d4a574",
        "policy":   "#d9b87a",
        "fusion":   "#a5c5d4",
        "career":   "#c98a82",
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
