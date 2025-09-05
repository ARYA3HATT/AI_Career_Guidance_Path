from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import os
import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# --- 1. SETUP & LOADING AI MODELS ---

app = FastAPI(
    title="AI Career Guidance API",
    description="Provides intelligent career recommendations using semantic search.",
    version="2.0.0" # Version up!
)

# --- CORS Middleware ---
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load AI Models and Data ---
# This section runs once when the server starts up.
MODEL_NAME = 'all-MiniLM-L6-v2'
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
INDEX_FILE = os.path.join(RESULTS_DIR, 'onet_faiss.index')
ONET_JSON_FILE = os.path.join(RESULTS_DIR, 'onet_processed.json')

try:
    print("Loading AI model, career data, and search index. This may take a moment...")
    # Load the sentence transformer model
    model = SentenceTransformer(MODEL_NAME)
    
    # Load the FAISS index (our AI's "brain")
    index = faiss.read_index(INDEX_FILE)
    
    # Load the career metadata
    with open(ONET_JSON_FILE, 'r') as f:
        CAREER_PATHS = json.load(f)
        
    print(f"✅ AI models and data loaded successfully. {len(CAREER_PATHS)} careers ready.")

except Exception as e:
    print(f"[FATAL ERROR] Could not load AI models or data files: {e}")
    model = None
    index = None
    CAREER_PATHS = []

# --- 2. DEFINE DATA MODELS ---

class UserProfile(BaseModel):
    academic_background: str
    interests: List[str]
    strengths: List[str]
    personality_traits: List[str]
    preferred_industries: List[str]

class CareerRecommendation(BaseModel):
    title: str
    description: str
    match_score: float = Field(..., description="A similarity score (0-1) from the AI model.")

# --- 3. THE NEW AI-POWERED LOGIC ---

def create_user_query(user_profile: UserProfile) -> str:
    """
    Combines the user's profile into a single, rich string for the AI to understand.
    """
    interests_str = ", ".join(user_profile.interests)
    strengths_str = ", ".join(user_profile.strengths)
    personality_str = ", ".join(user_profile.personality_traits)
    
    return (f"A person with an academic background in {user_profile.academic_background}, "
            f"with interests in {interests_str}. Their strengths are {strengths_str}, "
            f"and their personality is {personality_str}.")

# --- 4. DEFINE API ENDPOINTS ---

@app.get("/", summary="Health Check")
def read_root():
    return {"message": f"Welcome to the AI Career Guidance API! {len(CAREER_PATHS)} careers loaded."}

@app.post("/recommend", response_model=List[CareerRecommendation], summary="Get AI-Powered Career Recommendations")
def get_recommendations(user_profile: UserProfile):
    """
    This is our main endpoint. It now uses semantic search to find the best career matches.
    """
    if not all([model, index, CAREER_PATHS]):
        return []

    print("Received recommendation request with profile:", user_profile.dict())
    
    # 1. Create a rich query from the user's profile
    query_text = create_user_query(user_profile)
    
    # 2. Convert the user query into a numerical embedding
    query_embedding = model.encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    
    # 3. Perform the AI similarity search
    # We ask FAISS to find the top 5 most similar careers
    distances, indices = index.search(query_embedding, 5)
    
    # 4. Format and return the results
    recommendations = []
    for score, idx in zip(distances[0], indices[0]):
        career = CAREER_PATHS[idx]
        recommendations.append({
            "title": career['title'],
            "description": career['description'],
            "match_score": round(float(score), 2)
        })
        
    print(f"Returning {len(recommendations)} AI-powered recommendations.")
    return recommendations

