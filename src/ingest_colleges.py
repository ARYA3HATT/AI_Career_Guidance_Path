import pandas as pd
import json
from sentence_transformers import SentenceTransformer
import faiss
import os

# Define file paths relative to the project root
DATA_DIR = os.path.join('..', 'data')
RESULTS_DIR = os.path.join('..', 'results')
COLLEGES_CSV = os.path.join(DATA_DIR, 'colleges_seed.csv')
EMB_INDEX_FILE = os.path.join(RESULTS_DIR, 'colleges_faiss.index')
META_FILE = os.path.join(RESULTS_DIR, 'colleges_meta.json')

def build_text(row):
    """Combines relevant college info into a single string for the AI model."""
    return f"{row['name']} | {row['programs']} | {row['keywords']} | {row['city']}"

def main():
    """Reads the CSV, generates AI embeddings, and saves the search index."""
    print("Starting the ingestion process...")

    # Ensure the results directory exists
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 1. Load the data
    try:
        df = pd.read_csv(COLLEGES_CSV)
        print(f"Successfully loaded {len(df)} colleges from CSV.")
    except FileNotFoundError:
        print(f"ERROR: The file was not found at {COLLEGES_CSV}")
        print("Please make sure 'colleges_seed.csv' is inside the 'data' folder.")
        return

    # 2. Prepare text for the AI model
    texts = [build_text(row) for _, row in df.iterrows()]

    # 3. Use the AI model to create embeddings (numerical representations)
    print("Loading AI model and generating embeddings... (This might take a moment)")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    print("Embeddings generated successfully.")

    # 4. Build and save the FAISS search index
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, EMB_INDEX_FILE)
    print(f"FAISS index saved to {EMB_INDEX_FILE}")

    # 5. Save the metadata (the actual college info)
    with open(META_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)
    print(f"Metadata saved to {META_FILE}")
    
    print("\n✅ Ingestion complete. Your AI search index is ready!")

if __name__ == "__main__":
    main()