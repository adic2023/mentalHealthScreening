// Updated App.js routing
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Test from './pages/Test';
import ParentTeacherDash from './pages/ParentTeacherDash';
import ChildRegistration from './pages/ChildRegistration';
import Review from './pages/Review';
import Results from './pages/Results';
import PsychDash from './pages/PsychDash';
import ChildDashboard from './pages/ChildDashboard'; // Ensure this file exists
import ThankYou from './pages/ThankYou';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/Test" element={<Test />} />
        <Route path="/ParentTeacherDashboard" element={<ParentTeacherDash />} />
        <Route path="/ChildDashboard" element={<ChildDashboard />} />
        <Route path="/ChildRegistration" element={<ChildRegistration />} />
        <Route path="/review/:testId" element={<Review />} />
        <Route path="/test-results/:childId" element={<Results />} />
        <Route path="/PsychDashboard" element={<PsychDash />} />
        <Route path="/thank-you" element={<ThankYou />} />
      </Routes>
    </Router>
  );
}

export default App;