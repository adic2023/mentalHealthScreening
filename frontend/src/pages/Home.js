import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Select from 'react-select';
import Header from '../components/Header';
import './Home.css';

export default function Home() {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState(null);
  const [isSignup, setIsSignup] = useState(false);

  const roleOptions = [
    { value: 'student', label: 'Student' },
    { value: 'parent', label: 'Parent' },
    { value: 'teacher', label: 'Teacher' },
    { value: 'psychologist', label: 'Psychologist' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password || !selectedRole) {
      alert('Please fill in all fields and select a role.');
      return;
    }

    try {
      const endpoint = isSignup ? '/auth/signup' : '/auth/login';
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          role: selectedRole.value
        })
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.detail || 'Something went wrong');
        return;
      }

      if (isSignup) {
        alert('Signup successful. Please log in.');
        setIsSignup(false);
        return;
      }

      // Login flow — Store necessary user details
      localStorage.setItem('userId', data.user_id);
      localStorage.setItem('userRole', data.role);
      localStorage.setItem('userEmail', email);

      // Navigate based on role
      if (data.role === 'psychologist') {
        navigate('/PsychDashboard');
      } else if (data.role === 'parent' || data.role === 'teacher') {
        navigate('/ParentTeacherDashboard');
      } else if (data.role === 'student') {
        // Student goes to child registration/login page
        navigate('/ChildRegistration');
      } else {
        // Fallback - shouldn't happen with current roles
        navigate('/ScreeningTest');
      }

    } catch (err) {
      console.error(err);
      alert('Network error');
    }
  };

  return (
    <div className="home-container">
      <Header />
      <main className="home-main">
        <form className="home-form" onSubmit={handleSubmit}>
          <h2 className="home-title">
            {isSignup ? 'Sign Up to Begin Screening' : 'Login to Begin Screening'}
          </h2>
          <input
            type="email"
            placeholder="Email"
            className="home-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            className="home-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Select
            options={roleOptions}
            value={selectedRole}
            onChange={(option) => setSelectedRole(option)}
            placeholder="Select Role"
            className="home-select"
            classNamePrefix="react-select"
          />
          <button type="submit" className="home-button">
            {isSignup ? 'Sign Up' : 'Login'}
          </button>
          <p style={{ textAlign: 'center', marginTop: '1rem' }}>
            {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
            <span
              onClick={() => setIsSignup(!isSignup)}
              style={{ color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
            >
              {isSignup ? 'Login here' : 'Sign up here'}
            </span>
          </p>
        </form>
      </main>
    </div>
  );
}