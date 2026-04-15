# 🥗 Nutri-RAG Advisor 2026

A high-performance, RAM-optimized Retrieval-Augmented Generation (RAG) application specifically designed for **Nutrition Science and Food Science** queries. Built with Streamlit, LangChain, and ChromaDB.

## 🚀 Features
- **Semantic Search:** Uses `all-MiniLM-L6-v2` to understand nutrition context beyond simple keywords.
- **2025 Scientific Data:** Knowledge base includes the latest 2024/2025 consensus on Vitamin D (Endocrine Society) and Protein Metabolism (Nature Metabolism).
- **RAM Optimized:** Specifically configured to run within Render's 512MB free tier.
- **Multi-Page Layout:** Includes Search, Home, and Knowledge Base statistics.

## 🛠️ Tech Stack
- **Frontend/App:** [Streamlit](https://streamlit.io/)
- **Orchestration:** [LangChain](https://www.langchain.com/)
- **Vector Store:** [ChromaDB](https://www.trychroma.com/)
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2`

## 📦 Local Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## ☁️ Deployment (Render)
This project is pre-configured for **Render** via `render.yaml`. 
1. Connect your GitHub repository to Render.
2. It will automatically detect the blueprint and deploy the service.

## 📂 Data Inventory
The `/data` directory contains 10 core scientific modules:
- Micronutrient Synergy
- Macronutrient Metabolism (Leucine Threshold)
- Gut Microbiome (SCFAs)
- Sports Ergogenic Aids
- Clinical Diabetes Nutrition
- Plant-Based Bioenergetics
- Hydration Kinetics
- Food Science & Processing
- 2020-2025 Dietary Guidelines
- Lifecycle Nutrition (Gestation to Geriatrics)

---
**Disclaimer:** This is an AI-powered advisor based on specific scientific documents. Always consult a medical professional for personalized dietary advice.
