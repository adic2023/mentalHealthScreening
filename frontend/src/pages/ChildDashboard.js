// ChildDashboard.js - updated to check review completion status
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import './ParentTeacherDash.css';

function ChildDashboard() {
  const navigate = useNavigate();
  const [childDetails, setChildDetails] = useState(null);
  const [testData, setTestData] = useState(null);
  const [reviewStatus, setReviewStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const childId = localStorage.getItem('childId');
  const email = localStorage.getItem('userEmail');

  useEffect(() => {
    if (!childId || !email) {
      setError("Missing child session information.");
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        const [childRes, testRes] = await Promise.all([
          fetch(`http://localhost:8000/child/${childId}`),
          fetch(`http://localhost:8000/test/summary?email=${email}&role=child`)
        ]);

        const childJson = await childRes.json();
        const testJson = await testRes.json();

        if (!childRes.ok) throw new Error(childJson.detail || 'Failed to fetch child');
        if (!testRes.ok) throw new Error(testJson.detail || 'Failed to fetch test');

        setChildDetails(childJson);
        const matchingTest = testJson.tests?.find(t => t.child_id === childId) || null;
        setTestData(matchingTest);

        // Check review status if test exists
        if (matchingTest) {
          try {
            const reviewRes = await fetch(`http://localhost:8000/review/${childId}?email=${email}&role=child`);
            if (reviewRes.ok) {
              const reviewJson = await reviewRes.json();
              setReviewStatus(reviewJson.status);
            } else {
              // Review not completed yet
              setReviewStatus('pending');
            }
          } catch (reviewError) {
            // Review not found or not completed
            setReviewStatus('pending');
          }
        }
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [childId, email]);

  const handleButtonClick = () => {
    if (!childDetails || !childDetails.age) return;

    // Check both age and review completion
    if (childDetails.age >= 18 && reviewStatus === 'reviewed') {
      navigate(`/test-results/${childDetails.child_id}?email=${email}&role=child`);
    }
  };

  const getButtonText = () => {
    if (!testData) return 'No Test Available';
    if (childDetails.age < 18) return 'Test In Progress';
    if (reviewStatus === 'reviewed') return 'View Results';
    return 'Awaiting Review';
  };

  const isButtonEnabled = () => {
    return testData && childDetails.age >= 18 && reviewStatus === 'reviewed';
  };

  if (loading) return <div className="dashboard-container"><Header showSignup={false} /><p>Loading...</p></div>;
  if (error) return <div className="dashboard-container"><Header showSignup={false} /><p>Error: {error}</p></div>;
  if (!childDetails) return null;

  return (
    <div className="dashboard-container">
      <Header showSignup={false} />
      <div className="dashboard-body">
        <main className="dashboard-main">
          <h2>Welcome, {childDetails.name}</h2>
          <div className="review-list">
            <div className="pending-card">
              <div className="pending-card-header">
                <h3>{childDetails.name}</h3>
                {testData && (
                  <span className={`pending-status ${reviewStatus === 'completed' ? 'completed' : 'pending'}`}>
                    {reviewStatus === 'completed' ? 'Review Completed' : 'Review Pending'}
                  </span>
                )}
              </div>
              <p>Age: {childDetails.age}</p>
              <p>Gender: {childDetails.gender}</p>
              <p><strong>Sharing Code:</strong> {childDetails.code}</p>
              {testData && (
                <button 
                  className={`review-btn ${isButtonEnabled() ? 'completed' : 'pending'}`} 
                  disabled={!isButtonEnabled()} 
                  onClick={handleButtonClick}
                >
                  {getButtonText()}
                </button>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default ChildDashboard;