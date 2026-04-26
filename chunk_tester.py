import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- DATA FROM APP.PY ---
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
    {"title": "Menstrual Cycle Syncing", "content": "Phase-specific nutrition: 1. Menstrual: Iron & Anti-inflammatories (red meat, ginger). 2. Follicular: Fermented foods & Cruciferous (sauerkraut, broccoli) for estrogen metabolism. 3. Ovulatory: High fiber & Omega-3s (berries, salmon) to clear excess estrogen. 4. Luteal: Magnesium & Complex Carbs (sweet potatoes, seeds) to support BMR rise and serotonin."}
]

def run_test():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
    docs = [Document(page_content=d["content"], metadata={"title": d["title"]}) for d in NUTRITION_DATA]
    
    # STRATEGY 1: Context-Heavy (Your App's Setting)
    splitter_1 = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks_1 = splitter_1.split_documents(docs)
    db_1 = Chroma.from_documents(chunks_1, embeddings)
    
    # STRATEGY 2: Precision-Focused (Very Small Chunks)
    splitter_2 = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
    chunks_2 = splitter_2.split_documents(docs)
    db_2 = Chroma.from_documents(chunks_2, embeddings)
    
    queries = [
        "What should I eat during my luteal phase?",
        "How does alcohol affect my diet?"
    ]
    
    print("--- 🧪 CHUNKING COMPARISON REPORT ---")
    for q in queries:
        print(f"\nQUERY: {q}")
        
        print("\n[STRATEGY 1: 600/100 (Current App)]")
        res1 = db_1.similarity_search_with_relevance_scores(q, k=1)
        print(f"Match: {res1[0][0].page_content}")
        
        print("\n[STRATEGY 2: 150/20 (Micro-Chunks)]")
        res2 = db_2.similarity_search_with_relevance_scores(q, k=1)
        print(f"Match: {res2[0][0].page_content}")

if __name__ == "__main__":
    run_test()
