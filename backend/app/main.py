import os
import json
import shutil
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from io import BytesIO
from .models import ProfessionalProfile, AutofillRequest, FormField

load_dotenv()

app = FastAPI(title="JobFill Agent Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Paths for Multi-User Storage
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data/users")
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_dir(user_id: str) -> str:
    path = os.path.join(DATA_DIR, user_id)
    os.makedirs(path, exist_ok=True)
    return path

def get_user_profile(user_id: str) -> Optional[ProfessionalProfile]:
    profile_path = os.path.join(get_user_dir(user_id), "profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r") as f:
                return ProfessionalProfile(**json.load(f))
        except Exception as e:
            print(f"Profile error for {user_id}: {e}")
            return None
    return None

@app.get("/health")
def health():
    return {"status": "ready"}

def run_ai_task(prompt: str, response_format: Dict = {"type": "json_object"}):
    # Stabilized models as of late 2025 / early 2026
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    last_err = None
    
    for model in models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional software engineer. Provide direct, factual answers. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format=response_format
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(f"Model {model} failed: {e}")
            last_err = e
            continue
    raise HTTPException(status_code=500, detail=f"AI failure: {str(last_err)}")

@app.post("/onboard/parse-cv")
async def parse_cv(file: UploadFile = File(...), x_user_id: str = Header(...)):
    try:
        content = await file.read()
        pdf = PdfReader(BytesIO(content))
        text = "".join([p.extract_text() for p in pdf.pages])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF Error: {str(e)}")

    prompt = f"""
    EXTRACT CV DATA:
    {text[:5000]}
    
    OBLIGATORY JSON STRUCTURE (NULL NOT ALLOWED, USE "" OR []):
    {{
        "full_name": "Full string name",
        "email": "email address",
        "phone": "formatted phone number",
        "location": "City, Country",
        "linkedin": "url",
        "github": "url",
        "portfolio": "url",
        "summary": "professional summary",
        "experience": [
            {{ "company": "name", "role": "title", "duration": "dates", "achievements": ["bullet 1"] }}
        ],
        "education": [
            {{ "institution": "uni", "degree": "bachelors", "year": "2020" }}
        ],
        "skills": ["skill 1", "skill 2"]
    }}
    """
    
    profile_raw = run_ai_task(prompt)
    
    # 3. Sanitize & Enforce Schema (Prevent crashing on missing keys)
    def clean(val, default): return val if val is not None else default
    
    sanitized = {
        "full_name": clean(profile_raw.get("full_name"), "N/A"),
        "email": clean(profile_raw.get("email"), "N/A"),
        "phone": clean(profile_raw.get("phone"), "N/A"),
        "location": clean(profile_raw.get("location"), "N/A"),
        "linkedin": clean(profile_raw.get("linkedin"), ""),
        "github": clean(profile_raw.get("github"), ""),
        "portfolio": clean(profile_raw.get("portfolio"), ""),
        "summary": clean(profile_raw.get("summary"), "Candidate profile"),
        "experience": [],
        "education": [],
        "skills": []
    }

    for exp in profile_raw.get("experience", []):
        sanitized["experience"].append({
            "company": clean(exp.get("company"), "N/A"),
            "role": clean(exp.get("role"), "Developer"),
            "duration": clean(exp.get("duration"), ""),
            "achievements": clean(exp.get("achievements"), [])
        })

    for edu in profile_raw.get("education", []):
        sanitized["education"].append({
            "institution": clean(edu.get("institution"), "N/A"),
            "degree": clean(edu.get("degree"), ""),
            "year": clean(edu.get("year"), "")
        })

    sanitized["skills"] = profile_raw.get("skills", [])
    if not isinstance(sanitized["skills"], list):
        sanitized["skills"] = [str(sanitized["skills"])]

    user_dir = get_user_dir(x_user_id)
    with open(os.path.join(user_dir, "profile.json"), "w") as f:
        json.dump(sanitized, f, indent=2)
            
    return sanitized

@app.get("/profile")
async def read_profile(x_user_id: str = Header(...)):
    profile = get_user_profile(x_user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.post("/autofill")
async def autofill_form(request: AutofillRequest, x_user_id: str = Header(...)):
    profile = get_user_profile(x_user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Session expired or invalid")
    
    profile_data = profile.model_dump()
    results = {}
    
    # 1. Direct Mapping (Optimized Heuristics)
    mapping = {
        "first name": "full_name", "last name": "full_name", "full name": "full_name",
        "email": "email", "phone": "phone", "linkedin": "linkedin", "github": "github",
        "location": "location", "current company": "experience[0].company"
    }
    
    ai_queue = []
    for field in request.fields:
        label_lower = (field.label or "").lower()
        matched = False
        for key, p_key in mapping.items():
            if key in label_lower:
                if p_key == "full_name":
                    results[field.name] = profile.full_name.split()[0] if "first" in label_lower else (profile.full_name.split()[-1] if "last" in label_lower else profile.full_name)
                elif p_key == "experience[0].company":
                    results[field.name] = profile.experience[0].company if profile.experience else ""
                else:
                    results[field.name] = profile_data.get(p_key, "")
                matched = True; break
        if not matched:
            ai_queue.append({"id": field.name, "label": field.label or field.placeholder})

    # 2. Agentic Responses
    if ai_queue:
        essential_background = {
            "name": profile.full_name,
            "summary": profile.summary,
            "top_skills": profile.skills[:10],
            "experience_summary": [f"{exp.role} at {exp.company}" for exp in profile.experience[:2]]
        }
        
        company = request.company_name or "your company"
        job = request.job_title or "this role"

        prompt = f"""
        ACT AS: {profile.full_name}, a Senior Backend Engineer.
        COMPANY: {company}
        TARGET ROLE: {job}
        
        BACKGROUND: {json.dumps(essential_background)}
        
        TASK: Write technical, human, and direct answers for these application questions.
        
        STRICT RULES:
        1. NO AI TONE: Don't use "Hiring Manager at [Title]". Just answer the specific question.
        2. NO PLACEHOLDERS: NEVER use brackets []. If you don't know something, be generic but solid.
        3. NO FLUFF: Skip the "I am excited" intro unless it's a cover letter field. Use technical facts.
        4. ACCURACY: If asked about the company, you are applying TO {company} FOR the role of {job}.
        
        QUESTIONS:
        {json.dumps(ai_queue, indent=2)}
        
        Return JSON object mapping ID to answer string.
        """
        
        try:
            ai_res = run_ai_task(prompt)
            results.update({str(k): str(v) for k, v in ai_res.items()})
        except Exception as e:
            print(f"AI response failed: {e}")
            pass
            
    return results
