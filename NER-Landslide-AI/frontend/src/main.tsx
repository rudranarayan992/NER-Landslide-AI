import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { GISMap } from './components/GISMap';
import { MobileApp } from './components/MobileApp';
import './styles.css';

function App() {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return isMobile ? <MobileApp isMobile={true} /> : <GISMap />;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
