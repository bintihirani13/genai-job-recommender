import pandas as pd
import random

# Load original dataset
df = pd.read_csv("jobs_data/cleaned_jobs.csv")

# Fake companies & locations
companies = ["Google", "Microsoft", "Amazon", "Infosys", "TCS", "Wipro", "Accenture"]
locations = ["Bangalore", "Hyderabad", "Mumbai", "Delhi", "Pune", "Chennai"]
experience_levels = ["0-2 years", "2-4 years", "3-5 years", "5+ years"]

df["company"] = [random.choice(companies) for _ in range(len(df))]
df["location"] = [random.choice(locations) for _ in range(len(df))]
df["experience"] = [random.choice(experience_levels) for _ in range(len(df))]
df["apply_link"] = "https://www.linkedin.com/jobs/"

# Rename columns properly
df = df.rename(columns={
    "Job Title": "job_title",
    "Job Description": "description"
})

df.to_csv("jobs_data/enhanced_jobs.csv", index=False)

print("✅ Enhanced dataset created!")
