from sklearn.tree import DecisionTreeClassifier
import numpy as np
import json
from pathlib import Path

class InjuryClassifier:
    def __init__(self):
        self.model = DecisionTreeClassifier(random_state=42)
        self.injury_data = self._load_injury_data()
        self.symptom_weights = {}
        self._initialize_weights()

    def _load_injury_data(self):
        """Load injury data from JSON file"""
        data_path = Path(__file__).parent.parent / 'data' / 'injury_data.json'
        with open(data_path, 'r') as f:
            return json.load(f)

    def _initialize_weights(self):
        """Initialize symptom weights for each body part and condition"""
        for body_part, data in self.injury_data.items():
            self.symptom_weights[body_part] = {}
            for condition, details in data['conditions'].items():
                for symptom in details['symptoms']:
                    if symptom not in self.symptom_weights[body_part]:
                        self.symptom_weights[body_part][symptom] = {}
                    self.symptom_weights[body_part][symptom][condition] = details['weight']

    def analyze_responses(self, responses, body_part):
        """
        Analyze the responses and return probable conditions
        
        Args:
            responses: List of tuples (question, boolean_response)
            body_part: String indicating the affected body part
        
        Returns:
            List of tuples (condition, confidence_score)
        """
        conditions = self.injury_data[body_part]["conditions"]
        scores = {condition: 0.0 for condition in conditions}
        
        # Calculate base scores
        for question, response in responses:
            if response:
                question = question.lower()
                for condition, details in conditions.items():
                    for symptom in details["symptoms"]:
                        if symptom.lower() in question:
                            scores[condition] += details["weight"]

        # Normalize scores
        max_score = max(scores.values()) if scores else 1
        if max_score > 0:
            scores = {k: (v / max_score) * 100 for k, v in scores.items()}

        # Sort conditions by confidence score
        sorted_conditions = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_conditions

    def get_condition_details(self, body_part, condition):
        """Get detailed information about a specific condition"""
        if body_part in self.injury_data and condition in self.injury_data[body_part]["conditions"]:
            return self.injury_data[body_part]["conditions"][condition]
        return None

    def get_next_question(self, body_part, previous_responses=None):
        """
        Get the next most relevant question based on previous responses
        
        Args:
            body_part: String indicating the affected body part
            previous_responses: List of previous (question, response) tuples
        
        Returns:
            Next question to ask or None if no more questions
        """
        if previous_responses is None:
            previous_responses = []

        available_questions = self.injury_data[body_part]["questions"]
        asked_questions = [q for q, _ in previous_responses]
        
        # Filter out already asked questions
        remaining_questions = [q for q in available_questions if q not in asked_questions]
        
        if not remaining_questions:
            return None
            
        return remaining_questions[0]