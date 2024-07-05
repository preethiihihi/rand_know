import logo from './logo.svg';
import './App.css';
import { BrowserRouter as Router, Route,Routes, Link } from 'react-router-dom';
import ContentDisplay from './con1';
import News from './con2';

function App() {
    return (
      <Router>
          <div className="App">
              <header>
              <h1>Explore</h1>
                  <nav>
                      <ul>
                          <li>
                              <Link to="/">Home</Link>
                          </li>
                          <li>
                              <Link to="/India_news">India News</Link>
                          </li>
                      </ul>
                  </nav>
                 
              </header>
              <main>
                  <Routes>
                      <Route path="/" element={<ContentDisplay />} />
                      <Route path="/India_news" element={<News />} />
                  </Routes>
              </main>
          </div>
      </Router>
  );
    
  
}

export default App;
