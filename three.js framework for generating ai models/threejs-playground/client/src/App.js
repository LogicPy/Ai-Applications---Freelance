// src/App.js
import React, { useState } from 'react';
import ThreeScene from './components/ThreeScene';
import CodeInputForm from './components/CodeInputForm';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

function App() {
  const [submittedCode, setSubmittedCode] = useState('');

  const handleCodeSubmit = (code) => {
    setSubmittedCode(code);
    console.log('Code submitted:', code);
  };

  const handleClearScene = () => {
    setSubmittedCode('// Clear the scene');
  };

  return (
    <ErrorBoundary>
      <div className="app-container">
        <ThreeScene code={submittedCode} />
        <CodeInputForm onSubmit={handleCodeSubmit} onClear={handleClearScene} />
      </div>
    </ErrorBoundary>
  );
}

export default App;
