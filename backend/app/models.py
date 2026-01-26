from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any

class Experience(BaseModel):
    model_config = ConfigDict(extra="ignore")
    company: str = ""
    role: str = ""
    location: str = ""
    duration: str = ""
    highlights: List[str] = []

class Education(BaseModel):
    model_config = ConfigDict(extra="ignore")
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    year: str = ""
    gpa: str = ""

class LegalInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    work_authorization_status: str = "" # e.g. 'Authorized', 'Requires Sponsorship'
    authorized_countries: List[str] = []
    visa_required: bool = False
    identity_ssn_last4: Optional[str] = None
    veteran_status: str = "No"

class DEIInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    gender: str = ""
    pronouns: str = ""
    ethnicity: str = ""
    disability_status: str = "" # 'Yes', 'No', 'Prefer not to say'
    lgbtq_status: str = ""

class LogisticsInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    current_salary: str = ""
    expected_salary: str = ""
    notice_period: str = ""
    relocation_willing: bool = False
    earliest_start_date: str = ""
    work_preference: str = "Hybrid" # 'Remote', 'Onsite', 'Hybrid'

class UltimateProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    # Core Identity (MANDATORY)
    full_name: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    city: str = ""
    country: str = ""
    
    # Socials
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    
    # Professional
    summary: str = ""
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    
    # Contextual Blocks (OPTIONAL but robust)
    legal: LegalInfo = Field(default_factory=LegalInfo)
    dei: DEIInfo = Field(default_factory=DEIInfo)
    logistics: LogisticsInfo = Field(default_factory=LogisticsInfo)
    
    # State Management
    onboarding_complete: bool = False

class FormField(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = ""
    name: str = ""
    label: str = ""
    placeholder: str = ""
    type: str = "text"
    context: str = "" 
    options: List[str] = []

class AutofillRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    fields: List[FormField]
    job_title: Optional[str] = None
    company_name: Optional[str] = None

class ChatMessage(BaseModel):
    role: str # user or assistant
    content: str

class OnboardingSession(BaseModel):
    user_id: str
    history: List[ChatMessage]
    current_profile: Dict[str, Any]
