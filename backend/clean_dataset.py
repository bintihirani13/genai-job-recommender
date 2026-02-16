import pandas as pd

df = pd.read_csv("jobs_data/job_title_des.csv")

# Remove unwanted column
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# Remove null values
df = df.dropna()

# Remove duplicate job descriptions
df = df.drop_duplicates(subset=["Job Title", "Job Description"])

# Save cleaned dataset
df.to_csv("jobs_data/cleaned_jobs.csv", index=False)

print("✅ Cleaned dataset saved as jobs_data/cleaned_jobs.csv")
print("Final Shape:", df.shape)
print("Columns:", df.columns)
