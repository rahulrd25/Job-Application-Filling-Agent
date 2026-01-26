"""
Comprehensive catalog of all possible job application questions.
Each question has:
- key: Normalized identifier for storage/matching
- category: Grouping for UI organization
- question: Human-readable prompt for onboarding
- type: Input type (text, email, tel, url, select, date, textarea)
- options: For select/radio fields
- required: Whether this is commonly required
"""

QUESTION_CATALOG = [
    # ===== 1. PERSONAL INFORMATION =====
    {
        "key": "first_name",
        "category": "personal",
        "question": "What is your first name?",
        "type": "text",
        "required": True
    },
    {
        "key": "middle_name",
        "category": "personal",
        "question": "What is your middle name? (Optional)",
        "type": "text",
        "required": False
    },
    {
        "key": "last_name",
        "category": "personal",
        "question": "What is your last name?",
        "type": "text",
        "required": True
    },
    {
        "key": "preferred_name",
        "category": "personal",
        "question": "What do you like to be called? (Preferred name)",
        "type": "text",
        "required": False
    },
    {
        "key": "email",
        "category": "personal",
        "question": "What is your email address?",
        "type": "email",
        "required": True
    },
    {
        "key": "phone",
        "category": "personal",
        "question": "What is your phone number?",
        "type": "tel",
        "required": True
    },
    {
        "key": "street_address",
        "category": "personal",
        "question": "What is your street address?",
        "type": "text",
        "required": False
    },
    {
        "key": "city",
        "category": "personal",
        "question": "What city do you live in?",
        "type": "text",
        "required": True
    },
    {
        "key": "state_province",
        "category": "personal",
        "question": "What is your state/province?",
        "type": "text",
        "required": False
    },
    {
        "key": "postal_code",
        "category": "personal",
        "question": "What is your postal/zip code?",
        "type": "text",
        "required": False
    },
    {
        "key": "country",
        "category": "personal",
        "question": "What country do you live in?",
        "type": "text",
        "required": True
    },
    
    # ===== 2. PROFESSIONAL LINKS =====
    {
        "key": "linkedin_url",
        "category": "professional_links",
        "question": "What is your LinkedIn profile URL?",
        "type": "url",
        "required": False
    },
    {
        "key": "portfolio_url",
        "category": "professional_links",
        "question": "What is your personal website or portfolio URL?",
        "type": "url",
        "required": False
    },
    {
        "key": "github_url",
        "category": "professional_links",
        "question": "What is your GitHub profile URL?",
        "type": "url",
        "required": False
    },
    {
        "key": "behance_url",
        "category": "professional_links",
        "question": "What is your Behance profile URL?",
        "type": "url",
        "required": False
    },
    {
        "key": "dribbble_url",
        "category": "professional_links",
        "question": "What is your Dribbble profile URL?",
        "type": "url",
        "required": False
    },
    {
        "key": "twitter_handle",
        "category": "professional_links",
        "question": "What is your Twitter/X handle?",
        "type": "text",
        "required": False
    },
    
    # ===== 3. EDUCATION =====
    {
        "key": "highest_degree",
        "category": "education",
        "question": "What is your highest level of education?",
        "type": "select",
        "options": ["High School Diploma", "Associate's Degree", "Bachelor's Degree", "Master's Degree", "PhD", "Professional Degree"],
        "required": True
    },
    {
        "key": "school_name",
        "category": "education",
        "question": "What is the name of your most recent school/university?",
        "type": "text",
        "required": False
    },
    {
        "key": "major_field_of_study",
        "category": "education",
        "question": "What was your major/field of study?",
        "type": "text",
        "required": False
    },
    {
        "key": "graduation_date",
        "category": "education",
        "question": "When did you graduate (or when do you expect to graduate)?",
        "type": "date",
        "required": False
    },
    {
        "key": "gpa",
        "category": "education",
        "question": "What was your GPA? (Optional, often for entry-level)",
        "type": "text",
        "required": False
    },
    
    # ===== 4. WORK HISTORY (Most Recent Role) =====
    {
        "key": "current_company",
        "category": "work_history",
        "question": "What is your current/most recent company name?",
        "type": "text",
        "required": False
    },
    {
        "key": "current_job_title",
        "category": "work_history",
        "question": "What is your current/most recent job title?",
        "type": "text",
        "required": False
    },
    {
        "key": "current_job_start_date",
        "category": "work_history",
        "question": "When did you start this role? (Month/Year)",
        "type": "text",
        "required": False
    },
    {
        "key": "current_job_end_date",
        "category": "work_history",
        "question": "When did this role end? (Leave blank if current, or enter Month/Year)",
        "type": "text",
        "required": False
    },
    {
        "key": "current_job_duties",
        "category": "work_history",
        "question": "Briefly describe your responsibilities in this role",
        "type": "textarea",
        "required": False
    },
    
    # ===== 5. LOGISTICS & AVAILABILITY =====
    {
        "key": "availability_date",
        "category": "logistics",
        "question": "What is the earliest date you can start working?",
        "type": "date",
        "required": False
    },
    {
        "key": "work_type_preference",
        "category": "logistics",
        "question": "What type of work are you seeking?",
        "type": "select",
        "options": ["Full-time", "Part-time", "Contract", "Internship", "Any"],
        "required": False
    },
    {
        "key": "salary_expectation",
        "category": "logistics",
        "question": "What is your desired annual salary? (e.g., 75000)",
        "type": "text",
        "required": False
    },
    {
        "key": "willing_to_relocate",
        "category": "logistics",
        "question": "Are you willing to relocate for this position?",
        "type": "select",
        "options": ["Yes", "No", "Maybe"],
        "required": False
    },
    {
        "key": "willing_to_travel",
        "category": "logistics",
        "question": "Are you willing to travel for work?",
        "type": "select",
        "options": ["Yes, up to 25%", "Yes, up to 50%", "Yes, up to 75%", "No"],
        "required": False
    },
    {
        "key": "notice_period",
        "category": "logistics",
        "question": "What is your notice period at your current job? (e.g., 2 weeks, 30 days)",
        "type": "text",
        "required": False
    },
    
    # ===== 6. WORK AUTHORIZATION & LEGAL =====
    {
        "key": "legally_authorized_to_work",
        "category": "legal",
        "question": "Are you legally authorized to work in the country where this job is located?",
        "type": "select",
        "options": ["Yes", "No"],
        "required": True
    },
    {
        "key": "require_visa_sponsorship",
        "category": "legal",
        "question": "Will you now or in the future require visa sponsorship?",
        "type": "select",
        "options": ["Yes", "No"],
        "required": False
    },
    {
        "key": "age_over_18",
        "category": "legal",
        "question": "Are you 18 years of age or older?",
        "type": "select",
        "options": ["Yes", "No"],
        "required": True
    },
    
    # ===== 7. SCREENING & DISCLOSURES =====
    {
        "key": "how_did_you_hear",
        "category": "screening",
        "question": "How did you hear about this position?",
        "type": "select",
        "options": ["LinkedIn", "Indeed", "Company Website", "Referral", "Recruiter", "Other"],
        "required": False
    },
    {
        "key": "employee_referral_name",
        "category": "screening",
        "question": "If you were referred by an employee, what is their name?",
        "type": "text",
        "required": False
    },
    {
        "key": "previously_applied",
        "category": "screening",
        "question": "Have you previously applied to or worked for this company?",
        "type": "select",
        "options": ["Yes", "No"],
        "required": False
    },
    {
        "key": "relatives_at_company",
        "category": "screening",
        "question": "Do you have any relatives currently working for this company?",
        "type": "select",
        "options": ["Yes", "No"],
        "required": False
    },
    
    # ===== 8. VOLUNTARY SELF-IDENTIFICATION (U.S.) =====
    {
        "key": "gender",
        "category": "self_id",
        "question": "What is your gender? (Optional - for government reporting)",
        "type": "select",
        "options": ["Male", "Female", "Non-binary", "Decline to self-identify"],
        "required": False
    },
    {
        "key": "race_ethnicity",
        "category": "self_id",
        "question": "What is your race/ethnicity? (Optional - for government reporting)",
        "type": "select",
        "options": [
            "Hispanic or Latino",
            "White",
            "Black or African American",
            "Asian",
            "Native Hawaiian or Pacific Islander",
            "American Indian or Alaska Native",
            "Two or more races",
            "Decline to self-identify"
        ],
        "required": False
    },
    {
        "key": "veteran_status",
        "category": "self_id",
        "question": "Are you a protected veteran? (Optional - for government reporting)",
        "type": "select",
        "options": ["Yes", "No", "Decline to self-identify"],
        "required": False
    },
    {
        "key": "disability_status",
        "category": "self_id",
        "question": "Do you have a disability? (Optional - for government reporting)",
        "type": "select",
        "options": ["Yes", "No", "Decline to self-identify"],
        "required": False
    },
    
    # ===== ACCESSIBILITY & ACCOMMODATIONS =====
    {
        "key": "require_accommodations",
        "category": "accessibility",
        "question": "Do you require any accommodations during the interview process?",
        "type": "select",
        "options": ["Yes", "No"],
        "required": False
    },
    {
        "key": "accommodation_details",
        "category": "accessibility",
        "question": "If yes, please describe what accommodations you need",
        "type": "textarea",
        "required": False
    },
    
    # ===== 10. EXPERIENCE & PITCH (FOR AI GENERATION) =====
    {
        "key": "career_summary_bullets",
        "category": "pitch",
        "question": "Bullet points of your key achievements/career summary",
        "type": "textarea",
        "required": False
    },
    {
        "key": "why_this_role_generic",
        "category": "pitch",
        "question": "What generally motivates you to apply for new roles?",
        "type": "textarea",
        "required": False
    },
    {
        "key": "notable_projects",
        "category": "pitch",
        "question": "Briefly mention 2-3 notable projects you've built",
        "type": "textarea",
        "required": False
    }
]


def get_questions_by_category():
    """Group questions by category for UI organization"""
    categories = {}
    for q in QUESTION_CATALOG:
        cat = q["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(q)
    return categories


def get_question_by_key(key: str):
    """Retrieve a specific question by its key"""
    for q in QUESTION_CATALOG:
        if q["key"] == key:
            return q
    return None
