

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, array, lit, col, split, get_json_object 
from pyspark.sql.types import BooleanType, ArrayType, StringType
import json
import math

# Sample 
SAMPLE_JOB_ID = "upskalor"
SAMPLE_RULES = {
    "branches": ["CSE", "IT", "ECE"],
    "min_cgpa": 7.5,
    "allow_backlogs": False,
    "req_skills": ["Python", "SQL", "Spark"],
    "nice_skills": ["ML", "Cloud"],
    "passout_years": [2025],
    "projects_min": 2,
    "test_ts": "2024-10-15T10:00:00Z"
}



# Start Spark Session
spark = SparkSession.builder.appName("PlacementAgentShortlister").getOrCreate()



def compute_eligibility_spark(
    branch, cgpa, backlogs, passout_year, skills_list, projects, rules_json_str
):

    rules = json.loads(rules_json_str)
    reasons = []

    if branch not in rules.get("branches", []):
        reasons.append(f"Branch '{branch}' not in allowed list.")

  
    if cgpa < rules.get("min_cgpa", 0.0):
        reasons.append(f"CGPA {cgpa} is below minimum required.")

  
    if not rules.get("allow_backlogs", True) and backlogs > 0:
        reasons.append("Backlogs not allowed.")


    allowed_years = rules.get("passout_years")
    if allowed_years and passout_year not in allowed_years:
        reasons.append(f"Passout year {passout_year} not allowed.")

    
    req_skills = set(rules.get("req_skills", []))
    student_skills = set(skills_list if skills_list else [])
    required_skill_hits = len(req_skills.intersection(student_skills))

    if req_skills:
        k_min = max(1, math.ceil(0.6 * len(req_skills)))
        if required_skill_hits < k_min:
            reasons.append(f"Required skill hits ({required_skill_hits}) below threshold ({k_min}).")

    min_projects = rules.get("projects_min")
    if min_projects is not None and projects < min_projects:
        reasons.append(f"Project count ({projects}) below minimum required ({min_projects}).")

    is_eligible = (len(reasons) == 0)
    
   
    return json.dumps({"eligible": is_eligible, "reasons": reasons})

eligibility_udf = udf(compute_eligibility_spark, StringType())








def run_spark_shortlister(rules, job_id, student_excel_path):
    
    student_df = spark.read.format("com.crealytics.spark.excel") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(student_excel_path) \
        .withColumn(
            # comma-separated string into an array
            # Ensure your skills column is named 'skills' in the Excel file.
            "skills_array", 
            split(col("skills"), ", ")
        )
    
    
 
    rules_json_str = json.dumps(rules)
    
   
    shortlist_df = student_df.withColumn(
        "eligibility_data",
        eligibility_udf(
            col("branch"), 
            col("cgpa"), 
            col("backlogs"), 
            col("passout_year"), 
            col("skills_array"), 
            col("projects"), 
            lit(rules_json_str) 
        )
    )
    
   
 
    final_df = shortlist_df.withColumn(
        "eligible", 
        get_json_object(col("eligibility_data"), "$.eligible").cast(BooleanType())
    ).withColumn(
        "reasons", 
        get_json_object(col("eligibility_data"), "$.reasons")
    ).select(
        lit(job_id).alias("job_id"), 
        "student_id", 
        "eligible", 
        "reasons"
    )
    
 
    eligible_count = final_df.filter(col("eligible") == True).count()
    rejected_count = final_df.filter(col("eligible") == False).count()
    total_count = final_df.count()
    
    print(f"Spark Results: Total={total_count}, Eligible={eligible_count}, Rejected={rejected_count}")
    
    # Export the shortlist CSV/JSON
    final_df.write.mode("overwrite").csv("/output/shortlist_J001.csv", header=True)
    
    return final_df


if __name__ == "__main__":
   
   
    MOCK_LARGE_EXCEL = "data/students.xlsx" 
    print(f"Starting PySpark Shortlister for Job ID: {SAMPLE_JOB_ID}")

    try:
       
        spark_report = run_spark_shortlister(SAMPLE_RULES, SAMPLE_JOB_ID, MOCK_LARGE_EXCEL)
        
       
        print("\n--- Sample Eligibility Report Top 20 ---")
        spark_report.limit(20).show(truncate=False)
        
      
        
    except Exception as e:
        print(f"An error occurred during Spark execution: {e}")

    finally:
        spark.stop()