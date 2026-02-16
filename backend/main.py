from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util

# ------------------ LOAD ENV ------------------

load_dotenv()
RAPID_KEY = os.getenv("RAPID_API_KEY")

# ------------------ APP INIT ------------------

app = FastAPI()

# Enable CORS (frontend connect karne ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# ------------------ HOME ROUTE ------------------

@app.get("/")
def home():
    return {"message": "GenAI Job Recommender Running 🚀"}

# ------------------ PDF TEXT EXTRACTION ------------------

def extract_text_from_pdf(file_bytes):
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text

# ------------------ AI MATCH SCORE ------------------

def calculate_match_score(resume_text, job_text):
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_text, convert_to_tensor=True)
    score = util.cos_sim(resume_embedding, job_embedding)
    return round(float(score[0][0]) * 100, 2)

# ------------------ SKILL EXTRACTION ------------------

def extract_skills(resume_text):
    skill_list = [
        "python", "machine learning", "data science", "deep learning",
        "sql", "java", "react", "node", "aws", "azure",
        "docker", "tensorflow", "pytorch", "nlp",
        "computer vision", "power bi", "excel", "c++"
    ]

    found_skills = []
    lower_text = resume_text.lower()

    for skill in skill_list:
        if skill in lower_text:
            found_skills.append(skill)

    return found_skills

# ------------------ MAIN API ------------------

@app.post("/recommend-from-resume")
async def recommend_from_resume(file: UploadFile = File(...)):

    try:
        contents = await file.read()
        resume_text = extract_text_from_pdf(contents)

        if not resume_text.strip():
            return {"results": []}

        # 🔥 Extract skills
        skills = extract_skills(resume_text)

        # If no skills found
        if not skills:
            skills = ["software engineer"]

        # Create clean search query
        search_query = " ".join(skills[:5])

        print("Search Query:", search_query)

        # RapidAPI endpoint
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

        print("API Response:", data)

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
                "skills_detected": skills
            })

        return {"results": results}

    except Exception as e:
        print("Error:", e)
        return {"results": []}
