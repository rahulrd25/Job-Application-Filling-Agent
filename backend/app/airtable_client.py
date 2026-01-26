"""
Airtable client for storing and retrieving user responses.
Provides a clean interface to the UserResponses table.
"""

from pyairtable import Api
import os
from typing import Dict, Optional, List


class AirtableClient:
    def __init__(self):
        api_key = os.getenv('AIRTABLE_API_KEY')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        table_name = os.getenv('AIRTABLE_TABLE_NAME', 'jobfilling_Data')
        
        if not api_key or not base_id:
            raise ValueError("AIRTABLE_API_KEY and AIRTABLE_BASE_ID must be set in environment")
        
        self.api = Api(api_key)
        self.base = self.api.base(base_id)
        self.table = self.base.table(table_name)
    
    def save_answer(self, user_id: str, category: str, question_key: str, question_text: str, answer: str) -> dict:
        """
        Save a single question-answer pair for a user.
        Updates existing record if the question_key already exists for this user.
        """
        # Check if answer already exists
        existing = self.table.all(formula=f"AND({{user_id}}='{user_id}', {{question_key}}='{question_key}')")
        
        data = {
            'user_id': user_id,
            'category': category,
            'question_key': question_key,
            'question_text': question_text,
            'answer': answer
        }
        
        if existing:
            # Update existing record
            return self.table.update(existing[0]['id'], data)
        else:
            # Create new record
            return self.table.create(data)
    
    def save_multiple_answers(self, user_id: str, answers: List[Dict[str, str]]) -> List[dict]:
        """
        Save multiple answers at once (batch operation).
        answers: List of dicts with keys: category, question_key, question_text, answer
        """
        results = []
        for ans in answers:
            result = self.save_answer(
                user_id=user_id,
                category=ans['category'],
                question_key=ans['question_key'],
                question_text=ans['question_text'],
                answer=ans['answer']
            )
            results.append(result)
        return results
    
    def get_all_answers(self, user_id: str) -> Dict[str, str]:
        """
        Retrieve all answers for a user as a dictionary: {question_key: answer}
        """
        records = self.table.all(formula=f"{{user_id}}='{user_id}'")
        return {r['fields']['question_key']: r['fields']['answer'] for r in records if 'answer' in r['fields']}
    
    def get_answer(self, user_id: str, question_key: str) -> Optional[str]:
        """
        Get a specific answer for a user by question key.
        Returns None if not found.
        """
        records = self.table.all(formula=f"AND({{user_id}}='{user_id}', {{question_key}}='{question_key}')")
        if records and 'answer' in records[0]['fields']:
            return records[0]['fields']['answer']
        return None
    
    def get_answers_by_category(self, user_id: str, category: str) -> Dict[str, str]:
        """
        Get all answers for a specific category.
        """
        records = self.table.all(formula=f"AND({{user_id}}='{user_id}', {{category}}='{category}')")
        return {r['fields']['question_key']: r['fields']['answer'] for r in records if 'answer' in r['fields']}
    
    def delete_all_answers(self, user_id: str) -> int:
        """
        Delete all answers for a user (for testing/reset purposes).
        Returns count of deleted records.
        """
        records = self.table.all(formula=f"{{user_id}}='{user_id}'")
        for record in records:
            self.table.delete(record['id'])
        return len(records)
    
    def has_completed_onboarding(self, user_id: str) -> bool:
        """
        Check if user has completed onboarding (has at least basic required fields).
        Required fields: first_name, last_name, email, phone
        """
        required_keys = ['first_name', 'last_name', 'email', 'phone']
        answers = self.get_all_answers(user_id)
        return all(key in answers and answers[key] for key in required_keys)
