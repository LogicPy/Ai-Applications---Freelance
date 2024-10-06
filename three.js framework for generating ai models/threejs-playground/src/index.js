// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css'; // Global styles

ReactDOM.render(
  // <React.StrictMode> // Optional: Uncomment during development
    <App />,
  // </React.StrictMode>,
  document.getElementById('root')
);
