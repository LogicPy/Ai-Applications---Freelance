// src/components/CodeInputForm.js
import React, { useState } from 'react';
import './CodeInputForm.css';
import Editor from '@monaco-editor/react'; // Ensure this library is installed

function CodeInputForm({ onSubmit }) {
  const [code, setCode] = useState('// Enter your Three.js code here\n');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedSnippet, setSelectedSnippet] = useState('');

  const snippets = {
    'Default Cube': '// Default Three.js setup\n',
    'Tetris-like 3D Effect': `// Tetris-like 3D effect
const tetrominoes = [];
let tetrominoIndex = 0;

// Create a floor plane
const floorGeometry = new THREE.PlaneGeometry(10, 0.1);
const floorMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff, opacity: 0.5, transparent: true });
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -5;
scene.add(floor);

// Define the shapes and their colors
const shapes = [
  { geometry: new THREE.BoxGeometry(1, 1, 1), color: 0xff0000 }, // Red cube
  { geometry: new THREE.BoxGeometry(1, 2, 1), color: 0x00ff00 }, // Green rectangle
  { geometry: new THREE.BoxGeometry(2, 1, 1), color: 0x0000ff }, // Blue rectangle
  { geometry: new THREE.BoxGeometry(2, 2, 1), color: 0xffff00 }, // Yellow square
  { geometry: new THREE.BoxGeometry(1, 1, 2), color: 0xff00ff }, // Magenta cube
];

// Function to create a new tetromino
function createTetromino() {
  const shape = shapes[Math.floor(Math.random() * shapes.length)];
  const tetromino = new THREE.Mesh(shape.geometry, new THREE.MeshBasicMaterial({ color: shape.color }));
  tetromino.position.z = 0;
  tetromino.position.y = 10;
  tetromino.rotation.x = Math.PI / 2;
  tetrominoes.push(tetromino);
  scene.add(tetromino);
}

// Function to update and move the tetrominoes
function updateTetrominoes() {
  for (let i = tetrominoes.length - 1; i >= 0; i--) {
    const tetromino = tetrominoes[i];
    tetromino.position.y -= 0.1;
    if (tetromino.position.y < -5) {
      // Check for horizontal lines and clear them
      const lines = [];
      for (let j = -5; j < 0; j++) {
        let lineComplete = true;
        for (let k = -5; k < 5; k++) {
          let occupied = false;
          for (let l = 0; l < tetrominoes.length; l++) {
            if (tetrominoes[l].position.y === j && tetrominoes[l].position.x === k) {
              occupied = true;
              break;
            }
          }
          if (!occupied) {
            lineComplete = false;
            break;
          }
        }
        if (lineComplete) {
          lines.push(j);
        }
      }
      for (let j = lines.length - 1; j >= 0; j--) {
        for (let k = 0; k < tetrominoes.length; k++) {
          if (tetrominoes[k].position.y === lines[j]) {
            scene.remove(tetrominoes[k]);
            tetrominoes.splice(k, 1);
          }
        }
        for (let k = 0; k < tetrominoes.length; k++) {
          if (tetrominoes[k].position.y > lines[j]) {
            tetrominoes[k].position.y -= 1;
          }
        }
      }
      // Remove the tetromino that reached the bottom
      scene.remove(tetromino);
      tetrominoes.splice(i, 1);
    }
  }
}

// Create a new tetromino every second
setInterval(createTetromino, 1000);

// Animate the scene
function animate() {
  requestAnimationFrame(animate);
  updateTetrominoes();
  renderer.render(scene, camera);
}
animate();`,
    // Add more snippets as needed
  };

  const handleSnippetChange = (e) => {
    const selected = e.target.value;
    setSelectedSnippet(selected);
    if (snippets[selected]) {
      setCode(snippets[selected]);
    }
  };

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
      <h2>Enter Your Three.js Code</h2>
      <form onSubmit={handleSubmit}>
        <label htmlFor="snippets">Choose a Snippet:</label>
        <select id="snippets" value={selectedSnippet} onChange={handleSnippetChange}>
          <option value="">-- Select a Snippet --</option>
          {Object.keys(snippets).map((snippetName) => (
            <option key={snippetName} value={snippetName}>
              {snippetName}
            </option>
          ))}
        </select>
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
