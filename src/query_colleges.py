import faiss
import json
from sentence_transformers import SentenceTransformer
import os

# Define file paths
RESULTS_DIR = os.path.join('..', 'results')
EMB_INDEX_FILE = os.path.join(RESULTS_DIR, 'colleges_faiss.index')
META_FILE = os.path.join(RESULTS_DIR, 'colleges_meta.json')
MODEL_NAME = "all-MiniLM-L6-v2"

def get_colleges_for_text(query_text, top_k=3):
    """Finds the top_k most relevant colleges for a given text query."""
    
    # 1. Load the AI model
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Convert the query text into a numerical embedding
    query_embedding = model.encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    
    # 3. Load the search index and metadata
    index = faiss.read_index(EMB_INDEX_FILE)
    with open(META_FILE, "r") as f:
        meta = json.load(f)
        
    # 4. Perform the AI-powered search
    distances, indices = index.search(query_embedding, top_k)
    
    # 5. Format and return the results
    results = []
    for score, idx in zip(distances[0], indices[0]):
        college_info = meta[idx]
        college_info['match_score'] = round(float(score), 2)
        results.append(college_info)
        
    return results

if __name__ == "__main__":
    # --- This is where you can test the recommender ---
    # Example: Let's find colleges for a career in design
    career_query = "A career in user experience and visual interface design"
    
    print(f"Finding top colleges for the query: '{career_query}'\n")
    
    recommended_colleges = get_colleges_for_text(career_query)
    
    for college in recommended_colleges:
        print(f"- {college['name']} (Score: {college['match_score']})")
        print(f"  Location: {college['city']}, {college['state']}")
        print(f"  Programs: {college['programs']}")
        print("-" * 20)