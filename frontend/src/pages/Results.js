import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import './Results.css';

function Results() {
  const { childId } = useParams(); // Changed from 'id' to 'childId' to match the route
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
          `http://localhost:8000/test/results/${childId}?email=${userEmail}&role=${userRole}`
        );
        if (!resultRes.ok) throw new Error('Failed to fetch user test results');
        const result = await resultRes.json();

        // Initialize result data with test results
        let resultData = {
          childName: result.child_name || 'Unknown',
          testDate: result.review_date || result.created_at?.split('T')[0] || 'N/A',
          testType: 'SDQ Screening',
          takenBy: userRole,
          psychologistName: 'Pending',
          reviewDate: 'Pending',
          scores: {},
          psychologistReview: 'Review is still pending. Please check back later.'
        };

        // Process scores from the test data structure
        if (result.user_score && result.user_score.subscale_scores) {
          const subscaleScores = result.user_score.subscale_scores;
          const maxScore = result.user_score.max_possible_score || 50;
          
          // Map the subscale scores to the expected format
          const processedScores = {};
          Object.entries(subscaleScores).forEach(([key, value]) => {
            // Determine score level based on SDQ scoring guidelines
            let level = 'normal';
            if (key === 'prosocial') {
              // For prosocial, lower scores are concerning
              if (value <= 4) level = 'abnormal';
              else if (value <= 5) level = 'borderline';
              else level = 'normal';
            } else {
              // For other subscales, higher scores are concerning
              if (value >= 7) level = 'abnormal';
              else if (value >= 6) level = 'borderline';
              else level = 'normal';
            }
            
            processedScores[key] = {
              score: value,
              maxScore: 10,
              level: level
            };
          });
          
          resultData.scores = processedScores;
        }

        // Try to fetch psychologist review (this might fail with 422)
        try {
          const reviewRes = await fetch(`http://localhost:8000/review/${childId}?email=${userEmail}&role=${userRole}`);
          if (reviewRes.ok) {
            const review = await reviewRes.json();
            // Update with review data if available
            if (review.status === "reviewed") {
              resultData.psychologistName = review?.reviewed_by || 'System';
              resultData.reviewDate = review?.submitted_at?.split('T')[0] || 'Completed';
              resultData.psychologistReview = review.psychologist_review || review.ai_generated_summary || 'Review completed but content not available.';
            }
          } else {
            console.log('Review not yet available (422 expected for pending reviews)');
          }
        } catch (reviewError) {
          console.log('Review fetch failed (expected for pending reviews):', reviewError.message);
        }

        setResultData(resultData);
      } catch (error) {
        console.error('Error fetching results:', error);
        // Set error state with minimal data
        setResultData({
          childName: 'Unknown',
          testDate: 'N/A',
          testType: 'SDQ Screening',
          takenBy: 'Unknown',
          psychologistName: 'Error',
          reviewDate: 'Error',
          scores: {},
          psychologistReview: 'Error loading results. Please try again later.'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [childId]); // Changed from 'id' to 'childId'

  const getScoreColor = (level) => {
    if (!level) return '#6b7280'; // Default color if level is undefined
    switch (level.toLowerCase()) {
      case 'normal': return '#10b981';
      case 'borderline': return '#f59e0b';
      case 'abnormal': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getScoreWidth = (score, maxScore) => {
    if (!score || !maxScore) return 0;
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

  if (!resultData) {
    return (
      <div className="results-container">
        <Header showSignup={false} />
        <div className="loading-container">
          <p>Error loading results. Please try again later.</p>
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
              {resultData.scores && Object.keys(resultData.scores).length > 0 ? (
                Object.entries(resultData.scores).map(([category, data]) => (
                  <div key={category} className="score-item">
                    <div className="score-header">
                      <span className="score-category">
                        {category === 'peer' ? 'Peer Problems' :
                         category === 'prosocial' ? 'Prosocial Behavior' :
                         category === 'emotional' ? 'Emotional Symptoms' :
                         category === 'conduct' ? 'Conduct Problems' :
                         category === 'hyperactivity' ? 'Hyperactivity' :
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
                ))
              ) : (
                <p>No score data available</p>
              )}
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