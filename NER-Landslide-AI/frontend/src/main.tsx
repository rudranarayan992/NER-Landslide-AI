import React from 'react';
import ReactDOM from 'react-dom/client';
import { GISMap } from './components/GISMap';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <GISMap />
  </React.StrictMode>,
);
