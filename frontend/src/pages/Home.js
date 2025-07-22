import React from 'react';
import { Link } from "react-router-dom"
// import Navbar from './Navbar';
import './Home.css'; 

function Home() {
  return (
    <div className="home-page">
      <p>Go To <strong> <Link to ="/screeningTest">test</Link></strong></p>
    </div>
  );
}

export default Home;
