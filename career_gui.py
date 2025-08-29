import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from tkinter.scrolledtext import ScrolledText
import json
import re
import os
from difflib import get_close_matches

# --------------------------------------------------------------------------
# MODULE 1: DATABASE
# --------------------------------------------------------------------------
CAREER_PATHS = [
    {
        "name": "Software Engineer (Backend)",
        "description": "Builds and maintains the server-side logic of web applications.",
        "keywords": {
            "strengths": ["problem-solving", "logical thinking", "analytical", "coding", "debugging"],
            "interests": ["coding", "technology", "building things", "puzzles", "software"],
            "academic": ["computer science", "engineering", "mathematics", "software"]
        },
        "skills_to_acquire": ["Proficiency in a backend language (Python, Java, Go)", "Database Management (SQL, NoSQL)", "API Design", "Cloud Computing (AWS, Azure)"],
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
        "skills_to_acquire": ["Figma or Sketch", "User Research Methods", "Wireframing & Prototyping", "Understanding of Color Theory and Typography"],
        "resources": ["Coursera: 'Google UX Design Professional Certificate'", "Nielsen Norman Group website for articles"]
    }
]

# --------------------------------------------------------------------------
# MODULE 2: CORE LOGIC
# --------------------------------------------------------------------------
def fuzzy_match(word, keyword_list, weight):
    """Returns weighted score if word is a close match to items in keyword_list."""
    matches = get_close_matches(word, keyword_list, n=1, cutoff=0.7)
    return weight if matches else 0

def analyze_user_data(user_data):
    """Analyzes user data and returns scored career recommendations."""
    scored_careers = []
    for career in CAREER_PATHS:
        score = 0
        # Strengths (weight: 3)
        for s in user_data.get('strengths', []):
            score += fuzzy_match(s, career['keywords']['strengths'], 3)

        # Interests (weight: 2)
        for i in user_data.get('interests', []):
            score += fuzzy_match(i, career['keywords']['interests'], 2)

        # Academic (weight: 1)
        for keyword in career['keywords']['academic']:
            if keyword in user_data.get('academic_background', '').lower():
                score += 1

        if score > 0:
            scored_careers.append({"career": career, "score": score})

    return sorted(scored_careers, key=lambda x: x['score'], reverse=True)

def generate_roadmap_data(recommendation, user_data):
    """Generates a structured roadmap for the selected career."""
    career = recommendation['career']
    time_commitment = user_data.get('time_commitment', '3 months')
    skills = career.get('skills_to_acquire', [])

    try:
        months = int(re.findall(r'\d+', time_commitment)[0])
        total_weeks = months * 4
    except (IndexError, TypeError):
        total_weeks = 12

    weeks_per_skill = max(1, total_weeks // len(skills)) if skills else 0
    timeline = []
    start_week = 1
    for i, skill in enumerate(skills):
        end_week = start_week + weeks_per_skill - 1
        if i == len(skills) - 1:
            end_week = total_weeks
        timeline.append(f"Weeks {start_week}-{end_week}: Focus on {skill}")
        start_week = end_week + 1

    return {
        "career_name": career['name'],
        "match_score": recommendation['score'],
        "fit_reason": f"This path aligns with your strengths in {', '.join(user_data.get('strengths', []))} "
                      f"and interests in {', '.join(user_data.get('interests', []))}.",
        "timeline_title": f"Your {time_commitment} Skill Development Plan",
        "timeline": timeline,
        "resources": career.get('resources', [])
    }

# --------------------------------------------------------------------------
# MODULE 3: GUI APPLICATION
# --------------------------------------------------------------------------
class CareerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personalized Career Guidance Engine")
        self.geometry("650x700")
        self.recommendations = []
        self.user_data = {}
        self.create_widgets()
        self.load_user_data()

    def create_widgets(self):
        style = ttk.Style(self)
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12, "bold"))
        style.configure("TEntry", font=("Helvetica", 12))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))

        # --- Input Frame ---
        input_frame = ttk.Frame(self, padding="20")
        input_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(input_frame, text="Your Profile", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)

        # Field of Study
        ttk.Label(input_frame, text="📚 Field of Study:").grid(row=1, column=0, sticky="w", pady=5)
        self.study_entry = ttk.Entry(input_frame, width=40)
        self.study_entry.grid(row=1, column=1, sticky="ew")

        # Interests
        ttk.Label(input_frame, text="🎨 Interests (comma-separated):").grid(row=2, column=0, sticky="w", pady=5)
        self.interests_entry = ttk.Entry(input_frame, width=40)
        self.interests_entry.grid(row=2, column=1, sticky="ew")

        # Strengths
        ttk.Label(input_frame, text="💪 Strengths (comma-separated):").grid(row=3, column=0, sticky="w", pady=5)
        self.strengths_entry = ttk.Entry(input_frame, width=40)
        self.strengths_entry.grid(row=3, column=1, sticky="ew")

        # Time Commitment
        ttk.Label(input_frame, text="⏳ Time Commitment:").grid(row=4, column=0, sticky="w", pady=5)
        self.time_entry = ttk.Entry(input_frame, width=40)
        self.time_entry.grid(row=4, column=1, sticky="ew")
        self.time_entry.insert(0, "e.g., 6 months")

        # Generate Button
        generate_button = ttk.Button(input_frame, text="Generate Recommendations", command=self.generate_recommendations)
        generate_button.grid(row=5, column=0, columnspan=2, pady=20)

        # --- Results Frame ---
        results_frame = ttk.Frame(self, padding="20")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(results_frame, text="Top Career Matches", style="Header.TLabel").pack(pady=10)

        self.results_listbox = tk.Listbox(results_frame, font=("Helvetica", 12), height=10)
        self.results_listbox.pack(fill="both", expand=True)
        self.results_listbox.bind("<<ListboxSelect>>", self.show_roadmap)

    def generate_recommendations(self):
        academic = self.study_entry.get()
        interests = self.interests_entry.get()
        strengths = self.strengths_entry.get()
        time = self.time_entry.get()

        if not all([academic, interests, strengths, time]):
            messagebox.showerror("Error", "Please fill out all fields.")
            return

        self.user_data = {
            'academic_background': academic,
            'interests': [i.strip().lower() for i in interests.split(',')],
            'strengths': [s.strip().lower() for s in strengths.split(',')],
            'time_commitment': time
        }

        # Save for persistence
        with open("last_user.json", "w") as f:
            json.dump(self.user_data, f, indent=4)

        self.recommendations = analyze_user_data(self.user_data)

        self.results_listbox.delete(0, tk.END)
        if not self.recommendations:
            self.results_listbox.insert(tk.END, "No strong matches found.")
        else:
            for rec in self.recommendations:
                self.results_listbox.insert(tk.END, f"{rec['career']['name']} (Score: {rec['score']})")

    def show_roadmap(self, event):
        selected_indices = self.results_listbox.curselection()
        if not selected_indices:
            return
        selected_index = selected_indices[0]
        selected_recommendation = self.recommendations[selected_index]
        roadmap_data = generate_roadmap_data(selected_recommendation, self.user_data)
        RoadmapWindow(self, roadmap_data)

    def load_user_data(self):
        if os.path.exists("last_user.json"):
            try:
                with open("last_user.json", "r") as f:
                    self.user_data = json.load(f)
                self.study_entry.insert(0, self.user_data.get("academic_background", ""))
                self.interests_entry.insert(0, ", ".join(self.user_data.get("interests", [])))
                self.strengths_entry.insert(0, ", ".join(self.user_data.get("strengths", [])))
                self.time_entry.delete(0, tk.END)
                self.time_entry.insert(0, self.user_data.get("time_commitment", ""))
            except:
                pass

class RoadmapWindow(Toplevel):
    def __init__(self, parent, roadmap_data):
        super().__init__(parent)
        self.roadmap_data = roadmap_data
        self.title(f"Roadmap for {roadmap_data['career_name']}")
        self.geometry("700x500")

        text_area = ScrolledText(self, wrap="word", font=("Helvetica", 12), padx=15, pady=15)
        text_area.pack(fill="both", expand=True)

        text_area.insert(tk.END, f"🚀 ROADMAP FOR: {roadmap_data['career_name']}\n", "header")
        text_area.insert(tk.END, f"(Match Score: {roadmap_data['match_score']})\n\n", "subheader")
        text_area.insert(tk.END, "🎯 Why it's a strong fit:\n", "bold")
        text_area.insert(tk.END, f"   {roadmap_data['fit_reason']}\n\n")
        text_area.insert(tk.END, f"🗓️ {roadmap_data['timeline_title']}:\n", "bold")
        for item in roadmap_data['timeline']:
            text_area.insert(tk.END, f"   - {item}\n")
        text_area.insert(tk.END, "\n📚 Recommended Resources:\n", "bold")
        for resource in roadmap_data['resources']:
            text_area.insert(tk.END, f"   - {resource}\n")

        text_area.tag_configure("header", font=("Helvetica", 16, "bold"))
        text_area.tag_configure("subheader", font=("Helvetica", 12, "italic"))
        text_area.tag_configure("bold", font=("Helvetica", 12, "bold"))
        text_area.config(state="disabled")

        save_button = ttk.Button(self, text="Save Roadmap to JSON", command=self.save_roadmap)
        save_button.pack(pady=10)

    def save_roadmap(self):
        safe_name = re.sub(r'[^A-Za-z0-9_]+', '_', self.roadmap_data['career_name'])
        filename = f"Roadmap_{safe_name}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.roadmap_data, f, indent=4)
            messagebox.showinfo("Success", f"Roadmap saved to {os.path.abspath(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

if __name__ == "__main__":
    app = CareerApp()
    app.mainloop()
