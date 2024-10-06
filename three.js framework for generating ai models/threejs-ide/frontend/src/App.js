// frontend/src/App.js

import React, { useState } from 'react';
import axios from 'axios';
import ThreeJSRenderer from './components/ThreeJSRenderer';
import CodeDisplay from './components/CodeDisplay';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt.');
      return;
    }

    setLoading(true);
    setError('');
    setCode('');

    try {
      const response = await axios.post(
        '/api/generate-threejs', // Proxy to backend
        { prompt },
        {
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': process.env.REACT_APP_API_KEY,
          },
        }
      );
      setCode(response.data.code);
    } catch (err) {
      console.error('Error generating code:', err);
      setError('An error occurred while generating code.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Three.js Ai Prompter (3D Ai-model-generator)</h1>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your 3D model or 3D scene..."
          rows="4"
          cols="50"
        />
        <br />
        <button onClick={handleGenerate} disabled={loading}>
          {loading ? 'Generating...' : 'Generate Three.js Code'}
        </button>
        {error && <p className="error">{error}</p>}
      </header>
      <main>
        {/* Render the 3D scene */}
        {code && <ThreeJSRenderer code={code} />}
        
        {/* Render the code display below the scene */}
        {code && <CodeDisplay code={code} />}
      </main>
    </div>
  );
}

export default App;
