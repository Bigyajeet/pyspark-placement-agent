
#  PySpark Placement Agent Shortlister

This AI agent is an instantaneous screening tool designed specifically to help Training and Placement Officers (TPOs) manage high-volume campus recruitment. It uses algorithmic matching to process candidate profiles against job requirements for skills, experience, and academic criteria. The agent can select or reject candidates within seconds based on predefined rules, streamlining the initial filtering process and allowing TPOs to focus only on highly relevant candidates.

## 🎯 Project Goal

The primary objective is to demonstrate **distributed data processing** of a large Excel file. It performs multiple eligibility checks (CGPA, backlogs, skills matching, passout year, etc.) using PySpark **User Defined Functions (UDFs)** for fast and scalable shortlisting.

## 💡 Benefits for Placement Officers (TPOs)

  * **Speed:** The application can quickly process thousands of student records simultaneously, drastically cutting down shortlisting time from hours to minutes.
  * **Accuracy:** It ensures every student is evaluated fairly against precise, code-enforced rules, eliminating manual screening errors.
  * **Customization:** TPOs can easily update job requirements for different companies without rewriting complex manual spreadsheets or logic.
  * **Auditability:** The process generates a clean, structured output file that provides clear, documented reasons for every student's eligibility status.

##  Features

  * **Scalable Excel Processing:** Uses the `spark-excel` connector to efficiently read `.xlsx` files, enabling handling of millions of records.
  * **Configurable Rules:** Eligibility criteria are easily defined and modified in the `SAMPLE_RULES` dictionary within `pyengine.py`.
  * **Distributed Logic:** Eligibility checks are executed across the Spark cluster using PySpark UDFs for high performance.
  * **Detailed Output:** Generates a final CSV report including student ID, eligibility status, and specific rejection reasons.

## 🛠️ Prerequisites

To run this project, you must have the following installed and configured on your system:

1.  **Java Development Kit (JDK):** Version 8 or higher (required by Spark).
2.  **Apache Spark:** Version 3.x or 4.x.
      * **Environment Variables:** Ensure `SPARK_HOME` is set to your Spark installation directory.
3.  **Python:** Version 3.x.
      * **Libraries:** Install PySpark, which is the only library strictly required in the virtual environment.

<!-- end list -->

```bash
# Set your preferred Python environment (e.g., a virtual environment)
# Then install PySpark
pip install pyspark
```

##  Getting Started

Follow these steps to set up and run the shortlisting process on your system.

### 1\. Project Structure

Ensure your project directory matches this structure:

```
placement_agent/
├── data/
│   └── students.xlsx  # <--- REQUIRED: Your input data file
├── pyengine.py        # <--- The main PySpark script
└── README.md
```

### 2\. Configure Input Data

Place your student data in **`data/students.xlsx`**. The Excel file **must** contain the following columns for the script to execute correctly:

| Column Name | Data Type | Example Value |
| :--- | :--- | :--- |
| `student_id` | String/Int | 1001 |
| `branch` | String | CSE |
| `cgpa` | Numeric | 8.2 |
| `backlogs` | Integer | 0 |
| `passout_year` | Integer | 2025 |
| `skills` | **Comma-Separated String** | Python, SQL, Spark |
| `projects` | Integer | 3 |

### 3\. Execution Commands

Use the `spark-submit` tool to run the application, ensuring you pass the necessary external package for Excel support.

#### A. Set Python Environment (Windows/Troubleshooting)

This command ensures Spark uses your local Python executable. You must run this command **before** `spark-submit` in the same terminal session.

**For Windows/Command Prompt:**

```bash
set PYSPARK_PYTHON=python
```

**For macOS/Linux (Bash/Zsh):**

```bash
export PYSPARK_PYTHON=python
```

#### B. Run the PySpark Job

This command tells Spark to download and link the `spark-excel` connector while executing your script.

```bash
spark-submit \
  --packages com.crealytics:spark-excel_2.12:0.13.5 \
  pyengine.py
```

### 4\. Viewing Results

Upon successful execution, the script will print a summary of the shortlisting to the console. The final output is saved to the following directory:

`D:/upsakalor/placement_agent/output/upskalor_shortlist/`

This directory will contain multiple `.csv` part files (standard Spark output) that collectively form your final shortlist report.

## ⚙️ Configuration (`pyengine.py`)

You can modify the job requirements by editing the `SAMPLE_RULES` dictionary near the top of **`pyengine.py`**:

```python
SAMPLE_RULES = {
    "branches": ["CSE", "IT", "ECE"],
    "min_cgpa": 7.5,
    "allow_backlogs": False,
    "req_skills": ["python", "sql", "spark"], # REQUIRED skills (60% hit rate)
    "nice_skills": ["ml", "cloud"],          # Bonus skills (for ranking/nice_hits)
    "passout_years": [2025],
    "projects_min": 2,
    # ... other rules ...
}
```
