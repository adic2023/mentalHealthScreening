// App.js
import './App.css';
import Test from './pages/Test.js';
import Home from './pages/Home.js'
import {Routes, Route} from "react-router-dom"

function App() {
  return (
    <div className="App">
       <Routes> 
          <Route path="/" element={<Home/>}/>
          <Route path="/ScreeningTest" element={<Test />}/>
        </Routes>
    </div>
  );
}

export default App;
