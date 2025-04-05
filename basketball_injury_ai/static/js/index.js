window.onload = function () {
    // Get all SVG elements and convert to Array
    const pieces = Array.from(document.getElementsByTagName('svg'));
    
    // Add click handlers
    pieces.forEach(piece => {
        piece.onclick = function(event) {
            // Get the clicked position from either the target or its parent
            const position = event.target.getAttribute('data-position') || 
                           event.target.parentElement.getAttribute('data-position');
            
            if (position) {
                // Log the clicked body part
                console.log('Clicked body part:', position);
                
                // Visual feedback
                pieces.forEach(p => {
                    p.style.fill = '#57c9d5'; // Reset all to default color
                });
                piece.style.fill = '#ff7d16'; // Highlight clicked part

                // Send request to backend to get questions
                fetch('/get_questions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        body_part: position
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.questions && Array.isArray(data.questions)) {
                        displayQuestions(data.questions, position);
                    } else {
                        throw new Error('Invalid questions data');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Display error message to user
                    alert('Error loading questions. Please try again.');
                });
            }
        }
    });

    function displayQuestions(questions, bodyPart) {
        const formContainer = document.getElementById('form-container');
        
        if (!formContainer) {
            console.error('Form container not found!');
            return;
        }

        formContainer.innerHTML = `
            <div class="card mt-4">
                <div class="card-header">
                    <h3>Assessment for ${bodyPart}</h3>
                </div>
                <div class="card-body">
                    <form id="assessment-form">
                        ${questions.map((question, index) => generateQuestionHTML(question, index)).join('')}
                        <button type="submit" class="btn btn-primary mt-4">Submit Assessment</button>
                    </form>
                </div>
            </div>
        `;

        // Initialize special inputs
        questions.forEach((question, index) => {
            if (question.type === 'scale') {
                const slider = document.getElementById(`q${index}-slider`);
                const output = document.getElementById(`q${index}-value`);
                if (slider && output) {
                    output.innerHTML = slider.value;
                    slider.oninput = function() {
                        output.innerHTML = this.value;
                    }
                }
            }
        });

        // Add submit handler
        document.getElementById('assessment-form').onsubmit = function(e) {
            e.preventDefault();
            
            // Collect responses
            const responses = questions.map((question, index) => {
                let answer;
                
                switch (question.type) {
                    case 'choice':
                        const radio = document.querySelector(`input[name="q${index}"]:checked`);
                        answer = radio ? radio.value : null;
                        break;
                    
                    case 'multiple':
                        const checkboxes = document.querySelectorAll(`input[name="q${index}"]:checked`);
                        answer = Array.from(checkboxes).map(cb => cb.value).join(', ');
                        break;
                    
                    case 'scale':
                        answer = document.getElementById(`q${index}-slider`).value;
                        break;
                    
                    case 'text':
                        answer = document.getElementById(`q${index}-text`).value;
                        break;
                    
                    default:
                        answer = null;
                }

                return {
                    question: question.question,
                    answer: answer || 'No response',
                    type: question.type,
                    body_part: bodyPart
                };
            });

            // Send responses to backend
            fetch('/analyze_responses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    responses: responses
                })
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data, formContainer);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error analyzing responses. Please try again.');
            });
        };
    }

    function generateQuestionHTML(question, index) {
        switch (question.type) {
            case 'choice':
                return `
                    <div class="form-group question-group">
                        <label class="font-weight-bold mb-3">${question.question}</label>
                        <div class="btn-group-vertical w-100">
                            ${question.options.map(option => `
                                <label class="btn btn-outline-primary mb-2">
                                    <input type="radio" name="q${index}" value="${option}" required> ${option}
                                </label>
                            `).join('')}
                        </div>
                    </div>
                `;

            case 'multiple':
                return `
                    <div class="form-group question-group">
                        <label class="font-weight-bold mb-3">${question.question}</label>
                        <div class="checkbox-group">
                            ${question.options.map(option => `
                                <div class="custom-control custom-checkbox mb-2">
                                    <input type="checkbox" class="custom-control-input" id="q${index}-${option}" name="q${index}" value="${option}">
                                    <label class="custom-control-label" for="q${index}-${option}">${option}</label>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;

            case 'scale':
                return `
                    <div class="form-group question-group">
                        <label class="font-weight-bold mb-3">${question.question}</label>
                        <div class="range-container">
                            <input type="range" class="custom-range" id="q${index}-slider" 
                                   min="1" max="10" step="1" value="5" required>
                            <div class="range-labels d-flex justify-content-between">
                                <span>1</span>
                                <span>2</span>
                                <span>3</span>
                                <span>4</span>
                                <span>5</span>
                                <span>6</span>
                                <span>7</span>
                                <span>8</span>
                                <span>9</span>
                                <span>10</span>
                            </div>
                            <div class="text-center mt-2">
                                Selected value: <span id="q${index}-value" class="font-weight-bold">5</span>
                            </div>
                        </div>
                    </div>
                `;

            case 'text':
                return `
                    <div class="form-group question-group">
                        <label class="font-weight-bold mb-3">${question.question}</label>
                        <textarea class="form-control" id="q${index}-text" rows="3" required></textarea>
                    </div>
                `;

            default:
                return `
                    <div class="form-group question-group">
                        <label class="font-weight-bold mb-3">${question.question}</label>
                        <input type="text" class="form-control" id="q${index}-text" required>
                    </div>
                `;
        }
    }

    function displayResults(data, container) {
        container.innerHTML = `
            <div class="card mt-4">
                <div class="card-header">
                    <h3>Assessment Results</h3>
                </div>
                <div class="card-body">
                    <div class="diagnosis">
                        <h4>Diagnosis:</h4>
                        <p>${data.diagnosis}</p>
                    </div>
                    <div class="recommendations mt-4">
                        <h4>Recommended Doctors:</h4>
                        <ul class="list-unstyled">
                            ${data.doctors.map(doctor => `
                                <li class="border-bottom py-2">
                                    <strong>${doctor.name}</strong> - ${doctor.specialty}<br>
                                    <small>Location: ${doctor.location}<br>
                                    Contact: ${doctor.contact}</small>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    <button onclick="window.location.reload()" class="btn btn-primary mt-3">
                        Start New Assessment
                    </button>
                </div>
            </div>
        `;
    }
};