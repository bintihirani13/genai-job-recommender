# recommender.py

from sentence_transformers import SentenceTransformer
import numpy as np

# ------------------ LAZY LOAD MODEL ------------------

model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer("paraphrase-MiniLM-L3-v2")  # 🔥 light model
    return model

# ------------------ QUERY ENHANCEMENT ------------------

def enhance_query(query):
    synonyms = {
        "web dev": "frontend backend full stack web development react node",
        "ai": "machine learning deep learning nlp artificial intelligence",
        "data": "data science python sql analytics"
    }

    query = query.lower()

    for key, value in synonyms.items():
        if key in query:
            query += " " + value

    return query

# ------------------ MAIN RECOMMENDER ------------------

def recommend_jobs(user_query, jobs_data, top_k=3):

    model = get_model()

    enhanced_query = enhance_query(user_query)

    query_embedding = model.encode(enhanced_query)

    scores = []

    for job in jobs_data:
        job_text = (job.get("title", "") + " " + job.get("description", "")).lower()

        job_embedding = model.encode(job_text)

        # cosine similarity
        similarity = np.dot(query_embedding, job_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(job_embedding)
        )

        score = round(float(similarity) * 100, 2)

        # 🔥 small boost
        if score > 50:
            score += 10
        elif score > 30:
            score += 5

        score = min(score, 95)

        scores.append((score, job))

    # sort by score
    scores.sort(key=lambda x: x[0], reverse=True)

    results = []

    for score, job in scores[:top_k]:
        results.append({
            "job_title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "apply_link": job.get("apply_link"),
            "similarity": score,
            "reason": f"Semantic match score {score}%"
        })

    return results