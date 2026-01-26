import os
import json
from groq import Groq
from typing import Dict, List, Optional

class IntelligenceAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def generate_answer(self, field_label: str, user_profile: Dict[str, str], job_details: Dict[str, str]) -> str:
        """
        Generate a tailored answer for a complex form field using Groq.
        """
        profile_summary = "\n".join([f"{k}: {v}" for k, v in user_profile.items()])
        job_summary = f"Company: {job_details.get('company', 'Unknown')}\nRole: {job_details.get('job_title', 'Role')}"

        prompt = f"""
        Write a professional, direct, and human-sounding answer for this job application question: "{field_label}"

        USER PROFILE:
        {profile_summary}

        CONTEXT (JOB):
        {job_summary}

        STRICT WRITING RULES (ANTI-AI SLOP):
        1. **NO AI TONE**: Avoid "I am thrilled," "In today's fast-paced world," "passionate about," or "strive for excellence." Use plain, direct English.
        2. **HUMAN STYLE**: Write like a real person who values time. No empty fluff, no corporate buzzwords (e.g., "synergy," "cutting-edge," "leverage"), and NO long dashes or complex punctuation.
        3. **GENUINE**: Use the actual facts from the User Profile. Do not hallucinate achievements. If the user mentions a project, talk about it simply.
        4. **CONCISE**: Max 2 short paragraphs for cover letters. 1-2 sentences for shorter questions.
        5. **NO TEMPLATES**: Do not use "Dear Hiring Manager" or "Sincerely" unless it is a full cover letter. Even then, keep it grounded.
        6. **JD MATCH**: subtly mention how the user's specific experience (not general skills) fits this specific role/company.

        RETURN ONLY THE FINAL TEXT. NO PREAMBLE.
        """

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a direct, no-nonsense career assistant. You write in a grounded, human-to-human style. You hate AI buzzwords and corporate jargon."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[GROQ ERROR] {e}")
            return f"Error generating answer: {str(e)}"
