import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Header from '../components/Header';
import { Sidebar, Menu, MenuItem } from 'react-pro-sidebar';
import './PsychDash.css';

function PsychDash() {
  const [reviews, setReviews] = useState([]);
  const [view, setView] = useState("pending");
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;
  const navigate = useNavigate();

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const endpoint =
          view === "pending"
            ? "http://localhost:8000/reviews/pending"
            : "http://localhost:8000/reviews/completed";

        const response = await fetch(endpoint);
        const data = await response.json();

        const withScores = await Promise.all(
          data.map(async (item, index) => {
            let score = null;

            if (view === "pending") {
              try {
                const res = await fetch(`http://localhost:8000/score/by-child/${item.child_id}`);
                const result = await res.json();
                score = result.total_score;
              } catch (err) {
                console.error("Error fetching score for", item.child_id);
              }
            }

            return {
              id: item.child_id || index + 1,
              name: item.name || `Child ${index + 1}`,
              date: item.date || 'Unknown',
              screeningType: 'SDQ',
              status: view,
              score,
            };
          })
        );

        setReviews(withScores);
      } catch (error) {
        console.error("Failed to fetch reviews:", error);
      }
    };

    fetchReviews();
  }, [view]);

  const getScoreColor = (score) => {
    if (score == null || view !== "pending") return '';
    if (score <= 15) return 'low-score';    // red
    if (score <= 25) return 'medium-score'; // orange
    return 'high-score';                    // green
  };

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = reviews.slice(indexOfFirstItem, indexOfLastItem);

  const filteredItems = currentItems.filter((review) =>
    review.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    review.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(reviews.length / itemsPerPage);

  const handleSubmit = (id) => {
    navigate(`/review/${id}`);
  };

  return (
    <div className="dashboard-container">
      <Header showSignup={false} />
      <div className="dashboard-body">
        <Sidebar>
          <Menu>
            <Link to="/screeningTest"><MenuItem> Test Interface </MenuItem></Link>
            <MenuItem><a href="https://www.sdqinfo.org/a0.html">SDQ Information</a></MenuItem>
          </Menu>
        </Sidebar>

        <main className="dashboard-main">
          <div className="tab-toggle">
            <button
              className={view === "pending" ? "active-tab" : ""}
              onClick={() => setView("pending")}
            >
              Pending
            </button>
            <button
              className={view === "completed" ? "active-tab" : ""}
              onClick={() => setView("completed")}
            >
              Completed
            </button>
          </div>

          <h2>{view === "pending" ? "Pending Reports" : "Completed Reviews"}</h2>
          <h4>({indexOfFirstItem + 1}–{Math.min(indexOfLastItem, reviews.length)})</h4>

          <input
            type="text"
            placeholder="Search by name or child ID"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-bar"
          />

          <div className="review-list">
            {filteredItems.map((review) => (
              <div
                className={`pending-card ${getScoreColor(review.score)}`}
                key={review.id}
              >
                <div className="pending-card-header">
                  <h3>{review.name}</h3>
                  <span className="pending-status">{review.status}</span>
                </div>
                <p>Date: {review.date}</p>
                <p>Type: {review.screeningType}</p>
                {view === "pending" && review.score != null && (
                  <p className="score-label">Score: {review.score}</p>
                )}
                <button className="review-btn" onClick={() => handleSubmit(review.id)}>
                  {view === "pending" ? "Review" : "View"}
                </button>
              </div>
            ))}
          </div>

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
        </main>
      </div>
    </div>
  );
}

export default PsychDash;
