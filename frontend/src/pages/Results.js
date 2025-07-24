import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import './Results.css';

function Results() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [resultData, setResultData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call to fetch results
    setTimeout(() => {
      const mockResultData = {
        id: id,
        childName: `Child ${String.fromCharCode(65 + parseInt(id.split('-')[1]) - 1)}`,
        testDate: '2025-07-15',
        testType: 'SDQ Screening',
        takenBy: localStorage.getItem('userRole') || 'Parent',
        psychologistName: 'Dr. Sarah Johnson',
        reviewDate: '2025-07-18',
        overallAssessment: 'Normal',
        scores: {
          emotional: { score: 3, level: 'Normal', maxScore: 10 },
          conduct: { score: 2, level: 'Normal', maxScore: 10 },
          hyperactivity: { score: 6, level: 'Borderline', maxScore: 10 },
          peerProblems: { score: 1, level: 'Normal', maxScore: 10 },
          prosocial: { score: 8, level: 'Normal', maxScore: 10 }
        },
        psychologistReview: `Based on the SDQ screening results, ${resultData?.childName || 'the child'} shows overall normal behavioral patterns with some borderline concerns in hyperactivity/inattention. 

The emotional symptoms score of 3 is within the normal range, indicating good emotional regulation. The conduct problems score of 2 suggests minimal behavioral issues.

However, the hyperactivity/inattention score of 6 falls in the borderline range, which may warrant some attention. This could manifest as difficulty concentrating, restlessness, or impulsive behavior.

The peer relationship score of 1 is excellent, showing strong social skills and positive interactions with peers. The prosocial behavior score of 8 is also very good, indicating kindness, helpfulness, and consideration for others.

Recommendations:
1. Monitor the child's attention and activity levels in different settings
2. Provide structured activities that can help channel energy positively
3. Consider consultation with a pediatrician if hyperactivity symptoms persist
4. Continue to encourage the child's strong prosocial behaviors
5. Maintain open communication about any concerns

Overall, the child demonstrates good social and emotional development with minor areas for attention. Regular monitoring and supportive strategies should be sufficient at this time.`
      };
      setResultData(mockResultData);
      setLoading(false);
    }, 1000);
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
          {/* Child Information Card */}
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
            <h2>Assessment Scores</h2>
            <div className="scores-grid">
              {Object.entries(resultData.scores).map(([category, data]) => (
                <div key={category} className="score-item">
                  <div className="score-header">
                    <span className="score-category">
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                      {category === 'peerProblems' && ' Problems'}
                      {category === 'prosocial' && ' Behavior'}
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
              {resultData.psychologistReview.split('\n\n').map((paragraph, index) => (
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