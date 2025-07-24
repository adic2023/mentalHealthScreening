import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import './ChildRegistration.css';

function ChildRegistration() {
  const [isFirstTime, setIsFirstTime] = useState(true);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [registrationComplete, setRegistrationComplete] = useState(false);
  const [childData, setChildData] = useState(null);
  
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/child/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          age: parseInt(age),
          gender,
          first_time: isFirstTime,
          code: isFirstTime ? null : code
        })
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.detail || 'Registration failed');
        return;
      }

      // Store child data for the test
      setChildData(data);
      localStorage.setItem('childId', data.child_id);
      localStorage.setItem('childName', data.name);
      localStorage.setItem('childAge', data.age.toString());

      if (isFirstTime) {
        // Show the sharing code
        setRegistrationComplete(true);
      } else {
        // Returning user - go directly to test
        navigate('/ScreeningTest');
      }

    } catch (err) {
      console.error(err);
      alert('Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleStartTest = () => {
    navigate('/ScreeningTest');
  };

  if (registrationComplete && childData) {
    return (
      <div className="child-registration-container">
        <Header showSignup={false} />
        <div className="registration-success">
          <div className="success-card">
            <h2>Registration Successful!</h2>
            <p>Hi {childData.name}! You've been registered successfully.</p>
            
            <div className="sharing-code-section">
              <h3>Your Sharing Code:</h3>
              <div className="code-display">
                <span className="sharing-code">{childData.code}</span>
              </div>
              <p className="code-instructions">
                {childData.instructions}
              </p>
            </div>

            <div className="next-steps">
              <h4>What happens next?</h4>
              <ol>
                <li>You'll take the assessment about yourself</li>
                <li>Your parent and teacher will use code <strong>{childData.code}</strong> to take assessments about you</li>
                <li>Once everyone completes their assessments, a psychologist will review the results</li>
                <li>You'll receive detailed feedback and recommendations</li>
              </ol>
            </div>

            <button className="start-test-btn" onClick={handleStartTest}>
              Start My Assessment
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="child-registration-container">
      <Header showSignup={false} />
      <div className="registration-form-container">
        <div className="registration-card">
          <h2>Child Registration</h2>
          
          <div className="toggle-section">
            <p>Are you taking the assessment for the first time?</p>
            <div className="toggle-buttons">
              <button 
                className={isFirstTime ? 'toggle-btn active' : 'toggle-btn'}
                onClick={() => setIsFirstTime(true)}
              >
                First Time
              </button>
              <button 
                className={!isFirstTime ? 'toggle-btn active' : 'toggle-btn'}
                onClick={() => setIsFirstTime(false)}
              >
                Returning User
              </button>
            </div>
          </div>

          <form onSubmit={handleRegister} className="registration-form">
            {isFirstTime ? (
              <>
                <div className="form-group">
                  <label htmlFor="name">Child's Name:</label>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter child's full name"
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="age">Age:</label>
                  <input
                    id="age"
                    type="number"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    placeholder="Enter age (4-17)"
                    min="4"
                    max="17"
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="gender">Gender:</label>
                  <select
                    id="gender"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    required
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </>
            ) : (
              <div className="form-group">
                <label htmlFor="code">Enter your sharing code:</label>
                <input
                  id="code"
                  type="text"
                  value={code}
                  onChange={(e) => setCode(e.target.value.toUpperCase())}
                  placeholder="Enter 8-character code"
                  maxLength="8"
                  required
                />
                <small>This is the code you received when you first registered</small>
              </div>
            )}

            <button type="submit" className="register-btn" disabled={loading}>
              {loading ? 'Processing...' : isFirstTime ? 'Register' : 'Continue'}
            </button>
          </form>

          <div className="info-section">
            <h4>About the SDQ Assessment:</h4>
            <ul>
              <li>25 questions about behavior and emotions</li>
              <li>Takes 5-10 minutes to complete</li>
              <li>Completely confidential</li>
              <li>Results reviewed by qualified professionals</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChildRegistration;