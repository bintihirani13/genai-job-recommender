from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF

from sklearn.metrics.pairwise import cosine_similarity

# ------------------ LOAD ENV ------------------

load_dotenv()
RAPID_KEY = os.getenv("RAPID_API_KEY")

# ------------------ LAZY MODEL LOAD ------------------

model = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("paraphrase-MiniLM-L3-v2")  # 🔥 light model
    return model

# ------------------ APP ------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ HOME ------------------

@app.get("/")
def home():
    return {"message": "GenAI Job Recommender Running 🚀"}

# ------------------ PDF TEXT ------------------

def extract_text_from_pdf(file_bytes):
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text.lower()

# ------------------ SKILLS ------------------

IMPORTANT_SKILLS = {
    "python", "machine learning", "data science", "deep learning",
    "nlp", "tensorflow", "pytorch", "sql", "data"
}

def extract_skills(text):
    found = []
    text = text.lower()
    for skill in IMPORTANT_SKILLS:
        if skill in text:
            found.append(skill)
    return found

# ------------------ MATCH SCORE ------------------

def calculate_match_score(resume_text, job_text):
    try:
        model = get_model()

        resume_text = resume_text.lower()
        job_text = job_text.lower()

        # ✅ Skills
        resume_skills = set(extract_skills(resume_text))
        job_skills = set(extract_skills(job_text))

        overlap = len(resume_skills & job_skills)

        skill_score = (overlap / len(resume_skills)) * 100 if resume_skills else 0

        # ✅ Semantic (short text only)
        short_resume = " ".join(resume_skills)
        short_job = " ".join(job_skills)

        if short_resume and short_job:
            resume_embedding = model.encode([short_resume])
            job_embedding = model.encode([short_job])

            semantic_sim = cosine_similarity(resume_embedding, job_embedding)[0][0]
            semantic_score = semantic_sim * 100
        else:
            semantic_score = 0

        # ✅ Final score
        final_score = (0.7 * semantic_score) + (0.3 * skill_score)

        final_score = min(final_score + 5, 92)

        return round(final_score, 2)

    except:
        return 0.0

# ------------------ RESUME API ------------------

@app.post("/recommend-from-resume")
async def recommend_from_resume(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        resume_text = extract_text_from_pdf(contents)

        if not resume_text.strip():
            return {"results": []}

        skills = extract_skills(resume_text)

        if not skills:
            skills = ["software engineer"]

        search_query = " ".join(skills[:5])

        url = "https://jsearch.p.rapidapi.com/search"

        querystring = {
            "query": search_query,
            "page": "1",
            "num_pages": "1",
            "country": "in"
        }

        headers = {
            "X-RapidAPI-Key": RAPID_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        results = []

        for job in data.get("data", [])[:5]:

            title = job.get("job_title")
            company = job.get("employer_name")
            location = job.get("job_city")
            apply_link = job.get("job_apply_link")
            description = job.get("job_description") or ""

            job_text = (title or "") + " " + description

            match_score = calculate_match_score(resume_text, job_text)

            results.append({
                "title": title,
                "company": company,
                "location": location,
                "apply_link": apply_link,
                "match_score": match_score,
                "skills_detected": skills,
                "reason": f"Matched {len(set(skills) & set(extract_skills(job_text)))} skills"
            })

        return {"results": results}

    except Exception as e:
        print("Error:", e)
        return {"results": []}