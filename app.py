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
from langchain.docstore.document import Document

# --- CONFIGURATION ---
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- 10 NUTRITION DOCUMENTS (Integrated List) ---
NUTRITION_DATA = [
    {"title": "Micronutrient Synergy", "content": "Vitamin D3 acts as a secosteroid hormone essential for intestinal calcium absorption. The 2025 RDA remains 600-800 IU. Synergy exists with Vitamin K2, which directs calcium to bones rather than arteries. Non-heme iron absorption is enhanced by Vitamin C via the reduction of ferric to ferrous iron."},
    {"title": "Protein & Leucine", "content": "The Leucine Threshold is the ~2.5g of leucine required to trigger mTORC1 for muscle protein synthesis. High-quality proteins like whey (DIAAS ~1.09) are superior to plant sources (soy ~0.90) for reaching this threshold quickly with lower total calories."},
    {"title": "Gut Microbiome", "content": "Short-Chain Fatty Acids (SCFAs) like Butyrate are produced via fermentation of resistant starch. Butyrate is the primary fuel for colonocytes and has anti-inflammatory properties through HDAC inhibition. Diversity in plant intake (30+ types/week) is the best predictor of gut health."},
    {"title": "Sports Ergogenics", "content": "Creatine monohydrate increases phosphocreatine stores by 20-40%, facilitating rapid ATP regeneration. Beta-alanine acts as an intracellular buffer by increasing carnosine levels. Caffeine (3-6 mg/kg) reduces perceived exertion by antagonizing adenosine receptors."},
    {"title": "Diabetes & GL", "content": "Medical Nutrition Therapy for Type 2 Diabetes focuses on Glycemic Load (GL) rather than just Glycemic Index. A GL < 10 is low-impact. Fiber intake of 50g/day has been shown to significantly lower HbA1c levels and improve insulin sensitivity."},
    {"title": "Hydration Homeostasis", "content": "Hydration is governed by plasma osmolality (280-295 mOsm/kg). Hyponatremia occurs when over-hydrating with plain water dilutes sodium levels (<135 mmol/L). Electrolytes Na+ and K+ are critical for the Na+/K+-ATPase pump function."},
    {"title": "Food Processing", "content": "Thermal processing can degrade Vitamin C but increases bioavailability of Lycopene and Beta-carotene by breaking cell walls. Ultra-processed foods (NOVA Class 4) are linked to a 20% increase in all-cause mortality due to low nutrient density."},
    {"title": "Dietary Guidelines", "content": "The 2020-2025 DGA recommends limiting added sugars to <10% and sodium to <2300mg. It introduces 'The First 1000 Days' focus, emphasizing iron and Vitamin D for infants. The Healthy Eating Index (HEI) average for Americans is currently 58/100."},
    {"title": "Lifecycle Nutrition", "content": "Maternal needs include 400-600mcg of Folate to prevent neural tube defects. Geriatric needs focus on preventing sarcopenia with 1.2-1.5g/kg protein and addressing Vitamin B12 malabsorption due to decreased intrinsic factor production."},
    {"title": "Plant-Based Optimization", "content": "Vegan diets require B12 supplementation (2.4mcg) and strategic Lysine intake. The conversion of ALA to EPA/DHA is inefficient (<5%), making algae-based DHA supplements beneficial for maintaining omega-3 status without fish consumption."}
]

# --- PAGE SETUP ---
st.set_page_config(page_title="Nutri-RAG Advisor", page_icon="🥗", layout="wide")

@st.cache_resource
def get_vector_db():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={'device': 'cpu'})
    if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
        docs = [Document(page_content=d["content"], metadata={"title": d["title"]}) for d in NUTRITION_DATA]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        db = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)
        return db
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

def clear_db():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    st.cache_resource.clear()
    st.success("Database cleared! Refresh the page to re-ingest.")

# --- SIDEBAR ---
st.sidebar.title("🥗 Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Semantic Search", "Nutrition Stats"])
if st.sidebar.button("🗑️ Clear Database"):
    clear_db()

# --- PAGES ---
if page == "Home":
    st.title("🥗 Nutrition Knowledge Engine")
    st.write("Welcome to your RAG-powered nutrition science advisor. Explore the latest in metabolic health and food science.")

elif page == "Semantic Search":
    st.title("🔍 Search Science")
    db = get_vector_db()
    query = st.text_input("Ask a question:", placeholder="e.g., What is the leucine threshold?")
    if query:
        results = db.similarity_search_with_relevance_scores(query, k=3)
        for doc, score in results:
            with st.expander(f"Source: {doc.metadata['title']} (Match: {score:.2f})"):
                st.write(doc.page_content)

elif page == "Nutrition Stats":
    st.title("📊 Nutrition Stats")
    st.metric("Total Knowledge Modules", len(NUTRITION_DATA))
    st.write("Current Database Inventory:")
    for d in NUTRITION_DATA:
        st.text(f"• {d['title']}")
