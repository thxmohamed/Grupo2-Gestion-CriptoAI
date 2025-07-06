import './App.css'
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import { useState, useEffect } from 'react'
import Header from "./components/Header"
import HomePage from './components/HomePage';
import AdminPage from './components/AdminPage';
import UserMetricsPage from './components/UserMetricsPage';
import Dashboard from './components/Dashboard';
import Portfolio from './components/Portfolio';
import Record from './components/Record'
import NotFound from './components/NotFound';
import Register from './components/Register';
import Login from './components/Login';


function App() {
  const [user, setUser] = useState(null);

  // Check for stored user data on app load
  useEffect(() => {
    const storedUser = localStorage.getItem('userData');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('userData');
      }
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('userData');
  };
  
  return (
      <Router>
          <div className="container" style={{ minHeight: '100vh' }}>
          <Header user={user} onLogout={handleLogout}></Header>
            <main style={{ flex: 1 }}>
              <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/register" element={<Register />} />
              <Route path="/login" element={<Login onLogin={handleLogin} />} />
              <Route path="/admin" element={<AdminPage />} />
               <Route path="/admin/user/:userId" element={<UserMetricsPage />} />
              <Route path="/dashboard" element={<Dashboard user={user} />} />
              <Route path="/portfolio" element={<Portfolio user={user} />} />
              <Route path="/historial" element={<Record />} />

                <Route path="*" element={<NotFound/>} />
              </Routes>
            </main>
          </div>
      </Router>
  );
}

export default App