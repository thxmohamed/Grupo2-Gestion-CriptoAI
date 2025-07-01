import './App.css'
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import Header from "./components/Header"
import HomePage from './components/HomePage';
import AdminPage from './components/AdminPage';
import UserMetricsPage from './components/UserMetricsPage';
import Dashboard from './components/Dashboard';
import Portfolio from './components/Portfolio';
import Record from './components/Record'
import NotFound from './components/NotFound';


function App() {
  
  return (
      <Router>
          <div className="container" style={{ minHeight: '100vh' }}>
          <Header></Header>
            <main style={{ flex: 1 }}>
              <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/admin" element={<AdminPage />} />
               <Route path="/admin/user/:userId" element={<UserMetricsPage />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/historial" element={<Record />} />

                <Route path="*" element={<NotFound/>} />
              </Routes>
            </main>
          </div>
      </Router>
  );
}

export default App