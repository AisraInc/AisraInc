import requests
import json
import os
import traceback
from typing import List, Dict, Any, Optional

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
            print("\n=== API Call Details ===")
            print("URL:", self.api_url)
            print("Headers:", {k: v if k != 'Authorization' else '[REDACTED]' for k, v in self.headers.items()})
            print("Payload:", json.dumps(payload, indent=2))

            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )

            print("\n=== API Response Details ===")
            print("Status Code:", response.status_code)
            print("Response Headers:", dict(response.headers))

            response.raise_for_status()
            response_json = response.json()

            print("Response JSON:", json.dumps(response_json, indent=2))

            return response_json['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            print(f"\n=== API Request Error ===")
            print(f"Error: {str(e)}")
            if response := getattr(e, 'response', None):
                print(f"Response Status: {response.status_code}")
                print(f"Response Text: {response.text}")
            raise

    def generate_initial_questions(self, body_part: str) -> List[Dict]:
        """Generate initial questions for the specified body part with answer types"""
        prompt = f"""As a sports medicine expert, generate 5 specific diagnostic questions for a basketball player's {body_part} injury.
        Consider the anatomy and common basketball injuries for the {body_part} area.
        
        For each question, provide the appropriate input type based on what's being asked:
        - Use "scale" (1-10) for pain or intensity questions
        - Use "choice" for yes/no or specific options
        - Use "multiple" when multiple selections are possible
        - Use "text" for open-ended questions requiring detailed responses
        
        Return the questions in this JSON format:
        [
            {{
                "question": "Question text here",
                "type": "scale/choice/multiple/text",
                "options": "1-10" or ["option1", "option2"] or null for text
            }}
        ]
        
        Make questions specific to {body_part} injuries in basketball."""

        messages = [
            {"role": "system", "content": "You are a sports medicine expert specializing in basketball injuries."},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = self._make_api_call(messages)
            print("\n=== Question Generation Response ===")
            print(response_text)
            
            # Extract JSON array from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start == -1 or json_end == 0:
                raise json.JSONDecodeError("No JSON array found in response", response_text, 0)
            
            json_str = response_text[json_start:json_end]
            questions = json.loads(json_str)
            return questions
            
        except Exception as e:
            print(f"Failed to generate questions: {str(e)}")
            # Fallback questions
            return [
                {
                    "question": f"Rate the pain level in your {body_part}",
                    "type": "scale",
                    "options": "1-10"
                },
                {
                    "question": f"What type of pain do you feel in your {body_part}?",
                    "type": "choice",
                    "options": ["Sharp", "Dull", "Throbbing", "Burning"]
                },
                {
                    "question": f"Which movements make your {body_part} pain worse?",
                    "type": "multiple",
                    "options": ["Jumping", "Running", "Turning", "Stretching", "Walking"]
                },
                {
                    "question": f"Describe how the {body_part} injury occurred",
                    "type": "text",
                    "options": None
                },
                {
                    "question": f"Is there any swelling in your {body_part}?",
                    "type": "choice",
                    "options": ["Yes", "No"]
                }
            ]

    def analyze_injury(self, body_part: str, qa_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the injury based on question-answer history"""
        try:
            # Format the Q&A history
            qa_formatted = "\n".join([
                f"Q: {qa['question']}\nA: {qa['answer']}"
                for qa in qa_history
            ])

            prompt = f"""Based on the following question-answer history for a {body_part} injury in basketball:

{qa_formatted}

Provide a detailed analysis in this JSON format:
{{
    "possible_conditions": [
        {{
            "name": "specific condition name",
            "confidence": "percentage number between 0-100",
            "description": "detailed description of the condition",
            "severity": "mild/moderate/severe",
            "recommendations": [
                "specific recommendation 1",
                "specific recommendation 2",
                "..."
            ]
        }}
    ]
}}

Focus on common basketball injuries for the {body_part} area. Be specific and detailed in your analysis."""

            messages = [
                {"role": "system", "content": "You are a sports medicine expert specializing in basketball injuries."},
                {"role": "user", "content": prompt}
            ]

            print("\n=== Analysis Request ===")
            print("Body Part:", body_part)
            print("Q&A History:", json.dumps(qa_history, indent=2))

            response_text = self._make_api_call(messages)

            print("\n=== Analysis Response ===")
            print(response_text)

            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end <= 0:
                raise ValueError("No JSON found in response")

            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)

            if not isinstance(result, dict) or 'possible_conditions' not in result:
                raise ValueError("Invalid response structure")

            return result

        except Exception as e:
            print(f"\n=== Analysis Error ===")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            
            return {
                "possible_conditions": [{
                    "name": "Analysis Error",
                    "confidence": 0,
                    "description": f"Error analyzing responses: {str(e)}. Please consult a medical professional for accurate diagnosis.",
                    "severity": "unknown",
                    "recommendations": [
                        "Consult a sports medicine specialist",
                        "Apply RICE protocol (Rest, Ice, Compression, Elevation)",
                        "Avoid activities that cause pain",
                        "Seek immediate medical attention if pain is severe"
                    ]
                }]
            }

    def generate_follow_up(self, body_part: str, previous_qa: Dict[str, Any]) -> Dict:
        """Generate a follow-up question based on previous Q&A"""
        prompt = f"""Based on this Q&A about a {body_part} injury:
Q: {previous_qa['question']}
A: {previous_qa['answer']}

Generate a follow-up question in this JSON format:
{{
    "question": "your follow-up question",
    "type": "scale/choice/multiple/text",
    "options": "1-10" or ["option1", "option2"] or null for text
}}

Make the question specific to basketball injuries and the {body_part} area."""

        messages = [
            {"role": "system", "content": "You are a sports medicine expert specializing in basketball injuries."},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = self._make_api_call(messages)
            print("\n=== Follow-up Question Response ===")
            print(response_text)
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Failed to generate follow-up question: {str(e)}")
            return {
                "question": "Is there anything else you'd like to add about your injury?",
                "type": "text",
                "options": None
            }