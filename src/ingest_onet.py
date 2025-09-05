import pandas as pd
import os
import json

# --- Configuration ---
# Define the paths to our data and where the results should go.
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'onet_data')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
OUTPUT_JSON_FILE = os.path.join(RESULTS_DIR, 'onet_processed.json')

# A dictionary to map the cryptic filenames to friendly names
ONET_FILES = {
    'occupations': 'Occupation Data.txt',
    'tasks': 'Task Statements.txt',
    'skills': 'Skills.txt',
    'knowledge': 'Knowledge.txt',
    'work_activities': 'Work Activities.txt'
}

def main():
    """
    This is our main data processing function. It reads the raw O*NET text files,
    combines them, and saves a clean JSON file ready for our AI.
    """
    print("--- Starting O*NET Data Ingestion Process ---")

    # Ensure the results directory exists
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # --- 1. Load the raw data files into Pandas DataFrames ---
    print("Step 1: Loading raw data files...")
    try:
        dataframes = {}
        for key, filename in ONET_FILES.items():
            path = os.path.join(DATA_DIR, filename)
            # O*NET files are tab-separated
            dataframes[key] = pd.read_csv(path, sep='\t', on_bad_lines='warn')
            print(f"  - Loaded {filename}")
    except FileNotFoundError as e:
        print(f"\n[ERROR] A required file was not found: {e.filename}")
        print("Please ensure all O*NET .txt files are in the 'data/onet_data' folder.")
        return

    # --- 2. Process and combine the data ---
    print("\nStep 2: Processing and combining data for each occupation...")
    
    # We'll use the main 'occupations' dataframe as our base
    processed_careers = []
    
    # Let's iterate through each occupation in the main list
    for index, occupation in dataframes['occupations'].iterrows():
        onet_soc_code = occupation['O*NET-SOC Code']
        
        career_profile = {
            'onet_soc_code': onet_soc_code,
            'title': occupation['Title'],
            'description': occupation['Description'],
            'tasks': [],
            'skills': [],
            'knowledge': [],
            'work_activities': []
        }
        
        # Find all tasks for this occupation and add them to the profile
        tasks_for_occupation = dataframes['tasks'][dataframes['tasks']['O*NET-SOC Code'] == onet_soc_code]
        career_profile['tasks'] = tasks_for_occupation['Task'].tolist()
        
        # Find all skills for this occupation
        skills_for_occupation = dataframes['skills'][dataframes['skills']['O*NET-SOC Code'] == onet_soc_code]
        career_profile['skills'] = skills_for_occupation['Element Name'].tolist()
        
        # Find all knowledge areas for this occupation
        knowledge_for_occupation = dataframes['knowledge'][dataframes['knowledge']['O*NET-SOC Code'] == onet_soc_code]
        career_profile['knowledge'] = knowledge_for_occupation['Element Name'].tolist()
        
        # Find all work activities for this occupation
        activities_for_occupation = dataframes['work_activities'][dataframes['work_activities']['O*NET-SOC Code'] == onet_soc_code]
        career_profile['work_activities'] = activities_for_occupation['Element Name'].tolist()

        processed_careers.append(career_profile)

    print(f"  - Successfully processed {len(processed_careers)} occupations.")

    # --- 3. Save the final, clean data to a JSON file ---
    print(f"\nStep 3: Saving the processed data to {OUTPUT_JSON_FILE}...")
    with open(OUTPUT_JSON_FILE, 'w') as f:
        json.dump(processed_careers, f, indent=2)
        
    print("\n--- ✅ O*NET Data Ingestion Complete ---")
    print("Your new, powerful career database is ready!")

if __name__ == "__main__":
    main()
