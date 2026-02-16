import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import os

DATA_PATH = "jobs_data/enhanced_jobs.csv"

print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

model = SentenceTransformer("all-MiniLM-L6-v2")

# Create ChromaDB persistent client
os.makedirs("vector_db", exist_ok=True)
client = chromadb.PersistentClient(path="vector_db")

# Delete old collection if exists
try:
    client.delete_collection(name="jobs_collection")
except:
    pass

collection = client.get_or_create_collection(name="jobs_collection")

print("Generating embeddings and storing into ChromaDB...")

for idx, row in df.iterrows():
    job_title = str(row["job_title"])
    job_desc = str(row["description"])
    company = str(row["company"])
    location = str(row["location"])
    experience = str(row["experience"])
    apply_link = str(row["apply_link"])

    text = job_title + " " + job_desc
    embedding = model.encode(text).tolist()

    collection.add(
        ids=[str(idx)],
        embeddings=[embedding],
        documents=[job_desc],
        metadatas=[{
            "job_title": job_title,
            "company": company,
            "location": location,
            "experience": experience,
            "apply_link": apply_link
        }]
    )

print("✅ Vector DB rebuilt successfully with enhanced metadata!")
