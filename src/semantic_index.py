import json
import os
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# --- Configuration ---
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
ONET_JSON_FILE = os.path.join(RESULTS_DIR, 'onet_processed.json')
INDEX_FILE = os.path.join(RESULTS_DIR, 'onet_faiss.index')

# The name of the AI model we'll use from Hugging Face
MODEL_NAME = 'all-MiniLM-L6-v2'

def create_text_for_embedding(career: dict) -> str:
    """
    Combines the most important text fields of a career into a single string.
    This gives the AI a rich context to understand the career's meaning.
    """
    title = career.get('title', '')
    description = career.get('description', '')
    tasks = ". ".join(career.get('tasks', []))
    skills = ", ".join(career.get('skills', []))
    
    # Combine everything into a comprehensive paragraph
    return f"Career Title: {title}. Description: {description}. Common Tasks: {tasks}. Required Skills: {skills}."

def main():
    """
    Main function to build and save the semantic search index.
    """
    print("--- Starting AI Index Building Process ---")
    
    # --- 1. Load the processed O*NET data ---
    try:
        with open(ONET_JSON_FILE, 'r') as f:
            careers = json.load(f)
        print(f"Step 1: Successfully loaded {len(careers)} careers from {ONET_JSON_FILE}.")
    except FileNotFoundError:
        print(f"[ERROR] The file {ONET_JSON_FILE} was not found. Please run the ingest_onet.py script first.")
        return

    # --- 2. Create the rich text descriptions for each career ---
    career_texts = [create_text_for_embedding(career) for career in careers]
    print("Step 2: Created rich text descriptions for all careers.")

    # --- 3. Load the AI model and generate embeddings ---
    print(f"Step 3: Loading the '{MODEL_NAME}' AI model. This may take a few moments...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("         Generating embeddings for all careers. This is the main AI processing step and will take some time...")
    embeddings = model.encode(career_texts, show_progress_bar=True, convert_to_numpy=True)
    print("         Embeddings generated successfully.")

    # --- 4. Build and save the FAISS index ---
    # FAISS is a library for super-fast similarity search.
    embedding_dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(embedding_dimension) # Using Inner Product for similarity
    
    # We normalize the embeddings to use cosine similarity, which is great for text.
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    
    faiss.write_index(index, INDEX_FILE)
    print(f"Step 4: FAISS index with {index.ntotal} vectors saved to {INDEX_FILE}.")

    print("\n--- ✅ AI Index Building Complete ---")
    print("The AI has been trained on your career database.")

if __name__ == "__main__":
    main()
