import streamlit as st
import os

# --- RENDER SQLITE FIX ---
# Render's default SQLite is too old for ChromaDB. 
# We swap it with pysqlite3-binary if running on Linux.
if os.environ.get("IS_RENDER") == "true":
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# --- CONFIGURATION ---
DATA_PATH = "data/"
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- PAGE SETUP ---
st.set_page_config(page_title="Nutri-RAG Advisor", page_icon="🥗", layout="wide")

# --- FUNCTIONS ---
@st.cache_resource
def get_vector_db():
    """Initializes and returns the Chroma vector database."""
    # Force CPU to save RAM on Render (512MB limit)
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}
    )
    
    # Ensure data directory exists
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        
    if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
        st.info("Ingesting nutrition documents into vector database...")
        # Load Markdown files from data/
        loader = DirectoryLoader(DATA_PATH, glob="*.md", loader_cls=TextLoader)
        docs = loader.load()
        
        if not docs:
            st.warning("No documents found in 'data/' folder. Please add .md files.")
            return None
            
        # Split into chunks (Recursive Strategy)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(docs)
        
        # Create Chroma DB
        db = Chroma.from_documents(
            chunks, embeddings, persist_directory=CHROMA_PATH
        )
        st.success(f"Indexed {len(chunks)} nutrition data chunks.")
    else:
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    return db

def render_home():
    st.title("🥗 Nutri-RAG Knowledge Engine")
    st.markdown("""
    Welcome to the **Nutrition Science RAG Advisor**. This application uses 
    **Retrieval-Augmented Generation** to provide scientifically verified 
    answers regarding human nutrition.
    
    ### Core Knowledge Domains:
    - **Micronutrient Synergy:** Vitamin D, Iron, and Bioavailability.
    - **Metabolic Science:** The Leucine Threshold and mTOR activation.
    - **Gut Health:** SCFAs, Microbiome diversity, and Butyrate.
    - **Sports Nutrition:** Creatine, Beta-alanine, and Performance.
    - **Clinical Therapy:** Glycemic Load and Type 2 Diabetes management.
    - **Lifecycle Nutrition:** Maternal, Pediatric, and Geriatric needs.
    """)

def render_search():
    st.title("🔍 Semantic Science Search")
    db = get_vector_db()
    
    if db is None:
        st.error("Vector database could not be initialized. Check your 'data/' folder.")
        return

    query = st.text_input("Ask a nutrition science question:", 
                         placeholder="e.g., What is the risk of high protein intake?")
    
    if query:
        with st.spinner("Analyzing scientific documents..."):
            # Perform Similarity Search
            results = db.similarity_search_with_relevance_scores(query, k=3)
            
            if results:
                st.subheader("Top Research Findings:")
                for doc, score in results:
                    with st.expander(f"Source: {os.path.basename(doc.metadata.get('source', 'Unknown'))} (Relevance: {score:.2f})"):
                        st.write(doc.page_content)
                        st.caption(f"Context: Scientific Database | Match Quality: {score*100:.1f}%")
            else:
                st.warning("No direct matches found in the current database.")

def render_stats():
    st.title("📊 Database Statistics")
    if os.path.exists(DATA_PATH):
        files = os.listdir(DATA_PATH)
        st.metric("Documents in /data", len(files))
        st.write("Current Inventory:")
        for f in files:
            st.text(f"📄 {f}")
    else:
        st.error("Data directory not found.")

# --- MAIN APP FLOW ---
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Search Science", "Data Stats"])
    
    if page == "Home":
        render_home()
    elif page == "Search Science":
        render_search()
    elif page == "Data Stats":
        render_stats()

if __name__ == "__main__":
    main()
