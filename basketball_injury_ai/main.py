import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from utils.together_handler import TogetherAIHandler
from utils.doctor_recommender import DoctorRecommender

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self, width=750, height=500)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Bind arrow keys
        self.canvas.bind_all("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Down>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class BasketballInjuryDiagnostic:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Basketball Injury Assessment AI")
        self.root.geometry("800x600")
        
        # Initialize components
        self.setup_ai()
        
        # State variables
        self.current_body_part = None
        self.responses = []
        self.current_question = None
        self.questions_queue = []
        
        # Initialize doctor recommender
        self.doctor_recommender = DoctorRecommender()
        
        self.setup_ui()

    def setup_ai(self):
        """Setup Together.ai handler with API key"""
        # Create API key window
        api_key_window = tk.Toplevel(self.root)
        api_key_window.title("Together.ai API Key")
        api_key_window.geometry("400x150")
        
        # Center the window
        api_key_window.transient(self.root)
        api_key_window.grab_set()
        
        # Add label
        ttk.Label(
            api_key_window,
            text="Enter your Together.ai API Key:",
            font=('Helvetica', 12)
        ).pack(pady=10)
        
        # Add entry field with default API key
        api_key_var = tk.StringVar(value="df5a2877292db5445be835e35a71e8300391cabb4883b28fc1dd5ec06e60e5ce")
        api_key_entry = ttk.Entry(api_key_window, textvariable=api_key_var, width=50)
        api_key_entry.pack(pady=10)
        
        def save_key():
            key = api_key_var.get().strip()
            if key:
                try:
                    self.ai_handler = TogetherAIHandler(key)
                    api_key_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid API key: {str(e)}")
            else:
                messagebox.showerror("Error", "API key is required")
        
        # Add save button
        ttk.Button(
            api_key_window,
            text="Save",
            command=save_key
        ).pack(pady=10)
        
        # Wait for the window to close
        self.root.wait_window(api_key_window)

    def setup_ui(self):
        # Create scrollable main frame
        self.scroll_frame = ScrollableFrame(self.root)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.main_frame = self.scroll_frame.scrollable_frame
        
        # Title
        title_label = ttk.Label(
            self.main_frame,
            text="Basketball Injury Assessment AI",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)
        
        # Body part selection
        self.setup_body_part_selection()
        
        # Question area
        self.question_frame = ttk.Frame(self.main_frame)
        self.question_frame.pack(pady=20, fill="x")
        
        # Result area
        self.result_text = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            width=70,
            height=20,  # Increased height for doctor recommendations
            font=('Helvetica', 11)
        )
        self.result_text.pack(pady=20, padx=20)
        
        # Progress indicator
        self.progress_label = ttk.Label(
            self.main_frame,
            text="",
            font=('Helvetica', 10)
        )
        self.progress_label.pack(pady=5)
        
        # Reset button
        self.reset_button = ttk.Button(
            self.main_frame,
            text="Start New Assessment",
            command=self.reset_assessment
        )
        self.reset_button.pack(pady=10)
        self.reset_button.pack_forget()

    def setup_body_part_selection(self):
        body_part_frame = ttk.Frame(self.main_frame)
        body_part_frame.pack(pady=10)
        
        ttk.Label(
            body_part_frame,
            text="Select injured body part:",
            font=('Helvetica', 12)
        ).pack(side=tk.LEFT, padx=5)
        
        body_parts = ["Ankle", "Knee", "Shoulder", "Hip", "Back", "Wrist", "Elbow"]
        self.body_part_var = tk.StringVar()
        self.body_part_combo = ttk.Combobox(
            body_part_frame,
            textvariable=self.body_part_var,
            values=body_parts,
            width=30
        )
        self.body_part_combo.pack(side=tk.LEFT, padx=5)
        self.body_part_combo.bind('<<ComboboxSelected>>', self.on_body_part_selected)

    def on_body_part_selected(self, event=None):
        self.current_body_part = self.body_part_var.get()
        if not self.current_body_part:
            return
            
        self.responses = []
        self.questions_queue = []
        self.progress_label.config(text="Generating questions...")
        
        # Clear previous results
        self.result_text.delete(1.0, tk.END)
        self.reset_button.pack_forget()
        
        # Show next question
        self.show_next_question()

    def show_next_question(self):
        # Clear previous question
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        
        if not self.questions_queue:
            try:
                # Get new questions from AI
                self.questions_queue = self.ai_handler.generate_initial_questions(self.current_body_part)
                self.progress_label.config(text="")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate questions: {str(e)}")
                self.progress_label.config(text="Error generating questions")
                return
        
        if not self.questions_queue:
            self.analyze_responses()
            return
            
        question_data = self.questions_queue.pop(0)
        self.current_question = question_data
        
        # Display question
        question_label = ttk.Label(
            self.question_frame,
            text=question_data["question"],
            font=('Helvetica', 11),
            wraplength=500
        )
        question_label.pack(pady=10)
        
        # Create appropriate input based on question type
        if question_data["type"] == "choice":
            self.create_choice_input(question_data["options"])
        elif question_data["type"] == "scale":
            self.create_scale_input()
        else:  # text input
            self.create_text_input()

    def create_choice_input(self, options):
        choice_frame = ttk.Frame(self.question_frame)
        choice_frame.pack(pady=5)
        
        for option in options:
            btn = ttk.Button(
                choice_frame,
                text=option,
                command=lambda o=option: self.handle_response(o)
            )
            btn.pack(side=tk.LEFT, padx=5)

    def create_scale_input(self):
        scale_frame = ttk.Frame(self.question_frame)
        scale_frame.pack(pady=5)
        
        scale_var = tk.IntVar(value=5)  # Default value
        
        # Add value label
        value_label = ttk.Label(scale_frame, text="5")
        value_label.pack(side=tk.TOP)
        
        def update_value(event):
            value_label.config(text=str(scale_var.get()))
        
        scale = ttk.Scale(
            scale_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            variable=scale_var,
            length=200,
            command=update_value
        )
        scale.pack(side=tk.LEFT, padx=5)
        
        submit_btn = ttk.Button(
            scale_frame,
            text="Submit",
            command=lambda: self.handle_response(str(scale_var.get()))
        )
        submit_btn.pack(side=tk.LEFT, padx=5)

    def create_text_input(self):
        text_frame = ttk.Frame(self.question_frame)
        text_frame.pack(pady=5)
        
        text_var = tk.StringVar()
        entry = ttk.Entry(text_frame, textvariable=text_var, width=50)
        entry.pack(side=tk.LEFT, padx=5)
        
        submit_btn = ttk.Button(
            text_frame,
            text="Submit",
            command=lambda: self.handle_response(text_var.get())
        )
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to submit
        entry.bind('<Return>', lambda e: self.handle_response(text_var.get()))

    def handle_response(self, answer):
        if not answer:
            messagebox.showwarning("Warning", "Please provide an answer")
            return
            
        self.responses.append({
            "question": self.current_question["question"],
            "answer": answer,
            "type": self.current_question["type"]
        })
        
        # Show progress
        self.progress_label.config(
            text=f"Question {len(self.responses)} of 5 completed"
        )
        
        if len(self.responses) >= 5:
            self.analyze_responses()
        else:
            self.show_next_question()

   
        self.progress_label.config(text="Analyzing responses and finding specialists...")
        
        try:
            # Get injury analysis
            analysis = self.ai_handler.analyze_injury(
                self.current_body_part,
                self.responses
            )
            
            # Get doctor recommendations
            recommended_doctors = self.doctor_recommender.recommend_doctors(analysis)
            
            # Format results
            result_text = "Assessment Results:\n\n"
            for condition in analysis["possible_conditions"]:
                result_text += f"{condition['name']}:\n"
                result_text += f"Confidence: {condition['confidence']}%\n"
                result_text += f"Description: {condition['description']}\n"
                result_text += "Recommendations:\n"
                for rec in condition['recommendations']:
                    result_text += f"- {rec}\n"
                result_text += "\n"
            
            # Add doctor recommendations
            result_text += "\nRecommended Specialists:\n"
            result_text += "=" * 50 + "\n"
            
            if recommended_doctors:
                for i, doctor in enumerate(recommended_doctors, 1):
                    result_text += f"\nTop Recommendation #{i}:"
                    result_text += self.doctor_recommender.format_doctor_recommendation(doctor)
                    result_text += "-" * 40 + "\n"
            else:
                result_text += "\nNo specific specialists found for this condition. Please consult a general sports medicine physician.\n"
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_text)
            self.reset_button.pack()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze responses: {str(e)}")
        
        self.progress_label.config(text="")

    def reset_assessment(self):
        self.responses = []
        self.current_question = None
        self.questions_queue = []
        self.body_part_var.set('')
        self.result_text.delete(1.0, tk.END)
        self.reset_button.pack_forget()
        self.progress_label.config(text="")
        
        # Clear question frame
        for widget in self.question_frame.winfo_children():
            widget.destroy()

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

You must return a valid JSON object. Focus on common basketball injuries for the {body_part} area."""

        messages = [
            {"role": "system", "content": "You are a sports medicine expert specializing in basketball injuries."},
            {"role": "user", "content": prompt}
        ]

        # Debug print
        print("\n=== API Request ===")
        print("Messages:", json.dumps(messages, indent=2))

        response_text = self._make_api_call(messages)

        # Debug print
        print("\n=== API Response ===")
        print("Raw response:", response_text)

        # Extract JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end <= 0:
            print("\n=== JSON Extraction Failed ===")
            print("Could not find JSON markers in response")
            raise ValueError("No JSON found in response")

        json_str = response_text[json_start:json_end]
        
        # Debug print
        print("\n=== Extracted JSON ===")
        print("JSON string:", json_str)

        result = json.loads(json_str)
        
        # Validate result structure
        if not isinstance(result, dict) or 'possible_conditions' not in result:
            print("\n=== Invalid Result Structure ===")
            print("Result:", result)
            raise ValueError("Invalid response structure")

        return result

    except json.JSONDecodeError as e:
        print(f"\n=== JSON Decode Error ===")
        print(f"Error: {str(e)}")
        print(f"Failed text: {json_str if 'json_str' in locals() else 'No JSON string extracted'}")
        return {
            "possible_conditions": [{
                "name": "Diagnosis Error",
                "confidence": 0,
                "description": "Unable to analyze responses due to technical error",
                "recommendations": [
                    "Please consult a medical professional",
                    "If pain is severe, visit emergency care",
                    "Apply RICE (Rest, Ice, Compression, Elevation) in the meantime"
                ]
            }]
        }
    except Exception as e:
        print(f"\n=== General Error ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print(f"Full error details: {traceback.format_exc()}")
        return {
            "possible_conditions": [{
                "name": "System Error",
                "confidence": 0,
                "description": f"Error analyzing responses: {str(e)}",
                "recommendations": ["Please consult a medical professional"]
            }]
        }


    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BasketballInjuryDiagnostic()
    app.run()


#     basketball_injury_ai/
# ├── data/
# │   ├── injury_data.json
# │   ├── doctors_database.json
# │   └── exercises_database.json    <-- New file
# ├── models/
# │   └── injury_classifier.py
# ├── utils/
# │   ├── together_handler.py
# │   ├── doctor_recommender.py
# │   └── rehab_planner.py          <-- New file
# ├── main.py
# └── rehab_program.py              <-- New file