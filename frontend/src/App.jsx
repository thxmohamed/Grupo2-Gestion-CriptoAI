import './App.css'
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import Header from "./components/Header"
import HomePage from './components/HomePage';
import Dashboard from './components/Dashboard';
import Record from './components/Record'
import NotFound from './components/NotFound';


function App() {
  
  return (
      <Router>
          <div className="container">
          <Header></Header>
            <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/historial" element={<Record />} />

              <Route path="*" element={<NotFound/>} />
            </Routes>
          </div>
      </Router>
  );
}

export default App