"""
JobFill Pro API - Redesigned with Pure Matching (No LLM Generation)
Architecture: Questionnaire → Airtable → Keyword Matching
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from dotenv import load_dotenv

from .airtable_client import AirtableClient
from .matcher import FieldMatcher
from .intelligence import IntelligenceAgent
from .questions import QUESTION_CATALOG, get_questions_by_category, get_question_by_key

load_dotenv()

app = FastAPI(title="JobFill Pro API - Pure Matching Edition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler for improved debugging
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    print(f"CRITICAL ERROR: {error_msg}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "trace": str(exc)},
    )

# ===== MODELS =====

class FormField(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: Optional[str] = ""
    name: Optional[str] = ""
    label: Optional[str] = ""
    type: Optional[str] = "text"
    placeholder: Optional[str] = ""
    context: Optional[str] = ""
    options: Optional[List[str]] = []

class AutofillRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    fields: List[FormField]
    company_name: str = "Unknown"
    job_title: str = "Role"

class SaveAnswerRequest(BaseModel):
    question_key: str
    answer: str

class SaveMultipleAnswersRequest(BaseModel):
    answers: List[dict]  # [{question_key, answer}, ...]


# ===== ENDPOINTS =====

@app.get("/")
async def root():
    return {
        "service": "JobFill Pro API", 
        "version": "2.0",
        "architecture": "Pure Matching (No LLM)",
        "database": "Airtable"
    }


@app.get("/questions")
async def get_questions():
    """
    Get all available questions organized by category.
    Used by frontend to build the onboarding questionnaire.
    """
    return {
        "categories": get_questions_by_category(),
        "total_questions": len(QUESTION_CATALOG)
    }


@app.get("/questions/{category}")
async def get_questions_for_category(category: str):
    """Get questions for a specific category"""
    questions_by_cat = get_questions_by_category()
    if category not in questions_by_cat:
        raise HTTPException(404, f"Category '{category}' not found")
    return questions_by_cat[category]


@app.get("/profile")
async def get_profile(x_user_id: str = Header(...)):
    """
    Get user's stored answers from Airtable.
    Returns all question-answer pairs.
    """
    try:
        airtable = AirtableClient()
        answers = airtable.get_all_answers(x_user_id)
        completed = airtable.has_completed_onboarding(x_user_id)
        
        return {
            "user_id": x_user_id,
            "answers": answers,
            "completed_onboarding": completed,
            "answer_count": len(answers)
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to retrieve profile: {str(e)}")


@app.post("/save-answer")
async def save_single_answer(request: SaveAnswerRequest, x_user_id: str = Header(...)):
    """
    Save a single answer to Airtable.
    Updates if already exists.
    """
    try:
        question = get_question_by_key(request.question_key)
        if not question:
            raise HTTPException(404, f"Question key '{request.question_key}' not found")
        
        airtable = AirtableClient()
        result = airtable.save_answer(
            user_id=x_user_id,
            category=question['category'],
            question_key=request.question_key,
            question_text=question['question'],
            answer=request.answer
        )
        
        return {"success": True, "question_key": request.question_key}
    except Exception as e:
        raise HTTPException(500, f"Failed to save answer: {str(e)}")


@app.post("/save-answers")
async def save_multiple_answers(request: SaveMultipleAnswersRequest, x_user_id: str = Header(...)):
    """
    Save multiple answers at once (for bulk onboarding).
    """
    try:
        airtable = AirtableClient()
        formatted_answers = []
        
        for answer_data in request.answers:
            question = get_question_by_key(answer_data['question_key'])
            if question:
                formatted_answers.append({
                    'category': question['category'],
                    'question_key': answer_data['question_key'],
                    'question_text': question['question'],
                    'answer': answer_data['answer']
                })
        
        airtable.save_multiple_answers(x_user_id, formatted_answers)
        
        return {
            "success": True,
            "saved_count": len(formatted_answers)
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to save answers: {str(e)}")


@app.post("/autofill")
async def autofill_form(request: AutofillRequest, x_user_id: str = Header(...)):
    """
    Pure matching-based autofill.
    NO LLM/AI - only keyword matching against stored answers.
    """
    try:
        # 1. Get user's stored answers from Airtable
        airtable = AirtableClient()
        user_answers = airtable.get_all_answers(x_user_id)
        
        if not user_answers or len(user_answers) == 0:
            raise HTTPException(404, "Please complete onboarding first. No answers found.")
        
        # 2. Use pure keyword matching + LLM intelligence
        matcher = FieldMatcher(user_answers)
        intel = IntelligenceAgent()
        mappings = {}
        missing_fields = []
        
        # Filter out ghost fields
        valid_fields = [f for f in request.fields if (f.id and f.id.strip()) or (f.name and f.name.strip())]
        
        for field in valid_fields:
            # A. Check if it's a creative field (Cover Letter, interest, etc.)
            if matcher.is_creative_field(field.label, field.name):
                print(f"[AUTOFILL] Using Groq for complex field: {field.label}")
                value = intel.generate_answer(
                    field_label=field.label,
                    user_profile=user_answers,
                    job_details={
                        "company": request.company_name,
                        "job_title": request.job_title
                    }
                )
            else:
                # B. Try to find a matching question key (Direct match)
                value = matcher.match_field(
                    field_label=field.label,
                    field_name=field.name,
                    field_type=field.type,
                    options=field.options
                )
            
            if value:
                # Use ID as primary key, fall back to name
                field_key = field.id if field.id and field.id.strip() else field.name
                mappings[field_key] = value
            else:
                # Couldn't match - suggest what question this might be
                suggested_key = matcher.suggest_question_key(field.label, field.name)
                missing_fields.append({
                    "field_label": field.label,
                    "suggested_question_key": suggested_key
                })
        
        print(f"[AUTOFILL] Mapped {len(mappings)} fields for {x_user_id}")
        print(f"[AUTOFILL] Missing {len(missing_fields)} fields")
        
        return {
            "mappings": mappings,
            "missing_fields": missing_fields,
            "total_fields": len(valid_fields),
            "matched_count": len(mappings)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AUTOFILL ERROR] {e}")
        return {"mappings": {}, "missing_fields": [], "error": str(e)}


@app.delete("/profile")
async def delete_profile(x_user_id: str = Header(...)):
    """
    Delete all user data from Airtable (for testing/reset).
    """
    try:
        airtable = AirtableClient()
        count = airtable.delete_all_answers(x_user_id)
        return {"success": True, "deleted_count": count}
    except Exception as e:
        raise HTTPException(500, f"Failed to delete profile: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Airtable connection
        airtable = AirtableClient()
        return {
            "status": "healthy",
            "database": "airtable",
            "connection": "ok"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "airtable",
            "connection": "failed",
            "error": str(e)
        }
