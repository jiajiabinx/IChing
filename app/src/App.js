import React, { useState } from 'react';
import { ArrowRight, ArrowLeft, Upload } from 'lucide-react';
import axios from 'axios';

const questions = [
  { id: 'dob', question: "What's your date of birth?", type: 'date' },
  { id: 'pronouns', question: "What are your pronouns?", type: 'text' },
  { id: 'education', question: "What's your highest educational level?", type: 'select', options: ['High School', 'Bachelor', 'Master', 'PhD', 'Other'] },
  { id: 'institutions', question: "What are the educational institutions that you have attended?", type: 'textarea' },
  { id: 'parents_professions', question: "What are/were your parents' professions?", type: 'textarea' },
  { id: 'additional_info', question: "Other information that can help us learn more about you? Maybe a resume?", type: 'file' }
];

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});
  const [file, setFile] = useState(null);

  const handleInputChange = (e) => {
    const { id, value } = e.target;
    setFormData({ ...formData, [id]: value });
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    const data = new FormData();
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    if (file) {
      data.append('file', file);
    }

    try {
      const response = await axios.post('/api/submit_form', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      console.log(response.data);
      alert('Form submitted successfully!');
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Error submitting form. Please try again.');
    }
  };

  const currentQuestion = questions[currentStep];

  const renderInput = () => {
    switch (currentQuestion.type) {
      case 'date':
        return <input type="date" id={currentQuestion.id} onChange={handleInputChange} className="w-full p-2 border rounded text-center" />;
      case 'select':
        return (
          <select id={currentQuestion.id} onChange={handleInputChange} className="w-full p-2 border rounded text-center">
            <option value="">Select an option</option>
            {currentQuestion.options.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        );
      case 'textarea':
        return <textarea id={currentQuestion.id} onChange={handleInputChange} className="w-full p-2 border rounded text-center" rows="4" />;
      case 'file':
        return (
          <div className="flex items-center justify-center w-full">
            <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="w-10 h-10 mb-3 text-gray-400" />
                <p className="mb-2 text-sm text-gray-500 text-center"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                <p className="text-xs text-gray-500 text-center">PDF, DOC, DOCX (MAX. 10MB)</p>
              </div>
              <input id="dropzone-file" type="file" className="hidden" onChange={handleFileChange} />
            </label>
          </div>
        );
      default:
        return <input type="text" id={currentQuestion.id} onChange={handleInputChange} className="w-full p-2 border rounded text-center" />;
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-10 p-6 bg-white rounded-lg shadow-xl text-center">
      <h1 className="text-2xl font-bold mb-4 text-gray-800">Questionnaire</h1>
      <div className="mb-6">
        <h2 className="text-xl mb-2">{currentQuestion.question}</h2>
        {renderInput()}
      </div>
      <div className="flex justify-center space-x-4">
        <button 
          onClick={() => setCurrentStep(Math.max(0, currentStep - 1))} 
          disabled={currentStep === 0}
          className="p-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 disabled:opacity-50"
        >
          <ArrowLeft size={24} />
        </button>
        {currentStep < questions.length - 1 ? (
          <button 
            onClick={() => setCurrentStep(Math.min(questions.length - 1, currentStep + 1))}
            className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            <ArrowRight size={24} />
          </button>
        ) : (
          <button 
            onClick={handleSubmit}
            className="p-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Submit
          </button>
        )}
      </div>
    </div>
  );
}

export default App;