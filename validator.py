import os
from app import get_vector_db

def test_queries():
    print("--- 🧪 RAG Validation Test ---")
    db = get_vector_db()
    
    queries = [
        "What is the leucine threshold for muscle growth?",
        "How much Vitamin D is recommended in 2025?",
        "What are the benefits of Butyrate for the gut?",
        "What is a low Glycemic Load value?",
        "How to avoid hyponatremia during exercise?",
        "How do I fix a car engine?" # Irrelevant query
    ]
    
    for q in queries:
        print(f"\nQUERY: {q}")
        results = db.similarity_search_with_relevance_scores(q, k=1)
        if results:
            doc, score = results[0]
            print(f"RESULT: Found in {doc.metadata.get('title')} (Match Quality: {score*100:.1f}%)")
            print(f"CONTENT: {doc.page_content[:150]}...")
        else:
            print("RESULT: No relevant documents found.")

if __name__ == "__main__":
    test_queries()
