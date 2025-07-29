// ParentTeacherDash.js
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { Sidebar, Menu, MenuItem, SubMenu } from 'react-pro-sidebar';
import './ParentTeacherDash.css';

function ParentTeacherDash() {
  const [userTests, setUserTests] = useState([]);
  const [isFirstTime, setIsFirstTime] = useState(false);
  const [userType, setUserType] = useState('parent');
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const itemsPerPage = 12;

  const navigate = useNavigate();

  useEffect(() => {
    const role = localStorage.getItem('userRole') || 'parent';
    const email = localStorage.getItem('userEmail');
    setUserType(role);

    if (!email) {
      setError("User email not found. Please login again.");
      setLoading(false);
      return;
    }

    fetch(`http://localhost:8000/test/summary?email=${email}&role=${role}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json();
      })
      .then(async data => {
        if (data.status === "not_started") {
          setIsFirstTime(true);
          setUserTests([]);
        } else {
          setIsFirstTime(false);

          const enrichedTests = await Promise.all(
            data.tests.map(async (test) => {
              try {
                const res = await fetch(`http://localhost:8000/child/${test.child_id}`);
                const child = await res.json();
                return {
                  ...test,
                  childName: child.name || 'Unknown',
                  code: child.code || 'N/A',
                  date: test.date
                    ? new Date(test.date).toISOString().split('T')[0]
                    : new Date().toISOString().split('T')[0],
                  testType: test.test_type || 'SDQ',
                };
              } catch (err) {
                console.error('Error fetching child info for test:', test.test_id);
                return {
                  ...test,
                  childName: 'Unknown',
                  code: 'N/A',
                  date: test.date
                    ? new Date(test.date).toISOString().split('T')[0]
                    : new Date().toISOString().split('T')[0],
                  testType: test.test_type || 'SDQ',
                };
              }
            })
          );

          setUserTests(enrichedTests);
        }

        setLoading(false);
      })
      .catch(err => {
        console.error("Error loading dashboard:", err);
        setError("Failed to load dashboard data. Please try again.");
        setLoading(false);
      });
  }, []);

  const handleTakeNewTest = () => navigate('/ChildRegistration');

  const handleViewResults = (childId, status) => {
    console.log('handleViewResults called with:', { childId, status });
    // Fixed: Check for the correct status value
    if (status === "Review Completed") {
      console.log('Navigating to results for child:', childId);
      navigate(`/test-results/${childId}`);
    }
  };

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = userTests.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(userTests.length / itemsPerPage);

  return (
    <div className="dashboard-container">
      <Header showSignup={false} />
      <div className="dashboard-body">
        <Sidebar>
          <Menu>
            <MenuItem>
              <button
                onClick={handleTakeNewTest}
                style={{
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  width: '100%',
                  fontWeight: '600'
                }}
              >
                📝 Take New Test
              </button>
            </MenuItem>
            <SubMenu label="View Test History" />
            <MenuItem component={<a href="https://www.sdqinfo.org/a0.html" target="_blank" rel="noopener noreferrer" />}>
              SDQ Information
            </MenuItem>
            <MenuItem>Contact Support</MenuItem>
          </Menu>
        </Sidebar>

        <main className="dashboard-main">
          {isFirstTime ? (
            <div className="first-time-container">
              <div className="first-time-card">
                <h2>Welcome, {userType === 'parent' ? 'Parent' : 'Teacher'}!</h2>
                <p>Help us understand the child's mental health better by taking your first assessment.</p>
                <div className="info-section">
                  <h3>About the SDQ Assessment:</h3>
                  <ul>
                    <li>25 simple questions about the child's behavior</li>
                    <li>Takes approximately 5-10 minutes to complete</li>
                    <li>Results reviewed by qualified psychologists</li>
                    <li>Detailed feedback and recommendations provided</li>
                  </ul>
                </div>
                <button className="take-new-test-btn" onClick={handleTakeNewTest}>
                  Take New Test
                </button>
              </div>
            </div>
          ) : (
            <>
              <h2>Your Test History</h2>
              <h4>({indexOfFirstItem + 1}–{Math.min(indexOfLastItem, userTests.length)} of {userTests.length})</h4>
              <div className="review-list">
                {currentItems.map((test) => {
                  console.log('Test data:', test); 
                  return(
                  <div className="pending-card" key={test.test_id}>
                    <div className="pending-card-header">
                      <h3>{test.childName}</h3>
                      <span className={`pending-status ${test.status === 'Review Completed' ? 'reviewed' : test.status === 'Review Pending' ? 'pending' : ''}`}>
                        {test.status}
                      </span>
                    </div>
                    <p>Date: {test.date}</p>
                    <p>Type: {test.testType}</p>
                    <p><strong>Sharing Code:</strong> {test.code}</p>
                    {test.status === 'Review Completed' ? (
                      <button
                        className="review-btn completed"
                        onClick={() => handleViewResults(test.child_id, test.status)}
                      >
                        View Results
                      </button>

                    ) : (
                      <button className="review-btn pending" disabled>
                        {test.status === 'In Progress' ? 'Test In Progress' : test.status === 'Review Pending' ? 'Awaiting Review' : test.status === 'Submitted - Waiting for Others' ? 'Waiting for Others' : 'Pending'}
                      </button>
                    )}
                  </div>
                );
              })}
              </div>

              <div className="review-list" style={{ marginTop: '2rem' }}>
                <div className="pending-card add-new-card">
                  <div className="add-new-content">
                    <h3>Take New Assessment</h3>
                    <p>Start a new SDQ screening for a child</p>
                    <button className="review-btn new-test" onClick={handleTakeNewTest}>
                      + New Test
                    </button>
                  </div>
                </div>
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  {Array.from({ length: totalPages }, (_, i) => (
                    <button
                      key={i}
                      onClick={() => setCurrentPage(i + 1)}
                      className={currentPage === i + 1 ? 'active-page' : ''}
                    >
                      {i + 1}
                    </button>
                  ))}
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default ParentTeacherDash;