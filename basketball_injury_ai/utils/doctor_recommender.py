import json
from pathlib import Path
from typing import List, Dict, Any

class DoctorRecommender:
    def __init__(self):
        self.doctors_data = self._load_doctors_data()

    def _load_doctors_data(self) -> Dict:
        """Load doctors database from JSON file"""
        data_path = Path(__file__).parent.parent / 'data' / 'doctors_database.json'
        with open(data_path, 'r') as f:
            return json.load(f)

    def recommend_doctors(self, injury_analysis: Dict[str, Any]) -> List[Dict]:
        """
        Recommend doctors based on injury analysis
        Returns sorted list of doctors based on relevance and rating
        """
        recommended_doctors = []
        conditions = injury_analysis.get("possible_conditions", [])
        
        if not conditions:
            return []

        # Extract relevant body parts and conditions
        relevant_terms = set()
        for condition in conditions:
            # Add condition-specific terms
            condition_terms = condition["name"].lower().split()
            relevant_terms.update(condition_terms)
            
            # Add body part terms
            if "shoulder" in condition["name"].lower():
                relevant_terms.add("shoulder")
            elif "knee" in condition["name"].lower():
                relevant_terms.add("knee")
            # Add more body part mappings as needed

        # Score each doctor based on relevance and rating
        for doctor in self.doctors_data["doctors"]:
            score = 0
            
            # Check specialties match
            specialty_matches = sum(
                any(term in specialty.lower() for term in relevant_terms)
                for specialty in doctor["specialties"]
            )
            score += specialty_matches * 2  # Weight specialty matches heavily
            
            # Add rating contribution
            score += doctor["rating"]
            
            # Add experience contribution
            score += min(doctor["experience"] / 10, 2)  # Cap experience score at 2
            
            if score > 0:
                recommended_doctors.append({
                    **doctor,
                    "relevance_score": score
                })

        # Sort by score and return top recommendations
        recommended_doctors.sort(key=lambda x: x["relevance_score"], reverse=True)
        return recommended_doctors[:3]  # Return top 3 recommendations

    def format_doctor_recommendation(self, doctor: Dict) -> str:
        """Format doctor information for display"""
        return f"""
Doctor: {doctor['name']}
Specialties: {', '.join(doctor['specialties'])}
Experience: {doctor['experience']} years
Rating: {doctor['rating']}/5.0 ({doctor['reviews']} reviews)
Hospital: {doctor['hospital']}
Location: {doctor['location']}
Available: {', '.join(doctor['available_days'])}
Languages: {', '.join(doctor['languages'])}
Contact:
- Phone: {doctor['contact']['phone']}
- Email: {doctor['contact']['email']}
"""