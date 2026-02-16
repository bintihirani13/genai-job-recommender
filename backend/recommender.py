import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load ChromaDB (persistent database)
client = chromadb.PersistentClient(path="vector_db")

# Load collection
collection = client.get_collection(name="jobs_collection")


def recommend_jobs(user_query, top_k=5):
    # Convert user query into embedding
    query_embedding = model.encode(user_query).tolist()

    # Search in vector database
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    recommended_jobs = []

    for i in range(len(results["documents"][0])):
        metadata = results["metadatas"][0][i]
        job_description = results["documents"][0][i]
        distance = results["distances"][0][i]

        similarity = round(1 - distance, 3)

        recommended_jobs.append({
            "job_title": metadata.get("job_title", "N/A"),
            "company": metadata.get("company", "N/A"),
            "location": metadata.get("location", "N/A"),
            "experience": metadata.get("experience", "Not specified"),
            "apply_link": metadata.get("apply_link", "#"),
            "similarity": similarity,
            "full_description": job_description
        })

    return recommended_jobs


if __name__ == "__main__":
    print("\n==============================")
    print("  GenAI Job Recommendation System")
    print("==============================\n")

    query = input("👉 Enter your job preference (skills/role): ")

    jobs = recommend_jobs(query, top_k=5)

    print("\n🔥 Top Recommended Jobs:\n")

    for idx, job in enumerate(jobs, 1):
        print(f"{idx}. {job['job_title']} ({job['company']})")
        print(f"   Location: {job['location']}")
        print(f"   Experience: {job['experience']}")
        print(f"   Similarity: {job['similarity']}")
        print(f"   {job['full_description'][:200]}...\n")
