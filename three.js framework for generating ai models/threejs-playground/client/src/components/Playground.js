import React, { useState, useRef, useEffect } from 'react';
import MonacoEditor from 'react-monaco-editor';
import * as THREE from 'three';

const Playground = () => {
  const [code, setCode] = useState('// Write your code here!');
  const [zoom, setZoom] = useState(5); // Camera zoom level
  const mountRef = useRef(null);
  const editorRef = useRef(null); // Store the editor instance
  let camera, renderer, scene;

  const handleEditorChange = (newValue) => {
    setCode(newValue);
  };

  const editorDidMount = (editor) => {
    editorRef.current = editor; // Store the editor instance in ref
  };

  const initializeScene = () => {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = zoom;
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    mountRef.current.innerHTML = ''; // Clear existing rendering
    mountRef.current.appendChild(renderer.domElement);
  };

  useEffect(() => {
    initializeScene();

    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (editorRef.current) {
        editorRef.current.layout(); // Adjust editor layout on window resize
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      mountRef.current.removeChild(renderer.domElement);
    };
  }, []);

  const executeCode = () => {
    try {
      const func = new Function('THREE', 'scene', 'camera', 'renderer', code);
      initializeScene();
      func(THREE, scene, camera, renderer); // Execute the user-provided code
    } catch (err) {
      console.error('Error executing code:', err);
    }
  };

  const zoomIn = () => {
    if (camera) {
      setZoom((prevZoom) => {
        const newZoom = Math.max(prevZoom - 1, 1);
        camera.position.z = newZoom; // Update camera position directly after zoom
        return newZoom;
      });
    } else {
      console.error('Camera is not defined');
    }
  };

  const zoomOut = () => {
    if (camera) {
      setZoom((prevZoom) => {
        const newZoom = prevZoom + 1;
        camera.position.z = newZoom; // Update camera position directly after zoom
        return newZoom;
      });
    } else {
      console.error('Camera is not defined');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div ref={mountRef} style={{ flex: 1 }}></div>
      <div style={{ flex: 1 }}>
        <MonacoEditor
          height="500px"
          width="100%"
          language="javascript"
          theme="vs-dark"
          value={code}
          onChange={handleEditorChange}
          editorDidMount={editorDidMount}
        />
        <button onClick={executeCode}>Run Code</button>
        <br />
        <button onClick={zoomIn}>Zoom In</button>
        <button onClick={zoomOut}>Zoom Out</button>
      </div>
    </div>
  );
};

export default Playground;
