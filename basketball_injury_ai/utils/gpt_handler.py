import requests
from typing import List, Dict, Any
import os
import json

class TogetherAIHandler:
    def __init__(self, api_key: str = None):
        """Initialize Together.ai handler with API key"""
        self.api_key = api_key or os.getenv('TOGETHER_API_KEY')
        if not self.api_key:
            raise ValueError("Together.ai API key is required. Set it as TOGETHER_API_KEY environment variable or pass it to the constructor.")
        self.api_url = "https://api.together.xyz/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Using Mixtral as default model, but you can change this
        self.model = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    def _make_api_call(self, messages: List[Dict[str, str]]) -> str:
        """Make API call to Together.ai"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 800
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"API call failed: {str(e)}")
            if response := getattr(e, 'response', None):
                print(f"Error details: {response.text}")
            raise

    def generate_initial_questions(self, body_part: str) -> List[str]:
        """Generate initial questions for the specified body part"""
        prompt = f"""As a sports medicine expert, generate 5 key diagnostic questions for a basketball player 
        with a {body_part} injury. Questions should help identify common basketball-related injuries. 
        Format: return only the questions as a numbered list."""

        messages = [
            {"role": "system", "content": "You are a sports medicine expert specializing in basketball injuries."},
            {"role": "user", "content": prompt}
        ]

        try:
            questions_text = self._make_api_call(messages)
            # Parse the response to extract questions
            questions = [q.split('. ', 1)[1] if '. ' in q else q 
                        for q in questions_text.strip().split('\n') 
                        if q.strip() and not q.startswith('Here') and not q.startswith('These')]
            return questions
        except Exception as e:
            print(f"Failed to generate questions: {str(e)}")
            # Fallback questions if API fails
            return [
                "Can you describe the pain level?",
                "When did the injury occur?",
                "How did the injury happen?",
                "Is there any swelling?",
                "Can you move the affected area?"
            ]

    def analyze_injury(self, body_part: str, qa_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the injury based on question-answer history"""
        qa_formatted = "\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}"
            for qa in qa_history
        ])

        prompt = f"""Based on the following question-answer history for a {body_part} injury in basketball:

{qa_formatted}

Provide an analysis in the following JSON format:
{{
    "possible_conditions": [
        {{
            "name": "condition name",
            "confidence": "confidence percentage (number)",
            "description": "brief description",
            "recommendations": ["rec1", "rec2", ...]
        }}
    ]
}}

Ensure the response is valid JSON format."""

        messages = [
            {"role": "system", "content": "You are a sports medicine expert specializing in basketball injuries."},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = self._make_api_call(messages)
            # Extract JSON from response (in case there's additional text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError:
            return {
                "possible_conditions": [{
                    "name": "Analysis Error",
                    "confidence": 0,
                    "description": "Unable to analyze responses",
                    "recommendations": ["Please consult a medical professional"]
                }]
            }

    def generate_follow_up(self, body_part: str, previous_qa: Dict[str, Any]) -> str:
        """Generate a follow-up question based on previous Q&A"""
        prompt = f"""Given this Q&A about a {body_part} injury:
Q: {previous_qa['question']}
A: {previous_qa['answer']}

Generate one specific follow-up question to better understand the injury.
Format: Return only the question text."""

        messages = [
            {"role": "system", "content": "You are a sports medicine expert specializing in basketball injuries."},
            {"role": "user", "content": prompt}
        ]

        try:
            return self._make_api_call(messages).strip()
        except Exception as e:
            print(f"Failed to generate follow-up question: {str(e)}")
            return None