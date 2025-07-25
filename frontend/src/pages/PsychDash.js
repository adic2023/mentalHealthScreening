import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link } from "react-router-dom";
import Header from '../components/Header';
import { Sidebar, Menu, MenuItem, SubMenu } from 'react-pro-sidebar';
import './PsychDash.css';

function PsychDash() {
  const [pendingReviews, setPendingReviews] = useState([]);

  useEffect(() => {
    const data = Array.from({ length: 30 }).map((_, i) => ({
      id: `${i + 1}`,
      name: `Student ${String.fromCharCode(65 + i)}`,
      date: `2025-07-${(20 + i).toString().padStart(2, '0')}`,
      screeningType: 'SDQ',
      status: 'Awaiting Review',
    }));
    setPendingReviews(data);
  }, []);

  const navigate = useNavigate();
  const handleSubmit = (id) => {
    navigate(`/review/${id}`);
  };

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = pendingReviews.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(pendingReviews.length / itemsPerPage);

  return (
    <div className="dashboard-container">
      <Header showSignup={false} />
      <div className="dashboard-body">
        <Sidebar>
          <Menu>
            <SubMenu label="View Reviewed Reports">
            </SubMenu>
            <Link to="/screeningTest"><MenuItem> Test Interface </MenuItem></Link>
            <MenuItem><a href="https://www.sdqinfo.org/a0.html">SDQ Information</a></MenuItem>
          </Menu>
        </Sidebar>

        <main className="dashboard-main">
          <h2>Pending Reports</h2>
        <h4>({indexOfFirstItem + 1}–{Math.min(indexOfLastItem, pendingReviews.length)})</h4>
          <div className="review-list">
            {currentItems.map((review) => (
              <div className="pending-card" key={review.id}>
                <div className="pending-card-header">
                  <h3>{review.name}</h3>
                  <span className="pending-status">{review.status}</span>
                </div>
                <p>Date: {review.date}</p>
                <p>Type: {review.screeningType}</p>
                <button className="review-btn" onClick={() => handleSubmit(review.id)}>
                  Review
                </button>
              </div>
            ))}
          </div>

          {/* Pagination Buttons */}
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