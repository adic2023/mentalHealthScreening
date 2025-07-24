import React, { useState, useEffect } from 'react';
import Chatbox from '../components/Chatbox';
import Header from '../components/Header';
import './Test.css'; 

function Test() {
  const [childCode, setChildCode] = useState('');
  const [childData, setChildData] = useState(null);
  const [userRole, setUserRole] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState('code_entry'); // 'code_entry' or 'chat'

  useEffect(() => {
    // Get user info from localStorage
    const role = localStorage.getItem('userRole');
    const email = localStorage.getItem('userEmail');
    
    if (!role || !email) {
      setError('User session expired. Please login again.');
      return;
    }
    
    setUserRole(role);
    setUserEmail(email);

    // If this is a child (student) and they have registered data, skip code entry
    if (role === 'student') {
      const storedChildId = localStorage.getItem('childId');
      const storedChildName = localStorage.getItem('childName');
      const storedChildAge = localStorage.getItem('childAge');

      if (storedChildId && storedChildName && storedChildAge) {
        setChildData({
          child_id: storedChildId,
          name: storedChildName,
          age: parseInt(storedChildAge)
        });
        setStep('chat');
      }
    }
  }, []);

  const handleChildCodeSubmit = async (e) => {
    e.preventDefault();
    
    if (!childCode.trim()) {
      setError('Please enter a child code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`http://localhost:8000/child/code/${childCode}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Invalid child code');
      }

      // Store child data and move to chat step
      setChildData({
        child_id: data.child_id,
        name: data.name,
        age: data.age,
        message: data.message
      });
      
      setStep('chat');

    } catch (err) {
      console.error('Code verification error:', err);
      setError(err.message || 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToCodeEntry = () => {
    setStep('code_entry');
    setChildData(null);
    setChildCode('');
    setError('');
  };

  // Show error state
  if (error && !userRole) {
    return (
      <div className="test-page">
        <Header showSignup={false} />
        <div className="test-container">
          <div className="error-container">
            <h2>Session Error</h2>
            <p>{error}</p>
            <button onClick={() => window.location.href = '/'}>
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show code entry form for parent/teacher
  if (step === 'code_entry' && userRole !== 'student') {
    return (
      <div className="test-page">
        <Header showSignup={false} />
        <div className="test-container">
          <div className="code-entry-container">
            <h1>SDQ Assessment - {userRole === 'parent' ? 'Parent' : 'Teacher'} Version</h1>
            <p>Please enter the child's sharing code to begin the assessment</p>
            
            {error && (
              <div className="error-message">
                <p>{error}</p>
              </div>
            )}
            
            <form onSubmit={handleChildCodeSubmit} className="code-entry-form">
              <div className="form-group">
                <label htmlFor="childCode">Child's Sharing Code:</label>
                <input
                  id="childCode"
                  type="text"
                  value={childCode}
                  onChange={(e) => setChildCode(e.target.value.toUpperCase())}
                  placeholder="Enter 8-character code"
                  maxLength="8"
                  className="code-input"
                  required
                  disabled={loading}
                />
                <small>This code was provided when the child first registered</small>
              </div>
              <button 
                type="submit" 
                className="code-submit-btn"
                disabled={loading || !childCode.trim()}
              >
                {loading ? 'Verifying...' : 'Find Child'}
              </button>
            </form>

            <div className="info-section">
              <h4>About this Assessment:</h4>
              <ul>
                <li>You'll answer questions about the child's behavior</li>
                <li>Takes approximately 5-10 minutes</li>
                <li>Your responses will be combined with others for professional review</li>
                <li>All information is confidential</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show chat interface with child data
  if (step === 'chat' && childData) {
    return (
      <div className="test-page">
        <Header showSignup={false} />
        <div className="test-header-info">
          <div className="child-info">
            <h2>Assessment for: <strong>{childData.name}</strong> (Age: {childData.age})</h2>
            <p>Respondent: <strong>{userRole === 'student' ? 'Child' : userRole.charAt(0).toUpperCase() + userRole.slice(1)}</strong></p>
            {userRole !== 'student' && (
              <button className="back-btn" onClick={handleBackToCodeEntry}>
                ← Change Child
              </button>
            )}
          </div>
        </div>
        <Chatbox 
          childData={childData}
          userRole={userRole}
          userEmail={userEmail}
        />
      </div>
    );
  }

  // Loading state
  return (
    <div className="test-page">
      <Header showSignup={false} />
      <div className="test-container">
        <div className="loading-container">
          <p>Loading...</p>
        </div>
      </div>
    </div>
  );
}

export default Test;