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

**Model used:** `intfloat/multilingual-e5-small`

I chose a multilingual model because the app is in **Slovenian**, a language not supported by the default English-only `all-MiniLM-L6-v2`. The final model choice required two iterations due to a deployment constraint:

| Model | Parameters | Runtime RAM | Slovenian | Render free tier |
|-------|-----------|-------------|-----------|-----------------|
| `all-MiniLM-L6-v2` (default) | 22M | ~90 MB | ❌ | ✅ fits |
| `paraphrase-multilingual-MiniLM-L12-v2` (first attempt) | 118M | ~470 MB | ✅ | ❌ OOM crash |
| `intfloat/multilingual-e5-small` (final) | 33M | ~117 MB | ✅ | ✅ fits |

**Deployment issue encountered:** After switching to `paraphrase-multilingual-MiniLM-L12-v2`, Render's free web service (512 MB RAM) crashed on startup with exit code 2. The model's 118M parameters require ~470 MB of RAM at runtime, which — combined with PyTorch, ChromaDB, and Streamlit — exceeded the memory limit.

**Solution:** I switched to `intfloat/multilingual-e5-small`, which supports 100+ languages including Slovenian, uses the same 384-dimensional embedding space as the default model, and fits comfortably within the 512 MB limit at ~117 MB runtime RAM. Slovenian search quality is preserved since the model was explicitly trained on multilingual data.

The model is loaded once at startup with `@st.cache_resource` to avoid re-downloading on every query, and forced to CPU to ensure compatibility with Render's environment.

---

### Interesting Findings

- **Off-topic queries behave gracefully:** Searching for unrelated terms like *"avto"* (car) or *"vreme"* (weather) still returns results (ChromaDB always returns k results), but with very low match percentages (~5–15%). The match % label on each card makes this visible to the user, so they can judge result quality themselves.

- **Symptom combinations improve recipe matching:** Selecting a single symptom like *"Utrujenost"* returns a good recipe, but combining *"Utrujenost"* + *"Megla v glavi"* shifts the result toward energy-and-focus recipes (like the Frittata or Poke Bowl), which are semantically closer to the combined query vector. The multilingual model handles compound Slovenian terms well.

- **Recipe filter was essential:** Before adding the `filter={"source": "recipe"}` metadata filter to the Mood-Prep Kitchen, the app would sometimes return a research document chunk (e.g. a paragraph about fatty acids) instead of a recipe. The filter guarantees the Kitchen page always shows structured, cook-ready results.

---

## Page 3: Reflections & Extensions

### What I Learned
This project tied together everything from the course in a concrete, deployable product. The most valuable insight was understanding how `chunk_size` is not just a technical parameter but a semantic design decision — it determines how much *context* travels with each retrieved result. I also learned that multilingual embedding models require almost no extra effort to integrate but unlock an entirely different audience for the application.

### What I Would Improve With More Time
- **Add LLM response generation:** The app currently returns raw document chunks. Connecting the Anthropic API (the key is already in `.env`) would allow Claude to synthesize a conversational answer from the retrieved chunks — making it true RAG rather than retrieval-only.
- **Add user feedback:** A thumbs up/down button on each result would create a feedback loop to measure retrieval quality over time.
- **Expand the recipe database:** 10 recipes cover common symptoms but miss many combinations. Adding 20–30 more would improve the Kitchen's usefulness.
- **Hybrid search:** Combining semantic search (ChromaDB) with keyword search (BM25) would improve results for specific ingredient names or exact scientific terms.
