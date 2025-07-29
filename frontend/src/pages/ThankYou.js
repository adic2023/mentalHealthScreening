import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import './ThankYou.css';

function ThankYou() {
  const [userRole, setUserRole] = useState('');
  const [childName, setChildName] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Get user data from localStorage
    const role = localStorage.getItem('userRole');
    const name = localStorage.getItem('childName');
    
    if (!role) {
      // If no role found, redirect to home
      navigate('/');
      return;
    }

    setUserRole(role);
    setChildName(name || 'the child');
    setLoading(false);

    // Auto-redirect after 30 seconds
    const timer = setTimeout(() => {
      handleRedirectToDashboard();
    }, 30000);

    return () => clearTimeout(timer);
  }, [navigate]);

  const handleRedirectToDashboard = () => {
    switch (userRole) {
      case 'student':
        navigate('/ChildDashboard');
        break;
      case 'parent':
      case 'teacher':
        navigate('/ParentTeacherDashboard');
        break;
      case 'psychologist':
        navigate('/PsychDashboard');
        break;
      default:
        navigate('/');
    }
  };

  const getDashboardButtonText = () => {
    switch (userRole) {
      case 'student':
        return 'Go to My Dashboard';
      case 'parent':
        return 'Go to Parent Dashboard';
      case 'teacher':
        return 'Go to Teacher Dashboard';
      case 'psychologist':
        return 'Go to Psychologist Dashboard';
      default:
        return 'Go to Dashboard';
    }
  };

  const getPersonalizedMessage = () => {
    switch (userRole) {
      case 'student':
        return {
          title: "Great Job! 🌟",
          subtitle: "You've completed the assessment!",
          description: "Thank you for taking the time to answer all the questions honestly. Your responses will help us better understand how you're doing."
        };
      case 'parent':
        return {
          title: "Thank You! 👨‍👩‍👧‍👦",
          subtitle: `Assessment for ${childName} completed!`,
          description: "Thank you for providing valuable insights about your child's behavior and well-being. Your input is crucial for a comprehensive assessment."
        };
      case 'teacher':
        return {
          title: "Thank You! 🍎",
          subtitle: `Assessment for ${childName} completed!`,
          description: "Thank you for sharing your observations about this student's behavior in the classroom setting. Your professional insights are invaluable."
        };
      default:
        return {
          title: "Thank You!",
          subtitle: "Assessment completed!",
          description: "Thank you for completing the assessment."
        };
    }
  };

  if (loading) {
    return (
      <div className="thank-you-page">
        <Header showSignup={false} />
        <div className="thank-you-container">
          <div className="loading-spinner">Loading...</div>
        </div>
      </div>
    );
  }

  const message = getPersonalizedMessage();

  return (
    <div className="thank-you-page">
      <Header showSignup={false} />
      
      <div className="thank-you-container">
        <div className="thank-you-card">
          {/* Success Icon */}
          <div className="success-icon">
            <div className="checkmark">
              <div className="checkmark-circle">
                <div className="checkmark-stem"></div>
                <div className="checkmark-kick"></div>
              </div>
            </div>
          </div>

          {/* Main Message */}
          <div className="thank-you-content">
            <h1 className="thank-you-title">{message.title}</h1>
            <h2 className="thank-you-subtitle">{message.subtitle}</h2>
            <p className="thank-you-description">{message.description}</p>
          </div>

          {/* Review Timeline */}
          <div className="review-timeline">
            <div className="timeline-icon">⏰</div>
            <div className="timeline-content">
              <h3>What Happens Next?</h3>
              <p>
                Your responses have been successfully submitted and will be reviewed by our qualified psychologists. 
                The comprehensive review will be ready in <strong>2-5 business days</strong>.
              </p>
              <div className="timeline-steps">
                <div className="step completed">
                  <span className="step-number">1</span>
                  <span className="step-text">Assessment Completed ✓</span>
                </div>
                <div className="step current">
                  <span className="step-number">2</span>
                  <span className="step-text">Professional Review (2-5 days)</span>
                </div>
                <div className="step pending">
                  <span className="step-number">3</span>
                  <span className="step-text">Results Available</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="thank-you-actions">
            <button 
              className="dashboard-btn primary"
              onClick={handleRedirectToDashboard}
            >
              {getDashboardButtonText()}
            </button>
            
            <button 
              className="dashboard-btn secondary"
              onClick={() => navigate('/')}
            >
              Return to Home
            </button>
          </div>

          {/* Additional Info */}
          <div className="additional-info">
            <div className="info-box">
              <h4>📧 Email Notification</h4>
              <p>You'll receive an email notification once the review is complete and results are available.</p>
            </div>
            
            <div className="info-box">
              <h4>🔒 Privacy & Security</h4>
              <p>All responses are confidential and will only be accessed by qualified professionals.</p>
            </div>
          </div>

          {/* Auto-redirect notice */}
          <div className="auto-redirect-notice">
            <small>You'll be automatically redirected to your dashboard in 30 seconds</small>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ThankYou;