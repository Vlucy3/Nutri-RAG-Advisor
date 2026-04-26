# Her-RAG Svetovalka 2026 — Project Report
**Retrieval-Augmented Generation Web Application**
**Author:** Lucija Vovk | **GitHub:** https://github.com/Vlucy3/Nutri-RAG-Advisor | **Live App:** https://nutrition-rag-app.onrender.com

---

## Page 1: Application Overview

### Topic Description
I chose **women's hormonal nutrition** as the topic for this project. As a young woman, I find the connection between the menstrual cycle, food choices, and mood genuinely interesting, and I wanted to build something I would actually use. The app covers four hormonal phases of the menstrual cycle, science-backed recipes for specific symptoms (fatigue, anxiety, brain fog, bloating), and the latest 2024–2025 research on macronutrients, gut health, micronutrient synergy, and clinical nutrition.

### What the App Does
**Her-RAG Svetovalka 2026** is a Slovenian-language RAG web application with four pages:

- **Domov (Home)** — Introduction to the app and its purpose.
- **Hormonsko iskanje (Hormonal Search)** — Users type a nutrition question in Slovenian and the app returns the most relevant document chunks from the knowledge base, with a match percentage and source label.
- **Kuhinja za razpoloženje (Mood-Prep Kitchen)** — Users select how they feel from a list of symptoms (e.g. Utrujenost/Fatigue, Tesnoba/Anxiety) and the app retrieves the best-matching recipe with ingredients, instructions, and a scientific explanation.
- **Statistika (Stats)** — Shows the full knowledge base breakdown and a live chunking strategy comparison.

### Screenshot
*[INSERT SCREENSHOT of the Hormonsko iskanje page with a query and results here]*

### Links
- **GitHub repository:** https://github.com/Vlucy3/Nutri-RAG-Advisor
- **Live Render deployment:** https://nutrition-rag-app.onrender.com

---

## Page 2: Technical Details

### Documents
The knowledge base contains **30 total documents** across three source types:

| Source | Count | Description |
|--------|-------|-------------|
| Science modules | 5 | Short hormonal science facts (infradian rhythm, cortisol, PCOS, endometriosis, estrogen metabolism) |
| Recipes | 10 | Mood-targeted recipes with ingredients, instructions, and biochemical mechanisms |
| Research documents | 15 | Longer markdown files sourced and adapted from WHO guidelines, Endocrine Society publications, Nature Metabolism (2024), and nutrition science literature |

All content was written in **Slovenian**. Research documents cover topics including: menstrual cycle phase nutrition, gut microbiome and SCFAs, macronutrient metabolism, hydration kinetics, micronutrient synergy, plant-based bioenergetics, clinical diabetes nutrition, sports ergogenic aids, dietary guidelines 2020–2025, and practical eating tips.

---

### Chunking Strategy *(most important section)*

**Chosen strategy: `chunk_size=600, chunk_overlap=100`**

I chose `chunk_size=600` because my documents contain multi-sentence scientific explanations that lose meaning when split too finely. A chunk of 600 characters is large enough to keep a full hormonal phase description (e.g. the entire Luteal phase paragraph) in a single chunk, which means retrieval returns complete, context-rich answers rather than isolated fragments.

The `chunk_overlap=100` ensures that sentences spanning a chunk boundary are not lost — if a key recommendation appears at the end of one chunk, it also appears at the start of the next, preventing gaps in retrieved context.

**Comparison with Strategy B: `chunk_size=150, chunk_overlap=20`**

I tested a second strategy using micro-chunks (150/20), which is visible live in the Statistika page of the app. The results were clearly worse:

> **Example query:** *"lutealna faza in magnezij"* (luteal phase and magnesium)
>
> - **Strategy A (600/100):** Returned the full Luteal phase paragraph: *"Progesteron prevladuje in dviga bazalno presnovno hitrost za 100–300 kalorij... Osredotočite se na živila, bogata z magnezijem (bučna semena, špinača), da zmanjšate zadrževanje vode in tesnobo..."* — full context, actionable recommendation included.
>
> - **Strategy B (150/20):** Returned only a recipe fragment: *"Magnezij (kakav) + B6 (banana) = tvorba melatonina za globok spanec."* — the magnesium reference was found, but without any hormonal context or dietary reasoning.

**Conclusion:** Strategy A (600/100) consistently returns richer, more informative chunks. Strategy B produces more precise keyword matching but sacrifices the surrounding scientific context that makes the answer useful.

---

### Embedding Model

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`

The final model selection required three iterations, each revealing a different constraint:

| Model | Parameters | Runtime RAM | Render | Search quality |
|-------|-----------|-------------|--------|---------------|
| `all-MiniLM-L6-v2` (default, **final**) | 22M | ~90 MB | ✅ fits | ✅ excellent |
| `paraphrase-multilingual-MiniLM-L12-v2` (attempt 1) | 118M | ~470 MB | ❌ OOM crash | — |
| `intfloat/multilingual-e5-small` (attempt 2) | 33M | ~117 MB | ✅ fits | ❌ poor match |

**Attempt 1 — Out of memory:** After switching to `paraphrase-multilingual-MiniLM-L12-v2`, Render's free web service (512 MB RAM) crashed on startup with exit code 2. The model's 118M parameters require ~470 MB RAM at runtime which, combined with PyTorch, ChromaDB, and Streamlit, exceeded the limit.

**Attempt 2 — Semantic mismatch:** `intfloat/multilingual-e5-small` fitted in memory but produced poor recipe matches in the Mood-Prep Kitchen. E5 models require explicit `"query: "` and `"passage: "` prefixes during encoding to work correctly. LangChain's `HuggingFaceEmbeddings` does not add these prefixes automatically, causing a mismatch between document and query embedding spaces.

**Final decision:** Reverted to `all-MiniLM-L6-v2`. The knowledge base is in English and the model produces reliable, high-quality semantic matches. It fits comfortably within Render's 512 MB limit and is loaded once at startup with `@st.cache_resource`, forced to CPU for deployment compatibility.

---

### Interesting Findings

- **Off-topic queries behave gracefully:** Searching for unrelated terms like *"car engine"* or *"weather forecast"* still returns results (ChromaDB always returns k results), but with very low match percentages (~5–15%). The match % label on each result card makes this visible to the user so they can judge relevance themselves.

- **Symptom combinations improve recipe matching:** Selecting a single symptom like *"Fatigue"* returns a good recipe, but combining *"Fatigue"* + *"Brain Fog"* shifts the result toward energy-and-focus recipes (like the Frittata or Poke Bowl), which are semantically closer to the combined query vector. The model handles multi-symptom queries well because the joint embedding captures the intersection of both concepts.

- **Recipe filter was essential:** Before adding the `filter={"source": "recipe"}` metadata filter to the Mood-Prep Kitchen, the app would sometimes return a research document chunk (e.g. a paragraph about fatty acids) instead of a recipe card. The filter guarantees the Kitchen page always shows structured, cook-ready results.

---

## Page 3: Reflections & Extensions

### What I Learned
This project tied together everything from the course in a concrete, deployable product. The most valuable insight was understanding how `chunk_size` is not just a technical parameter but a semantic design decision — it determines how much *context* travels with each retrieved result. I also learned that embedding model selection is a real engineering decision: two models that look similar on paper (both ~100MB, both multilingual) can behave very differently in production due to architectural requirements like query/passage prefixes, and that memory constraints on free cloud tiers must be accounted for from the start.

### What I Would Improve With More Time
- **Add LLM response generation:** The app currently returns raw document chunks. Connecting the Anthropic API (the key is already in `.env`) would allow Claude to synthesize a conversational answer from the retrieved chunks — making it true RAG rather than retrieval-only.
- **Add user feedback:** A thumbs up/down button on each result would create a feedback loop to measure retrieval quality over time.
- **Expand the recipe database:** 10 recipes cover common symptoms but miss many combinations. Adding 20–30 more would improve the Kitchen's usefulness.
- **Hybrid search:** Combining semantic search (ChromaDB) with keyword search (BM25) would improve results for specific ingredient names or exact scientific terms.
