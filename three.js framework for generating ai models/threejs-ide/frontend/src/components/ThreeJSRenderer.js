// frontend/src/components/ThreeJSRenderer.js

import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'; // Add this import
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter'; // Import OBJExporter
import * as esprima from 'esprima';

const ThreeJSRenderer = ({ code }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);  // Reference to the scene for exporting
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);

  useEffect(() => {
    if (!code) return;

    // Clear any existing scene
    mountRef.current.innerHTML = '';

    // Create a new scene, camera, and renderer
    const scene = new THREE.Scene();
    sceneRef.current = scene;  // Assign the scene to the ref for later access

    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 2, 5); // Adjust camera position for better view
    cameraRef.current = camera;  // Store the camera in ref for later use

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;  // Store the renderer for export

    // Add OrbitControls for mouse interaction
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = false;
    controls.minDistance = 1;
    controls.maxDistance = 500;
    controls.maxPolarAngle = Math.PI / 2;

    // Log the generated code for debugging
    console.log('Executing Three.js Code:', code);

    // Validate the generated code syntax using Esprima
    try {
      esprima.parseScript(code);
    } catch (parseError) {
      console.error('Generated code has syntax errors:', parseError.message);
      return; // Stop execution if syntax errors are found
    }

    // Create a function to execute the generated code
    const executeCode = () => {
      try {
        console.log('Executing Function Constructor with code:', code);
        const func = new Function('THREE', 'scene', 'camera', 'renderer', code);
        func(THREE, scene, camera, renderer);
        console.log('Code executed successfully.');
      } catch (error) {
        console.error('Error executing generated Three.js code:', error);
      }
    };

    executeCode();

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update(); // Update controls on each frame
      renderer.render(scene, camera);
    };

    animate();

    // Cleanup on component unmount
    return () => {
      mountRef.current.innerHTML = '';
    };
  }, [code]);

  // Export function to save the model as an OBJ file
  const exportModelAsObj = () => {
    const exporter = new OBJExporter();

    if (sceneRef.current && sceneRef.current.children.length > 0) {
      const objData = exporter.parse(sceneRef.current);  // Export the current scene
      const blob = new Blob([objData], { type: 'text/plain' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'model.obj';
      link.click();
      console.log('Model exported as OBJ.');
    } else {
      console.error('No objects found in the scene for export.');
    }
  };

  return (
    <div>
      <div ref={mountRef} style={{ width: '100%', height: '100vh' }} />
      <button onClick={exportModelAsObj}>Export as OBJ</button>
    </div>
  );
};

export default ThreeJSRenderer;
