import math
import pandas as pd
import json 




# Sample 
SAMPLE_JOB_ID = "upskalor tech"
SAMPLE_RULES = {
    "branches": ["CSE", "IT", "ECE"],
    "min_cgpa": 7.5,
    "allow_backlogs": False,
    "req_skills": ["Python", "SQL", "ML"], 
    "nice_skills": ["AI", "Cloud", "Git"],
    "passout_years": [2025],
    "projects_min": 2,
    "test_ts": "2024-10-15T10:00:00Z"
}

#  Data Loading and Preprocessing
def load_student_data(file_path="data/students.xlsx"):
    try:
        df = pd.read_excel(file_path) 
        df['skills'] = df['skills'].apply(
            lambda x: [s.strip() for s in str(x).split(',')] if pd.notna(x) else []
        )
        print(f"Loaded {len(df)} student records from {file_path}.")
        return df
    except FileNotFoundError:
        print(f"Error: Student data file not found at {file_path}")
        return pd.DataFrame()

STUDENT_DF = load_student_data()


# Eligibility 


def compute_eligibility(student, rules):
  
    reasons = []

  
    if student['branch'] not in rules.get("branches", []):
        reasons.append(f"Branch '{student['branch']}' not in allowed list.")

    
    min_cgpa = rules.get("min_cgpa", 0.0)
    if student['cgpa'] < min_cgpa:
        reasons.append(f"CGPA {student['cgpa']} is below minimum required ({min_cgpa}).")

    if not rules.get("allow_backlogs", True) and student['backlogs'] > 0:
        reasons.append("Backlogs not allowed.")

   
    allowed_years = rules.get("passout_years")
    if allowed_years and student['passout_year'] not in allowed_years:
        reasons.append(f"Passout year {student['passout_year']} not allowed.")

    
    req_skills = set(rules.get("req_skills", []))
    student_skills = set(student['skills'])
   
    required_skill_hits = len(req_skills.intersection(student_skills))
    
    
    if req_skills: # Only apply if required skills are specified
        k_min = max(1, math.ceil(0.6 * len(req_skills)))
        
        if required_skill_hits < k_min:
            reasons.append(f"Required skill hits ({required_skill_hits}) below threshold ({k_min}). Target: {len(req_skills)} required skills.")

  
    min_projects = rules.get("projects_min")
    if min_projects is not None and student['projects'] < min_projects:
        reasons.append(f"Project count ({student['projects']}) below minimum required ({min_projects}).")

  
    is_eligible = (len(reasons) == 0)
    return is_eligible, reasons



def run_shortlister(student_df, rules, job_id):
    
    results = []
    
    
    for index, student in student_df.iterrows():
        
        is_eligible, reasons = compute_eligibility(student, rules)
        
        
        nice_skills = set(rules.get("nice_skills", []))
        student_skills = set(student['skills'])
        nice_hits = len(nice_skills.intersection(student_skills))
        
        results.append({
            'job_id': job_id,
            'student_id': student['student_id'],
            'eligible': is_eligible,
            'reasons': json.dumps(reasons), 
            'nice_hits': nice_hits,
            'computed_at': pd.Timestamp.now()
        })
    
    eligibility_df = pd.DataFrame(results)
    
   
    eligible_count = eligibility_df['eligible'].sum()
    rejected_count = len(eligibility_df) - eligible_count
    
    print(f"\n--- Shortlist Results for {job_id} ---")
    print(f"Total Students Processed: {len(eligibility_df)}")
    print(f"Eligible Count: {eligible_count}")
    print(f"Rejected Count: {rejected_count}")
    
    return eligibility_df




if __name__ == "__main__":
    if STUDENT_DF.empty:
         print("Cannot run shortlister: Student data is empty.")
    else:
        
        rules_to_run = SAMPLE_RULES
        job_id_to_run = SAMPLE_JOB_ID
        
       
        eligibility_report = run_shortlister(STUDENT_DF, rules_to_run, job_id_to_run)
        
      
        print("\n--- Sample Eligibility Table Eligible Students---")
       
        eligible_sample = eligibility_report[eligibility_report['eligible'] == True]
        print(eligible_sample[['student_id', 'eligible', 'nice_hits']].head())

        print("\n--- Sample Eligibility Table Rejected Students ---")
       
        rejected = eligibility_report[eligibility_report['eligible'] == False].head(5)
        if not rejected.empty:
            print(rejected[['student_id', 'eligible', 'reasons']])
        else:
            print("No students were rejected in this sample.")