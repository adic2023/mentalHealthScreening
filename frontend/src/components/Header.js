import React from 'react';
import { Link } from "react-router-dom";
import './Header.css';

export default function Header({ showSignup = true }) {
  return (
    <header className="header">
      <h1 className="header-title">🧠 Mental Health Screening Exam</h1>
      <nav className="header-nav">
        <a href="https://www.thelivelovelaughfoundation.org/find-help/helplines">Resources</a>
        <Link to="/screeningTest">Test</Link>
        <a href="https://www.who.int/news-room/fact-sheets/detail/mental-disorders">Common Issues</a>
        {showSignup && (
          <button className="header-button">Sign Up</button>
        )}
      </nav>
    </header>
  );
}