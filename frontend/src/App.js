// App.js
import './App.css';
import Test from './pages/Test.js';
import Home from './pages/Home.js'
import Review from './pages/Review.js';
import Results from './pages/Results.js';
import ParentTeacherDash from './pages/ParentTeacherDash.js';
import {Routes, Route} from "react-router-dom"
import PsychDash from './pages/PsychDash.js';
import ChildRegistration from './pages/ChildRegistration.js';

function App() {
  return (
    <div className="App">
       <Routes> 
          <Route path="/" element={<Home/>}/>
          <Route path="/ScreeningTest" element={<Test />}/>
          <Route path="/PsychDashboard" element={<PsychDash/>}/>
          <Route path="/ParentTeacherDashboard" element={<ParentTeacherDash/>}/>
          <Route path="/ChildRegistration" element={<ChildRegistration />} />
          <Route path="/review/:id" element={<Review/>}/>
          <Route path="/results/:id" element={<Results/>}/>
        </Routes>
    </div>
  );
}

export default App;