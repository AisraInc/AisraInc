class QuestionGenerator:
    def __init__(self, injury_data):
        self.injury_data = injury_data
        self.question_weights = {}
        self._initialize_question_weights()

    def _initialize_question_weights(self):
        """Initialize weights for questions based on their diagnostic value"""
        for body_part, data in self.injury_data.items():
            self.question_weights[body_part] = {}
            for question in data['questions']:
                weight = 0
                # Calculate question weight based on how many conditions it helps identify
                for condition in data['conditions'].values():
                    for symptom in condition['symptoms']:
                        if symptom.lower() in question.lower():
                            weight += condition['weight']
                self.question_weights[body_part][question] = weight

    def get_next_question(self, body_part, previous_responses=None):
        """
        Get the next most relevant question based on previous responses
        
        Args:
            body_part: String indicating the affected body part
            previous_responses: List of previous (question, response) tuples
        
        Returns:
            dict containing question text and possible answers
        """
        if previous_responses is None:
            previous_responses = []

        # Get all questions for the body part
        available_questions = self.injury_data[body_part]["questions"]
        
        # Filter out already asked questions
        asked_questions = [q for q, _ in previous_responses]
        remaining_questions = [q for q in available_questions if q not in asked_questions]

        if not remaining_questions:
            return None

        # Sort questions by weight
        sorted_questions = sorted(
            remaining_questions,
            key=lambda q: self.question_weights[body_part].get(q, 0),
            reverse=True
        )

        return {
            "question_text": sorted_questions[0],
            "answers": ["Yes", "No"],
            "type": "binary"
        }

    def generate_follow_up_question(self, body_part, previous_question, response):
        """
        Generate a follow-up question based on the previous response
        
        Args:
            body_part: String indicating the affected body part
            previous_question: The last question asked
            response: The response to the previous question
        
        Returns:
            dict containing follow-up question or None
        """
        conditions = self.injury_data[body_part]["conditions"]
        
        # If the previous response was positive, generate a more specific follow-up
        if response:
            for condition, details in conditions.items():
                for symptom in details["symptoms"]:
                    if symptom.lower() in previous_question.lower():
                        # Generate a more specific follow-up question
                        follow_up = {
                            "question_text": f"Can you describe the {symptom} in more detail?",
                            "answers": ["Mild", "Moderate", "Severe"],
                            "type": "severity"
                        }
                        return follow_up
        
        return None

    def get_severity_questions(self, body_part, condition):
        """Generate severity assessment questions for a specific condition"""
        base_questions = [
            {
                "question_text": "How would you rate the pain level?",
                "answers": ["Mild (1-3)", "Moderate (4-7)", "Severe (8-10)"],
                "type": "severity"
            },
            {
                "question_text": "How much does this affect your daily activities?",
                "answers": ["Minimal impact", "Moderate impact", "Severe impact"],
                "type": "impact"
            }
        ]
        
        # Add condition-specific questions
        if condition in self.injury_data[body_part]["conditions"]:
            condition_data = self.injury_data[body_part]["conditions"][condition]
            for symptom in condition_data["symptoms"]:
                base_questions.append({
                    "question_text": f"How severe is the {symptom}?",
                    "answers": ["Mild", "Moderate", "Severe"],
                    "type": "severity"
                })
        
        return base_questions