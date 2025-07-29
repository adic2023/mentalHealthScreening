import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import './Results.css';

function Results() {
  const { id } = useParams(); // id = child_id
  const navigate = useNavigate();
  const [resultData, setResultData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userEmail = localStorage.getItem('userEmail');
        const userRole = localStorage.getItem('userRole');

        // Fetch user's own test scores
        const resultRes = await fetch(
          `http://localhost:8000/test/results/${id}?email=${userEmail}&role=${userRole}`
        );
        if (!resultRes.ok) throw new Error('Failed to fetch user test results');
        const result = await resultRes.json();

        // Fetch psychologist review
        const reviewRes = await fetch(`http://localhost:8000/review/${id}`);
        if (!reviewRes.ok) throw new Error('Failed to fetch psychologist review');
        const review = await reviewRes.json();

        setResultData({
          childName: result.child_name,
          testDate: result.review_date || 'N/A',
          testType: 'SDQ Screening',
          takenBy: userRole,
          psychologistName: review?.reviewed_by || 'Pending',
          reviewDate: review?.reviewed_at?.split('T')[0] || 'Pending',
          scores: result.user_score || {},
          psychologistReview: review.psychologist_review || review.ai_summary || 'Pending'
        });
      } catch (error) {
        console.error('Error fetching results:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const getScoreColor = (level) => {
    switch (level.toLowerCase()) {
      case 'normal': return '#10b981';
      case 'borderline': return '#f59e0b';
      case 'abnormal': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getScoreWidth = (score, maxScore) => {
    return (score / maxScore) * 100;
  };

  if (loading) {
    return (
      <div className="results-container">
        <Header showSignup={false} />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading results...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="results-container">
      <Header showSignup={false} />
      <main className="results-main">
        <div className="results-header">
          <button 
            className="back-btn"
            onClick={() => navigate('/ParentTeacherDashboard')}
          >
            ← Back to Dashboard
          </button>
          <h1>Assessment Results</h1>
        </div>

        <div className="results-content">
          {/* Info Card */}
          <div className="info-card">
            <h2>Assessment Information</h2>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Child Name:</span>
                <span className="info-value">{resultData.childName}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Test Date:</span>
                <span className="info-value">{resultData.testDate}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Test Type:</span>
                <span className="info-value">{resultData.testType}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Taken By:</span>
                <span className="info-value">{resultData.takenBy}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Reviewed By:</span>
                <span className="info-value">{resultData.psychologistName}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Review Date:</span>
                <span className="info-value">{resultData.reviewDate}</span>
              </div>
            </div>
          </div>

          {/* Scores Card */}
          <div className="scores-card">
            <h2>Your Assessment Scores</h2>
            <div className="scores-grid">
              {Object.entries(resultData.scores).map(([category, data]) => (
                <div key={category} className="score-item">
                  <div className="score-header">
                    <span className="score-category">
                      {category === 'peerProblems' ? 'Peer Problems' :
                       category === 'prosocial' ? 'Prosocial Behavior' :
                       category.charAt(0).toUpperCase() + category.slice(1)}
                    </span>
                    <span 
                      className="score-level"
                      style={{ color: getScoreColor(data.level) }}
                    >
                      {data.level}
                    </span>
                  </div>
                  <div className="score-bar-container">
                    <div 
                      className="score-bar"
                      style={{ 
                        width: `${getScoreWidth(data.score, data.maxScore)}%`,
                        backgroundColor: getScoreColor(data.level)
                      }}
                    ></div>
                  </div>
                  <div className="score-numbers">
                    <span>{data.score}/{data.maxScore}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Psychologist Review Card */}
          <div className="review-card">
            <h2>Psychologist Review & Recommendations</h2>
            <div className="review-content">
              {resultData.psychologistReview.split('\n').map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Results;
