// src/components/CodeInputForm.js
import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import './CodeInputForm.css';

function CodeInputForm({ onSubmit }) {
  const [code, setCode] = useState('// Enter your Three.js code here\n');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    try {
      onSubmit(code);
      setError('');
      setSuccess('Code submitted successfully!');
    } catch (err) {
      setError('Error executing code.');
      setSuccess('');
      console.error(err);
    }
  };

  return (
    <div className="code-input-form">
      <h2>Wayne's Personal Three.js Playground</h2>
      <form onSubmit={handleSubmit}>
        <label htmlFor="code">Code:</label>
        <Editor
          height="300px"
          defaultLanguage="javascript"
          defaultValue="// Write your Three.js code here"
          value={code}
          onChange={(value) => setCode(value)}
          theme="vs-dark"
        />
        {error && <p className="error-message">{error}</p>}
        {success && <p className="success-message">{success}</p>}
        <button type="submit">Run Code</button>
      </form>
    </div>
  );
}

export default CodeInputForm;
