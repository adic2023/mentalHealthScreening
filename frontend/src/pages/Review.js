import React, { useEffect, useState } from "react";
import axios from "axios";
import "./review.css";
import { useParams, useNavigate } from 'react-router-dom';

const CATEGORIES = {
  EMOTIONAL: [2, 7, 12, 15, 23],
  CONDUCT: [4, 6, 11, 17, 21],
  HYPERACTIVITY: [1, 9, 14, 20, 24],
  PEER: [5, 10, 13, 18, 22],
  PROSOCIAL: [0, 3, 8, 16, 19],
};

const Review = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [reviewData, setReviewData] = useState(null);
  const [expanded, setExpanded] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [reviewText, setReviewText] = useState("");
  const [loading, setLoading] = useState(true);
  const [showQuestion, setShowQuestion] = useState(null);

  useEffect(() => {
    if (!testId) return;

    setLoading(true);
    axios.get(`http://localhost:8000/reviews/${testId}`)
      .then(res => {
        setReviewData(res.data);
        setReviewText(res.data.psychologist_review || "");
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load review:", err);
        setLoading(false);
      });
  }, [testId]);

  const toggleExpand = (index) => {
    setExpanded(prev => (prev === index ? null : index));
    setShowQuestion(null);
  };

  const toggleQuestion = (index) => {
    setShowQuestion(prev => (prev === index ? null : index));
  };

  const handleReviewSubmit = () => {
    setLoading(true);
    axios.post("http://localhost:8000/reviews/submit", {
      child_id: reviewData?.child_info?.child_id,
      psychologist_review: reviewText,
      reviewer_id: "reviewer123"
    }).then(() => {
      setEditMode(false);
      setLoading(false);
      alert("Review submitted successfully!");
      navigate('/PsychDashboard');  // Corrected casing
    }).catch(err => {
      console.error("Failed to submit review:", err);
      setLoading(false);
      alert("Submission failed. Please try again.");
    });
  };

  const getScore = (index, type) => {
    const respondent = reviewData?.tests?.[type];
    const found = respondent?.confirm_options?.find(q => q.question_index === index);
    return found?.selected_option || "-";
  };

  const getCategoryScore = (categoryKey, type) => {
    return reviewData?.tests?.[type]?.scores?.subscale_scores?.[categoryKey.toLowerCase()] ?? 0;
  };

  const getChatHistory = (index, type) => {
    const vectorResponses = reviewData?.tests?.[type]?.vector_responses ?? [];
    const conversations = vectorResponses
      .filter(entry => entry.question_index === index)
      .map(entry => entry.text);

    if (conversations.length === 0) return <i>No conversation found</i>;

    return (
      <div className="conversation-history">
        {conversations.map((text, i) => (
          <div key={i} className="conversation-item">
            <span className="conversation-text">{text}</span>
          </div>
        ))}
      </div>
    );
  };

  const getCompletedTestTypes = () => {
    if (!reviewData?.tests) return [];
    return Object.keys(reviewData.tests).filter(type =>
      reviewData.tests[type] && reviewData.tests[type].submitted
    );
  };

  if (loading) {
    return <div className="review-container"><div className="loading">Loading review data...</div></div>;
  }

  if (!reviewData) {
    return <div className="review-container"><div className="error">Failed to load review data</div></div>;
  }

  const completedTests = getCompletedTestTypes();
  const questions = reviewData.questions ?? [];

  return (
    <div className="review-container">
      <div className="review-header">
        <div className="child-info">
          <h1>Review for {reviewData?.child_info?.name || "Unknown Child"}</h1>
          <div className="child-details">
            <span>Age: {reviewData?.child_info?.age || "Unknown"}</span>
            <span>•</span>
            <span>Child ID: {reviewData?.child_id}</span>
          </div>
          <div className="test-status">
            <strong>Tests completed by:</strong> {completedTests.map(type => type.charAt(0).toUpperCase() + type.slice(1)).join(', ')}
          </div>
        </div>
        <div className="review-status">
          <span className={`status-badge ${reviewData.status}`}>
            {reviewData.status === 'pending' ? 'Pending Review' : 'Reviewed'}
          </span>
        </div>
      </div>

      {Object.entries(CATEGORIES).map(([catName, indices]) => {
        const avgScore = completedTests.length > 0
          ? Math.round(completedTests.reduce((sum, type) =>
            sum + getCategoryScore(catName, type), 0) / completedTests.length)
          : 0;

        return (
          <div key={catName} className="category-block">
            <h2 className="category-title">
              {catName} - {avgScore}
              <span className="category-subtitle">({indices.length} questions)</span>
            </h2>
            <div className="questions-table">
              <div className="table-header">
                <div className="col-question">Q#</div>
                <div className="col-respondent">Student</div>
                <div className="col-respondent">Parent</div>
                <div className="col-respondent">Teacher</div>
                <div className="col-actions">Actions</div>
              </div>

              {indices.map((index) => (
                <div key={index} className="question-row">
                  <div className="question-main">
                    <div className="col-question">{index + 1}</div>
                    <div className="col-respondent">{getScore(index, "child")}</div>
                    <div className="col-respondent">{getScore(index, "parent")}</div>
                    <div className="col-respondent">{getScore(index, "teacher")}</div>
                    <div className="col-actions">
                      <button
                        className="action-btn question-btn"
                        onClick={() => toggleQuestion(index)}
                      >
                        {showQuestion === index ? "Hide Q" : "Show Q"}
                      </button>
                      <button
                        className="action-btn view-btn"
                        onClick={() => toggleExpand(index)}
                      >
                        {expanded === index ? "Hide" : "View"}
                      </button>
                    </div>
                  </div>

                  {showQuestion === index && (
                    <div className="question-display">
                      <strong>Question {index + 1}:</strong> {questions[index]}
                    </div>
                  )}

                  {expanded === index && (
                    <div className="chat-history-section">
                      <div className="chat-columns">
                        <div className="chat-column">
                          <div className="chat-header">Student Conversation</div>
                          <div className="chat-content">
                            {getChatHistory(index, "child")}
                          </div>
                        </div>
                        <div className="chat-column">
                          <div className="chat-header">Parent Conversation</div>
                          <div className="chat-content">
                            {getChatHistory(index, "parent")}
                          </div>
                        </div>
                        <div className="chat-column">
                          <div className="chat-header">Teacher Conversation</div>
                          <div className="chat-content">
                            {getChatHistory(index, "teacher")}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}

      <div className="review-footer">
        <div className="ai-review-section">
          <h2 className="section-title">Psychologist Review</h2>
          <div className="review-editor">
            <textarea
              className={`review-textarea ${editMode ? 'editable' : 'readonly'}`}
              readOnly={!editMode}
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              placeholder="Enter your professional assessment and recommendations here..."
            />
            <div className="review-actions">
              {!editMode ? (
                <button
                  className="edit-btn"
                  onClick={() => setEditMode(true)}
                >
                  Edit Review
                </button>
              ) : (
                <div className="edit-actions">
                  <button
                    className="cancel-btn"
                    onClick={() => {
                      setEditMode(false);
                      setReviewText(reviewData.psychologist_review || "");
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    className="submit-btn"
                    onClick={handleReviewSubmit}
                    disabled={!reviewText.trim()}
                  >
                    Submit Review
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Review;