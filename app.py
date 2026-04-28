import streamlit as st
import os
import shutil

# --- RENDER SQLITE FIX ---
if os.environ.get("IS_RENDER") == "true":
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- CONFIGURATION ---
CHROMA_PATH = "chroma_db_v15"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# --- CORE KNOWLEDGE: MODULES AND RECIPES ---
NUTRITION_DATA = [
    {"title": "Infradian Rhythm (Cycle Syncing)", "content": "For women aged 25, nutrition must account for the infradian rhythm. In the Follicular phase, estrogen increases, leading to higher insulin sensitivity. Post-ovulation (Luteal), progesterone rises, increasing metabolic rate by 5-10%. Cravings during this time are often serotonin-driven; complex carbs can help."},
    {"title": "Professional Stress & Cortisol", "content": "Stress at age 25 triggers cortisol, which promotes visceral belly fat. Behavioral nutrition suggests 'Stress-Eating' is a biological attempt to lower cortisol. Magnesium and Omega-3s can dampen this response, reducing the urge for junk food during deadlines."},
    {"title": "The Satiety Index (Volume Eating)", "content": "Satiety per calorie is key for busy 20-somethings. Boiled potatoes and apples rank high; croissants rank low. 'Volume Eating'—high-fiber, high-water foods—stretches the stomach lining to signal the brain to stop eating via the vagus nerve."},
    {"title": "Dopaminergic UPF Cravings", "content": "Ultra-processed foods (UPFs) target the dopamine reward system. In a 25-year-old brain, the reward system is highly sensitive. The 'Crowding Out' strategy—adding protein before a craving food—helps regain cognitive control over portion sizes."},
    {"title": "Sleep-Leptin-Ghrelin Triangle", "content": "Under 7 hours of sleep leads to a 15% drop in Leptin (satiety) and a 25% spike in Ghrelin (hunger). This causes a 300-500 calorie surplus the next day, usually from sugar. Prioritize sleep to protect metabolic health."},
    {"title": "Peak Bone Mass Window", "content": "Age 25 is the final window for peak bone density. Behavioral priority must be given to 1,200mg Calcium and 2,000 IU Vitamin D3. This 'banks' minerals to prevent osteoporosis later in life. It is a critical period for skeletal health."},
    {"title": "Cognitive Bioenergetics (Focus)", "content": "Stable blood glucose prevents 'Brain Fog.' The 'Fiber First' rule—eating salad before starch—reduces glucose spikes by 30%. Choline (from eggs) and B-vitamins are essential for focus and memory during high-pressure workdays."},
    {"title": "Social Eating & Alcohol", "content": "Alcohol inhibits fat oxidation by 70%. Psychologically, it lowers inhibitions for high-calorie snacks. A 'Pre-Game' of 20g protein and water before an event reduces impulsive food choices by 40%."},
    {"title": "Hormonal Fat Synthesis", "content": "Cholesterol is the backbone of estrogen and progesterone. Diets under 20% fat can lead to hormonal imbalances. Prioritize avocados and olive oil for skin health, collagen, and hormonal regularity in your mid-20s."},
    {"title": "Protein Leverage Hypothesis", "content": "The body drives hunger until a protein threshold (1.2-1.6g/kg) is met. Prioritizing 30g of protein at breakfast sets the neurochemical tone for the day and significantly reduces late-night snacking behavior."},
    {"title": "Menstrual Cycle Syncing", "content": "Phase-specific nutrition: 1. Menstrual: Iron & Anti-inflammatories (red meat, ginger). 2. Follicular: Fermented foods & Cruciferous (sauerkraut, broccoli) for estrogen metabolism. 3. Ovulatory: High fiber & Omega-3s (berries, salmon) to clear excess estrogen. 4. Luteal: Magnesium & Complex Carbs (sweet potatoes, seeds) to support BMR rise and serotonin."},
    {"title": "Menstrual Phase Nutrition (Days 1-5)", "content": "The Menstrual Phase (Days 1-5) is when progesterone and estrogen are at their lowest. The primary physiological stress is iron loss and uterine inflammation caused by prostaglandins. Recommended foods: iron-rich sources such as heme iron from grass-fed beef or non-heme iron from lentils paired with Vitamin C to enhance absorption. Anti-inflammatory foods like ginger, turmeric, and dark chocolate (>70% cacao) help mitigate prostaglandin-induced cramping. Avoid excess sodium to reduce bloating."},
    {"title": "Follicular Phase Nutrition (Days 6-13)", "content": "The Follicular Phase (Days 6-13) is characterized by rising estrogen, which increases insulin sensitivity and energy levels. The body becomes more efficient at utilizing carbohydrates for fuel during this phase. Recommended foods: cruciferous vegetables (broccoli, cauliflower) containing Indole-3-Carbinol (I3C) to support estrogen metabolism. Fermented foods like kimchi or kefir support the estrobolome — gut bacteria that help metabolize and eliminate excess hormones."},
    {"title": "Ovulatory Phase Nutrition (Day 14)", "content": "The Ovulatory Phase occurs around Day 14 of the menstrual cycle. During ovulation, estrogen peaks and there is often a surge in energy, sociability, and a slight rise in body temperature. Luteinizing Hormone (LH) triggers the release of the egg. Recommended foods: high-fiber foods such as quinoa, berries, and flaxseeds are critical to bind and excrete excess estrogen through the digestive tract, preventing estrogen dominance. Anti-inflammatory Omega-3 fatty acids from wild-caught salmon or algae oil support the follicle's release and reduce inflammation."},
    {"title": "Luteal Phase Nutrition (Days 15-28)", "content": "The Luteal Phase (Days 15-28) is dominated by progesterone, which raises the basal metabolic rate (BMR) by 100-300 calories per day. Insulin sensitivity drops, making high-sugar foods more likely to cause fat storage and energy crashes. PMS symptoms like bloating, mood swings, and cravings are common. Recommended foods: magnesium-rich foods (pumpkin seeds, spinach) reduce PMS-related water retention and anxiety. Complex carbohydrates (sweet potatoes, chickpeas) provide glucose needed for serotonin production, preventing the common luteal-phase binge on refined sugars."},
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
        embeddings = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)
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
        except Exception as e:
            st.error(f"Could not delete database: {e}. Restart the app.")

@st.cache_data
def get_md_files():
    return sorted([f for f in os.listdir("data") if f.endswith(".md")]) if os.path.exists("data") else []

@st.cache_data
def get_chunk_comparison():
    sample_path = os.path.join("data", "menstrual_cycle_nutrition.md")
    if not os.path.exists(sample_path):
        return None, None, 0
    with open(sample_path, "r", encoding="utf-8") as f:
        sample_text = f.read()
    sample_doc = [Document(page_content=sample_text, metadata={"title": "Menstrual Cycle Nutrition"})]
    splitter_a = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    splitter_b = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
    return splitter_a.split_documents(sample_doc), splitter_b.split_documents(sample_doc), sample_text

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div style="font-size:3rem;text-align:center">🧘‍♀️</div>', unsafe_allow_html=True)
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
    md_files = get_md_files()
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

    chunks_a, chunks_b, sample_text = get_chunk_comparison()
    if chunks_a is not None:
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
