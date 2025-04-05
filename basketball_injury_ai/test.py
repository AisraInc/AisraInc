from utils.together_handler import TogetherAIHandler
import json 

# Initialize with your API key
handler = TogetherAIHandler(api_key='df5a2877292db5445be835e35a71e8300391cabb4883b28fc1dd5ec06e60e5ce')

# Test question generation
questions = handler.generate_initial_questions('knee')
print("Generated Questions:", json.dumps(questions, indent=2))

# Test analysis
test_qa = [
    {
        "question": "Rate your pain level",
        "answer": "7",
        "type": "scale"
    },
    {
        "question": "Is there any swelling?",
        "answer": "Yes",
        "type": "choice"
    }
]

analysis = handler.analyze_injury('knee', test_qa)
print("Analysis:", json.dumps(analysis, indent=2))