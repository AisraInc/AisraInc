from flask import Flask, render_template, request, jsonify
from utils.together_handler import TogetherAIHandler
from utils.doctor_recommender import DoctorRecommender
import json  # Add this import
import traceback  # Add this import
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')
CORS(app)

# Initialize with your Together.ai API key
ai_handler = TogetherAIHandler(api_key='df5a2877292db5445be835e35a71e8300391cabb4883b28fc1dd5ec06e60e5ce')
doctor_recommender = DoctorRecommender()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_questions', methods=['POST'])
def get_questions():
    try:
        data = request.get_json()
        body_part = data.get('body_part')
        
        if not body_part:
            return jsonify({'error': 'No body part specified'}), 400
        
        # Generate questions using Together.ai
        questions = ai_handler.generate_initial_questions(body_part)
        
        return jsonify({
            'questions': questions
        })
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_responses', methods=['POST'])
def analyze_responses():
    try:
        data = request.get_json()
        responses = data.get('responses', [])
        
        if not responses:
            return jsonify({'error': 'No responses provided'}), 400
        
        # Debug print
        print("\n=== Analyzing Responses ===")
        print("Responses received:", responses)
        
        body_part = responses[0].get('body_part', 'unspecified')
        
        # Analyze using Together.ai
        analysis = ai_handler.analyze_injury(body_part, responses)
        
        print("\n=== Analysis Result ===")
        print("Raw analysis:", json.dumps(analysis, indent=2))
        
        # Get the most likely condition
        if 'possible_conditions' in analysis and analysis['possible_conditions']:
            condition = analysis['possible_conditions'][0]
            diagnosis = (
                f"{condition['name']} (Confidence: {condition['confidence']}%)\n"
                f"{condition['description']}\n\n"
                f"Recommendations:\n" + "\n".join(f"- {r}" for r in condition['recommendations'])
            )
        else:
            raise ValueError("No conditions found in analysis")
        
        # Get doctor recommendations
        recommended_doctors = doctor_recommender.recommend_doctors(analysis)
        
        # Format doctor recommendations
        doctors = []
        for doctor in recommended_doctors:
            doctors.append({
                'name': doctor['name'],
                'specialty': ', '.join(doctor['specialties']),
                'location': doctor['hospital'],
                'contact': doctor['contact']['phone']
            })
        
        return jsonify({
            'diagnosis': diagnosis,
            'doctors': doctors
        })
        
    except Exception as e:
        print(f"\n=== Analysis Error ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')