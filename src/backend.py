from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import re

# --- MODULE 1: DATABASE (Temporary) ---
# This is our initial, hardcoded list of careers.
# Later, this will be replaced by our full AI engine reading from the O*NET database.
CAREER_PATHS = [
    {
        "name": "Software Engineer (Backend)",
        "description": "Builds and maintains the server-side logic of web applications.",
        "keywords": {
            "strengths": ["problem-solving", "logical thinking", "analytical", "coding", "debugging"],
            "interests": ["coding", "technology", "building things", "puzzles", "software"],
            "academic": ["computer science", "engineering", "mathematics", "software"]
        },
        "skills_to_acquire": ["Python or Java", "Database Management (SQL/NoSQL)", "API Design", "Cloud Computing (AWS/Azure)"],
        "resources": ["Coursera: 'Google IT Automation with Python'", "Book: 'Designing Data-Intensive Applications'"]
    },
    {
        "name": "Data Scientist",
        "description": "Uses data to answer complex questions and make predictions.",
        "keywords": {
            "strengths": ["analytical", "statistics", "math", "problem-solving", "coding", "curiosity"],
            "interests": ["data", "statistics", "machine learning", "research", "patterns"],
            "academic": ["statistics", "computer science", "mathematics", "physics", "economics"]
        },
        "skills_to_acquire": ["Python (Pandas, NumPy, Scikit-learn)", "SQL", "Statistical Modeling", "Machine Learning Concepts", "Data Visualization"],
        "resources": ["Coursera: 'IBM Data Science Professional Certificate'", "Kaggle.com for practical projects"]
    },
    {
        "name": "UX/UI Designer",
        "description": "Designs the user interface and experience for digital products.",
        "keywords": {
            "strengths": ["creative", "empathy", "visual design", "communication", "user research"],
            "interests": ["art", "design", "psychology", "technology", "drawing"],
            "academic": ["design", "psychology", "human-computer interaction", "art"]
        },
        "skills_to_acquire": ["Figma or Sketch", "User Research Methods", "Wireframing & Prototyping", "Color Theory & Typography"],
        "resources": ["Coursera: 'Google UX Design Professional Certificate'", "Nielsen Norman Group website"]
    }
]

# --- MODULE 2: ANALYSIS LOGIC ---
def analyze_user_data(user_data: dict) -> list:
    """
    Analyzes user data against the CAREER_PATHS database and returns
    a sorted list of scored career recommendations.
    """
    scored_careers = []
    for career in CAREER_PATHS:
        score = 0
        user_strengths = user_data.get('strengths', [])
        user_interests = user_data.get('interests', [])

        # Simple keyword matching logic with weights
        score += len(set(user_strengths) & set(career['keywords']['strengths'])) * 3
        score += len(set(user_interests) & set(career['keywords']['interests'])) * 2
        for keyword in career['keywords']['academic']:
            if keyword in user_data.get('academic_background', '').lower():
                score += 1

        if score > 0:
            scored_careers.append({"career": career, "score": score})

    # Sort careers by score in descending order
    return sorted(scored_careers, key=lambda x: x['score'], reverse=True)

# --- MODULE 3: FASTAPI SERVER SETUP ---

# Create the main FastAPI application instance
app = FastAPI(title="AI Career Guidance API")

# This is crucial security middleware. It allows our React frontend
# (which will run on a different address, like http://localhost:3000)
# to make requests to this backend server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, we allow all origins. For production, we would list our actual website's domain.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all request headers
)

# Define the data structure we expect from the React frontend using Pydantic.
# This ensures that the data sent to us is in the correct format.
class UserProfile(BaseModel):
    academic_background: str
    interests: list[str]
    strengths: list[str]

# --- API ENDPOINTS ---

@app.post("/recommend")
def get_recommendations(profile: UserProfile):
    """
    This is our main API endpoint. The React app will send a user's profile here.
    It receives the profile, runs our analysis logic, and returns the recommendations.
    """
    user_data_dict = profile.dict()
    recommendations = analyze_user_data(user_data_dict)
    return {"recommendations": recommendations}

@app.get("/")
def read_root():
    """
    This is a simple "health check" endpoint. We can visit this in a browser
    to confirm that our backend server is running correctly.
    """
    return {"message": "Welcome to the AI Career Guidance API. The server is running."}

