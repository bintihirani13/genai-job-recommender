import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

client = chromadb.PersistentClient(path="vector_db")
collection = client.get_collection(name="jobs_collection")


# 🔥 Important skills (weighted)
IMPORTANT_SKILLS = {
    "python", "machine", "learning", "deep", "nlp",
    "tensorflow", "pytorch", "sql", "data", "ai"
}


def enhance_query(query):
    query = query.lower()
    if "ai" in query:
        query += " machine learning deep learning nlp python tensorflow pytorch"
    return query


def clean_text(text):
    return text.lower().strip()


def recommend_jobs(user_query, top_k=3):
    enhanced_query = enhance_query(user_query)
    enhanced_query = clean_text(enhanced_query)

    query_embedding = model.encode([enhanced_query])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k,
        include=["documents", "metadatas", "embeddings"]
    )

    recommended_jobs = []

    for i in range(len(results["documents"][0])):

        job_description = results["documents"][0][i]
        metadata = results["metadatas"][0][i]
        job_embedding = np.array(results["embeddings"][0][i]).reshape(1, -1)

        # ✅ 1. Semantic score
        semantic_sim = cosine_similarity(query_embedding, job_embedding)[0][0]
        semantic_score = semantic_sim * 100

        # ✅ 2. Smart skill score (weighted 🔥)
        user_words = set(enhanced_query.split())
        job_words = set(clean_text(job_description).split())

        overlap = user_words & job_words

        score = 0
        for word in overlap:
            if word in IMPORTANT_SKILLS:
                score += 2   # important words double weight
            else:
                score += 1

        if len(user_words) == 0:
            skill_score = 0
        else:
            skill_score = (score / len(user_words)) * 100

        # ✅ 3. Final score (balanced)
        final_score = (0.85 * semantic_score) + (0.15 * skill_score)

        # small boost
        final_score = min(final_score + 10, 95)

        final_score = round(final_score, 2)

        recommended_jobs.append({
            "job_title": metadata.get("job_title", "N/A"),
            "company": metadata.get("company", "N/A"),
            "location": metadata.get("location", "N/A"),
            "experience": metadata.get("experience", "Not specified"),
            "apply_link": metadata.get("apply_link", "#"),
            "similarity": final_score,
            "reason": f"Matched {len(overlap)} keywords (weighted scoring)",
            "full_description": job_description
        })

    return recommended_jobs