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
CHROMA_PATH = "chroma_db_v9"
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"

# --- JEDRO ZNANJA: MODULI IN RECEPTI ---
NUTRITION_DATA = [
    {"title": "Infradiani ritem", "content": "Usklajevanje 28-dnevnega cikla ženske: folikularna faza (visoka občutljivost za insulin), lutealna faza (višji BMH +300 kcal)."},
    {"title": "Upravljanje kortizola", "content": "Obvladovanje poklicnega stresa z magnezijem in omega-3 maščobnimi kislinami za preprečevanje visceralne maščobe."},
    {"title": "Protokol za PCOS", "content": "Razmerje mio-inozitola 40:1 za obnovitev ovulacije in zmanjšanje androgenov, ki jih poganja hiperinzulinemija."},
    {"title": "Obramba pred endometriozo", "content": "Integracija prehrane MIND-DASH za zmanjšanje prostaglandinov PGE2 in medeničnega vnetja."},
    {"title": "Presnova estrogena", "content": "Vlakna (35 g) in I3C (križnice) za preprečevanje prevlade estrogena in napenjanja."},
    {"title": "Solata za stabilnost serotonina (slabo razpoloženje / PMS)", "content": "SESTAVINE: 150 g pečene purice, 1/2 skodelice kinoje, 1 skodelica špinače, 2 žlici orehov. \nNAVODILA: Pomešajte pečeno purico s kuhano kinojo in špinačo. Potresite z orehi. \nMEHANIZEM: Triptofan (purica) + kompleksni ogljikovi hidrati (kinoja) = dvig serotonina za padce razpoloženja v lutealni fazi."},
    {"title": "Skleda za dopamin in fokus (megla v glavi)", "content": "SESTAVINE: 150 g piščanca/tempeha, 1/2 skodelice divjega riža, 1 skodelica brokolija, 2 žlici bučnih semen. \nNAVODILA: Poparjte brokoli. Nanizajte divji riž, beljakovine in semena. \nMEHANIZEM: Tirozin (beljakovine) + cink (semena) = sinteza dopamina za visoko storilnost pri delu."},
    {"title": "Enolončnica za umiritev kortizola (tesnoba / stres)", "content": "SESTAVINE: 1 skodelica rdeče leče, 1 čajna žlička kurkume, 1 pločevinka kokosovega mleka, 2 skodelici ohrovta. \nNAVODILA: Kuhajte lečo in kurkumo v kokosovem mleku. Ohrovt dodajte na koncu. \nMEHANIZEM: Protivnetni kurkumin + vlakna leče = stabilizacija osi HPA in nadzor glukoze."},
    {"title": "Pražena zelenjava za izločanje estrogena (napenjanje)", "content": "SESTAVINE: 2 skodelici brokolija/cvetače, 150 g tofuja, 1 žlica mletega lanenega semena. \nNAVODILA: Popražite zelenjavo in tofu. Na koncu potresite z lanenim semenom brez toplotne obdelave. \nMEHANIZEM: I3C (križnice) + lignani (lan) = učinkovito izločanje hormonov za zmanjšanje napenjanja."},
    {"title": "Frittata za energijo in vzdržljivost (utrujenost)", "content": "SESTAVINE: 3 omega-3 jajca, 50 g dimljenega lososa, 5 špargeljevih poganjkov. \nNAVODILA: Stepite jajca čez nasekljane špargle. Pecite 12 minut. Postrežite z lososom. \nMEHANIZEM: Holin (jajca) + EPA/DHA (losos) = izboljšan spomin in mitohondrijska učinkovitost ATP."},
    {"title": "Fermentirana posodica za črevesje in možgane (socialna tesnoba)", "content": "SESTAVINE: 1/2 skodelice kimčija, 1/2 skodelice rjavega riža, 100 g miso lososa, morske alge nori. \nNAVODILA: Nanizajte riž, kimči in lososa v posodico. Jejte z nori algami. \nMEHANIZEM: Probiotiki (kimči) = obnovitev črevesne bariere, zmanjšanje nevrovnetja in razdražljivosti."},
    {"title": "Magnezijeva peka za spanec (nespečnost)", "content": "SESTAVINE: 1/2 skodelice ovsa, 1 žlica temnega kakava (>70 %), 1 banana, 1 žlica mandljevega masla. \nNAVODILA: Zdrobite banano, pomešajte z ovsom in kakavom. Pecite 15 minut. \nMEHANIZEM: Magnezij (kakav) + B6 (banana) = tvorba melatonina za globok spanec."},
    {"title": "Inzulinsko varni ovseni kosmiči za PCOS (hrepenenje po sladkem)", "content": "SESTAVINE: 1/2 skodelice celoovesnih kosmičev, 1 čajna žlička cimeta, 1/2 skodelice jagodičja, 1 žlica čia semen. \nNAVODILA: Skuhajte ovsene kosmiče. Vmešajte cimet in čia semena. Potresite z jagodičjem. \nMEHANIZEM: Cimet + vlakna (čia) = zblažen porast glukoze, zmanjšanje akne, ki jih sproža IGF-1."},
    {"title": "Protivnetni kari (medenične bolečine)", "content": "SESTAVINE: 1 skodelica čičerike, 2 žlici ingverja, 1 sladki krompir, 1 skodelica špinače. \nNAVODILA: Popražite krompir/čičeriko z začimbami za kari in svežim ingverjem. Špinačo dodajte na koncu. \nMEHANIZEM: Ingver (zaviralec COX) = zmanjšanje medeničnih krčev, ki jih povzročajo prostaglandini."},
    {"title": "Poke skleda za fokus (popoldanska utrujenost)", "content": "SESTAVINE: 120 g tune, 1/2 skodelice edamame, 1 skodelica kumare, 2 redkvice. \nNAVODILA: Združite sestavine na zeleni solati. Polijte z riževim kisom. \nMEHANIZEM: Jod (tuna) + hidracija (kumara) = podpora ščitnici in celična hidracija za odpravo megle v glavi."}
]

# --- PAGE SETUP ---
st.set_page_config(page_title="Her-RAG Svetovalka 2026", page_icon="🧘‍♀️", layout="wide")

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
        try: shutil.rmtree(CHROMA_PATH); st.success("Baza podatkov ponastavljena!")
        except: st.error("Znova zaženite aplikacijo za brisanje baze.")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3997/3997818.png", width=80)
    st.title("Her-RAG v2.5")
    page = st.radio("Meni", ["🏠 Domov", "🧠 Hormonsko iskanje", "🍲 Kuhinja za razpoloženje", "📊 Statistika"])
    if st.button("🗑️ Ponastavi bazo"): clear_db()

# --- PAGES ---
SOURCE_LABELS = {"recipe": "Recept", "module": "Modul", "research": "Raziskava"}

if page == "🏠 Domov":
    st.title("Dobrodošli v Her-RAG 2026")
    st.markdown("Natančna prehrana in vedenjska arhitektura razpoloženja za ženske.")

elif page == "🧠 Hormonsko iskanje":
    st.title("🧠 Endokrini repozitorij")
    db = get_vector_db()
    query = st.text_input("Iskanje hormonske znanosti:")
    if query:
        if db is None:
            st.error("Baza podatkov ni na voljo. Ponastavite in poskusite znova.")
        else:
            try:
                results = db.similarity_search_with_relevance_scores(query, k=3)
                for doc, score in results:
                    relevance = int(score * 100)
                    source_label = SOURCE_LABELS.get(doc.metadata.get("source", ""), "")
                    st.markdown(f"""<div class="result-card">
                        <div style="float:right;color:#95d5b2;font-size:0.9rem;">Ujemanje: {relevance}% &middot; {source_label}</div>
                        <h3>{doc.metadata.get('title')}</h3>
                        <p>{doc.page_content}</p>
                    </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Napaka iskanja: {e}")

elif page == "🍲 Kuhinja za razpoloženje":
    st.title("🍲 Kuhinja za razpoloženje")
    symptoms = st.multiselect("Danes se počutim:", ["Utrujenost", "Tesnoba", "Megla v glavi", "Napenjanje", "Slabo razpoloženje", "Hrepenenje po sladkem", "Nespečnost", "Medenične bolečine"])

    if symptoms:
        db = get_vector_db()
        if db is None:
            st.error("Baza podatkov ni na voljo. Ponastavite in poskusite znova.")
        else:
            with st.spinner("Iščem recept..."):
                try:
                    results = db.similarity_search_with_relevance_scores(
                        " ".join(symptoms), k=2, filter={"source": "recipe"}
                    )
                    for doc, score in results:
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
                                <div class="mechanism-box"><b>🔬 Znanstveno ozadje:</b><br>{mechanism}</div>
                            </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Napaka iskanja recepta: {e}")

elif page == "📊 Statistika":
    md_files = sorted([f for f in os.listdir("data") if f.endswith(".md")]) if os.path.exists("data") else []
    recipe_count = sum(1 for d in NUTRITION_DATA if "SESTAVINE:" in d["content"])
    module_count = len(NUTRITION_DATA) - recipe_count

    col1, col2, col3 = st.columns(3)
    col1.metric("Znanstveni moduli", module_count)
    col2.metric("Recepti", recipe_count)
    col3.metric("Raziskovalni dokumenti", len(md_files))

    st.markdown("---")
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Znanstveni moduli")
        for d in NUTRITION_DATA:
            if "SESTAVINE:" not in d["content"]:
                st.write(f"🔬 {d['title']}")
        st.subheader("Recepti")
        for d in NUTRITION_DATA:
            if "SESTAVINE:" in d["content"]:
                st.write(f"🍳 {d['title']}")
    with col_right:
        st.subheader("Raziskovalni dokumenti")
        for f in md_files:
            st.write(f"📄 {f.replace('.md', '').replace('_', ' ').title()}")

    st.markdown("---")
    st.subheader("🧪 Primerjava strategij deljenja besedila")
    st.write("Kako se isti dokument razdeli pri dveh različnih strategijah:")

    sample_path = os.path.join("data", "menstrual_cycle_nutrition.md")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            sample_text = f.read()
        sample_doc = [Document(page_content=sample_text, metadata={"title": "Prehrana menstrualnega cikla"})]

        splitter_a = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        splitter_b = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
        chunks_a = splitter_a.split_documents(sample_doc)
        chunks_b = splitter_b.split_documents(sample_doc)

        st.caption(f"Vzorec: **Prehrana menstrualnega cikla** — {len(sample_text)} znakov skupaj")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Strategija A: chunk_size=600, overlap=100** ✅ *uporabljena v tej aplikaciji*")
            st.markdown(f"*→ {len(chunks_a)} kos(ov) besedila*")
            for i, c in enumerate(chunks_a):
                st.text_area(f"Kos {i+1} ({len(c.page_content)} znakov)", c.page_content, height=160, key=f"ca_{i}")
        with col_b:
            st.markdown(f"**Strategija B: chunk_size=150, overlap=20** — mikro-kosi")
            st.markdown(f"*→ {len(chunks_b)} kos(ov) besedila*")
            for i, c in enumerate(chunks_b):
                st.text_area(f"Kos {i+1} ({len(c.page_content)} znakov)", c.page_content, height=160, key=f"cb_{i}")
