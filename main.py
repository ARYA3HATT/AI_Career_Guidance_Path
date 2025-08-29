import json
import re
import os

# --------------------------------------------------------------------------
# MODULE 1: CAREER DATABASE
# --------------------------------------------------------------------------
CAREER_PATHS = [
    {
        "name": "Software Engineer (Backend)",
        "description": "Builds and maintains the server-side logic of web applications.",
        "keywords": {
            "strengths": ["problem-solving", "logical thinking", "analytical", "coding", "debugging"],
            "interests": ["coding", "technology", "building things", "puzzles", "software"],
            "personality": ["analytical", "introverted", "detail-oriented", "patient"],
            "academic": ["computer science", "engineering", "mathematics", "software"],
            "industries": ["tech", "software development", "IT"]
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
            "personality": ["curious", "analytical", "patient", "methodical"],
            "academic": ["statistics", "computer science", "mathematics", "physics", "economics"],
            "industries": ["tech", "finance", "analytics"]
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
            "personality": ["creative", "empathetic", "collaborative", "visual"],
            "academic": ["design", "psychology", "human-computer interaction", "art"],
            "industries": ["tech", "design", "gaming", "advertising"]
        },
        "skills_to_acquire": ["Figma or Sketch", "User Research Methods", "Wireframing & Prototyping", "Color Theory & Typography"],
        "resources": ["Coursera: 'Google UX Design Professional Certificate'", "Nielsen Norman Group website"]
    },
    {
        "name": "IT Project Manager",
        "description": "Plans, executes, and closes technology projects.",
        "keywords": {
            "strengths": ["leadership", "organization", "communication", "planning", "problem-solving"],
            "interests": ["management", "technology", "business", "strategy"],
            "personality": ["organized", "outgoing", "decisive", "leader"],
            "academic": ["business", "management", "information systems", "computer science"],
            "industries": ["tech", "business", "finance", "IT"]
        },
        "skills_to_acquire": ["Agile & Scrum methodologies", "Project Management Software (Jira, Asana)", "Risk Management", "Budgeting"],
        "resources": ["Google Project Management Professional Certificate", "PMBOK Guide"]
    }
]

# --------------------------------------------------------------------------
# MODULE 2: USER INPUT
# --------------------------------------------------------------------------
def collect_user_data():
    print("\n--- 🚀 Personalized Career Guidance Engine ---\n")
    user_data = {
        'academic_background': input("📚 What is your field of study? > ").strip().lower(),
        'interests': [i.strip().lower() for i in input("🎨 Key interests/hobbies (comma-separated) > ").split(',')],
        'strengths': [s.strip().lower() for s in input("💪 Main strengths (comma-separated) > ").split(',')],
        'weaknesses': [w.strip().lower() for w in input("🌱 Weaknesses (comma-separated) > ").split(',')],
        'personality_traits': [p.strip().lower() for p in input("😊 Personality traits (comma-separated) > ").split(',')],
        'preferred_work_style': input("💼 Preferred work style (e.g., remote, team, independent) > ").strip().lower(),
        'preferred_industries': [i.strip().lower() for i in input("🏭 Preferred industries (comma-separated) > ").split(',')],
        'geographic_preference': input("🌍 Preferred work location > ").strip().lower(),
        'constraints': {
            'financial': input("💰 Financial constraints (if any) > ").strip().lower(),
            'time': input("⏳ Time commitment for skill development (e.g., 3 months, 6 months) > ").strip().lower()
        }
    }
    print("\nThank you! Analyzing your profile...\n")
    return user_data

# --------------------------------------------------------------------------
# MODULE 3: CAREER SCORING
# --------------------------------------------------------------------------
def calculate_match_score(user_data, career):
    score_details = {}
    total_score = 0

    # Strengths (weight 3)
    strengths_match = len(set(user_data['strengths']) & set(career['keywords']['strengths']))
    score_details['strengths'] = strengths_match * 3
    total_score += score_details['strengths']

    # Interests (weight 2)
    interests_match = len(set(user_data['interests']) & set(career['keywords']['interests']))
    score_details['interests'] = interests_match * 2
    total_score += score_details['interests']

    # Personality traits (weight 1)
    personality_match = len(set(user_data['personality_traits']) & set(career['keywords']['personality']))
    score_details['personality'] = personality_match * 1
    total_score += score_details['personality']

    # Academic background (weight 1)
    academic_match = sum(1 for keyword in career['keywords']['academic'] if keyword in user_data['academic_background'])
    score_details['academic'] = academic_match * 1
    total_score += score_details['academic']

    # Preferred industries (weight 1)
    industry_match = len(set(user_data['preferred_industries']) & set(career['keywords'].get('industries', [])))
    score_details['industries'] = industry_match * 1
    total_score += score_details['industries']

    return total_score, score_details

def analyze_user_data(user_data, top_n=5):
    scored_careers = []
    for career in CAREER_PATHS:
        score, details = calculate_match_score(user_data, career)
        if score > 0:
            scored_careers.append({"career": career, "score": score, "details": details})
    return sorted(scored_careers, key=lambda x: x['score'], reverse=True)[:top_n]

# --------------------------------------------------------------------------
# MODULE 4: TIMELINE & ROADMAP
# --------------------------------------------------------------------------
def generate_timeline(skills, time_commitment):
    try:
        months = int(re.findall(r'\d+', time_commitment)[0])
        total_weeks = months * 4
    except (IndexError, TypeError):
        total_weeks = 12
    if not skills: return ["- No specific skills listed."]
    weeks_per_skill = max(1, total_weeks // len(skills))
    timeline = []
    start_week = 1
    for i, skill in enumerate(skills):
        end_week = start_week + weeks_per_skill - 1
        if i == len(skills) - 1: end_week = total_weeks
        timeline.append(f"Weeks {start_week}-{end_week}: Focus on {skill}")
        start_week = end_week + 1
    return timeline

def generate_roadmap_data(recommendation, user_data):
    career = recommendation['career']
    timeline = generate_timeline(career.get('skills_to_acquire', []), user_data['constraints']['time'])
    return {
        "career_name": career['name'],
        "match_score": recommendation['score'],
        "score_breakdown": recommendation['details'],
        "description": career['description'],
        "fit_reason": f"Matches strengths: {', '.join(user_data['strengths'])}, interests: {', '.join(user_data['interests'])}, personality: {', '.join(user_data['personality_traits'])}.",
        "timeline_title": f"Your {user_data['constraints']['time']} Skill Development Plan",
        "timeline": timeline,
        "resources": career.get('resources', [])
    }

def display_roadmap(roadmap_data):
    print("\n" + "="*50)
    print(f"🚀 ROADMAP FOR: {roadmap_data['career_name']} (Score: {roadmap_data['match_score']})")
    print("="*50)
    print(f"\n🎯 Why it's a strong fit:\n   {roadmap_data['fit_reason']}")
    print("\n💡 Score Breakdown:")
    for key, val in roadmap_data['score_breakdown'].items():
        print(f"   {key.capitalize()}: {val}")
    print(f"\n🗓️ {roadmap_data['timeline_title']}:")
    for item in roadmap_data['timeline']:
        print(f"   - {item}")
    print("\n📚 Recommended Resources:")
    for res in roadmap_data['resources']:
        print(f"   - {res}")
    print("="*50)

def save_roadmaps_to_json(all_roadmaps):
    filename = "Career_Roadmaps.json"
    with open(filename, 'w') as f:
        json.dump(all_roadmaps, f, indent=4)
    print(f"\n✅ All roadmaps saved to '{os.path.abspath(filename)}'")

# --------------------------------------------------------------------------
# MODULE 5: MAIN INTERACTIVE MENU
# --------------------------------------------------------------------------
def main():
    user_data = collect_user_data()
    recommendations = analyze_user_data(user_data)

    if not recommendations:
        print("\n⚠️ No matching careers found.")
        return

    saved_roadmaps = []

    while True:
        print("\n--- Your Top Career Recommendations ---")
        for i, rec in enumerate(recommendations):
            print(f"  [{i+1}] {rec['career']['name']} (Score: {rec['score']})")
        print("\nEnter a number to view roadmap, 'save' to save all roadmaps, or 'quit' to exit.")

        choice = input("> ").strip().lower()
        if choice in ['quit', 'exit']:
            print("\nGoodbye! Best of luck on your career journey!")
            break
        elif choice == 'save':
            save_roadmaps_to_json(saved_roadmaps)
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(recommendations):
                    roadmap_data = generate_roadmap_data(recommendations[idx], user_data)
                    display_roadmap(roadmap_data)
                    saved_roadmaps.append(roadmap_data)
                else:
                    print("\n⚠️ Invalid number. Try again.")
            except ValueError:
                print("\n⚠️ Invalid input. Please enter a valid number or 'quit'.")

if __name__ == "__main__":
    main()
