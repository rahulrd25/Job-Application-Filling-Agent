from pydantic import BaseModel, Field
from typing import List, Optional

class Experience(BaseModel):
    company: str
    role: str
    duration: str
    achievements: List[str]

class Education(BaseModel):
    institution: str
    degree: str
    year: str

class ProfessionalProfile(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    linkedin: str
    github: str
    portfolio: Optional[str] = None
    summary: str
    experience: List[Experience]
    education: List[Education]
    skills: List[str]
    resume_path: Optional[str] = None
    resume_filename: Optional[str] = None

class FormField(BaseModel):
    label: str
    name: str
    type: str
    placeholder: Optional[str] = None
    context: Optional[str] = None  # Surrounding text or section name

class AutofillRequest(BaseModel):
    fields: List[FormField]
    job_description: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
