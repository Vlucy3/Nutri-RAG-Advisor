import streamlit as st
import os
import shutil

# --- RENDER SQLITE FIX ---
if os.environ.get("IS_RENDER") == "true":
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- CONFIGURATION ---
CHROMA_PATH = "chroma_db_v12"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- CORE KNOWLEDGE: MODULES AND RECIPES ---
NUTRITION_DATA = [
    {"title": "Infradian Rhythm", "content": "Women's 28-day cycle syncing: Follicular (high insulin sensitivity), Luteal (higher BMR +300kcal)."},
    {"title": "Cortisol Management", "content": "Professional stress mitigation via Magnesium and Omega-3s to prevent visceral fat storage."},
    {"title": "PCOS Protocol", "content": "40:1 Myo-inositol ratio to restore ovulation and reduce hyperinsulinemia-driven androgens."},
    {"title": "Endometriosis Defense", "content": "MIND-DASH diet integration to reduce PGE2 prostaglandins and pelvic inflammation."},
    {"title": "Estrogen Metabolism", "content": "Fiber (35g) and I3C (Cruciferous) to prevent estrogen dominance and bloating."},
    {"title": "The Serotonin Stability Salad (Low Mood / PMS)", "content": "INGREDIENTS: 150g Roasted Turkey, 1/2 cup Quinoa, 1 cup Spinach, 2 tbsp Walnuts. \nINSTRUCTIONS: Mix roasted turkey with cooked quinoa and spinach. Top with walnuts. \nMECHANISM: Tryptophan (Turkey) + Complex Carbs (Quinoa) = Serotonin boost for the Luteal phase mood dips."},
    {"title": "The Dopamine Focus Bowl (Brain Fog / Focus)", "content": "INGREDIENTS: 150g Chicken/Tempeh, 1/2 cup Wild Rice, 1 cup Broccoli, 2 tbsp Pumpkin Seeds. \nINSTRUCTIONS: Steam broccoli. Layer wild rice, protein, and seeds. \nMECHANISM: Tyrosine (Protein) + Zinc (Seeds) = Dopamine synthesis for high-performance workday focus."},
    {"title": "The Cortisol-Quencher Stew (Anxiety / Stress)", "content": "INGREDIENTS: 1 cup Red Lentils, 1 tsp Turmeric, 1 can Coconut Milk, 2 cups Kale. \nINSTRUCTIONS: Simmer lentils and turmeric in coconut milk. Add kale last. \nMECHANISM: Curcumin anti-inflammatory + Lentil fiber = HPA-axis stabilization and glucose control."},
    {"title": "The Estrogen-Clearance Stir-fry (Bloating / Periods)", "content": "INGREDIENTS: 2 cups Broccoli/Cauliflower, 150g Tofu, 1 tbsp Ground Flaxseed. \nINSTRUCTIONS: Stir-fry veg and tofu. Sprinkle raw flaxseed over the top after heat. \nMECHANISM: I3C (Cruciferous) + Lignans (Flax) = Efficient hormone excretion to reduce bloating."},
    {"title": "The Energy-Resilience Frittata (Fatigue)", "content": "INGREDIENTS: 3 Omega-3 Eggs, 50g Smoked Salmon, 5 Asparagus spears. \nINSTRUCTIONS: Whisk eggs over chopped asparagus. Bake for 12 mins. Top with salmon. \nMECHANISM: Choline (Eggs) + EPA/DHA (Salmon) = Enhanced memory and mitochondrial ATP efficiency."},
    {"title": "The Gut-Brain Ferment Jar (Social Anxiety)", "content": "INGREDIENTS: 1/2 cup Kimchi, 1/2 cup Brown Rice, 100g Miso Salmon, Seaweed nori. \nINSTRUCTIONS: Layer rice, kimchi, and salmon in a jar. Eat with nori. \nMECHANISM: Probiotics (Kimchi) = Repaired gut barrier, reducing neuro-inflammation and irritability."},
    {"title": "The Magnesium Sleep Bake (Insomnia)", "content": "INGREDIENTS: 1/2 cup Oats, 1 tbsp Dark Cacao (>70%), 1 Banana, 1 tbsp Almond Butter. \nINSTRUCTIONS: Mash banana, mix with oats and cacao. Bake for 15 mins. \nMECHANISM: Magnesium (Cacao) + B6 (Banana) = Melatonin production for deep recovery sleep."},
    {"title": "The PCOS Insulin-Safe Oats (Sugar Cravings / Acne)", "content": "INGREDIENTS: 1/2 cup Steel-cut Oats, 1 tsp Cinnamon, 1/2 cup Berries, 1 tbsp Chia Seeds. \nINSTRUCTIONS: Cook oats. Stir in cinnamon and chia. Top with berries. \nMECHANISM: Cinnamon + Fiber (Chia) = Blunted glucose spike, reducing IGF-1 acne triggers."},
    {"title": "The Anti-Inflammatory Curry (Pelvic Pain)", "content": "INGREDIENTS: 1 cup Chickpeas, 2 tbsp Ginger, 1 Sweet Potato, 1 cup Spinach. \nINSTRUCTIONS: Sauté potato/chickpeas with curry spices and fresh ginger. Add spinach last. \nMECHANISM: Ginger (COX-inhibitor) = Reduced prostaglandin-induced pelvic cramping."},
    {"title": "The Focus-Fuel Poke Bowl (Mid-day Slump)", "content": "INGREDIENTS: 120g Tuna, 1/2 cup Edamame, 1 cup Cucumber, 2 Radishes. \nINSTRUCTIONS: Combine ingredients over greens. Dress with rice vinegar. \nMECHANISM: Iodine (Tuna) + Hydration (Cucumber) = Thyroid support and cellular hydration to fix brain fog."}
]

# --- PAGE SETUP ---
st.set_page_config(page_title="Her-RAG Advisor 2026", page_icon="🧘‍♀️", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #0f0c29; border-right: 1px solid #e94560; }
    .result-card { background-color: #16213e; padding: 25px; border-radius: 20px; border-left: 8px solid #e94560; box-shadow: 0 15px 25px rgba(0,0,0,0.4); margin-bottom: 25px; }
    h1, h2, h3 { color: #e94560; font-weight: 800; }
    .ingredient-tag { background-color: #1a1a2e; color: #95d5b2; padding: 3px 10px; border-radius: 5px; font-size: 0.9rem; border: 0.5px solid #2d6a4f; }
    .mechanism-box { background-color: #0f0c29; padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px dashed #e94560; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_vector_db():
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={'device': 'cpu'})
        if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
            docs = []
            for d in NUTRITION_DATA:
                is_recipe = "INGREDIENTS:" in d["content"]
                docs.append(Document(
                    page_content=d["content"],
                    metadata={"title": d["title"], "source": "recipe" if is_recipe else "module"}
                ))
            data_dir = "data"
            if os.path.exists(data_dir):
                for filename in sorted(os.listdir(data_dir)):
                    if filename.endswith(".md"):
                        with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
                            content = f.read()
                        title = filename.replace(".md", "").replace("_", " ").title()
                        docs.append(Document(page_content=content, metadata={"title": title, "source": "research"}))
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
            chunks = text_splitter.split_documents(docs)
            db = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)
            return db
        return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

def clear_db():
    st.cache_resource.clear()
    if os.path.exists(CHROMA_PATH):
        try: shutil.rmtree(CHROMA_PATH); st.success("Database Reset!")
        except: st.error("Restart app to clear database.")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3997/3997818.png", width=80)
    st.title("Her-RAG v2.5")
    page = st.radio("Menu", ["🏠 Home", "🧠 Hormonal Search", "🍲 Mood-Prep Kitchen", "📊 Stats"])
    if st.button("🗑️ Reset Database"): clear_db()

# --- PAGES ---
SOURCE_LABELS = {"recipe": "Recipe", "module": "Module", "research": "Research"}

if page == "🏠 Home":
    st.title("Welcome to Her-RAG 2026")
    st.markdown("Precision Nutrition & Behavioral Mood-Architecture for women.")

elif page == "🧠 Hormonal Search":
    st.title("🧠 Endocrine Repository")
    db = get_vector_db()
    query = st.text_input("Search for hormonal science:")
    if query:
        if db is None:
            st.error("Database unavailable. Please reset and try again.")
        else:
            try:
                results = db.similarity_search_with_relevance_scores(query, k=3)
                for doc, score in results:
                    relevance = int(score * 100)
                    source_label = SOURCE_LABELS.get(doc.metadata.get("source", ""), "")
                    st.markdown(f"""<div class="result-card">
                        <div style="float:right;color:#95d5b2;font-size:0.9rem;">Match: {relevance}% &middot; {source_label}</div>
                        <h3>{doc.metadata.get('title')}</h3>
                        <p>{doc.page_content}</p>
                    </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Search error: {e}")

elif page == "🍲 Mood-Prep Kitchen":
    st.title("🍲 Mood-Prep Kitchen")
    symptoms = st.multiselect("Today I feel:", ["Fatigue", "Anxiety", "Brain Fog", "Bloating", "Low Mood", "Sugar Cravings", "Insomnia", "Pelvic Pain"])

    if symptoms:
        db = get_vector_db()
        if db is None:
            st.error("Database unavailable. Please reset and try again.")
        else:
            with st.spinner("Finding recipe match..."):
                try:
                    all_results = db.similarity_search_with_relevance_scores(
                        " ".join(symptoms), k=50
                    )
                    recipes = [(doc, score) for doc, score in all_results
                               if doc.metadata.get("source") == "recipe"][:2]

                    if not recipes:
                        st.warning("No recipes found. Try clicking 'Reset Database' in the sidebar and refresh.")
                    else:
                        for doc, score in recipes:
                            title = doc.metadata.get('title')
                            content = doc.page_content
                            parts = content.split('\n')
                            ingredients = parts[0] if len(parts) > 0 else ""
                            instructions = parts[1] if len(parts) > 1 else ""
                            mechanism = parts[2] if len(parts) > 2 else ""

                            st.markdown(f"""
                                <div class="result-card">
                                    <h2 style="margin-top:0;">{title}</h2>
                                    <div style="margin-bottom:15px;">{ingredients}</div>
                                    <div style="font-style:italic;">{instructions}</div>
                                    <div class="mechanism-box"><b>🔬 Scientific Why:</b><br>{mechanism}</div>
                                </div>
                            """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Recipe search error: {e}")

elif page == "📊 Stats":
    md_files = sorted([f for f in os.listdir("data") if f.endswith(".md")]) if os.path.exists("data") else []
    recipe_count = sum(1 for d in NUTRITION_DATA if "INGREDIENTS:" in d["content"])
    module_count = len(NUTRITION_DATA) - recipe_count

    col1, col2, col3 = st.columns(3)
    col1.metric("Science Modules", module_count)
    col2.metric("Recipes", recipe_count)
    col3.metric("Research Documents", len(md_files))

    st.markdown("---")
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Science Modules")
        for d in NUTRITION_DATA:
            if "INGREDIENTS:" not in d["content"]:
                st.write(f"🔬 {d['title']}")
        st.subheader("Recipes")
        for d in NUTRITION_DATA:
            if "INGREDIENTS:" in d["content"]:
                st.write(f"🍳 {d['title']}")
    with col_right:
        st.subheader("Research Documents")
        for f in md_files:
            st.write(f"📄 {f.replace('.md', '').replace('_', ' ').title()}")

    st.markdown("---")
    st.subheader("🧪 Chunking Strategy Comparison")
    st.write("How the same document splits under two different strategies:")

    sample_path = os.path.join("data", "menstrual_cycle_nutrition.md")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            sample_text = f.read()
        sample_doc = [Document(page_content=sample_text, metadata={"title": "Menstrual Cycle Nutrition"})]

        splitter_a = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        splitter_b = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
        chunks_a = splitter_a.split_documents(sample_doc)
        chunks_b = splitter_b.split_documents(sample_doc)

        st.caption(f"Sample: **Menstrual Cycle Nutrition** — {len(sample_text)} total characters")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Strategy A: chunk_size=600, overlap=100** ✅ *used in this app*")
            st.markdown(f"*→ {len(chunks_a)} chunk(s) produced*")
            for i, c in enumerate(chunks_a):
                st.text_area(f"Chunk {i+1} ({len(c.page_content)} chars)", c.page_content, height=160, key=f"ca_{i}")
        with col_b:
            st.markdown(f"**Strategy B: chunk_size=150, overlap=20** — micro-chunks")
            st.markdown(f"*→ {len(chunks_b)} chunk(s) produced*")
            for i, c in enumerate(chunks_b):
                st.text_area(f"Chunk {i+1} ({len(c.page_content)} chars)", c.page_content, height=160, key=f"cb_{i}")
