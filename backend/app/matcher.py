"""
Pure keyword-based matcher for form fields.
NO AI/LLM - only deterministic string matching.
"""

from typing import Optional, List, Dict
import re


class FieldMatcher:
    def __init__(self, user_answers: Dict[str, str]):
        """
        Initialize with user's stored answers.
        user_answers: {question_key: answer}
        """
        self.answers = user_answers
        
        # Keywords that suggest a field needs AI generation rather than simple matching
        self.creative_keywords = [
            'cover letter', 'why do you want', 'interest you', 'tell us about', 
            'describe your experience', 'statement', 'additional information',
            'why should we hire', 'about yourself', 'briefly explain'
        ]
        
        # Comprehensive keyword mappings for each question key
        self.keyword_map = {
            # Personal Information
            'full_name': ['full name', 'complete name', 'name', 'your name'],
            'first_name': ['first', 'firstname', 'fname', 'given', 'forename'],
            'middle_name': ['middle', 'middlename', 'mname'],
            'last_name': ['last', 'lastname', 'lname', 'surname', 'family'],
            'preferred_name': ['preferred', 'nickname', 'goes by'],
            'email': ['email', 'e-mail', 'mail'],
            'phone': ['phone', 'mobile', 'cell', 'telephone', 'tel', 'contact number'],
            'street_address': ['street', 'address line', 'address 1'],
            'city': ['city', 'town'],
            'state_province': ['state', 'province', 'region'],
            'postal_code': ['zip', 'postal', 'postcode', 'zipcode'],
            'country': ['country', 'nation'],
            
            # Professional Links
            'linkedin_url': ['linkedin', 'linkedin.com', 'linkedin profile'],
            'portfolio_url': ['portfolio', 'website', 'personal site'],
            'github_url': ['github', 'github.com', 'github profile'],
            'behance_url': ['behance', 'behance.net'],
            'dribbble_url': ['dribbble', 'dribbble.com'],
            'twitter_handle': ['twitter', 'x.com', 'handle'],
            
            # Education
            'highest_degree': ['degree', 'education level', 'highest education'],
            'school_name': ['school', 'university', 'college', 'institution'],
            'major_field_of_study': ['major', 'field of study', 'concentration', 'degree in'],
            'graduation_date': ['graduation', 'graduated', 'graduation date'],
            'gpa': ['gpa', 'grade point'],
            
            # Work History
            'current_company': ['current company', 'employer', 'current employer', 'company name'],
            'current_job_title': ['current title', 'job title', 'position', 'role'],
            'current_job_start_date': ['start date', 'from', 'employment start'],
            'current_job_end_date': ['end date', 'to', 'employment end'],
            'current_job_duties': ['responsibilities', 'duties', 'job description'],
            
            # Logistics
            'availability_date': ['available', 'start date', 'earliest start', 'when can you start', 'date available'],
            'work_type_preference': ['work type', 'employment type', 'full-time', 'part-time', 'office', 'home', 'hybrid', 'remote', 'office days'],
            'salary_expectation': ['salary', 'desired salary', 'expected salary', 'compensation', 'remuneration'],
            'willing_to_relocate': ['relocate', 'relocation', 'willing to move'],
            'willing_to_travel': ['travel', 'willing to travel'],
            'notice_period': ['notice', 'notice period', 'availability'],
            
            # Legal
            'legally_authorized_to_work': ['authorized', 'right to work', 'work authorization', 'legally work', 'authorized to work'],
            'require_visa_sponsorship': ['visa', 'sponsorship', 'work permit', 'visa sponsorship', 'require sponsorship', 'need sponsorship'],
            'age_over_18': ['18', 'age', 'over 18', 'at least 18'],
            
            # Screening
            'how_did_you_hear': ['how did you hear', 'source', 'referral source'],
            'employee_referral_name': ['referred by', 'referral', 'employee name'],
            'previously_applied': ['previously applied', 'applied before', 'worked here'],
            'relatives_at_company': ['relatives', 'family members'],
            
            # Self-ID
            'gender': ['gender', 'sex'],
            'race_ethnicity': ['race', 'ethnicity', 'ethnic'],
            'veteran_status': ['veteran', 'military'],
            'disability_status': ['disability', 'disabled'],
            
            # Accessibility
            'require_accommodations': ['accommodation', 'disability', 'accessible'],
            'accommodation_details': ['accommodation details', 'specific needs']
        }
    
    def normalize(self, text: str) -> str:
        """Normalize text for matching: lowercase, remove extra spaces"""
        if not text:
            return ""
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return re.sub(r'\s+', ' ', text.strip())
    
    def match_field(self, field_label: str, field_name: str = "", field_type: str = "text", options: List[str] = None) -> Optional[str]:
        """
        Match a form field to a stored answer using keyword matching.
        Returns the answer if a match is found, None otherwise.
        """
        # Combine label and name for matching
        search_text = self.normalize(f"{field_label} {field_name}")
        
        # Priority matching: find the LONGEST keyword that matches.
        best_match_key = None
        best_match_len = 0
        
        for key, keywords in self.keyword_map.items():
            for kw in keywords:
                if kw in search_text:
                    if len(kw) > best_match_len:
                        best_match_len = len(kw)
                        best_match_key = key
        
        if not best_match_key:
            return None
            
        # 1. Direct answer found
        if best_match_key in self.answers:
            answer = self.answers[best_match_key]
        
        # 2. Synthetic field: Full Name from First + Last
        elif best_match_key == 'full_name' and 'first_name' in self.answers and 'last_name' in self.answers:
            answer = f"{self.answers['first_name']} {self.answers['last_name']}"
            
        else:
            return None
        
        # If it's a select/radio field with options, try to match the answer to an option
        if (field_type in ['select', 'radio'] or options) and options:
            matched_option = self._match_to_option(answer, options)
            return matched_option if matched_option else answer
        
        return answer
    
    def _match_to_option(self, answer: str, options: List[str]) -> Optional[str]:
        """
        Match a stored answer to one of the available options.
        Uses fuzzy matching for flexibility.
        """
        answer_lower = answer.lower()
        
        # First try exact match
        for option in options:
            if option.lower() == answer_lower:
                return option
        
        # Then try partial match
        for option in options:
            if answer_lower in option.lower() or option.lower() in answer_lower:
                return option
        
        # Special handling for Yes/No questions
        if answer_lower in ['yes', 'y', 'true', '1']:
            for option in options:
                if option.lower() in ['yes', 'y']:
                    return option
        elif answer_lower in ['no', 'n', 'false', '0']:
            for option in options:
                if option.lower() in ['no', 'n']:
                    return option
        
        return None
    
    def suggest_question_key(self, field_label: str, field_name: str = "") -> Optional[str]:
        """
        Suggest which question key this field might be asking for.
        Used to help users know what information is missing.
        """
        search_text = self.normalize(f"{field_label} {field_name}")
        
        for key, keywords in self.keyword_map.items():
            if any(kw in search_text for kw in keywords):
                return key
        
        return None

    def is_creative_field(self, field_label: str, field_name: str = "") -> bool:
        """Check if a field requires creative writing (AI)."""
        search_text = self.normalize(f"{field_label} {field_name}")
        return any(kw in search_text for kw in self.creative_keywords)
