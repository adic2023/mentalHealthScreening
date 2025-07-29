import React, { useState, useEffect } from 'react';
import Chatbox from '../components/Chatbox';
import Header from '../components/Header';
import './Test.css';

function Test() {
  const [childData, setChildData] = useState(null);
  const [userRole, setUserRole] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const role = localStorage.getItem('userRole');
    const email = localStorage.getItem('userEmail');
    const childId = localStorage.getItem('childId');
    const childName = localStorage.getItem('childName');
    const childAge = localStorage.getItem('childAge');

    if (!role || !email) {
      setError('User session expired. Please login again.');
      setLoading(false);
      return;
    }

    setUserRole(role);
    setUserEmail(email);

    if (childId && childName && childAge) {
      setChildData({
        child_id: childId,
        name: childName,
        age: parseInt(childAge)
      });
    } else {
      setError('No child information found. Please register a child first.');
    }

    setLoading(false);
  }, []);

  if (loading) {
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

  if (error) {
    return (
      <div className="test-page">
        <Header showSignup={false} />
        <div className="test-container">
          <div className="error-container">
            <h2>Error</h2>
            <p>{error}</p>
            <button onClick={() => window.location.href = '/register-child'}>
              Go to Registration
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="test-page">
      <Header showSignup={false} />
      <div className="test-header-info">
        <div className="child-info">
          <h2>Assessment for: <strong>{childData.name}</strong> (Age: {childData.age})</h2>
          <p>Respondent: <strong>{userRole === 'student' ? 'Child' : userRole.charAt(0).toUpperCase() + userRole.slice(1)}</strong></p>
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

export default Test;
